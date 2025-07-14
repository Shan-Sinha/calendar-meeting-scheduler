from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    model_config = {
        "from_attributes": True  # Replaces orm_mode = True
    }

class Token(BaseModel):
    access_token: str
    token_type: str