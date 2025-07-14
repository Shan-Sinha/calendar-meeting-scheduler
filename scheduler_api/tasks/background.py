from fastapi import BackgroundTasks
from sqlalchemy import delete, select
from datetime import datetime, timedelta
from dependencies import get_db
from models import Meeting
from services.notification_service import send_reminder
import asyncio
import logging

logger = logging.getLogger(__name__)

async def purge_old_meetings():
    async for db in get_db():
        try:
            cutoff = datetime.utcnow() - timedelta(days=30)
            await db.execute(delete(Meeting).where(Meeting.end_time < cutoff))
            await db.commit()
            logger.info(f"Purged meetings older than {cutoff}")
        except Exception as e:
            logger.error(f"Error purging meetings: {e}")
            await db.rollback()

async def send_reminders():
    async for db in get_db():
        try:
            now = datetime.utcnow()
            reminder_window = now + timedelta(minutes=30)
            
            stmt = (
                select(Meeting)
                .options(selectinload(Meeting.attendees))
                .where(
                    and_(
                        Meeting.start_time > now,
                        Meeting.start_time <= reminder_window,
                        Meeting.reminder_sent == False  # noqa: E712
                    )
                )
            )
            result = await db.execute(stmt)
            meetings = result.scalars().all()
            
            for meeting in meetings:
                await send_reminder(meeting)
                meeting.reminder_sent = True
                db.add(meeting)
            
            await db.commit()
            logger.info(f"Sent reminders for {len(meetings)} meetings")
        except Exception as e:
            logger.error(f"Error sending reminders: {e}")