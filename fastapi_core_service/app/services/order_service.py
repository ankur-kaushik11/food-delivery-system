"""
Order service for handling order creation and management.
"""
from sqlalchemy.orm import Session
from app.models.models import Order, OrderItem, Dish, Fee
from app.schemas.schemas import OrderCreate, CheckoutRequest
from app.services import cart_service, offer_service, delivery_service
from app.utils.notifications import notify_order_placed
from decimal import Decimal
from fastapi import HTTPException, status
from typing import Optional


def get_fees(db: Session, restaurant_id: int) -> tuple[Decimal, Decimal]:
    """
    Get delivery and platform fees for restaurant.
    Returns restaurant-specific fees if available, otherwise platform-level fees.
    """
    # Try restaurant-specific fees first
    fee = db.query(Fee).filter(Fee.restaurant_id == restaurant_id).first()
    
    # Fall back to platform-level fees
    if not fee:
        fee = db.query(Fee).filter(Fee.restaurant_id == None).first()
    
    if not fee:
        # Default fees if none configured
        return Decimal("30.00"), Decimal("5.00")
    
    return fee.delivery_fee, fee.platform_fee


def calculate_order_total(
    items_total: Decimal,
    discount: Decimal,
    delivery_fee: Decimal,
    platform_fee: Decimal
) -> Decimal:
    """Calculate total order amount."""
    total = items_total - discount + delivery_fee + platform_fee
    return round(total, 2)


def create_order_from_cart(
    db: Session,
    user_id: int,
    checkout_request: CheckoutRequest
) -> Order:
    """
    Create order from current cart.
    """
    # Validate cart
    cart = cart_service.validate_cart_for_checkout(user_id, db)
    restaurant_id = cart["restaurant_id"]
    
    # Calculate items total
    items_total = Decimal("0.00")
    order_items_data = []
    
    for dish_id, quantity in cart["items"].items():
        dish = db.query(Dish).filter(Dish.id == dish_id).first()
        if not dish:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dish {dish_id} not found"
            )
        
        item_total = dish.price * quantity
        items_total += item_total
        
        order_items_data.append({
            "dish_id": dish_id,
            "quantity": quantity,
            "price_snapshot": dish.price
        })
    
    # Get fees
    delivery_fee, platform_fee = get_fees(db, restaurant_id)
    
    # Apply offer
    offer, discount_amount = offer_service.apply_offer(
        db, user_id, restaurant_id, items_total, checkout_request.offer_id
    )
    
    # Calculate total
    total_amount = calculate_order_total(items_total, discount_amount, delivery_fee, platform_fee)
    
    # Create order
    order = Order(
        customer_id=user_id,
        restaurant_id=restaurant_id,
        status="placed",
        total_amount=total_amount,
        discount_amount=discount_amount,
        delivery_fee=delivery_fee,
        platform_fee=platform_fee,
        payment_mode=checkout_request.payment_mode.value
    )
    
    db.add(order)
    db.flush()  # Get order ID
    
    # Create order items
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=order.id,
            **item_data
        )
        db.add(order_item)
    
    db.commit()
    db.refresh(order)
    
    # Clear cart
    cart_service.clear_cart(user_id)
    
    # Send notifications
    notify_order_placed(db, order)
    
    return order


def reorder(db: Session, user_id: int, order_id: int) -> dict:
    """
    Recreate cart from a past order.
    Returns cart data.
    """
    # Get original order
    original_order = db.query(Order).filter(
        Order.id == order_id,
        Order.customer_id == user_id
    ).first()
    
    if not original_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Clear current cart
    cart_service.clear_cart(user_id)
    
    # Add items from original order to cart
    for order_item in original_order.items:
        dish = db.query(Dish).filter(Dish.id == order_item.dish_id).first()
        
        if not dish:
            continue  # Skip if dish no longer exists
        
        if not dish.available:
            continue  # Skip unavailable dishes
        
        try:
            cart_service.add_to_cart(user_id, dish.id, order_item.quantity, db)
        except HTTPException:
            # If adding fails (e.g., restaurant inactive), skip
            continue
    
    # Return updated cart
    cart = cart_service.get_cart(user_id, db)
    
    if cart.item_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not recreate order. Items may no longer be available."
        )
    
    return {
        "message": "Order items added to cart successfully",
        "cart": cart,
        "note": "Prices reflect current rates and may differ from original order"
    }
