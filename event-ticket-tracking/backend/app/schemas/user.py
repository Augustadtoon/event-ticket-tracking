from pydantic import BaseModel, EmailStr, validator
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str  # student or admin
    
    # Student optional fields
    student_number: Optional[str] = None
    year_level: Optional[str] = None
    department: Optional[str] = None
    course: Optional[str] = None
    
    # Admin optional fields
    organization: Optional[str] = None
    position: Optional[str] = None

    @validator("email")
    def validate_rtu_email(cls, v):
        if not v.lower().endswith("@rtu.edu.ph"):
            raise ValueError("Only RTU institutional emails (@rtu.edu.ph) are allowed.")
        return v.lower()

    @validator("role")
    def validate_role(cls, v):
        role_lower = v.lower()
        # Handle "roleStudent" or "roleAdmin" from frontend or direct signup
        if "student" in role_lower:
            return "student"
        elif "admin" in role_lower:
            return "admin"
        else:
            raise ValueError("Role must be 'student' or 'admin'.")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @validator("email")
    def validate_rtu_email(cls, v):
        if not v.lower().endswith("@rtu.edu.ph"):
            raise ValueError("Only RTU institutional emails (@rtu.edu.ph) are allowed.")
        return v.lower()

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    student_number: Optional[str] = None
    year_level: Optional[str] = None
    department: Optional[str] = None
    course: Optional[str] = None
    organization: Optional[str] = None
    position: Optional[str] = None

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str