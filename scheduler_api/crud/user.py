from sqlalchemy import select
from models import User
from schemas import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession

async def get_user_by_email(db: AsyncSession, email: str):
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: UserCreate):
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=user.password  # Already hashed
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user