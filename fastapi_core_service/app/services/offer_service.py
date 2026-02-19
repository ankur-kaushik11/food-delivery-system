"""
Offer service for handling offer eligibility and application.
"""
from sqlalchemy.orm import Session
from app.models.models import Offer, Order, User
from decimal import Decimal
from typing import Optional, Tuple


def get_applicable_offers(
    db: Session,
    user_id: int,
    restaurant_id: int,
    order_amount: Decimal
) -> list[Offer]:
    """
    Get all applicable offers for a user's order.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []
    
    # Check if user is first-time customer
    previous_orders = db.query(Order).filter(
        Order.customer_id == user_id,
        Order.status != "cancelled"
    ).count()
    is_first_time = previous_orders == 0
    
    # Query restaurant-specific and platform-level offers
    offers = db.query(Offer).filter(
        Offer.active == True,
        Offer.min_order_value <= order_amount,
        (Offer.restaurant_id == restaurant_id) | (Offer.restaurant_id == None)
    ).all()
    
    # Filter offers based on first-time user condition
    applicable_offers = []
    for offer in offers:
        if offer.first_time_user_only and not is_first_time:
            continue
        applicable_offers.append(offer)
    
    return applicable_offers


def get_best_offer(
    db: Session,
    user_id: int,
    restaurant_id: int,
    order_amount: Decimal
) -> Optional[Offer]:
    """
    Get the best applicable offer (highest discount).
    Restaurant-specific offers take precedence over platform-level offers.
    """
    applicable_offers = get_applicable_offers(db, user_id, restaurant_id, order_amount)
    
    if not applicable_offers:
        return None
    
    # Separate restaurant-specific and platform offers
    restaurant_offers = [o for o in applicable_offers if o.restaurant_id == restaurant_id]
    platform_offers = [o for o in applicable_offers if o.restaurant_id is None]
    
    # Restaurant-specific offers take precedence
    if restaurant_offers:
        return max(restaurant_offers, key=lambda o: o.discount_percentage)
    
    if platform_offers:
        return max(platform_offers, key=lambda o: o.discount_percentage)
    
    return None


def calculate_discount(offer: Optional[Offer], order_amount: Decimal) -> Decimal:
    """
    Calculate discount amount based on offer.
    """
    if not offer:
        return Decimal("0.00")
    
    discount = (order_amount * offer.discount_percentage) / Decimal("100")
    return round(discount, 2)


def apply_offer(
    db: Session,
    user_id: int,
    restaurant_id: int,
    order_amount: Decimal,
    offer_id: Optional[int] = None
) -> Tuple[Optional[Offer], Decimal]:
    """
    Apply offer to order and return offer and discount amount.
    If offer_id is provided, validate and use it.
    Otherwise, use the best applicable offer.
    """
    if offer_id:
        offer = db.query(Offer).filter(Offer.id == offer_id).first()
        if not offer or not offer.active:
            return None, Decimal("0.00")
        
        # Validate offer is applicable
        applicable_offers = get_applicable_offers(db, user_id, restaurant_id, order_amount)
        if offer not in applicable_offers:
            return None, Decimal("0.00")
    else:
        offer = get_best_offer(db, user_id, restaurant_id, order_amount)
    
    discount = calculate_discount(offer, order_amount)
    return offer, discount
