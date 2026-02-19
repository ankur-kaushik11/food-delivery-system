"""
Delivery Partner API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies.auth import get_delivery_partner_user
from app.models.models import User, DeliveryPartner, Order
from app.schemas.schemas import (
    DeliveryPartnerToggle, DeliveryPartnerResponse,
    OrderResponse, OrderStatusUpdate
)
from app.services import delivery_service
from app.utils.notifications import notify_order_status_change

router = APIRouter(prefix="/api/delivery", tags=["Delivery Partner"])


def get_delivery_partner_record(db: Session, user_id: int) -> DeliveryPartner:
    """Get delivery partner record for user."""
    partner = db.query(DeliveryPartner).filter(DeliveryPartner.user_id == user_id).first()
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery partner record not found"
        )
    return partner


@router.put("/toggle-availability", response_model=DeliveryPartnerResponse)
def toggle_availability(
    toggle_data: DeliveryPartnerToggle,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_delivery_partner_user)
):
    """Toggle delivery partner availability."""
    partner = get_delivery_partner_record(db, current_user.id)
    
    partner.available = toggle_data.available
    db.commit()
    db.refresh(partner)
    
    return partner


@router.get("/assigned-orders", response_model=List[OrderResponse])
def get_assigned_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_delivery_partner_user)
):
    """Get orders assigned to delivery partner."""
    orders = db.query(Order).filter(
        Order.delivery_partner_id == current_user.id,
        Order.status.in_(["preparing", "out_for_delivery"])
    ).order_by(Order.created_at.desc()).all()
    
    return orders


@router.put("/orders/{order_id}/status", response_model=OrderResponse)
def update_delivery_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_delivery_partner_user)
):
    """
    Update order delivery status.
    Delivery partner can move: preparing -> out_for_delivery -> delivered.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Assign delivery partner if moving to out_for_delivery
    if status_update.status.value == "out_for_delivery" and order.status == "preparing":
        if not order.delivery_partner_id:
            # Assign current delivery partner
            order.delivery_partner_id = current_user.id
            # Mark as unavailable
            partner = get_delivery_partner_record(db, current_user.id)
            partner.available = False
    
    # Verify order is assigned to this delivery partner for status updates
    if order.status in ["out_for_delivery", "delivered"]:
        if order.delivery_partner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This order is not assigned to you"
            )
    
    # Validate status transitions
    valid_transitions = {
        "preparing": ["out_for_delivery"],
        "out_for_delivery": ["delivered"]
    }
    
    if order.status not in valid_transitions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update status from {order.status}"
        )
    
    if status_update.status.value not in valid_transitions[order.status]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from {order.status} to {status_update.status.value}"
        )
    
    old_status = order.status
    order.status = status_update.status.value
    
    # Release delivery partner when order is delivered
    if order.status == "delivered" and order.delivery_partner_id:
        delivery_service.release_delivery_partner(db, order.delivery_partner_id)
    
    db.commit()
    db.refresh(order)
    
    # Send notifications
    notify_order_status_change(db, order, old_status)
    
    return order
