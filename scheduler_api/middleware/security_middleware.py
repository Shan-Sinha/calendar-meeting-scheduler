import os
import re
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import HTTPException, Request
from jose import jwt
from typing import Callable
from starlette.types import ASGIApp
from dotenv import load_dotenv

load_dotenv()

class SecurityMiddleware(BaseHTTPMiddleware):
    EXCLUDED_PATHS = [
        "/auth/login",
        "/auth/register",
        "/docs",
        "/openapi.json",
        "/health",
        "/favicon.ico"
    ]
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.JWT_SECRET = os.getenv("JWT_SECRET", "your_strong_secret_here")
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")

    async def dispatch(self, request: Request, call_next: Callable):
        # Check if path should be excluded
        if any(re.fullmatch(pattern, request.url.path) is not None for pattern in self.EXCLUDED_PATHS):
            print("Inside")
            return await call_next(request)
        
        print("Outside")
        # Get Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="Authorization header missing")
        
        # Extract token
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
        
        token = parts[1]
        
        try:
            payload = jwt.decode(token, self.JWT_SECRET, algorithms=[self.ALGORITHM])
            request.state.user_email = payload.get("sub")
            if not request.state.user_email:
                raise HTTPException(status_code=401, detail="Invalid token payload")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
        
        return await call_next(request)