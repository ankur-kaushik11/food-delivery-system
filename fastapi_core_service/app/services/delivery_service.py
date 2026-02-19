"""
Delivery partner assignment service.
"""
from sqlalchemy.orm import Session
from app.models.models import DeliveryPartner, Restaurant
from typing import Optional


def assign_delivery_partner(db: Session, restaurant_id: int) -> Optional[int]:
    """
    Find and assign an available delivery partner.
    Matches by pin_code with restaurant.
    Returns delivery partner user_id or None if no partner available.
    """
    # Get restaurant pin_code
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        return None
    
    # Find available delivery partner in same pin_code
    delivery_partner = db.query(DeliveryPartner).filter(
        DeliveryPartner.available == True,
        DeliveryPartner.pin_code == restaurant.pin_code
    ).first()
    
    if not delivery_partner:
        return None
    
    # Mark delivery partner as unavailable
    delivery_partner.available = False
    db.commit()
    
    return delivery_partner.user_id


def release_delivery_partner(db: Session, user_id: int) -> None:
    """
    Mark delivery partner as available again.
    """
    delivery_partner = db.query(DeliveryPartner).filter(
        DeliveryPartner.user_id == user_id
    ).first()
    
    if delivery_partner:
        delivery_partner.available = True
        db.commit()
