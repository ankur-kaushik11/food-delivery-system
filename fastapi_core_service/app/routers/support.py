"""
Customer Care/Support API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.dependencies.auth import get_customer_care_user
from app.models.models import User, Complaint
from app.schemas.schemas import ComplaintResponse, ComplaintResolve
from app.utils.notifications import notify_complaint_resolved

router = APIRouter(prefix="/api/support", tags=["Customer Care"])


@router.get("/complaints", response_model=List[ComplaintResponse])
def list_all_complaints(
    status_filter: str = "open",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_care_user)
):
    """List all complaints (filterable by status)."""
    query = db.query(Complaint)
    
    if status_filter and status_filter in ["open", "resolved"]:
        query = query.filter(Complaint.status == status_filter)
    
    complaints = query.order_by(Complaint.created_at.desc()).all()
    return complaints


@router.put("/complaints/{complaint_id}/resolve", response_model=ComplaintResponse)
def resolve_complaint(
    complaint_id: int,
    resolve_data: ComplaintResolve,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_care_user)
):
    """Resolve a complaint."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    if complaint.status == "resolved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Complaint is already resolved"
        )
    
    complaint.status = "resolved"
    complaint.resolution_notes = resolve_data.resolution_notes
    complaint.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(complaint)
    
    # Send notification to customer
    notify_complaint_resolved(db, complaint.id, complaint.customer_id, complaint.order_id)
    
    return complaint
