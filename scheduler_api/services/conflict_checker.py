from sqlalchemy import select, and_, or_, not_
from datetime import datetime
from models import Meeting, User
from utils.time_utils import ensure_utc

async def has_time_conflict(db, start: datetime, end: datetime, user_ids: list[int], exclude_meeting_id: int = None):
    """
    Check if any user has overlapping meetings, optionally excluding a specific meeting by ID.
    """
    # Convert to UTC for comparison
    start_utc = ensure_utc(start)
    end_utc = ensure_utc(end)
    
    conditions = [
        User.id.in_(user_ids),
        or_(
            and_(
                Meeting.start_time < end_utc,
                Meeting.end_time > start_utc
            ),
            Meeting.start_time.between(start_utc, end_utc),
            Meeting.end_time.between(start_utc, end_utc)
        )
    ]
    if exclude_meeting_id is not None:
        conditions.append(Meeting.id != exclude_meeting_id)
    
    stmt = (
        select(Meeting)
        .join(Meeting.attendees)
        .where(and_(*conditions))
        .limit(1)
    )
    
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None