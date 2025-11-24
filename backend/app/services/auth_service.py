"""Authentication service"""
from fastapi import HTTPException
from app.core.database import get_database
from app.core.security import hash_password, verify_password, create_token
from app.schemas.user import User, UserCreate, UserLogin

class AuthService:
    """Authentication service for user management"""
    
    @staticmethod
    async def register_user(user_data: UserCreate) -> dict:
        """Register a new user"""
        db = get_database()
        
        # Check if user exists
        existing = await db.users.find_one({"email": user_data.email})
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        user = User(
            email=user_data.email,
            name=user_data.name,
            passwordHash=hash_password(user_data.password)
        )
        
        doc = user.model_dump()
        doc['createdAt'] = doc['createdAt'].isoformat()
        await db.users.insert_one(doc)
        
        # Create token
        token = create_token(user.id)
        
        return {
            "token": token,
            "user": {"id": user.id, "email": user.email, "name": user.name}
        }
    
    @staticmethod
    async def login_user(credentials: UserLogin) -> dict:
        """Login a user"""
        db = get_database()
        
        user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
        if not user or not user.get('passwordHash'):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not verify_password(credentials.password, user['passwordHash']):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token = create_token(user['id'])
        
        return {
            "token": token,
            "user": {"id": user['id'], "email": user['email'], "name": user['name']}
        }
