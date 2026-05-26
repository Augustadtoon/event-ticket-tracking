from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AttendanceScanRequest(BaseModel):
    qr_data: str  # This is the registration ID UUID scanned from the QR code

class AttendanceResponse(BaseModel):
    id: int
    registration_id: str
    scanned_at: datetime
    scanner_admin_id: int

    class Config:
        orm_mode = True

class AttendeeDetail(BaseModel):
    student_id: int
    name: str
    student_number: Optional[str] = None
    email: str
    course: Optional[str] = None
    year_level: Optional[str] = None
    department: Optional[str] = None
    scanned_at: datetime
    registered_at: datetime

    class Config:
        orm_mode = True
