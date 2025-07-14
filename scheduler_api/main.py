import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from middleware.security_middleware import SecurityMiddleware
from routers import meetings, availability, auth
from tasks.background import purge_old_meetings, send_reminders
from core.database import create_tables
from contextlib import asynccontextmanager
import logging
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    logger.info("Starting background tasks")
    create_tables()
    # asyncio.create_task(run_periodic_tasks())
    yield
    # Shutdown tasks
    logger.info("Stopping application")

app = FastAPI(
    title="Meeting Scheduler API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None
)

# Add security middleware
app.add_middleware(SecurityMiddleware)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(meetings.router, prefix="/meetings", tags=["Meetings"])
app.include_router(availability.router, prefix="/availability", tags=["Availability"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Background task runner
async def run_periodic_tasks():
    while True:
        try:
            await asyncio.gather(
                purge_old_meetings(),
                send_reminders()
            )
            await asyncio.sleep(300)  # Run every 5 minutes
        except Exception as e:
            logger.error(f"Background task error: {e}")
            await asyncio.sleep(60)  # Wait before retrying