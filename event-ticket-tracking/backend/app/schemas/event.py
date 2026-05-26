from pydantic import BaseModel
from typing import Optional, List, Any

class EventCreate(BaseModel):
    title: str
    description: str
    date: str  # ISO Date format, e.g. "2026-05-30"
    time_limit: Optional[int] = None  # time limit in minutes
    custom_questions: Optional[List[Any]] = None  # JSON/List representation of custom questions

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    time_limit: Optional[int] = None
    custom_questions: Optional[List[Any]] = None

class EventResponse(BaseModel):
    id: int
    title: str
    description: str
    date: str
    time_limit: Optional[int] = None
    custom_questions: Optional[List[Any]] = None
    created_by_admin_id: int

    class Config:
        orm_mode = True
