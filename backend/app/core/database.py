"""MongoDB database connection and utilities"""
import os
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

# MongoDB client and database
client = None
db = None

async def init_db():
    """Initialize MongoDB connection (called on startup)"""
    global client, db
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client[settings.DB_NAME]
    return db

async def close_db():
    """Close MongoDB connection (called on shutdown)"""
    global client
    if client:
        client.close()

def get_db():
    """Get database instance (for dependency injection)"""
    return db
