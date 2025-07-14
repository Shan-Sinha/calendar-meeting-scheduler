from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, Request
from core.database import get_db as get_db_session

async def get_db() -> AsyncSession:
    async for session in get_db_session():
        yield session

async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Get the current user from request state."""
    if not hasattr(request.state, "user_email"):
        return None
    
    from crud.user import get_user_by_email
    return await get_user_by_email(db, request.state.user_email)

async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
):
    """Get the current active user."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user