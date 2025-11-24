"""Security utilities for authentication and authorization"""
from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import UUID
import bcrypt
import jwt
from fastapi import HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import get_db

security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str) -> str:
    """Create a JWT token for a user"""
    exp = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    payload = {"user_id": user_id, "exp": exp}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    """Decode and validate a JWT token"""
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Get the current authenticated user"""
    from app.models.user import User
    
    payload = decode_token(credentials.credentials)
    user_id = UUID(payload["user_id"])
    
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Return dict format for compatibility with existing code
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name
    }

async def get_workspace_id(x_workspace_id: Optional[str] = Header(None)) -> str:
    """Get workspace ID from header"""
    if not x_workspace_id:
        raise HTTPException(status_code=400, detail="Workspace ID required in X-Workspace-Id header")
    return x_workspace_id

async def verify_workspace_access(workspace_id: str, user: dict) -> bool:
    """Verify user has access to workspace"""
    db = get_database()
    membership = await db.workspace_memberships.find_one({
        "workspaceId": workspace_id,
        "userId": user["id"]
    })
    if not membership:
        raise HTTPException(status_code=403, detail="Access denied to workspace")
    return True
