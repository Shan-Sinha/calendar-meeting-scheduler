from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from dependencies import get_db
from services.conflict_checker import has_time_conflict
from crud.user import get_user_by_email
import logging
from utils.time_utils import ensure_utc

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/availability/{email}")
async def check_availability(
    email: str,
    start: datetime,
    end: datetime,
    db: AsyncSession = Depends(get_db),
):  
    try:
        user = await get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        start_utc = ensure_utc(start)
        end_utc = ensure_utc(end)
        is_conflict = await has_time_conflict(db, start_utc, end_utc, [user.id])
        return {
            "available": not is_conflict,
            "user_id": user.id,
            "email": user.email
        }
    except Exception as e:
        logger.error(f"Availability check error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )