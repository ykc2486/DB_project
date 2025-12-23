from fastapi import UploadFile
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

# Schemas for User operations
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

class ModifyUser(BaseModel):
    """
    Docstring for ModifyUser
    """
    email: Optional[EmailStr] = Field(None, description="The new email address of the user.")
    password: Optional[str] = Field(None, min_length=8, description="The new password for the user account.")
    address: Optional[str] = Field(None, max_length=256, description="The new address of the user.")

# Schemas for Item operations
class ItemCreate(BaseModel):
    """
    Docstring for ItemCreate
    """
    title: str = Field(..., max_length=100, description="The title of the item.")
    description: Optional[str] = Field(None, description="The description of the item.")
    condition: str = Field(..., max_length=50, description="The condition of the item.")
    price: Optional[int] = Field(None, ge=0, description="The price of the item if for sale.")
    exchange_type: bool = Field(..., description="Indicates if the item is for sale (False) or exchange (True).")
    desired_item: Optional[str] = Field(None, description="The desired item for exchange if applicable.")
    category: int = Field(..., description="The category ID of the item.")
    total_images: int = Field(0, ge=0, description="The total number of images for the item.")
    images: Optional[List[UploadFile]] = Field(None, description="Image files associated with the item.")

class ItemResponse(BaseModel):
    """
    Docstring for ItemResponse
    """
    item_id: int
    title: str
    description: Optional[str]
    condition: str
    owner_id: int
    post_date: datetime
    price: Optional[int]
    exchange_type: bool
    status: bool
    desired_item: Optional[str]
    total_images: int
    category: int
    images: Optional[List[str]] = Field(None, description="List of image paths for the item.")

# Schemas for wishlist operations
class WishlistCreate(BaseModel):
    """
    Docstring for WishlistCreate
    """
    item_id: int = Field(..., description="The ID of the item to add to the wishlist.")

class WishlistResponse(BaseModel):
    """
    Docstring for WishlistResponse
    """
    user_id: int
    item_id: int
    added_date: datetime
    item: Optional[ItemResponse] = None

# Schemas for Transaction operations
class TransactionCreate(BaseModel):
    """
    Docstring for TransactionCreate
    """
    item_id: int = Field(..., description="The ID of the item to transact.")

class TransactionResponse(BaseModel):
    """
    Docstring for TransactionResponse
    """
    transaction_id: int
    item_id: int
    buyer_id: int
    seller_id: int
    transaction_date: datetime
    status: str
    completion_date: Optional[datetime]
    item: Optional[ItemResponse] = None

class TransactionUpdate(BaseModel):
    """
    Docstring for TransactionUpdate
    """
    status: str = Field(..., description="The new status of the transaction (e.g., completed, cancelled).")

# Schemas for Message operations
class MessageCreate(BaseModel):
    """
    Docstring for MessageCreate
    """
    receiver_id: int = Field(..., description="The ID of the user receiving the message.")
    content: str = Field(..., description="The content of the message.")
    item_id: Optional[int] = Field(None, description="Optional ID of the item related to the message.")

class MessageResponse(BaseModel):
    """
    Docstring for MessageResponse
    """
    message_id: int
    sender_id: int
    receiver_id: int
    content: str
    sent_at: datetime
    is_read: bool = False
    item_id: Optional[int] = None

