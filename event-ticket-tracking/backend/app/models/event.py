from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from app.db.database import Base
import datetime

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    date = Column(String, nullable=False)  # ISO Date String (e.g. YYYY-MM-DD) or DateTime string
    time_limit = Column(Integer, nullable=True)  # in minutes (e.g., scan allowed within N minutes of event start)
    custom_questions = Column(JSON, nullable=True)  # List of dicts representing custom questions
    created_by_admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    creator = relationship("User", back_populates="created_events")
    registrations = relationship("Registration", back_populates="event", cascade="all, delete-orphan")
