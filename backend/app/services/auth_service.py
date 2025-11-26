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
        
        if not user or not user.get("password_hash"):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not verify_password(credentials.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create token
        token = create_token(user["id"])
        
        return {
            "token": token,
            "user": {"id": user["id"], "email": user["email"], "name": user["name"]}
        }
