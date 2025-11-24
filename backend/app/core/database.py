"""Database connection and utilities"""
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.config import settings

# MongoDB client
client: AsyncIOMotorClient = None
db: AsyncIOMotorDatabase = None

def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return db

async def connect_to_mongo():
    """Connect to MongoDB"""
    global client, db
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client[settings.DB_NAME]

async def close_mongo_connection():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
