from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # stores password hash
    role = Column(String, nullable=False)      # student / admin
    
    # Student specific fields
    student_number = Column(String, nullable=True)
    year_level = Column(String, nullable=True)
    department = Column(String, nullable=True)
    course = Column(String, nullable=True)
    
    # Admin specific fields
    organization = Column(String, nullable=True)
    position = Column(String, nullable=True)

    # Relationships
    registrations = relationship("Registration", back_populates="student", cascade="all, delete-orphan")
    created_events = relationship("Event", back_populates="creator")
    scanned_attendances = relationship("Attendance", back_populates="scanner")