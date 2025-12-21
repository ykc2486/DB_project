from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from argon2 import PasswordHasher
from datetime import datetime
from . import models, schemas
from .database import get_db
from .auth import authenticate_user, get_token, verify_token
import uuid
import os
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
    """
    Create a new user.
    """
    # Check if email already exists
    db_user_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username already exists
    db_user_username = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    ph = PasswordHasher()
    hashed_password = ph.hash(user.password)

    new_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        address=user.address,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Add phone numbers if provided
    if user.phones:
        for phone_num in user.phones:
            try:
                new_phone = models.Phone(user_id=new_user.user_id, phone_number=phone_num)
                db.add(new_phone)
                db.commit()
            except Exception:
                db.rollback()
                pass
    
    phones = db.query(models.Phone).filter(models.Phone.user_id == new_user.user_id).all()
    phone_list = [p.phone_number for p in phones]

    return schemas.UserResponse(
        user_id=new_user.user_id,
        username=new_user.username,
        email=new_user.email,
        is_active=new_user.is_active,
        join_date=new_user.join_date,
        address=new_user.address,
        phones=phone_list
    )

@router.get("/users/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get user by ID.
    """
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    phones = db.query(models.Phone).filter(models.Phone.user_id == user_id).all()
    phone_list = [p.phone_number for p in phones]
    
    return schemas.UserResponse(
        user_id=db_user.user_id,
        username=db_user.username,
        email=db_user.email,
        is_active=db_user.is_active,
        join_date=db_user.join_date,
        address=db_user.address,
        phones=phone_list
    )

@router.post("/login", response_model=schemas.Token)
def login(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Login user and return access token.
    """
    user = db.query(models.User).filter(models.User.username == user_login.username).first()
    
    ph = PasswordHasher()

    if not authenticate_user(user_login.username, user_login.password, db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = get_token(user.user_id)  
    return {"access_token": access_token, "token_type": "bearer"}

@router.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, user_in: schemas.ModifyUser, db: Session = Depends(get_db)):
    """
    Update user information.
    """
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_in.email:
        db_user.email = user_in.email
    if user_in.password:
        ph = PasswordHasher()
        db_user.password_hash = ph.hash(user_in.password)
    if user_in.address:
        db_user.address = user_in.address
        
    db.commit()
    db.refresh(db_user)
    
    phones = db.query(models.Phone).filter(models.Phone.user_id == user_id).all()
    phone_list = [p.phone_number for p in phones]
    
    return schemas.UserResponse(
        user_id=db_user.user_id,
        username=db_user.username,
        email=db_user.email,
        is_active=db_user.is_active,
        join_date=db_user.join_date,
        address=db_user.address,
        phones=phone_list
    )

"""
-----------------------------
        Item Routes
-----------------------------
"""

@router.post("/items/", response_model=schemas.ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """
    Create a new item.
    """

    if(len(item.images) > 3):
        raise HTTPException(status_code=400, detail="Maximum 3 images allowed per item")

    img_paths = []
    for img in item.images:
        if(img.content_type not in ["image/jpeg", "image/png"]):
            raise HTTPException(status_code=400, detail="Invalid image format. Only JPEG and PNG are allowed.")
        file_ext = img.filename.split(".")[-1]
        unique_name = f"{uuid.uuid4()}.{file_ext}"
        save_path = os.path.join(UPLOAD_DIRECTORY, unique_name)
        
        with open(save_path, "wb") as buffer:
            content = img.read()
            buffer.write(content)
        
        img_paths.append(f"/{UPLOAD_DIRECTORY}/{unique_name}")

    new_item = models.Item(
        title=item.title,
        description=item.description,
        condition=item.condition,
        owner_id=token['user_id'],
        price=item.price,
        exchange_type=item.exchange_type,
        status=item.status,
        desired_item=item.desired_item,
        category=item.category
    )
    
    existing_category = db.query(models.Category).filter(models.Category.category_id == item.category).first()
    if not existing_category:
        # Create the category on the fly when the provided category_id does not exist
        new_category = models.Category(
            category_id=item.category,
            category_name=str(item.category)
        )
        db.add(new_category)

    for path in img_paths:
        new_image = models.ItemImage(
            image_data_name=path,
            item=new_item
        )
        db.add(new_image)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return schemas.ItemResponse(
        item_id=new_item.item_id,
        title=new_item.title,
        description=new_item.description,
        condition=new_item.condition,
        owner_id=new_item.owner_id,
        post_date=new_item.post_date,
        price=new_item.price,
        exchange_type=new_item.exchange_type,
        status=new_item.status,
        desired_item=new_item.desired_item,
        total_images=len(img_paths),
        category=new_item.category,
        images=img_paths
    )

@router.get("/items/{item_id}", response_model=schemas.ItemResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
    """
    Get item by ID.
    """
    db_item = db.query(models.Item).filter(models.Item.item_id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    images = db.query(models.ItemImage).filter(models.ItemImage.item_id == item_id).all()
    image_paths = [img.image_data_name for img in images]
    
    return schemas.ItemResponse(
        item_id=db_item.item_id,
        title=db_item.title,
        description=db_item.description,
        condition=db_item.condition,
        owner_id=db_item.owner_id,
        post_date=db_item.post_date,
        price=db_item.price,
        exchange_type=db_item.exchange_type,
        status=db_item.status,
        desired_item=db_item.desired_item,
        total_images=db_item.total_images,
        category=db_item.category,
        images=image_paths
    )

@router.get("/items/", response_model=List[schemas.ItemResponse])
def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get a list of items with pagination.
    """
    items = db.query(models.Item).offset(skip).limit(limit).all()
    result = []
    for item in items:
        images = db.query(models.ItemImage).filter(models.ItemImage.item_id == item.item_id).all()
        image_paths = [img.image_data_name for img in images]
        result.append(
            schemas.ItemResponse(
                item_id=item.item_id,
                title=item.title,
                description=item.description,
                condition=item.condition,
                owner_id=item.owner_id,
                post_date=item.post_date,
                price=item.price,
                exchange_type=item.exchange_type,
                status=item.status,
                desired_item=item.desired_item,
                total_images=item.total_images,
                category=item.category,
                images=image_paths
            )
        )
    return result

"""
-----------------------------
        Image Route
-----------------------------
"""

@router.get("/images/{filename}")
def get_image(filename: str):
    """
    Retrieve an image file by filename.
    """
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(file_path)


"""
-----------------------------
        Wishlist Routes
-----------------------------
"""

@router.post("/wishlist/", response_model=schemas.WishlistResponse, status_code=status.HTTP_201_CREATED)
def add_to_wishlist(wishlist_in: schemas.WishlistCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """
    Add an item to the user's wishlist.
    """
    existing_entry = db.query(models.Wishlist).filter(
        models.Wishlist.user_id == token['user_id'],
        models.Wishlist.item_id == wishlist_in.item_id
    ).first()
    
    if existing_entry:
        raise HTTPException(status_code=400, detail="Item already in wishlist")
    
    new_wishlist_entry = models.Wishlist(
        user_id=token['user_id'],
        item_id=wishlist_in.item_id
    )
    
    db.add(new_wishlist_entry)
    db.commit()
    db.refresh(new_wishlist_entry)
    
    return schemas.WishlistResponse(
        wishlist_id=new_wishlist_entry.wishlist_id,
        user_id=new_wishlist_entry.user_id,
        item_id=new_wishlist_entry.item_id,
        added_date=new_wishlist_entry.added_date
    )

@router.get("/wishlist/", response_model=List[schemas.WishlistResponse])
def get_wishlist(db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """
    Get the user's wishlist.
    """
    wishlist_entries = db.query(models.Wishlist).filter(models.Wishlist.user_id == token['user_id']).all()
    
    result = []
    for entry in wishlist_entries:
        result.append(
            schemas.WishlistResponse(
                wishlist_id=entry.wishlist_id,
                user_id=entry.user_id,
                item_id=entry.item_id,
                added_date=entry.added_date
            )
        )
    return result

@router.delete("/wishlist/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_wishlist(item_id: int, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """
    Remove an item from the user's wishlist.
    """
    wishlist_entry = db.query(models.Wishlist).filter(
        models.Wishlist.user_id == token['user_id'],
        models.Wishlist.item_id == item_id
    ).first()
    
    if not wishlist_entry:
        raise HTTPException(status_code=404, detail="Item not found in wishlist")
    
    db.delete(wishlist_entry)
    db.commit()
    
    return

"""
-----------------------------
        Transaction Routes
-----------------------------
"""

@router.post("/transactions/", response_model=schemas.TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction_in: schemas.TransactionCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """
    Create a new transaction.
    """
    item = db.query(models.Item).filter(models.Item.item_id == transaction_in.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if item.owner_id == token['user_id']:
        raise HTTPException(status_code=400, detail="Cannot buy your own item")

    if not item.status:
         raise HTTPException(status_code=400, detail="Item is not available")

    new_transaction = models.Transaction(
        item_id=transaction_in.item_id,
        buyer_id=token['user_id'],
        seller_id=item.owner_id,
        status="pending"
    )
    
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    
    return schemas.TransactionResponse(
        transaction_id=new_transaction.transaction_id,
        item_id=new_transaction.item_id,
        buyer_id=new_transaction.buyer_id,
        seller_id=new_transaction.seller_id,
        transaction_date=new_transaction.transaction_date,
        status=new_transaction.status,
        completion_date=new_transaction.completion_date
    )

@router.get("/transactions/", response_model=List[schemas.TransactionResponse])
def get_transactions(db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """
    Get transactions for the current user.
    """
    user_id = token['user_id']
    transactions = db.query(models.Transaction).filter(
        (models.Transaction.buyer_id == user_id) | (models.Transaction.seller_id == user_id)
    ).all()
    
    result = []
    for t in transactions:
        result.append(schemas.TransactionResponse(
            transaction_id=t.transaction_id,
            item_id=t.item_id,
            buyer_id=t.buyer_id,
            seller_id=t.seller_id,
            transaction_date=t.transaction_date,
            status=t.status,
            completion_date=t.completion_date
        ))
    return result

@router.put("/transactions/{transaction_id}", response_model=schemas.TransactionResponse)
def update_transaction(transaction_id: int, trans_in: schemas.TransactionUpdate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """
    Update transaction status.
    """
    transaction = db.query(models.Transaction).filter(models.Transaction.transaction_id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    if token['user_id'] not in [transaction.buyer_id, transaction.seller_id]:
        raise HTTPException(status_code=403, detail="Not authorized")

    transaction.status = trans_in.status
    if trans_in.status == "completed":
        transaction.completion_date = datetime.now()
        # Mark item as sold/unavailable
        item = db.query(models.Item).filter(models.Item.item_id == transaction.item_id).first()
        if item:
            item.status = False 

    db.commit()
    db.refresh(transaction)
    
    return schemas.TransactionResponse(
        transaction_id=transaction.transaction_id,
        item_id=transaction.item_id,
        buyer_id=transaction.buyer_id,
        seller_id=transaction.seller_id,
        transaction_date=transaction.transaction_date,
        status=transaction.status,
        completion_date=transaction.completion_date
    )

"""
-----------------------------
        Message Routes
-----------------------------
"""

@router.post("/messages/", response_model=schemas.MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(msg_in: schemas.MessageCreate, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """
    Send a message.
    """
    receiver = db.query(models.User).filter(models.User.user_id == msg_in.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    new_message = models.Message(
        sender_id=token['user_id'],
        receiver_id=msg_in.receiver_id,
        content=msg_in.content,
        item_id=msg_in.item_id
    )
    
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    return schemas.MessageResponse(
        message_id=new_message.message_id,
        sender_id=new_message.sender_id,
        receiver_id=new_message.receiver_id,
        content=new_message.content,
        sent_at=new_message.sent_at,
        is_read=new_message.is_read,
        item_id=new_message.item_id
    )

@router.get("/messages/", response_model=List[schemas.MessageResponse])
def get_messages(db: Session = Depends(get_db), token: str = Depends(verify_token)):
    """
    Get all messages for the current user.
    """
    user_id = token['user_id']
    messages = db.query(models.Message).filter(
        (models.Message.sender_id == user_id) | (models.Message.receiver_id == user_id)
    ).order_by(models.Message.sent_at.desc()).all()
    
    result = []
    for m in messages:
        result.append(schemas.MessageResponse(
            message_id=m.message_id,
            sender_id=m.sender_id,
            receiver_id=m.receiver_id,
            content=m.content,
            sent_at=m.sent_at,
            is_read=m.is_read,
            item_id=m.item_id
        ))
    return result


