from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base  

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    address = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    join_date = Column(DateTime(timezone=True), server_default=func.now())

    phones = relationship("Phone", back_populates="user")
    items = relationship("Item", back_populates="owner")
    wishlist = relationship("Wishlist", back_populates="user")

class Phone(Base):
    __tablename__ = "phones"

    phone_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    phone_number = Column(String(20), nullable=False)

    user = relationship("User", back_populates="phones")

class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(100), nullable=False)

    items = relationship("Item", back_populates="category_rel")

class Item(Base):
    __tablename__ = "items"

    item_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    condition = Column(String(50), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    post_date = Column(DateTime(timezone=True), server_default=func.now())
    price = Column(Integer, nullable=True)
    exchange_type = Column(Boolean, default=False) # False=Sale, True=Exchange
    status = Column(Boolean, default=True) # True=Available, False=Sold/Unavailable
    desired_item = Column(String(100), nullable=True)
    category = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    total_images = Column(Integer, default=0)

    owner = relationship("User", back_populates="items")
    category_rel = relationship("Category", back_populates="items")
    images = relationship("ItemImage", back_populates="item")

class ItemImage(Base):
    __tablename__ = "item_images"

    image_id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.item_id"), nullable=False)
    image_data_name = Column(String(255), nullable=False)

    item = relationship("Item", back_populates="images")

class Wishlist(Base):
    __tablename__ = "wishlist"

    wishlist_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.item_id"), nullable=False)
    added_date = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="wishlist")
    item = relationship("Item")

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.item_id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    transaction_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default="pending") # pending, completed, cancelled
    completion_date = Column(DateTime(timezone=True), nullable=True)

    item = relationship("Item")
    buyer = relationship("User", foreign_keys=[buyer_id])
    seller = relationship("User", foreign_keys=[seller_id])

class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    content = Column(Text, nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    is_read = Column(Boolean, default=False)
    item_id = Column(Integer, ForeignKey("items.item_id"), nullable=True)

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
    item = relationship("Item")
