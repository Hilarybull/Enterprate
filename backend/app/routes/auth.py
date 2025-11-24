"""Authentication routes"""
from fastapi import APIRouter, Depends
from app.schemas.user import UserCreate, UserLogin
from app.services.auth_service import AuthService
from app.core.security import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register")
async def register(user_data: UserCreate):
    """Register a new user"""
    return await AuthService.register_user(user_data)

@router.post("/login")
async def login(credentials: UserLogin):
    """Login with email and password"""
    return await AuthService.login_user(credentials)

@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {"id": user['id'], "email": user['email'], "name": user['name']}

@router.get("/google")
async def google_auth():
    """Google OAuth integration (placeholder)"""
    return {"message": "Google OAuth integration - to be implemented"}
