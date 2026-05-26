from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base
import datetime

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(String, ForeignKey("registrations.id"), nullable=False, unique=True)
    scanned_at = Column(DateTime, default=datetime.datetime.utcnow)
    scanner_admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    registration = relationship("Registration", back_populates="attendance")
    scanner = relationship("User", back_populates="scanned_attendances")
