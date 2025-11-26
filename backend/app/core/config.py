"""Application configuration settings"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # MongoDB
    MONGO_URL: str = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    DB_NAME: str = os.environ.get("DB_NAME", "enterprate_os")
    
    # JWT
    JWT_SECRET: str = os.environ.get("JWT_SECRET", "enterprate-os-jwt-secret")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # CORS
    CORS_ORIGINS: str = os.environ.get("CORS_ORIGINS", "*")

settings = Settings()
