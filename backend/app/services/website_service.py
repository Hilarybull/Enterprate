"""Website service"""
import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import HTTPException
from app.core.database import get_db
from app.schemas.website import WebsiteCreate, WebsiteUpdate

class WebsiteService:
    """Service for website operations"""
    
    @staticmethod
    async def create_website(workspace_id: str, user_id: str, data: WebsiteCreate) -> dict:
        """Create a new website"""
        db = get_db()
        
        website_id = str(uuid.uuid4())
        website = {
            "id": website_id,
            "workspace_id": workspace_id,
            "name": data.name,
            "domain": data.domain,
            "status": "DRAFT",
            "created_by": user_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.websites.insert_one(website)
        
        # Log event
        await db.intelligence_events.insert_one({
            "id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "type": "website.created",
            "data": {"website_id": website_id, "name": data.name},
            "occurredAt": datetime.now(timezone.utc).isoformat()
        })
        
        return {k: v for k, v in website.items() if k != '_id'}
    
    @staticmethod
    async def get_websites(workspace_id: str) -> List[dict]:
        """Get all websites for a workspace"""
        db = get_db()
        
        websites = await db.websites.find(
            {"workspace_id": workspace_id}
        ).to_list(length=100)
        
        return [{k: v for k, v in ws.items() if k != '_id'} for ws in websites]
    
    @staticmethod
    async def get_website(website_id: str, workspace_id: str) -> dict:
        """Get a specific website"""
        db = get_db()
        
        website = await db.websites.find_one({
            "id": website_id,
            "workspace_id": workspace_id
        })
        
        if not website:
            raise HTTPException(status_code=404, detail="Website not found")
        
        return {k: v for k, v in website.items() if k != '_id'}
    
    @staticmethod
    async def delete_website(website_id: str, workspace_id: str) -> bool:
        """Delete a website"""
        db = get_db()
        
        result = await db.websites.delete_one({
            "id": website_id,
            "workspace_id": workspace_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Website not found")
        
        return True
