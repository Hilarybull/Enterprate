"""Authentication service"""
import uuid
from datetime import datetime, timezone
from fastapi import HTTPException
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_token
from app.schemas.user import UserCreate, UserLogin

class AuthService:
    """Authentication service for user management"""
    
    @staticmethod
    async def register_user(user_data: UserCreate) -> dict:
        """Register a new user"""
        db = get_db()
        
        # Check if user exists
        existing = await db.users.find_one({"email": user_data.email})
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        user_id = str(uuid.uuid4())
        user = {
            "id": user_id,
            "email": user_data.email,
            "name": user_data.name,
            "password_hash": hash_password(user_data.password),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.users.insert_one(user)
        
        # Create token
        token = create_token(user_id)
        
        return {
            "token": token,
            "user": {"id": user_id, "email": user_data.email, "name": user_data.name}
        }
    
    @staticmethod
    async def login_user(credentials: UserLogin) -> dict:
        """Login a user"""
        db = get_db()
        
        # Find user by email
        user = await db.users.find_one({"email": credentials.email})

        # Support both new and legacy password field names.
        password_hash = None
        if user:
            password_hash = user.get("password_hash") or user.get("passwordHash")

        if not user or not password_hash:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not verify_password(credentials.password, password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Create token
        user_id = user.get("id") or user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_token(user_id)
        
        return {
            "token": token,
            "user": {"id": user_id, "email": user["email"], "name": user["name"]}
        }
