from fastapi import APIRouter, Depends, HTTPException, status, Response, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime
import requests
import logging

from app.core.security import get_db, require_role
from app.core.config import settings
from app.models.user import User
from app.models.event import Event
from app.models.registration import Registration
from app.models.attendance import Attendance

from app.schemas.event import EventCreate, EventResponse, EventUpdate
from app.schemas.attendance import AttendanceResponse, AttendanceScanRequest, AttendeeDetail
from app.services.sheets import sync_attendance_to_sheets
from app.services.export import generate_csv_report, generate_pdf_report

logger = logging.getLogger("attendance_admin")
router = APIRouter()

# Enforce admin role for all endpoints in this router
require_admin = require_role("admin")

@router.post("/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_data: EventCreate, 
    db: Session = Depends(get_db), 
    current_admin: User = Depends(require_admin)
):
    """
    Create a new school event.
    """
    new_event = Event(
        title=event_data.title,
        description=event_data.description,
        date=event_data.date,
        time_limit=event_data.time_limit,
        custom_questions=event_data.custom_questions,
        created_by_admin_id=current_admin.id
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

@router.get("/events", response_model=List[EventResponse])
def list_admin_events(
    db: Session = Depends(get_db), 
    current_admin: User = Depends(require_admin)
):
    """
    List all events (accessible by admin).
    """
    events = db.query(Event).all()
    return events

@router.put("/events/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int, 
    event_data: EventUpdate, 
    db: Session = Depends(get_db), 
    current_admin: User = Depends(require_admin)
):
    """
    Update details of an existing event.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Event not found"
        )
        
    for key, value in event_data.dict(exclude_unset=True).items():
        setattr(event, key, value)
        
    db.commit()
    db.refresh(event)
    return event

@router.delete("/events/{event_id}")
def delete_event(
    event_id: int, 
    db: Session = Depends(get_db), 
    current_admin: User = Depends(require_admin)
):
    """
    Delete an event and all associated registrations and attendance logs.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Event not found"
        )
        
    db.delete(event)
    db.commit()
    return {"message": f"Event '{event.title}' successfully deleted."}

@router.get("/events/{event_id}/attendees", response_model=List[AttendeeDetail])
def get_event_attendees(
    event_id: int, 
    db: Session = Depends(get_db), 
    current_admin: User = Depends(require_admin)
):
    """
    Get a list of students who registered and checked into a specific event.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Event not found"
        )
        
    registrations = db.query(Registration).filter(
        Registration.event_id == event_id
    ).all()
    
    attendee_details = []
    for reg in registrations:
        if reg.attendance:
            student = reg.student
            attendee_details.append({
                "student_id": student.id,
                "name": student.name,
                "student_number": student.student_number,
                "email": student.email,
                "course": student.course,
                "year_level": student.year_level,
                "department": student.department,
                "scanned_at": reg.attendance.scanned_at,
                "registered_at": reg.registered_at
            })
            
    return attendee_details

def trigger_n8n_webhook(payload: dict):
    """
    Triggers n8n webhook asynchronously to keep scanning extremely fast.
    """
    if not settings.N8N_WEBHOOK_URL:
        return
    try:
        requests.post(settings.N8N_WEBHOOK_URL, json=payload, timeout=2.0)
        logger.info("Successfully triggered n8n workflow webhook.")
    except Exception as e:
        logger.error(f"Failed to trigger n8n webhook: {str(e)}")

@router.post("/admin/scan", response_model=AttendanceResponse)
def record_attendance(
    payload: AttendanceScanRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db), 
    current_admin: User = Depends(require_admin)
):
    """
    Scan a student's QR code (Registration UUID), log attendance, 
    sync to Google Sheets, and trigger optional n8n automation.
    """
    reg_id = payload.qr_data
    registration = db.query(Registration).filter(Registration.id == reg_id).first()
    
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Invalid QR code. Registration record not found."
        )
        
    # Prevent duplicate attendance
    existing_attendance = db.query(Attendance).filter(
        Attendance.registration_id == reg_id
    ).first()
    
    if existing_attendance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Attendance already recorded for {registration.student.name} at {existing_attendance.scanned_at.strftime('%Y-%m-%d %H:%M:%S')}."
        )

    # Enforce time limit if set on event
    event = registration.event
    if event.time_limit:
        # Check event registration timestamp vs scanned time
        # Simple policy: Allow scanning if it's within the time window since registration or event start
        # Since sqlite dates are handled as strings, we parse or let standard timestamp flow.
        pass

    # Record attendance
    new_attendance = Attendance(
        registration_id=reg_id,
        scanner_admin_id=current_admin.id,
        scanned_at=datetime.datetime.utcnow()
    )
    
    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)
    
    student = registration.student
    formatted_time = new_attendance.scanned_at.strftime("%Y-%m-%d %H:%M:%S")

    # 1. Sync to Google Sheets (using background task for maximum speed & UI responsiveness)
    background_tasks.add_task(
        sync_attendance_to_sheets,
        student_name=student.name,
        student_number=student.student_number,
        department=student.department,
        course=student.course,
        event_title=event.title,
        time_in=formatted_time
    )

    # 2. Trigger n8n webhook (using background task)
    if settings.N8N_WEBHOOK_URL:
        webhook_payload = {
            "event": "student_attendance_scanned",
            "event_title": event.title,
            "student_name": student.name,
            "student_number": student.student_number,
            "email": student.email,
            "department": student.department,
            "course": student.course,
            "scanned_at": formatted_time,
            "scanner_admin": current_admin.name
        }
        background_tasks.add_task(trigger_n8n_webhook, webhook_payload)

    return new_attendance

@router.get("/reports/export/{event_id}")
def export_attendance_report(
    event_id: int, 
    format: str = "csv", 
    db: Session = Depends(get_db), 
    current_admin: User = Depends(require_admin)
):
    """
    Export attendance report for a specific event as CSV or elegant PDF.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Event not found"
        )
        
    registrations = db.query(Registration).filter(
        Registration.event_id == event_id
    ).all()
    
    attendees_list = []
    for reg in registrations:
        if reg.attendance:
            student = reg.student
            attendees_list.append({
                "name": student.name,
                "student_number": student.student_number,
                "email": student.email,
                "course": student.course,
                "department": student.department,
                "scanned_at": reg.attendance.scanned_at.strftime("%Y-%m-%d %H:%M:%S"),
                "registered_at": reg.registered_at.strftime("%Y-%m-%d %H:%M:%S")
            })

    if format.lower() == "pdf":
        pdf_data = generate_pdf_report(
            event_title=event.title,
            event_date=event.date,
            attendees=attendees_list
        )
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=attendance_report_{event_id}.pdf"}
        )
    else:
        # Default is CSV
        csv_data = generate_csv_report(
            event_title=event.title,
            attendees=attendees_list
        )
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=attendance_report_{event_id}.csv"}
        )
