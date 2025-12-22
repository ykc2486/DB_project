from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
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
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    ph = PasswordHasher()
    new_user = models.User(
        username=user.username, email=user.email,
        password_hash=ph.hash(user.password), address=user.address
    )
    db.add(new_user); db.commit(); db.refresh(new_user)
    if user.phones:
        for p in user.phones:
            db.add(models.Phone(user_id=new_user.user_id, phone_number=p))
        db.commit()
    return read_user(new_user.user_id, db)

@router.get("/users/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not db_user: raise HTTPException(status_code=404, detail="User not found")
    phones = db.query(models.Phone).filter(models.Phone.user_id == user_id).all()
    return schemas.UserResponse(
        user_id=db_user.user_id, username=db_user.username, email=db_user.email,
        is_active=db_user.is_active, join_date=db_user.join_date,
        address=db_user.address, phones=[p.phone_number for p in phones]
    )

@router.post("/login", response_model=schemas.Token)
def login(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == user_login.username).first()
    if not user or not authenticate_user(user_login.username, user_login.password, db):
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
    if not db.query(models.Category).filter(models.Category.category_id == category).first():
        db.add(models.Category(category_id=category, category_name=f"Category {category}"))
        db.flush()

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

    new_item = models.Item(
        title=title, description=description, condition=condition,
        owner_id=user_id, price=price, exchange_type=exchange_type,
        status=True, desired_item=desired_item, category=category,
        total_images=len(img_paths)
    )
    db.add(new_item); db.commit(); db.refresh(new_item)
    for path in img_paths:
        db.add(models.ItemImage(image_data_name=path, item_id=new_item.item_id))
    db.commit(); db.refresh(new_item)
    return schemas.ItemResponse(
        item_id=new_item.item_id, title=new_item.title, description=new_item.description,
        condition=new_item.condition, owner_id=new_item.owner_id, post_date=new_item.post_date,
        price=new_item.price, exchange_type=new_item.exchange_type, status=new_item.status,
        desired_item=new_item.desired_item, total_images=len(img_paths),
        category=new_item.category, images=img_paths
    )

@router.get("/items/", response_model=List[schemas.ItemResponse])
def read_items(db: Session = Depends(get_db)):
    items = db.query(models.Item).all()
    result = []
    for i in items:
        imgs = db.query(models.ItemImage).filter(models.ItemImage.item_id == i.item_id).all()
        result.append(schemas.ItemResponse(
            item_id=i.item_id, title=i.title, description=i.description,
            condition=i.condition, owner_id=i.owner_id, post_date=i.post_date,
            price=i.price, exchange_type=i.exchange_type, status=i.status,
            desired_item=i.desired_item, total_images=i.total_images,
            category=i.category, images=[img.image_data_name for img in imgs]
        ))
    return result

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
    new_e = models.Wishlist(user_id=user_id, item_id=wish_in.item_id)
    db.add(new_e); db.commit(); db.refresh(new_e)
    return new_e

@router.get("/wishlist/", response_model=List[schemas.WishlistResponse])
def get_wishlist(db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    return db.query(models.Wishlist).filter(models.Wishlist.user_id == user_id).all()