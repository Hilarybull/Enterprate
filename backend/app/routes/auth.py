"""Authentication routes"""
from fastapi import APIRouter, Depends
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
    return await AuthService.register_user(user_data)

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login user"""
    return await AuthService.login_user(credentials)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: dict = Depends(get_current_user)):
    """Get current user info"""
    return user
