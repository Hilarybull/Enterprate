"""Google OAuth Schemas"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class GoogleAuthCallback(BaseModel):
    """Request schema for Google OAuth callback"""
    session_id: str


class GoogleUserResponse(BaseModel):
    """Response schema for Google authenticated user"""
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    created_at: Optional[datetime] = None


class GoogleAuthResponse(BaseModel):
    """Response schema for Google OAuth"""
    user: GoogleUserResponse
    token: str
    message: str = "Authentication successful"


class UserSession(BaseModel):
    """User session model"""
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime
