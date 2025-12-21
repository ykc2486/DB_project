from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas
from .database import get_db

router = APIRouter()

# --- User Routes ---

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

    hashed_password = user.password + "_hashed_secret" 

    new_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=user.password + "_hashed_secret",
        address=user.address,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Handle phones
    # Note: The Phone model currently uses user_id as Primary Key, which might limit to one phone per user 
    # unless the model is adjusted (e.g. composite PK or separate ID).
    if user.phones:
        for phone_num in user.phones:
            try:
                new_phone = models.Phone(user_id=new_user.user_id, phone_number=phone_num)
                db.add(new_phone)
                db.commit()
            except Exception:
                db.rollback()
                # In a real scenario, handle the error (e.g. duplicate phone or constraint violation)
                pass
    
    # Construct response
    # Fetch phones manually since there is no relationship property in User model yet
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
    
    # Verify password (placeholder - replace with actual verification)
    if not user or user.password_hash != user_login.password + "_hashed_secret":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token (placeholder - replace with JWT generation)
    access_token = f"fake-jwt-token-for-{user.username}"
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
        db_user.password_hash = user_in.password + "_hashed_secret"
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
