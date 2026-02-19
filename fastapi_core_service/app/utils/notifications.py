"""
Notification simulation service.
"""
from sqlalchemy.orm import Session
from app.models.models import Notification, User, Order
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def send_notification(
    db: Session,
    user_id: int,
    order_id: int,
    notification_type: str,
    message: str
) -> None:
    """
    Simulate sending notification by logging and storing in database.
    """
    # Log to console
    logger.info(f"[NOTIFICATION] Type: {notification_type}, User: {user_id}, Order: {order_id}, Message: {message}")
    print(f"[NOTIFICATION] Type: {notification_type}, User: {user_id}, Order: {order_id}, Message: {message}")
    
    # Store in database
    notification = Notification(
        user_id=user_id,
        order_id=order_id,
        type=notification_type,
        message=message,
        created_at=datetime.utcnow()
    )
    db.add(notification)
    db.commit()


def notify_order_placed(db: Session, order: Order) -> None:
    """Send notifications when order is placed."""
    # Notify customer
    send_notification(
        db,
        user_id=order.customer_id,
        order_id=order.id,
        notification_type="ORDER_PLACED_CUSTOMER",
        message=f"Your order #{order.id} has been placed successfully! Total: ₹{order.total_amount}"
    )
    
    # Notify restaurant owner
    send_notification(
        db,
        user_id=order.restaurant.owner_id,
        order_id=order.id,
        notification_type="ORDER_PLACED_RESTAURANT",
        message=f"New order #{order.id} received! Please start preparing."
    )


def notify_order_status_change(db: Session, order: Order, old_status: str) -> None:
    """Send notifications when order status changes."""
    status_messages = {
        "preparing": "Your order is being prepared",
        "out_for_delivery": "Your order is out for delivery",
        "delivered": "Your order has been delivered!",
        "cancelled": "Your order has been cancelled"
    }
    
    message = status_messages.get(order.status, f"Order status updated to {order.status}")
    
    # Notify customer
    send_notification(
        db,
        user_id=order.customer_id,
        order_id=order.id,
        notification_type=f"ORDER_STATUS_{order.status.upper()}",
        message=f"Order #{order.id}: {message}"
    )
    
    # Notify delivery partner when assigned
    if order.status == "out_for_delivery" and order.delivery_partner_id:
        send_notification(
            db,
            user_id=order.delivery_partner_id,
            order_id=order.id,
            notification_type="ORDER_ASSIGNED_DELIVERY",
            message=f"Order #{order.id} assigned to you for delivery"
        )


def notify_complaint_resolved(db: Session, complaint_id: int, customer_id: int, order_id: int) -> None:
    """Send notification when complaint is resolved."""
    send_notification(
        db,
        user_id=customer_id,
        order_id=order_id,
        notification_type="COMPLAINT_RESOLVED",
        message=f"Your complaint #{complaint_id} has been resolved"
    )
