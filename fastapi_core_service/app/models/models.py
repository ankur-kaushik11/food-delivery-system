"""
SQLAlchemy models for FastAPI Core Service.
"""
from sqlalchemy import Column, Integer, String, Decimal, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    """User role enum."""
    ADMIN = "Admin"
    RESTAURANT_OWNER = "Restaurant Owner"
    CUSTOMER = "Customer"
    DELIVERY_PARTNER = "Delivery Partner"
    CUSTOMER_CARE = "Customer Care"


class User(Base):
    """User model (read-only from Django)."""
    __tablename__ = "users_user"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    pin_code = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_staff = Column(Boolean, default=False)


class RestaurantStatus(str, enum.Enum):
    """Restaurant status enum."""
    ACTIVE = "active"
    INACTIVE = "inactive"


class Restaurant(Base):
    """Restaurant model."""
    __tablename__ = "restaurants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    owner_id = Column(Integer, ForeignKey("users_user.id"), nullable=False)
    pin_code = Column(String(10), nullable=False, index=True)
    status = Column(String(20), default=RestaurantStatus.ACTIVE.value)
    is_ordering_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    dishes = relationship("Dish", back_populates="restaurant", cascade="all, delete-orphan")
    offers = relationship("Offer", back_populates="restaurant")
    fees = relationship("Fee", back_populates="restaurant")


class Dish(Base):
    """Dish model."""
    __tablename__ = "dishes"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    price = Column(Decimal(10, 2), nullable=False)
    photo_path = Column(String(500), nullable=True)
    available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="dishes")


class OrderStatus(str, enum.Enum):
    """Order status enum."""
    PLACED = "placed"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentMode(str, enum.Enum):
    """Payment mode enum."""
    CASH = "cash"
    CARD = "card"
    UPI = "upi"


class Order(Base):
    """Order model."""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users_user.id"), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    delivery_partner_id = Column(Integer, ForeignKey("users_user.id"), nullable=True)
    status = Column(String(50), default=OrderStatus.PLACED.value)
    total_amount = Column(Decimal(10, 2), nullable=False)
    discount_amount = Column(Decimal(10, 2), default=0)
    delivery_fee = Column(Decimal(10, 2), nullable=False)
    platform_fee = Column(Decimal(10, 2), nullable=False)
    payment_mode = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("User", foreign_keys=[customer_id])
    restaurant = relationship("Restaurant", foreign_keys=[restaurant_id])
    delivery_partner = relationship("User", foreign_keys=[delivery_partner_id])
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    complaints = relationship("Complaint", back_populates="order")


class OrderItem(Base):
    """Order item model."""
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_snapshot = Column(Decimal(10, 2), nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    dish = relationship("Dish")


class DeliveryPartner(Base):
    """Delivery partner model."""
    __tablename__ = "delivery_partners"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users_user.id"), nullable=False, unique=True)
    available = Column(Boolean, default=True)
    pin_code = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])


class ComplaintStatus(str, enum.Enum):
    """Complaint status enum."""
    OPEN = "open"
    RESOLVED = "resolved"


class Complaint(Base):
    """Complaint model."""
    __tablename__ = "complaints"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("users_user.id"), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), default=ComplaintStatus.OPEN.value)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    order = relationship("Order", back_populates="complaints")
    customer = relationship("User", foreign_keys=[customer_id])


class Offer(Base):
    """Offer model."""
    __tablename__ = "offers"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=True)
    discount_percentage = Column(Decimal(5, 2), nullable=False)
    min_order_value = Column(Decimal(10, 2), nullable=False)
    first_time_user_only = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="offers")


class Fee(Base):
    """Fee model."""
    __tablename__ = "fees"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=True)
    delivery_fee = Column(Decimal(10, 2), nullable=False)
    platform_fee = Column(Decimal(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="fees")


class Notification(Base):
    """Notification model for simulation."""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users_user.id"), nullable=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    order = relationship("Order", foreign_keys=[order_id])
