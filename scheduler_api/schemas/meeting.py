from pydantic import BaseModel, field_validator, computed_field
from datetime import datetime
from typing import List, Optional
from .user import User

class MeetingBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    attendee_emails: List[str] = []

    @field_validator('end_time')
    def end_time_after_start_time(cls, v, values):
        if 'start_time' in values.data and v <= values.data['start_time']:
            raise ValueError("End time must be after start time")
        return v

class MeetingCreate(MeetingBase):
    pass

class MeetingUpdate(BaseModel):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    attendee_emails: Optional[List[str]] = None

class Meeting(MeetingBase):
    id: int
    organizer: User
    attendees: List[User]
    google_event_id: Optional[str] = None
    
    model_config = {
        "from_attributes": True
    }
    
    @computed_field
    @property
    def start_time_utc(self) -> str:
        return self.start_time.isoformat() + "Z"
    
    @computed_field
    @property
    def end_time_utc(self) -> str:
        return self.end_time.isoformat() + "Z"