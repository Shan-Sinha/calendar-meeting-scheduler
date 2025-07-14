from datetime import datetime, timezone
import pytz

def ensure_utc(dt: datetime) -> datetime:
    """Convert any datetime to UTC timezone-aware"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def convert_to_user_tz(dt: datetime, tz_str: str) -> datetime:
    """Convert UTC datetime to user's timezone"""
    utc_dt = ensure_utc(dt)
    user_tz = pytz.timezone(tz_str)
    return utc_dt.astimezone(user_tz)