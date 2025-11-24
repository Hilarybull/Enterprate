"""Authentication service"""
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.security import hash_password, verify_password, create_token
from app.schemas.user import UserCreate, UserLogin

class AuthService:
    """Authentication service for user management"""
    
    @staticmethod
    async def register_user(db: AsyncSession, user_data: UserCreate) -> dict:
        """Register a new user"""
        # Check if user exists
        stmt = select(User).where(User.email == user_data.email)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user (SQLAlchemy model, not Pydantic)
        user = User(
            email=user_data.email,
            name=user_data.name,
            password_hash=hash_password(user_data.password)
        )
        
        db.add(user)
        await db.flush()  # Flush to get the ID
        
        # Create token (convert UUID to string)
        token = create_token(str(user.id))
        
        return {
            "token": token,
            "user": {"id": str(user.id), "email": user.email, "name": user.name}
        }
    
    @staticmethod
    async def login_user(db: AsyncSession, credentials: UserLogin) -> dict:
        """Login a user"""
        # Find user by email
        stmt = select(User).where(User.email == credentials.email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user or not user.password_hash:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not verify_password(credentials.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create token (convert UUID to string)
        token = create_token(str(user.id))
        
        return {
            "token": token,
            "user": {"id": str(user.id), "email": user.email, "name": user.name}
        }
