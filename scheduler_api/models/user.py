from sqlalchemy import Column, String, Boolean,Integer,DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=True)  # For local auth
    is_active = Column(Boolean, default=True)
    google_id = Column(String(255), nullable=True)
    timezone = Column(String(50), default="UTC")

    organized_meetings = relationship("Meeting", back_populates="organizer")

   