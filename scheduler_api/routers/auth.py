import os
from fastapi import APIRouter, Depends, HTTPException, status, Request  
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from core.security import create_access_token, hash_password, verify_password
from crud.user import create_user, get_user_by_email
from dependencies import get_db
from schemas import UserCreate, Token, User
import logging
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/me", response_model=User)
async def get_current_user_profile(
    request: Request,  # Request parameter
    db: AsyncSession = Depends(get_db)
):
    """Get current user profile."""
    if not hasattr(request.state, "user_email"):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = await get_user_by_email(db, request.state.user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate,db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    existing_user = await get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = hash_password(user.password)
    new_user = await create_user(db, UserCreate(
        email=user.email,
        full_name=user.full_name,
        password=hashed_password
    ))
    return new_user

@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return JWT token."""
    user = await get_user_by_email(db, form_data.username)
    print(user)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def get_current_user_profile(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Get current user profile."""
    if not hasattr(request.state, "user_email"):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = await get_user_by_email(db, request.state.user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user