"""Google OAuth Service using Emergent Auth"""
import os
import uuid
import httpx
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from app.core.database import get_database
from app.schemas.google_auth import GoogleAuthCallback, GoogleUserResponse, GoogleAuthResponse
import jwt


class GoogleAuthService:
    """Service for handling Emergent-managed Google OAuth"""
    
    EMERGENT_AUTH_URL = "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"
    SESSION_EXPIRY_DAYS = 7
    
    @staticmethod
    async def process_callback(data: GoogleAuthCallback) -> GoogleAuthResponse:
        """
        Process Google OAuth callback
        1. Exchange session_id with Emergent Auth for user data
        2. Create or update user in database
        3. Create session and return JWT token
        """
        db = await get_database()
        
        # Step 1: Exchange session_id for user data from Emergent Auth
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    GoogleAuthService.EMERGENT_AUTH_URL,
                    headers={"X-Session-ID": data.session_id},
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    print(f"Emergent Auth error: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=401, 
                        detail="Invalid or expired session. Please try again."
                    )
                
                auth_data = response.json()
                
        except httpx.RequestError as e:
            print(f"Emergent Auth request error: {e}")
            raise HTTPException(
                status_code=503, 
                detail="Authentication service unavailable. Please try again."
            )
        
        # Extract user data from Emergent Auth response
        email = auth_data.get("email")
        name = auth_data.get("name", email.split("@")[0] if email else "User")
        picture = auth_data.get("picture")
        emergent_session_token = auth_data.get("session_token")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Google")
        
        # Step 2: Create or update user in database
        user_id = await GoogleAuthService._get_or_create_user(
            db, email, name, picture
        )
        
        # Step 3: Create session
        session_token = await GoogleAuthService._create_session(
            db, user_id, emergent_session_token
        )
        
        # Step 4: Generate JWT token for compatibility with existing auth system
        jwt_token = GoogleAuthService._generate_jwt_token(user_id, email, name)
        
        # Return response
        user_response = GoogleUserResponse(
            user_id=user_id,
            email=email,
            name=name,
            picture=picture,
            created_at=datetime.now(timezone.utc)
        )
        
        return GoogleAuthResponse(
            user=user_response,
            token=jwt_token,
            message="Authentication successful"
        )
    
    @staticmethod
    async def _get_or_create_user(db, email: str, name: str, picture: str) -> str:
        """Get existing user or create new one"""
        # Check if user exists by email
        existing_user = await db.users.find_one(
            {"email": email},
            {"_id": 0}
        )
        
        if existing_user:
            # Update existing user with latest Google data
            user_id = existing_user.get("id") or existing_user.get("user_id")
            
            # Update user info if changed
            await db.users.update_one(
                {"email": email},
                {"$set": {
                    "name": name,
                    "picture": picture,
                    "google_linked": True,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            return user_id
        
        # Create new user
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        new_user = {
            "id": user_id,
            "user_id": user_id,  # Both for compatibility
            "email": email,
            "name": name,
            "picture": picture,
            "google_linked": True,
            "password_hash": None,  # No password for Google users
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.users.insert_one(new_user)
        print(f"Created new Google user: {email} with ID: {user_id}")
        
        return user_id
    
    @staticmethod
    async def _create_session(db, user_id: str, emergent_session_token: str = None) -> str:
        """Create a new session for the user"""
        session_token = emergent_session_token or f"session_{uuid.uuid4().hex}"
        expires_at = datetime.now(timezone.utc) + timedelta(days=GoogleAuthService.SESSION_EXPIRY_DAYS)
        
        # Store session in database
        session_doc = {
            "user_id": user_id,
            "session_token": session_token,
            "expires_at": expires_at.isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Remove any existing sessions for this user (optional: keep multiple sessions)
        await db.user_sessions.delete_many({"user_id": user_id})
        
        # Insert new session
        await db.user_sessions.insert_one(session_doc)
        
        return session_token
    
    @staticmethod
    def _generate_jwt_token(user_id: str, email: str, name: str) -> str:
        """Generate JWT token for compatibility with existing auth system"""
        jwt_secret = os.environ.get("JWT_SECRET", "enterprate-os-jwt-secret")
        
        payload = {
            "sub": user_id,
            "email": email,
            "name": name,
            "exp": datetime.now(timezone.utc) + timedelta(days=GoogleAuthService.SESSION_EXPIRY_DAYS),
            "iat": datetime.now(timezone.utc)
        }
        
        return jwt.encode(payload, jwt_secret, algorithm="HS256")
    
    @staticmethod
    async def validate_session(session_token: str) -> dict:
        """Validate a session token and return user data"""
        db = await get_database()
        
        # Find session
        session = await db.user_sessions.find_one(
            {"session_token": session_token},
            {"_id": 0}
        )
        
        if not session:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        # Check expiry
        expires_at = session.get("expires_at")
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        if expires_at < datetime.now(timezone.utc):
            # Clean up expired session
            await db.user_sessions.delete_one({"session_token": session_token})
            raise HTTPException(status_code=401, detail="Session expired")
        
        # Get user data
        user_id = session.get("user_id")
        user = await db.users.find_one(
            {"$or": [{"id": user_id}, {"user_id": user_id}]},
            {"_id": 0}
        )
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
    
    @staticmethod
    async def logout(user_id: str) -> bool:
        """Delete user sessions (logout)"""
        db = await get_database()
        
        result = await db.user_sessions.delete_many({"user_id": user_id})
        return result.deleted_count > 0
