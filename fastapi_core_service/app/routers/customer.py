"""
Customer API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.dependencies.auth import get_customer_user
from app.models.models import User, Restaurant, Dish, Order, Complaint
from app.schemas.schemas import (
    RestaurantResponse, DishResponse, CartAddRequest, CartRemoveRequest,
    CartResponse, CheckoutRequest, OrderResponse, ComplaintCreate,
    ComplaintResponse, OrderItemResponse
)
from app.services import cart_service, order_service

router = APIRouter(prefix="/api", tags=["Customer"])


@router.get("/restaurants", response_model=List[RestaurantResponse])
def list_restaurants(
    pin_code: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """List all restaurants (filter by pin_code, only active and ordering enabled)."""
    query = db.query(Restaurant).filter(
        Restaurant.status == "active",
        Restaurant.is_ordering_enabled == True
    )
    
    if pin_code:
        query = query.filter(Restaurant.pin_code == pin_code)
    
    restaurants = query.all()
    return restaurants


@router.get("/restaurants/{restaurant_id}/menu", response_model=List[DishResponse])
def get_restaurant_menu(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get menu (dishes) for a specific restaurant."""
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    dishes = db.query(Dish).filter(
        Dish.restaurant_id == restaurant_id,
        Dish.available == True
    ).all()
    
    return dishes


@router.post("/cart/add", response_model=CartResponse)
def add_to_cart(
    request: CartAddRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Add item to cart."""
    return cart_service.add_to_cart(current_user.id, request.dish_id, request.quantity, db)


@router.post("/cart/remove", response_model=CartResponse)
def remove_from_cart(
    request: CartRemoveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Remove item from cart."""
    return cart_service.remove_from_cart(current_user.id, request.dish_id, db)


@router.get("/cart", response_model=CartResponse)
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get current cart."""
    return cart_service.get_cart(current_user.id, db)


@router.post("/checkout", response_model=OrderResponse)
def checkout(
    request: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Checkout and create order from cart."""
    order = order_service.create_order_from_cart(db, current_user.id, request)
    
    # Load items for response
    db.refresh(order)
    
    return order


@router.get("/orders/history", response_model=List[OrderResponse])
def get_order_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get order history for customer."""
    orders = db.query(Order).filter(
        Order.customer_id == current_user.id
    ).order_by(Order.created_at.desc()).all()
    
    return orders


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get specific order details."""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.customer_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order


@router.post("/orders/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Cancel an order (only if status is 'placed')."""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.customer_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.status != "placed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order can only be cancelled when status is 'placed'"
        )
    
    order.status = "cancelled"
    db.commit()
    db.refresh(order)
    
    # Release delivery partner if assigned
    if order.delivery_partner_id:
        from app.services import delivery_service
        delivery_service.release_delivery_partner(db, order.delivery_partner_id)
    
    return order


@router.post("/orders/{order_id}/reorder")
def reorder(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Recreate cart from a past order."""
    return order_service.reorder(db, current_user.id, order_id)


@router.post("/complaints", response_model=ComplaintResponse)
def create_complaint(
    request: ComplaintCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Create a complaint for an order."""
    # Verify order belongs to customer
    order = db.query(Order).filter(
        Order.id == request.order_id,
        Order.customer_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    complaint = Complaint(
        order_id=request.order_id,
        customer_id=current_user.id,
        description=request.description,
        status="open"
    )
    
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    
    return complaint


@router.get("/complaints", response_model=List[ComplaintResponse])
def get_my_complaints(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get all complaints filed by customer."""
    complaints = db.query(Complaint).filter(
        Complaint.customer_id == current_user.id
    ).order_by(Complaint.created_at.desc()).all()
    
    return complaints
