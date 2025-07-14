from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.meeting import MeetingCreate, Meeting, MeetingUpdate
from dependencies import get_db, get_current_active_user
from crud import meeting as crud
from services.calendar_adapter import GoogleCalendarAdapter
import logging
from datetime import datetime
from utils.time_utils import ensure_utc

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=Meeting, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    meeting: MeetingCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new meeting."""
    try:
        # Create meeting
        db_meeting = await crud.create_meeting(db, meeting, current_user.id)
        
        # Sync to Google Calendar if enabled
        if current_user.google_id:
            calendar = GoogleCalendarAdapter(current_user.google_credentials)
            google_event_id = await calendar.create_event(meeting)
            if google_event_id:
                db_meeting.google_event_id = google_event_id
                await db.commit()
                await db.refresh(db_meeting)
        
        return db_meeting
    except ValueError as e:
        logger.warning(f"Scheduling conflict: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating meeting: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/", response_model=list[Meeting])
async def get_meetings(
    request: Request,
    start: datetime = Query(None, description="Start date for filtering"),
    end: datetime = Query(None, description="End date for filtering"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get meetings for current user, optionally filtered by date range"""
    try:
        if start and end:
            start_utc = ensure_utc(start)
            end_utc = ensure_utc(end)
            return await crud.get_user_meetings_in_range(db, current_user.id, start_utc, end_utc)
        return await crud.get_user_meetings(db, current_user.id)
    except Exception as e:
        logger.error(f"Error getting meetings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/{meeting_id}", response_model=Meeting)
async def update_meeting(
    meeting_id: int = Path(..., description="ID of the meeting to update"),
    meeting_update: MeetingUpdate = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    updated = await crud.update_meeting(db, meeting_id, meeting_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return updated

@router.delete("/{meeting_id}", status_code=204)
async def delete_meeting(
    meeting_id: int = Path(..., description="ID of the meeting to delete"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    deleted = await crud.delete_meeting(db, meeting_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return None