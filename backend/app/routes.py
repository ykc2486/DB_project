from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
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
    # Check if email exists
    if db.execute(text("SELECT 1 FROM users WHERE email = :email"), {"email": user.email}).fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    ph = PasswordHasher()
    password_hash = ph.hash(user.password)
    
    # Insert user
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
    }).fetchone()
    
    new_user_id = result.user_id
    db.commit()
    
    if user.phones:
        for p in user.phones:
            db.execute(text("INSERT INTO phones (user_id, phone_number) VALUES (:user_id, :phone_number)"), 
                       {"user_id": new_user_id, "phone_number": p})
        db.commit()
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
def read_items(db: Session = Depends(get_db)):
    items = db.execute(text("SELECT * FROM items")).fetchall()
    result = []
    for i in items:
        imgs = db.execute(text("SELECT image_data_name FROM item_images WHERE item_id = :item_id"), {"item_id": i.item_id}).fetchall()
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