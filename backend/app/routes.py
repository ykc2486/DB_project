from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from argon2 import PasswordHasher
from datetime import datetime
import uuid
import os

from . import models, schemas
from .database import get_db
from .auth import authenticate_user, get_token, verify_token

router = APIRouter()
UPLOAD_DIRECTORY = "./uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

"""
-----------------------------
        User Routes
-----------------------------
"""

@router.post("/users/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.createUser, db: Session = Depends(get_db)):
    ph = PasswordHasher()
    password_hash = ph.hash(user.password)
    
    try:
        query = text("""
            INSERT INTO users (username, email, password_hash, address, is_active, join_date)
            VALUES (:username, :email, :password_hash, :address, true, now())
            RETURNING user_id
        """)
        
        result = db.execute(query, {
            "username": user.username,
            "email": user.email,
            "password_hash": password_hash,
            "address": user.address
        })
        
        row = result.fetchone()
        new_user_id = row.user_id

        if user.phones:
            for p in user.phones:
                db.execute(
                    text("INSERT INTO phones (user_id, phone_number) VALUES (:user_id, :phone_number)"), 
                    {"user_id": new_user_id, "phone_number": p}
                )
        
        db.commit()
        
    except IntegrityError as e:
        db.rollback()
        
        error_detail = str(e.orig)
        message = "Data integrity error"
        
        if "ix_users_username" in error_detail:
            message = f"username: '{user.username}' has already been registered"
        elif "ix_users_email" in error_detail:
            message = f"email: '{user.email}' has already been registered"

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

    return read_user(new_user_id, db)

@router.get("/users/me", response_model=schemas.UserResponse)
def read_current_user(db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    return read_user(user_id, db)

@router.get("/users/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.execute(text("SELECT * FROM users WHERE user_id = :user_id"), {"user_id": user_id}).fetchone()
    if not db_user: raise HTTPException(status_code=404, detail="User not found")
    phones = db.execute(text("SELECT phone_number FROM phones WHERE user_id = :user_id"), {"user_id": user_id}).fetchall()
    return schemas.UserResponse(
        user_id=db_user.user_id, username=db_user.username, email=db_user.email,
        is_active=db_user.is_active, join_date=db_user.join_date,
        address=db_user.address, phones=[p.phone_number for p in phones]
    )

@router.post("/login", response_model=schemas.Token)
def login(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(user_login.username, user_login.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return {"access_token": get_token(user.user_id), "token_type": "bearer"}

"""
-----------------------------
        Item Routes
-----------------------------
"""

@router.post("/items/", response_model=schemas.ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    condition: str = Form(...),
    price: int = Form(0),
    exchange_type: bool = Form(False),
    desired_item: Optional[str] = Form(None),
    category: int = Form(...),
    images: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    # 配合 auth.py，從 Query 參數接收 token 並得到 user_id (int)
    user_id: int = Depends(verify_token) 
):
    if not user_id: raise HTTPException(status_code=401, detail="Invalid token")

    # 解決 ForeignKeyViolation：自動建立分類 
    if not db.execute(text("SELECT 1 FROM categories WHERE category_id = :category"), {"category": category}).fetchone():
        db.execute(text("INSERT INTO categories (category_id, category_name) VALUES (:category, :name)"), 
                   {"category": category, "name": f"Category {category}"})
        db.commit()

    img_paths = []
    if images:
        for img in images:
            if not img.filename: continue
            file_ext = img.filename.split(".")[-1]
            unique_name = f"{uuid.uuid4()}.{file_ext}"
            save_path = os.path.join(UPLOAD_DIRECTORY, unique_name)
            with open(save_path, "wb") as buffer:
                # 解決 500 UnicodeDecodeError：讀取二進位數據
                buffer.write(img.file.read()) 
            img_paths.append(f"/api/images/{unique_name}")

    # Insert Item
    query = text("""
        INSERT INTO items (title, description, condition, owner_id, price, exchange_type, status, desired_item, category, total_images, post_date)
        VALUES (:title, :description, :condition, :owner_id, :price, :exchange_type, true, :desired_item, :category, :total_images, now())
        RETURNING item_id, post_date
    """)
    result = db.execute(query, {
        "title": title, "description": description, "condition": condition,
        "owner_id": user_id, "price": price, "exchange_type": exchange_type,
        "desired_item": desired_item, "category": category, "total_images": len(img_paths)
    }).fetchone()
    
    new_item_id = result.item_id
    post_date = result.post_date
    
    # Insert Images
    for path in img_paths:
        db.execute(text("INSERT INTO item_images (item_id, image_data_name) VALUES (:item_id, :path)"), 
                   {"item_id": new_item_id, "path": path})
    
    db.commit()
    
    return schemas.ItemResponse(
        item_id=new_item_id, title=title, description=description,
        condition=condition, owner_id=user_id, post_date=post_date,
        price=price, exchange_type=exchange_type, status=True,
        desired_item=desired_item, total_images=len(img_paths),
        category=category, images=img_paths
    )

@router.get("/items/", response_model=List[schemas.ItemResponse])
def read_items(
    db: Session = Depends(get_db), 
    search: Optional[str] = None, 
    sort: Optional[str] = None
):
    # 基礎 SQL 語句
    sql_str = "SELECT * FROM items WHERE status = true"
    params = {}

    # 實作 Search/Filter 功能 (使用 LIKE 進行模糊搜尋)
    if search:
        sql_str += " AND (title LIKE :search OR description LIKE :search)"
        params["search"] = f"%{search}%"

    # 實作 Sort 功能
    if sort == "price_asc":
        sql_str += " ORDER BY price ASC"
    elif sort == "price_desc":
        sql_str += " ORDER BY price DESC"
    else:
        # 預設按日期排序 (最新上架)
        sql_str += " ORDER BY post_date DESC"

    # 執行原生 SQL
    items = db.execute(text(sql_str), params).fetchall()
    
    result = []
    for i in items:
        # 取得圖片的 SQL 保持不變
        imgs = db.execute(text("SELECT image_data_name FROM item_images WHERE item_id = :item_id"), 
                          {"item_id": i.item_id}).fetchall()
        result.append(schemas.ItemResponse(
            item_id=i.item_id, title=i.title, description=i.description,
            condition=i.condition, owner_id=i.owner_id, post_date=i.post_date,
            price=i.price, exchange_type=i.exchange_type, status=i.status,
            desired_item=i.desired_item, total_images=i.total_images,
            category=i.category, images=[img.image_data_name for img in imgs]
        ))
    return result

@router.get("/items/{item_id}", response_model=schemas.ItemResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.execute(text("SELECT * FROM items WHERE item_id = :item_id"), {"item_id": item_id}).fetchone()
    if not item: raise HTTPException(status_code=404, detail="Item not found")
    imgs = db.execute(text("SELECT image_data_name FROM item_images WHERE item_id = :item_id"), {"item_id": item_id}).fetchall()
    return schemas.ItemResponse(
        item_id=item.item_id, title=item.title, description=item.description,
        condition=item.condition, owner_id=item.owner_id, post_date=item.post_date,
        price=item.price, exchange_type=item.exchange_type, status=item.status,
        desired_item=item.desired_item, total_images=item.total_images,
        category=item.category, images=[img.image_data_name for img in imgs]
    )

@router.get("/images/{filename}")
def get_image(filename: str):
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    if not os.path.exists(file_path): raise HTTPException(status_code=404)
    return FileResponse(file_path)

"""
-----------------------------
        Wishlist Routes
-----------------------------
"""
@router.post("/wishlist/", response_model=schemas.WishlistResponse)
def add_to_wishlist(wish_in: schemas.WishlistCreate, db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    # Insert Wishlist
    if query := db.execute(text("SELECT 1 FROM wishlist WHERE user_id = :user_id AND item_id = :item_id"), {"user_id": user_id, "item_id": wish_in.item_id}).fetchone():
        raise HTTPException(status_code=400, detail="Item already in wishlist")
    query = text("""
        INSERT INTO wishlist (user_id, item_id, added_date)
        VALUES (:user_id, :item_id, now())
        RETURNING added_date
    """)
    result = db.execute(query, {"user_id": user_id, "item_id": wish_in.item_id}).fetchone()
    added_date = result.added_date
    db.commit()
    
    # Fetch Item
    item_obj = db.execute(text("SELECT * FROM items WHERE item_id = :item_id"), {"item_id": wish_in.item_id}).fetchone()
    item_response = None
    if item_obj:
        imgs = db.execute(text("SELECT image_data_name FROM item_images WHERE item_id = :item_id"), {"item_id": item_obj.item_id}).fetchall()
        item_response = schemas.ItemResponse(
            item_id=item_obj.item_id, title=item_obj.title, description=item_obj.description,
            condition=item_obj.condition, owner_id=item_obj.owner_id, post_date=item_obj.post_date,
            price=item_obj.price, exchange_type=item_obj.exchange_type, status=item_obj.status,
            desired_item=item_obj.desired_item, total_images=item_obj.total_images,
            category=item_obj.category, images=[img.image_data_name for img in imgs]
        )

    return schemas.WishlistResponse(
        user_id=user_id,
        item_id=wish_in.item_id,
        added_date=added_date,
        item=item_response
    )

@router.get("/wishlist/", response_model=List[schemas.WishlistResponse])
def get_wishlist(db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    wishlist_items = db.execute(text("SELECT * FROM wishlist WHERE user_id = :user_id"), {"user_id": user_id}).fetchall()
    result = []
    for w in wishlist_items:
        # Fetch Item
        item_obj = db.execute(text("SELECT * FROM items WHERE item_id = :item_id"), {"item_id": w.item_id}).fetchone()
        item_response = None
        if item_obj:
            imgs = db.execute(text("SELECT image_data_name FROM item_images WHERE item_id = :item_id"), {"item_id": item_obj.item_id}).fetchall()
            item_response = schemas.ItemResponse(
                item_id=item_obj.item_id, title=item_obj.title, description=item_obj.description,
                condition=item_obj.condition, owner_id=item_obj.owner_id, post_date=item_obj.post_date,
                price=item_obj.price, exchange_type=item_obj.exchange_type, status=item_obj.status,
                desired_item=item_obj.desired_item, total_images=item_obj.total_images,
                category=item_obj.category, images=[img.image_data_name for img in imgs]
            )
        
        result.append(schemas.WishlistResponse(
            user_id=w.user_id,
            item_id=w.item_id,
            added_date=w.added_date,
            item=item_response
        ))
    return result

"""
-----------------------------
        Transaction Routes
-----------------------------
"""

@router.post("/transactions/", response_model=schemas.TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(trans_in: schemas.TransactionCreate, db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    # Check if item exists and is available
    item = db.execute(text("SELECT * FROM items WHERE item_id = :item_id"), {"item_id": trans_in.item_id}).fetchone()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not item.status:
        raise HTTPException(status_code=400, detail="Item is not available")
    if item.owner_id == user_id:
        raise HTTPException(status_code=400, detail="Cannot buy your own item")

    # Create transaction
    query = text("""
        INSERT INTO transactions (item_id, buyer_id, seller_id, transaction_date, status)
        VALUES (:item_id, :buyer_id, :seller_id, now(), 'pending')
        RETURNING transaction_id, transaction_date
    """)
    result = db.execute(query, {
        "item_id": trans_in.item_id,
        "buyer_id": user_id,
        "seller_id": item.owner_id
    }).fetchone()
    
    db.commit()
    
    # Fetch item details for response
    imgs = db.execute(text("SELECT image_data_name FROM item_images WHERE item_id = :item_id"), {"item_id": item.item_id}).fetchall()
    item_response = schemas.ItemResponse(
        item_id=item.item_id, title=item.title, description=item.description,
        condition=item.condition, owner_id=item.owner_id, post_date=item.post_date,
        price=item.price, exchange_type=item.exchange_type, status=item.status,
        desired_item=item.desired_item, total_images=item.total_images,
        category=item.category, images=[img.image_data_name for img in imgs]
    )

    return schemas.TransactionResponse(
        transaction_id=result.transaction_id,
        item_id=trans_in.item_id,
        buyer_id=user_id,
        seller_id=item.owner_id,
        transaction_date=result.transaction_date,
        status="pending",
        completion_date=None,
        item=item_response
    )

@router.get("/transactions/", response_model=List[schemas.TransactionResponse])
def get_transactions(db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    # Get transactions where user is buyer or seller
    query = text("""
        SELECT * FROM transactions 
        WHERE buyer_id = :user_id OR seller_id = :user_id
        ORDER BY transaction_date DESC
    """)
    transactions = db.execute(query, {"user_id": user_id}).fetchall()
    
    result = []
    for t in transactions:
        # Fetch Item
        item_obj = db.execute(text("SELECT * FROM items WHERE item_id = :item_id"), {"item_id": t.item_id}).fetchone()
        item_response = None
        if item_obj:
            imgs = db.execute(text("SELECT image_data_name FROM item_images WHERE item_id = :item_id"), {"item_id": item_obj.item_id}).fetchall()
            item_response = schemas.ItemResponse(
                item_id=item_obj.item_id, title=item_obj.title, description=item_obj.description,
                condition=item_obj.condition, owner_id=item_obj.owner_id, post_date=item_obj.post_date,
                price=item_obj.price, exchange_type=item_obj.exchange_type, status=item_obj.status,
                desired_item=item_obj.desired_item, total_images=item_obj.total_images,
                category=item_obj.category, images=[img.image_data_name for img in imgs]
            )
            
        result.append(schemas.TransactionResponse(
            transaction_id=t.transaction_id,
            item_id=t.item_id,
            buyer_id=t.buyer_id,
            seller_id=t.seller_id,
            transaction_date=t.transaction_date,
            status=t.status,
            completion_date=t.completion_date,
            item=item_response
        ))
    return result

@router.put("/transactions/{transaction_id}", response_model=schemas.TransactionResponse)
def update_transaction(transaction_id: int, trans_update: schemas.TransactionUpdate, db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    # Get transaction
    trans = db.execute(text("SELECT * FROM transactions WHERE transaction_id = :tid"), {"tid": transaction_id}).fetchone()
    if not trans:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    # Only buyer or seller can update? Or maybe specific rules.
    # For simplicity, let's say seller can complete or cancel, buyer can cancel.
    if user_id != trans.buyer_id and user_id != trans.seller_id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    # Update status
    completion_date = None
    if trans_update.status == "completed":
        completion_date = datetime.now()
        # Also mark item as sold
        db.execute(text("UPDATE items SET status = false WHERE item_id = :item_id"), {"item_id": trans.item_id})
        
    query = text("""
        UPDATE transactions 
        SET status = :status, completion_date = :cdate
        WHERE transaction_id = :tid
        RETURNING *
    """)
    updated_trans = db.execute(query, {
        "status": trans_update.status,
        "cdate": completion_date,
        "tid": transaction_id
    }).fetchone()
    db.commit()
    
    # Fetch Item
    item_obj = db.execute(text("SELECT * FROM items WHERE item_id = :item_id"), {"item_id": updated_trans.item_id}).fetchone()
    item_response = None
    if item_obj:
        imgs = db.execute(text("SELECT image_data_name FROM item_images WHERE item_id = :item_id"), {"item_id": item_obj.item_id}).fetchall()
        item_response = schemas.ItemResponse(
            item_id=item_obj.item_id, title=item_obj.title, description=item_obj.description,
            condition=item_obj.condition, owner_id=item_obj.owner_id, post_date=item_obj.post_date,
            price=item_obj.price, exchange_type=item_obj.exchange_type, status=item_obj.status,
            desired_item=item_obj.desired_item, total_images=item_obj.total_images,
            category=item_obj.category, images=[img.image_data_name for img in imgs]
        )

    return schemas.TransactionResponse(
        transaction_id=updated_trans.transaction_id,
        item_id=updated_trans.item_id,
        buyer_id=updated_trans.buyer_id,
        seller_id=updated_trans.seller_id,
        transaction_date=updated_trans.transaction_date,
        status=updated_trans.status,
        completion_date=updated_trans.completion_date,
        item=item_response
    )

"""
-----------------------------
        Message Routes
-----------------------------
"""

@router.post("/messages/", response_model=schemas.MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(msg_in: schemas.MessageCreate, db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    # Check if receiver exists
    receiver = db.execute(text("SELECT 1 FROM users WHERE user_id = :uid"), {"uid": msg_in.receiver_id}).fetchone()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
        
    query = text("""
        INSERT INTO messages (sender_id, receiver_id, content, sent_at, item_id)
        VALUES (:sender_id, :receiver_id, :content, now(), :item_id)
        RETURNING message_id, sent_at
    """)
    result = db.execute(query, {
        "sender_id": user_id,
        "receiver_id": msg_in.receiver_id,
        "content": msg_in.content,
        "item_id": msg_in.item_id
    }).fetchone()
    db.commit()
    
    return schemas.MessageResponse(
        message_id=result.message_id,
        sender_id=user_id,
        receiver_id=msg_in.receiver_id,
        content=msg_in.content,
        sent_at=result.sent_at,
        is_read=False,
        item_id=msg_in.item_id
    )

@router.get("/messages/{other_user_id}", response_model=List[schemas.MessageResponse])
def get_messages(other_user_id: int, db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    # Get messages between current user and other_user
    query = text("""
        SELECT * FROM messages 
        WHERE (sender_id = :user_id AND receiver_id = :other_id) 
           OR (sender_id = :other_id AND receiver_id = :user_id)
        ORDER BY sent_at ASC
    """)
    messages = db.execute(query, {"user_id": user_id, "other_id": other_user_id}).fetchall()
    
    return [schemas.MessageResponse(
        message_id=m.message_id,
        sender_id=m.sender_id,
        receiver_id=m.receiver_id,
        content=m.content,
        sent_at=m.sent_at,
        is_read=m.is_read if m.is_read is not None else False,
        item_id=m.item_id
    ) for m in messages]

@router.get("/conversations/", response_model=List[schemas.UserResponse])
@router.get("/conversations/", response_model=List[schemas.ConversationResponse])
def get_conversations(db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    # 修正 SQL：選取對話對象，並關聯該對話最後涉及的商品資訊
    query = text("""
        SELECT DISTINCT ON (u.user_id)
            u.user_id, u.username, 
            i.item_id, i.title as item_title,
            img.image_data_name as item_image
        FROM users u
        JOIN messages m ON (u.user_id = m.sender_id OR u.user_id = m.receiver_id)
        LEFT JOIN items i ON m.item_id = i.item_id
        LEFT JOIN item_images img ON i.item_id = img.item_id
        WHERE (m.sender_id = :user_id OR m.receiver_id = :user_id)
          AND u.user_id != :user_id
    """)
    rows = db.execute(query, {"user_id": user_id}).fetchall()
    
    return [schemas.ConversationResponse(
        user_id=r.user_id, 
        username=r.username,
        item_id=r.item_id,
        item_title=r.item_title,
        item_image=r.item_image
    ) for r in rows]

"""
-----------------------------
        Item Update & Delete
-----------------------------
"""

@router.put("/items/{item_id}")
def update_item(
    item_id: int, 
    item_update: schemas.ItemUpdate, 
    db: Session = Depends(get_db), 
    user_id: int = Depends(verify_token)
):
    # 1. 權限檢查：使用原生 SQL 確認商品是否存在且屬於目前使用者
    check_query = text("SELECT owner_id FROM items WHERE item_id = :item_id")
    item = db.execute(check_query, {"item_id": item_id}).fetchone()
    
    if not item:
        raise HTTPException(status_code=404, detail="找不到該商品")
    if item.owner_id != user_id:
        raise HTTPException(status_code=403, detail="您沒有權限修改此商品")

    # 2. 執行更新：使用原生 SQL UPDATE 語法
    update_query = text("""
        UPDATE items 
        SET title = :title, 
            description = :description, 
            condition = :condition, 
            price = :price, 
            exchange_type = :exchange_type, 
            desired_item = :desired_item
        WHERE item_id = :item_id
    """)
    
    db.execute(update_query, {
        "title": item_update.title,
        "description": item_update.description,
        "condition": item_update.condition,
        "price": item_update.price,
        "exchange_type": item_update.exchange_type,
        "desired_item": item_update.desired_item,
        "item_id": item_id
    })
    db.commit()
    
    return {"message": "商品資訊已成功更新"}


@router.delete("/items/{item_id}")
def delete_item(
    item_id: int, 
    db: Session = Depends(get_db), 
    user_id: int = Depends(verify_token)
):
    # 1. 權限檢查
    check_query = text("SELECT owner_id FROM items WHERE item_id = :item_id")
    item = db.execute(check_query, {"item_id": item_id}).fetchone()
    
    if not item:
        raise HTTPException(status_code=404, detail="找不到該商品")
    if item.owner_id != user_id:
        raise HTTPException(status_code=403, detail="您沒有權限刪除此商品")

    # 2. 執行刪除：先刪除關聯的圖片紀錄（避免外鍵衝突），再刪除商品本身
    db.execute(text("DELETE FROM item_images WHERE item_id = :item_id"), {"item_id": item_id})
    db.execute(text("DELETE FROM items WHERE item_id = :item_id"), {"item_id": item_id})
    
    db.commit()
    return {"message": "商品已成功刪除"}

# 在 routes.py 末尾新增交易刪除功能
@router.delete("/transactions/{transaction_id}")
def delete_transaction(
    transaction_id: int, 
    db: Session = Depends(get_db), 
    user_id: int = Depends(verify_token)
):
    # 權限檢查：確保只有買家或賣家可以刪除（或僅限管理權限，依需求而定）
    # 使用原生 SQL 檢查
    check_sql = text("SELECT buyer_id, seller_id FROM transactions WHERE transaction_id = :tid")
    trans = db.execute(check_sql, {"tid": transaction_id}).fetchone()
    
    if not trans:
        raise HTTPException(status_code=404, detail="找不到交易紀錄")
    if user_id != trans.buyer_id and user_id != trans.seller_id:
        raise HTTPException(status_code=403, detail="您沒有權限刪除此紀錄")

    # 執行刪除
    db.execute(text("DELETE FROM transactions WHERE transaction_id = :tid"), {"tid": transaction_id})
    db.commit()
    return {"message": "交易紀錄已刪除"}

@router.post("/users/me", response_model=schemas.UserResponse)
def update_current_user(
    email: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    phones: Optional[List[str]] = Form(None),
    db: Session = Depends(get_db), 
    user_id: int = Depends(verify_token) # 只需要這一個驗證
):
    # 確保 user_id 存在
    if not user_id:
        raise HTTPException(status_code=401, detail="驗證失敗")

    if email:
        db.execute(text("UPDATE users SET email = :email WHERE user_id = :id"), {"email": email, "id": user_id})  
    if address:
        db.execute(text("UPDATE users SET address = :address WHERE user_id = :id"), {"address": address, "id": user_id})
    
    if phones is not None:
        db.execute(text("DELETE FROM phones WHERE user_id = :id"), {"id": user_id})
        for p in phones:
            db.execute(text("INSERT INTO phones (user_id, phone_number) VALUES (:id, :num)"), 
                       {"id": user_id, "num": p})
    
    db.commit()
    # 呼叫 read_user 取得最新資料回傳
    return read_user(user_id, db)
