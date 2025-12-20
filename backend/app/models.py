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
    owner_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, ondelete="CASCADE")
    post_date = Column(DateTime(timezone=True), server_default=func.now())
    price = Column(Integer, nullable=True)
    exchange_type = Column(Boolean, nullable=False)  # 0: sell, 1: exchange
    status = Column(Boolean, nullable=False, default=True)  # 0: unavailable, 1: available
    desired_item = Column(String, nullable=True)  # for exchange items
    total_images = Column(Integer, default=0, nullable=False)

class ItemImage(Base):
    __tablename__ = "item_images"

    image_id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.item_id", ondelete="CASCADE"), nullable=False)
    image_data = Column(LargeBinary, nullable=False)