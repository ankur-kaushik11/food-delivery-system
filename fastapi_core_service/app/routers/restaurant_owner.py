"""
Restaurant Owner API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies.auth import get_restaurant_owner_user
from app.models.models import User, Restaurant, Dish, Order
from app.schemas.schemas import (
    DishCreate, DishUpdate, DishResponse, OrderResponse,
    OrderStatusUpdate, RestaurantToggleOrdering
)
from app.services import delivery_service
from app.utils.notifications import notify_order_status_change

router = APIRouter(prefix="/api/restaurant", tags=["Restaurant Owner"])


def get_owner_restaurant(db: Session, owner_id: int) -> Restaurant:
    """Get restaurant owned by user."""
    restaurant = db.query(Restaurant).filter(Restaurant.owner_id == owner_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No restaurant found for this owner"
        )
    return restaurant


@router.post("/dishes", response_model=DishResponse, status_code=status.HTTP_201_CREATED)
def create_dish(
    dish_data: DishCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_restaurant_owner_user)
):
    """Create a new dish."""
    restaurant = get_owner_restaurant(db, current_user.id)
    
    # Verify restaurant_id matches owner's restaurant
    if dish_data.restaurant_id != restaurant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only add dishes to your own restaurant"
        )
    
    dish = Dish(
        restaurant_id=dish_data.restaurant_id,
        name=dish_data.name,
        price=dish_data.price,
        photo_path=dish_data.photo_path,
        available=dish_data.available
    )
    
    db.add(dish)
    db.commit()
    db.refresh(dish)
    
    return dish


@router.get("/dishes", response_model=List[DishResponse])
def list_dishes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_restaurant_owner_user)
):
    """List all dishes for owner's restaurant."""
    restaurant = get_owner_restaurant(db, current_user.id)
    
    dishes = db.query(Dish).filter(Dish.restaurant_id == restaurant.id).all()
    return dishes


@router.put("/dishes/{dish_id}", response_model=DishResponse)
def update_dish(
    dish_id: int,
    dish_data: DishUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_restaurant_owner_user)
):
    """Update a dish."""
    restaurant = get_owner_restaurant(db, current_user.id)
    
    dish = db.query(Dish).filter(
        Dish.id == dish_id,
        Dish.restaurant_id == restaurant.id
    ).first()
    
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dish not found"
        )
    
    # Update fields
    update_data = dish_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dish, field, value)
    
    db.commit()
    db.refresh(dish)
    
    return dish


@router.delete("/dishes/{dish_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dish(
    dish_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_restaurant_owner_user)
):
    """Delete a dish."""
    restaurant = get_owner_restaurant(db, current_user.id)
    
    dish = db.query(Dish).filter(
        Dish.id == dish_id,
        Dish.restaurant_id == restaurant.id
    ).first()
    
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dish not found"
        )
    
    db.delete(dish)
    db.commit()
    
    return None


@router.get("/orders", response_model=List[OrderResponse])
def list_restaurant_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_restaurant_owner_user)
):
    """List all orders for owner's restaurant."""
    restaurant = get_owner_restaurant(db, current_user.id)
    
    orders = db.query(Order).filter(
        Order.restaurant_id == restaurant.id
    ).order_by(Order.created_at.desc()).all()
    
    return orders


@router.put("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_restaurant_owner_user)
):
    """
    Update order status (restaurant owner can move: placed -> preparing).
    """
    restaurant = get_owner_restaurant(db, current_user.id)
    
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.restaurant_id == restaurant.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Restaurant owner can only move from placed to preparing
    if order.status != "placed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order can only be moved to preparing from placed status"
        )
    
    if status_update.status.value != "preparing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant owner can only move order to preparing status"
        )
    
    old_status = order.status
    order.status = status_update.status.value
    db.commit()
    db.refresh(order)
    
    # Send notifications
    notify_order_status_change(db, order, old_status)
    
    return order


@router.put("/toggle-ordering")
def toggle_ordering(
    toggle_data: RestaurantToggleOrdering,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_restaurant_owner_user)
):
    """Enable/disable ordering for restaurant."""
    restaurant = get_owner_restaurant(db, current_user.id)
    
    restaurant.is_ordering_enabled = toggle_data.is_ordering_enabled
    db.commit()
    
    return {
        "message": f"Ordering {'enabled' if toggle_data.is_ordering_enabled else 'disabled'} successfully",
        "is_ordering_enabled": toggle_data.is_ordering_enabled
    }
