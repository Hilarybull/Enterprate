"""Growth service for leads and marketing"""
import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import HTTPException
from app.core.database import get_db
from app.schemas.lead import LeadCreate, LeadUpdate

class GrowthService:
    """Service for Growth/Marketing operations"""
    
    @staticmethod
    async def create_lead(workspace_id: str, user_id: str, data: LeadCreate) -> dict:
        """Create a new lead"""
        db = get_db()
        
        lead_id = str(uuid.uuid4())
        lead = {
            "id": lead_id,
            "workspace_id": workspace_id,
            "name": data.name,
            "email": data.email,
            "phone": data.phone,
            "source": data.source,
            "status": data.status or "NEW",
            "created_by": user_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.leads.insert_one(lead)
        
        # Log event
        await db.intelligence_events.insert_one({
            "id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "type": "lead.created",
            "data": {"lead_id": lead_id, "source": data.source},
            "occurredAt": datetime.now(timezone.utc).isoformat()
        })
        
        return {k: v for k, v in lead.items() if k != '_id'}
    
    @staticmethod
    async def get_leads(workspace_id: str) -> List[dict]:
        """Get all leads for a workspace"""
        db = get_db()
        
        leads = await db.leads.find(
            {"workspace_id": workspace_id}
        ).sort("created_at", -1).to_list(length=100)
        
        return [{k: v for k, v in lead.items() if k != '_id'} for lead in leads]
    
    @staticmethod
    async def update_lead(lead_id: str, workspace_id: str, data: LeadUpdate) -> dict:
        """Update a lead"""
        db = get_db()
        
        lead = await db.leads.find_one({
            "id": lead_id,
            "workspace_id": workspace_id
        })
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        update_data = data.model_dump(exclude_unset=True)
        if update_data:
            await db.leads.update_one(
                {"id": lead_id},
                {"$set": update_data}
            )
        
        updated = await db.leads.find_one({"id": lead_id})
        return {k: v for k, v in updated.items() if k != '_id'}
