"""Intelligence service for events and insights"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from app.core.database import get_db
from app.schemas.intelligence import EventCreate

class IntelService:
    """Service for Intelligence Graph operations"""
    
    @staticmethod
    async def log_event(workspace_id: str, event_type: str, data: dict = None) -> dict:
        """Log an intelligence event"""
        db = get_db()
        
        event = {
            "id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "type": event_type,
            "data": data or {},
            "occurredAt": datetime.now(timezone.utc).isoformat()
        }
        
        await db.intelligence_events.insert_one(event)
        return {k: v for k, v in event.items() if k != '_id'}
    
    @staticmethod
    async def get_events(
        workspace_id: str,
        event_type: Optional[str] = None,
        limit: int = 50
    ) -> List[dict]:
        """Get events for a workspace"""
        db = get_db()
        
        query = {"workspace_id": workspace_id}
        if event_type:
            query["type"] = event_type
        
        events = await db.intelligence_events.find(query).sort(
            "occurredAt", -1
        ).to_list(length=limit)
        
        return [{k: v for k, v in e.items() if k != '_id'} for e in events]
    
    @staticmethod
    async def create_event(workspace_id: str, data: EventCreate) -> dict:
        """Create a new event from API"""
        db = get_db()
        
        event = {
            "id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "type": data.type,
            "data": data.data or {},
            "occurredAt": datetime.now(timezone.utc).isoformat()
        }
        
        await db.intelligence_events.insert_one(event)
        return {k: v for k, v in event.items() if k != '_id'}
