"""Application configuration and settings"""
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional

ROOT_DIR = Path(__file__).parent.parent.parent

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database (PostgreSQL)
    DATABASE_URL: str
    # Legacy MongoDB settings (kept for backward compatibility during migration)
    MONGO_URL: Optional[str] = None
    DB_NAME: Optional[str] = None
    
    # Security
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24 * 7  # 1 week
    
    # CORS
    CORS_ORIGINS: str = "*"
    
    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    
    # LLM
    EMERGENT_LLM_KEY: Optional[str] = None
    
    # Frontend
    FRONTEND_URL: Optional[str] = None
    
    class Config:
        env_file = str(ROOT_DIR / ".env")
        case_sensitive = True

# Global settings instance
settings = Settings()
