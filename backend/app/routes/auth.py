"""Authentication routes"""
from fastapi import APIRouter, Depends, Response, Request
from app.services.auth_service import AuthService
from app.services.google_auth_service import GoogleAuthService
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.schemas.google_auth import GoogleAuthCallback, GoogleAuthResponse
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


# Google OAuth Endpoints
@router.post("/google/callback", response_model=GoogleAuthResponse)
async def google_callback(data: GoogleAuthCallback, response: Response):
    """
    Process Google OAuth callback from Emergent Auth
    Exchanges session_id for user data and creates session
    """
    result = await GoogleAuthService.process_callback(data)
    
    # Set httpOnly cookie for session_token (optional, for cookie-based auth)
    response.set_cookie(
        key="session_token",
        value=result.token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=7 * 24 * 60 * 60  # 7 days
    )
    
    return result


@router.post("/google/logout")
async def google_logout(response: Response, user: dict = Depends(get_current_user)):
    """Logout user and clear session"""
    user_id = user.get("id") or user.get("user_id")
    if user_id:
        await GoogleAuthService.logout(user_id)
    
    # Clear cookie
    response.delete_cookie(key="session_token", path="/")
    
    return {"message": "Logged out successfully"}

