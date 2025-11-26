"""Password reset routes"""
import os
import uuid
import logging
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.core.database import get_db
from app.core.security import hash_password

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

# In-memory store for reset tokens (in production, use Redis or DB)
reset_tokens = {}

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    newPassword: str

class VerifyTokenRequest(BaseModel):
    token: str

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Request a password reset link"""
    db = get_db()
    
    # Check if user exists
    user = await db.users.find_one({"email": request.email})
    
    if not user:
        # Don't reveal if email exists for security
        return {"message": "If an account with this email exists, a reset link has been sent."}
    
    # Generate reset token
    reset_token = str(uuid.uuid4())
    expiry = datetime.now(timezone.utc) + timedelta(hours=1)
    
    # Store token
    reset_tokens[reset_token] = {
        "user_id": user["id"],
        "email": request.email,
        "expires_at": expiry.isoformat()
    }
    
    # In production, send email here with reset link
    # For now, log the token (for testing purposes)
    logger.info(f"Password reset token generated for {request.email}: {reset_token}")
    
    # For demo purposes, return the token (in production, only send via email)
    return {
        "message": "If an account with this email exists, a reset link has been sent.",
        "resetToken": reset_token,  # Remove this in production!
        "note": "In production, this token would be sent via email"
    }

@router.post("/verify-reset-token")
async def verify_reset_token(request: VerifyTokenRequest):
    """Verify if a reset token is valid"""
    token_data = reset_tokens.get(request.token)
    
    if not token_data:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    # Check expiry
    expires_at = datetime.fromisoformat(token_data["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        del reset_tokens[request.token]
        raise HTTPException(status_code=400, detail="Reset token has expired")
    
    return {"valid": True, "email": token_data["email"]}

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset password using token"""
    db = get_db()
    
    # Verify token
    token_data = reset_tokens.get(request.token)
    
    if not token_data:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    # Check expiry
    expires_at = datetime.fromisoformat(token_data["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        del reset_tokens[request.token]
        raise HTTPException(status_code=400, detail="Reset token has expired")
    
    # Validate password
    if len(request.newPassword) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    # Update password
    new_hash = hash_password(request.newPassword)
    result = await db.users.update_one(
        {"id": token_data["user_id"]},
        {"$set": {"password_hash": new_hash}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Failed to update password")
    
    # Remove used token
    del reset_tokens[request.token]
    
    return {"message": "Password has been reset successfully. You can now login with your new password."}
