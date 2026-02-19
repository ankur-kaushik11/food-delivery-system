"""
Pydantic schemas for FastAPI requests and responses.
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum


# Enums
class UserRole(str, Enum):
    ADMIN = "Admin"
    RESTAURANT_OWNER = "Restaurant Owner"
    CUSTOMER = "Customer"
    DELIVERY_PARTNER = "Delivery Partner"
    CUSTOMER_CARE = "Customer Care"


class OrderStatus(str, Enum):
    PLACED = "placed"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentMode(str, Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"


class ComplaintStatus(str, Enum):
    OPEN = "open"
    RESOLVED = "resolved"


# User schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole
    pin_code: str


class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Restaurant schemas
class RestaurantBase(BaseModel):
    name: str
    pin_code: str


class RestaurantCreate(RestaurantBase):
    owner_id: int


class RestaurantResponse(RestaurantBase):
    id: int
    owner_id: int
    status: str
    is_ordering_enabled: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Dish schemas
class DishBase(BaseModel):
    name: str
    price: Decimal = Field(..., gt=0)
    photo_path: Optional[str] = None
    available: bool = True


class DishCreate(DishBase):
    restaurant_id: int


class DishUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[Decimal] = None
    photo_path: Optional[str] = None
    available: Optional[bool] = None


class DishResponse(DishBase):
    id: int
    restaurant_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Cart schemas
class CartItem(BaseModel):
    dish_id: int
    quantity: int = Field(..., gt=0)


class CartAddRequest(BaseModel):
    dish_id: int
    quantity: int = Field(..., gt=0)


class CartRemoveRequest(BaseModel):
    dish_id: int


class CartItemResponse(BaseModel):
    dish_id: int
    dish_name: str
    price: Decimal
    quantity: int
    subtotal: Decimal


class CartResponse(BaseModel):
    restaurant_id: Optional[int] = None
    restaurant_name: Optional[str] = None
    items: List[CartItemResponse]
    subtotal: Decimal
    item_count: int


# Order schemas
class OrderItemCreate(BaseModel):
    dish_id: int
    quantity: int


class OrderItemResponse(BaseModel):
    id: int
    dish_id: int
    quantity: int
    price_snapshot: Decimal
    
    class Config:
        from_attributes = True


class CheckoutRequest(BaseModel):
    payment_mode: PaymentMode
    offer_id: Optional[int] = None


class OrderCreate(BaseModel):
    restaurant_id: int
    items: List[OrderItemCreate]
    payment_mode: PaymentMode
    offer_id: Optional[int] = None


class OrderResponse(BaseModel):
    id: int
    customer_id: int
    restaurant_id: int
    delivery_partner_id: Optional[int] = None
    status: OrderStatus
    total_amount: Decimal
    discount_amount: Decimal
    delivery_fee: Decimal
    platform_fee: Decimal
    payment_mode: str
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


# Complaint schemas
class ComplaintCreate(BaseModel):
    order_id: int
    description: str = Field(..., min_length=10)


class ComplaintResolve(BaseModel):
    resolution_notes: str = Field(..., min_length=10)


class ComplaintResponse(BaseModel):
    id: int
    order_id: int
    customer_id: int
    description: str
    status: ComplaintStatus
    resolution_notes: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Offer schemas
class OfferResponse(BaseModel):
    id: int
    restaurant_id: Optional[int] = None
    discount_percentage: Decimal
    min_order_value: Decimal
    first_time_user_only: bool
    active: bool
    
    class Config:
        from_attributes = True


# Fee schemas
class FeeResponse(BaseModel):
    id: int
    restaurant_id: Optional[int] = None
    delivery_fee: Decimal
    platform_fee: Decimal
    
    class Config:
        from_attributes = True


# Delivery Partner schemas
class DeliveryPartnerToggle(BaseModel):
    available: bool


class DeliveryPartnerResponse(BaseModel):
    id: int
    user_id: int
    available: bool
    pin_code: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Restaurant Toggle schemas
class RestaurantToggleOrdering(BaseModel):
    is_ordering_enabled: bool
