from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.security import get_db, require_role
from app.models.user import User
from app.models.event import Event
from app.models.registration import Registration
from app.models.attendance import Attendance
from app.schemas.event import EventResponse
from app.schemas.registration import RegistrationResponse, RegistrationDetailResponse
from app.services.qr import generate_qr_base64

router = APIRouter()

# Enforce student role
require_student = require_role("student")

@router.get("/events", response_model=List[EventResponse])
def get_available_events(
    db: Session = Depends(get_db), 
    current_student: User = Depends(require_student)
):
    """
    Get a list of all events available for registration.
    """
    events = db.query(Event).all()
    return events

@router.post("/events/{event_id}/register", response_model=RegistrationDetailResponse)
def register_for_event(
    event_id: int, 
    db: Session = Depends(get_db), 
    current_student: User = Depends(require_student)
):
    """
    Register the logged-in student for a specific event.
    Checks for duplicates, generates registration UUID, produces base64 QR code image, and returns details.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Event not found"
        )
        
    # Prevent duplicate registration
    existing = db.query(Registration).filter(
        Registration.student_id == current_student.id,
        Registration.event_id == event_id
    ).first()
    
    if existing:
        # If already registered, return details including QR code
        qr_code = generate_qr_base64(existing.id)
        attended = existing.attendance is not None
        scanned_at = existing.attendance.scanned_at if attended else None
        
        return {
            "id": existing.id,
            "student_id": existing.student_id,
            "event_id": existing.event_id,
            "event_title": event.title,
            "registered_at": existing.registered_at,
            "qr_code_base64": qr_code,
            "attended": attended,
            "scanned_at": scanned_at
        }

    # Create new registration
    # Store registration UUID as the hash/identifier for verification
    import uuid
    reg_id = str(uuid.uuid4())
    
    new_reg = Registration(
        id=reg_id,
        student_id=current_student.id,
        event_id=event_id,
        qr_code_hash=reg_id
    )
    
    db.add(new_reg)
    db.commit()
    db.refresh(new_reg)
    
    qr_code = generate_qr_base64(reg_id)
    
    return {
        "id": new_reg.id,
        "student_id": new_reg.student_id,
        "event_id": new_reg.event_id,
        "event_title": event.title,
        "registered_at": new_reg.registered_at,
        "qr_code_base64": qr_code,
        "attended": False,
        "scanned_at": None
    }

@router.get("/history", response_model=List[RegistrationDetailResponse])
def get_attendance_history(
    db: Session = Depends(get_db), 
    current_student: User = Depends(require_student)
):
    """
    Fetch the student's historical event registrations, QR codes, and attendance statuses.
    """
    registrations = db.query(Registration).filter(
        Registration.student_id == current_student.id
    ).all()
    
    history_list = []
    for reg in registrations:
        attended = reg.attendance is not None
        scanned_at = reg.attendance.scanned_at if attended else None
        qr_code = generate_qr_base64(reg.id)
        
        history_list.append({
            "id": reg.id,
            "student_id": reg.student_id,
            "event_id": reg.event_id,
            "event_title": reg.event.title,
            "registered_at": reg.registered_at,
            "qr_code_base64": qr_code,
            "attended": attended,
            "scanned_at": scanned_at
        })
        
    return history_list
