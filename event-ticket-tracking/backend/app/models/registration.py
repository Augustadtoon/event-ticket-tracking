from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base
import datetime
import uuid

class Registration(Base):
    __tablename__ = "registrations"

    # UUID primary key to keep QR codes unique, random, and unguessable
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    qr_code_hash = Column(String, unique=True, index=True, nullable=False)
    registered_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    student = relationship("User", back_populates="registrations")
    event = relationship("Event", back_populates="registrations")
    attendance = relationship("Attendance", uselist=False, back_populates="registration", cascade="all, delete-orphan")
