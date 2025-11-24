"""Intelligence graph service"""
from app.core.database import get_database
from app.schemas.intelligence import IntelligenceEvent, IntelligenceEventCreate

class IntelService:
    """Service for intelligence graph features"""
    
    @staticmethod
    async def get_events(workspace_id: str, limit: int = 50) -> list:
        """Get intelligence events for a workspace"""
        db = get_database()
        
        events = await db.intelligence_events.find(
            {"workspaceId": workspace_id},
            {"_id": 0}
        ).sort("occurredAt", -1).limit(limit).to_list(limit)
        
        return events
    
    @staticmethod
    async def create_event(event_data: IntelligenceEventCreate, workspace_id: str, user_id: str) -> dict:
        """Create an intelligence event"""
        db = get_database()
        
        event = IntelligenceEvent(
            workspaceId=workspace_id,
            userId=user_id,
            type=event_data.type,
            payload=event_data.payload
        )
        
        doc = event.model_dump()
        doc['occurredAt'] = doc['occurredAt'].isoformat()
        await db.intelligence_events.insert_one(doc)
        
        return event.model_dump()
