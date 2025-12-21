from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base  

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    join_date = Column(DateTime(timezone=True), server_default=func.now())
    address = Column(Text, nullable=True)
    items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")

class Item(Base):
    __tablename__ = "items"

    item_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    condition = Column(String, nullable=False)
    
    owner_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    
    post_date = Column(DateTime(timezone=True), server_default=func.now())
    price = Column(Integer, nullable=True)
    exchange_type = Column(Boolean, nullable=False)  # 0: sell, 1: exchange
    status = Column(Boolean, nullable=False, default=True)  # 0: unavailable, 1: available
    desired_item = Column(String, nullable=True)  # for exchange items
    total_images = Column(Integer, default=0, nullable=False)
    
    category = Column(Integer, ForeignKey("categories.category_id"), nullable=False)

class ItemImage(Base):
    __tablename__ = "item_images"

    image_id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.item_id", ondelete="CASCADE"), nullable=False)
    image_data = Column(LargeBinary, nullable=False)

class Category(Base): # delete parent category idea
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String, unique=True, nullable=False)

class Wishlist(Base):
    __tablename__ = "wishlist"

    wishlist_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.item_id", ondelete="CASCADE"), nullable=False)
    added_date = Column(DateTime(timezone=True), server_default=func.now())

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    buyer_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    item_id = Column(Integer, ForeignKey("items.item_id", ondelete="SET NULL"), nullable=True)
    transaction_date = Column(DateTime(timezone=True), server_default=func.now())
    final_price = Column(Integer, nullable=True)
    rating = Column(Integer, nullable=True)  # rating given by buyer to seller
    review = Column(Text, nullable=True)  # review given by buyer to seller
    status = Column(String, nullable=False, default="pending")  # pending, completed, cancelled

class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.item_id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


    