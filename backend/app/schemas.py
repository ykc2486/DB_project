from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

class createUser(BaseModel):
    """
    Docstring for createUser
    """
    username: str = Field(..., min_length=3, max_length=24, description="The unique username of the user.")
    email: EmailStr = Field(..., description="The email address of the user.")
    password: str = Field(..., min_length=8, description="The password for the user account.")
    address: Optional[str] = Field(None, max_length=256, description="The address of the user.")
    phones: Optional[List[str]] = Field(None, description="List of phone numbers associated with the user.")

class UserResponse(BaseModel):
    """
    Docstring for UserResponse
    """
    user_id: int
    username: str
    email: EmailStr
    is_active: bool
    join_date: datetime
    address: Optional[str]
    phones: Optional[List[str]]

class UserLogin(BaseModel):
    """
    Docstring for UserLogin
    """
    username: str = Field(..., description="The username of the user.")
    password: str = Field(..., description="The password for the user account.")

class Token(BaseModel):
    """
    Docstring for Token
    """
    access_token: str
    token_type: str

