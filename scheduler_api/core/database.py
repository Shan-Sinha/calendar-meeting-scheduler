import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from dotenv import load_dotenv
from models.user import Base as UserBase
from models.meeting import Base as MeetingBase


# Load environment variables
load_dotenv()

# Get database settings
POSTGRES_URI = os.getenv("POSTGRES_URI", "postgresql+asyncpg://user:pass@localhost:5432/scheduler")
SYNC_POSTGRES_URI = POSTGRES_URI.replace("+asyncpg", "")

# Base = declarative_base()

# Async engine for application use
async_engine = create_async_engine(
    POSTGRES_URI,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)

# Sync engine for table creation
sync_engine = create_engine(SYNC_POSTGRES_URI)

# Create tables synchronously
def create_tables():
    UserBase.metadata.create_all(sync_engine)
    MeetingBase.metadata.create_all(sync_engine)


AsyncSessionLocal = sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autoflush=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()