"""Intelligence graph service"""
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.models.intelligence import IntelligenceEvent
from app.schemas.intelligence import IntelligenceEventCreate

class IntelService:
    """Service for intelligence graph features"""
    
    @staticmethod
    async def get_events(db: AsyncSession, workspace_id: str, limit: int = 50) -> list:
        """Get intelligence events for a workspace"""
        workspace_uuid = UUID(workspace_id)
        
        stmt = select(IntelligenceEvent).where(
            IntelligenceEvent.workspace_id == workspace_uuid
        ).order_by(desc(IntelligenceEvent.occurred_at)).limit(limit)
        
        result = await db.execute(stmt)
        events = result.scalars().all()
        
        return [
            {
                "id": str(event.id),
                "workspaceId": str(event.workspace_id),
                "userId": str(event.user_id) if event.user_id else None,
                "type": event.type,
                "payload": event.payload,
                "occurredAt": event.occurred_at.isoformat()
            }
            for event in events
        ]
    
    @staticmethod
    async def create_event(db: AsyncSession, event_data: IntelligenceEventCreate, workspace_id: str, user_id: str) -> dict:
        """Create an intelligence event"""
        workspace_uuid = UUID(workspace_id)
        user_uuid = UUID(user_id)
        
        event = IntelligenceEvent(
            workspace_id=workspace_uuid,
            user_id=user_uuid,
            type=event_data.type,
            payload=event_data.payload
        )
        
        db.add(event)
        await db.flush()
        
        return {
            "id": str(event.id),
            "workspaceId": str(event.workspace_id),
            "userId": str(event.user_id) if event.user_id else None,
            "type": event.type,
            "payload": event.payload,
            "occurredAt": event.occurred_at.isoformat()
        }
