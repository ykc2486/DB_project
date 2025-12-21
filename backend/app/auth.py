from sqlalchemy.orm import Session
from argon2 import PasswordHasher
from fastapi import Depends

import os
import jwt
import datetime
from dotenv import load_dotenv

from .database import get_db
from . import models

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY not found in environment variables")

def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    """
    Authenticate user by username and password.
    """
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return False
    
    ph = PasswordHasher()

    try:
        ph.verify(user.password_hash, password)
    except:
        return False
    return user

def get_token(user_id: int):
    """
    generate jwt
    """

    try:
        payload = {
            "user_id": user_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=72),
            "iat": datetime.datetime.utcnow()
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    except Exception as e:
        return None

def verify_token(token: str):
    """
    verify jwt
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None