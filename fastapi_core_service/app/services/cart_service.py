"""
Cart service for managing shopping cart.
Cart is stored in-memory per session (can be moved to Redis/database in production).
"""
from typing import Dict, List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.models import Dish, Restaurant
from app.schemas.schemas import CartItemResponse, CartResponse
from fastapi import HTTPException, status

# In-memory cart storage: {user_id: {restaurant_id: int, items: {dish_id: quantity}}}
cart_storage: Dict[int, Dict] = {}


def get_cart(user_id: int, db: Session) -> CartResponse:
    """Get user's cart."""
    if user_id not in cart_storage or not cart_storage[user_id].get("items"):
        return CartResponse(
            restaurant_id=None,
            restaurant_name=None,
            items=[],
            subtotal=Decimal("0.00"),
            item_count=0
        )
    
    cart = cart_storage[user_id]
    restaurant_id = cart.get("restaurant_id")
    items_dict = cart.get("items", {})
    
    # Get restaurant name
    restaurant_name = None
    if restaurant_id:
        restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        if restaurant:
            restaurant_name = restaurant.name
    
    # Build cart items with dish details
    items = []
    subtotal = Decimal("0.00")
    
    for dish_id, quantity in items_dict.items():
        dish = db.query(Dish).filter(Dish.id == dish_id).first()
        if dish:
            item_subtotal = dish.price * quantity
            items.append(CartItemResponse(
                dish_id=dish.id,
                dish_name=dish.name,
                price=dish.price,
                quantity=quantity,
                subtotal=item_subtotal
            ))
            subtotal += item_subtotal
    
    return CartResponse(
        restaurant_id=restaurant_id,
        restaurant_name=restaurant_name,
        items=items,
        subtotal=subtotal,
        item_count=sum(items_dict.values())
    )


def add_to_cart(user_id: int, dish_id: int, quantity: int, db: Session) -> CartResponse:
    """
    Add item to cart.
    Validates multi-restaurant restriction.
    """
    # Get dish
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dish not found"
        )
    
    if not dish.available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dish is not available"
        )
    
    # Check restaurant is active and ordering enabled
    restaurant = db.query(Restaurant).filter(Restaurant.id == dish.restaurant_id).first()
    if not restaurant or restaurant.status != "active" or not restaurant.is_ordering_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant is not accepting orders"
        )
    
    # Initialize cart if not exists
    if user_id not in cart_storage:
        cart_storage[user_id] = {"restaurant_id": dish.restaurant_id, "items": {}}
    
    cart = cart_storage[user_id]
    
    # Multi-restaurant restriction check
    if cart.get("restaurant_id") and cart["restaurant_id"] != dish.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cart contains items from different restaurant. Please clear cart or remove items from restaurant {cart['restaurant_id']} first."
        )
    
    # Set restaurant_id if cart was empty
    if not cart.get("restaurant_id"):
        cart["restaurant_id"] = dish.restaurant_id
    
    # Add or update item
    if dish_id in cart["items"]:
        cart["items"][dish_id] += quantity
    else:
        cart["items"][dish_id] = quantity
    
    return get_cart(user_id, db)


def remove_from_cart(user_id: int, dish_id: int, db: Session) -> CartResponse:
    """Remove item from cart."""
    if user_id not in cart_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart is empty"
        )
    
    cart = cart_storage[user_id]
    
    if dish_id not in cart.get("items", {}):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not in cart"
        )
    
    # Remove item
    del cart["items"][dish_id]
    
    # Clear restaurant_id if cart is empty
    if not cart["items"]:
        cart["restaurant_id"] = None
    
    return get_cart(user_id, db)


def clear_cart(user_id: int) -> None:
    """Clear user's cart."""
    if user_id in cart_storage:
        cart_storage[user_id] = {"restaurant_id": None, "items": {}}


def validate_cart_for_checkout(user_id: int, db: Session) -> Dict:
    """
    Validate cart before checkout.
    Returns cart data if valid.
    """
    if user_id not in cart_storage or not cart_storage[user_id].get("items"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )
    
    cart = cart_storage[user_id]
    restaurant_id = cart.get("restaurant_id")
    
    if not restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid cart state"
        )
    
    # Check restaurant status
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    if restaurant.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant is inactive"
        )
    
    if not restaurant.is_ordering_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant is not accepting orders"
        )
    
    # Validate all dishes are still available
    for dish_id in cart["items"].keys():
        dish = db.query(Dish).filter(Dish.id == dish_id).first()
        if not dish or not dish.available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dish {dish_id} is no longer available"
            )
    
    return cart
