from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import get_db, get_current_user
from app.models.event import Event
from app.schemas.event import EventResponse
from app.models.user import User

router = APIRouter()

@router.get("/{event_id}", response_model=EventResponse)
def get_event_details(
    event_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Public event details endpoint. Requires valid authentication.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Event not found"
        )
    return event
