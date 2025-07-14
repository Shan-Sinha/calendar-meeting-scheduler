from sqlalchemy import Column, String, DateTime, ForeignKey, Table,Integer
from sqlalchemy.orm import relationship
from models.base import Base
from models.user import User
from sqlalchemy.sql import func

meeting_attendees = Table(
    'meeting_attendees', Base.metadata,
    Column('meeting_id', ForeignKey('meetings.id'), primary_key=True),
    Column('user_id', ForeignKey(User.id), primary_key=True)
)


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False, index=True)
    location = Column(String(100), nullable=True)
    organizer_id = Column(ForeignKey(User.id), nullable=False)
    google_event_id = Column(String(255), nullable=True)
    
    attendees = relationship("User", secondary=meeting_attendees)
    organizer = relationship("User", back_populates="organized_meetings")



