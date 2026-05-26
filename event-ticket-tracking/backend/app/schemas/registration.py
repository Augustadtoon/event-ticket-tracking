from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RegistrationCreate(BaseModel):
    # Registration doesn't need input fields since student_id comes from token
    # and event_id is path parameter, but we can have custom_answers if they answer custom questions
    custom_answers: Optional[dict] = None

class RegistrationResponse(BaseModel):
    id: str
    student_id: int
    event_id: int
    qr_code_hash: str
    registered_at: datetime

    class Config:
        orm_mode = True

class RegistrationDetailResponse(BaseModel):
    id: str
    student_id: int
    event_id: int
    event_title: str
    registered_at: datetime
    qr_code_base64: str
    attended: bool
    scanned_at: Optional[datetime] = None

    class Config:
        orm_mode = True
