from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from models import Meeting, User
from schemas import MeetingCreate, MeetingUpdate
from services.conflict_checker import has_time_conflict
from utils.time_utils import ensure_utc
import logging

logger = logging.getLogger(__name__)

async def create_meeting(db, meeting: MeetingCreate, organizer_id: int):
    # Convert to UTC for storage
    start_utc = ensure_utc(meeting.start_time)
    end_utc = ensure_utc(meeting.end_time)
    
    # Get attendee objects
    stmt = select(User).where(User.email.in_(meeting.attendee_emails))
    result = await db.execute(stmt)
    attendees = result.scalars().all()
    
    # Check for conflicts
    if await has_time_conflict(db, start_utc, end_utc, [u.id for u in attendees] + [organizer_id]):
        raise ValueError("Scheduling conflict detected")
    
    # Create meeting
    db_meeting = Meeting(
        title=meeting.title,
        description=meeting.description,
        start_time=start_utc,
        end_time=end_utc,
        location=meeting.location,
        organizer_id=organizer_id
    )
    db_meeting.attendees = attendees
    
    db.add(db_meeting)
    await db.commit()
    await db.refresh(db_meeting)
    # Eagerly load relationships for async serialization
    stmt = (
        select(Meeting)
        .options(selectinload(Meeting.attendees), selectinload(Meeting.organizer))
        .where(Meeting.id == db_meeting.id)
    )
    result = await db.execute(stmt)
    return result.scalar_one()

async def get_user_meetings(db, user_id: int, start: datetime, end: datetime):
    stmt = (
        select(Meeting)
        .options(selectinload(Meeting.attendees), selectinload(Meeting.organizer))
        .join(Meeting.attendees)
        .where(
            and_(
                User.id == user_id,
                Meeting.start_time >= ensure_utc(start),
                Meeting.end_time <= ensure_utc(end)
            )
        )
        .order_by(Meeting.start_time)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_user_meetings_in_range(db: AsyncSession, user_id: int, start: datetime, end: datetime):
    """Get meetings for a user within a specific date range"""
    stmt = (
        select(Meeting)
        .options(selectinload(Meeting.attendees), selectinload(Meeting.organizer))
        .join(Meeting.attendees)
        .where(
            and_(
                User.id == user_id,
                Meeting.start_time >= ensure_utc(start),
                Meeting.end_time <= ensure_utc(end)
            )
        )
        .order_by(Meeting.start_time)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def update_meeting(db, meeting_id: int, meeting_update: MeetingUpdate):
    stmt = select(Meeting).where(Meeting.id == meeting_id).options(selectinload(Meeting.attendees))
    result = await db.execute(stmt)
    db_meeting = result.scalar_one_or_none()
    if not db_meeting:
        return None
    # Update fields if provided
    for field in ["title", "description", "start_time", "end_time", "location"]:
        value = getattr(meeting_update, field, None)
        if value is not None:
            setattr(db_meeting, field, value)
    # Update attendees if provided
    if meeting_update.attendee_emails is not None:
        stmt = select(User).where(User.email.in_(meeting_update.attendee_emails))
        result = await db.execute(stmt)
        attendees = result.scalars().all()
        db_meeting.attendees = attendees
    await db.commit()
    await db.refresh(db_meeting)
    return db_meeting

async def delete_meeting(db, meeting_id: int):
    stmt = select(Meeting).where(Meeting.id == meeting_id)
    result = await db.execute(stmt)
    db_meeting = result.scalar_one_or_none()
    if not db_meeting:
        return False
    await db.delete(db_meeting)
    await db.commit()
    return True