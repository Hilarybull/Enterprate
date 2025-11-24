"""Growth service for CRM/Lead management"""
from fastapi import HTTPException
from app.core.database import get_database
from app.schemas.lead import Lead, LeadCreate, LeadUpdate
from app.schemas.intelligence import IntelligenceEvent

class GrowthService:
    """Service for Growth CRM features"""
    
    @staticmethod
    async def get_leads(workspace_id: str) -> list:
        """Get all leads for a workspace"""
        db = get_database()
        leads = await db.leads.find({"workspaceId": workspace_id}, {"_id": 0}).to_list(100)
        return leads
    
    @staticmethod
    async def create_lead(lead_data: LeadCreate, workspace_id: str, user_id: str) -> dict:
        """Create a new lead"""
        db = get_database()
        
        lead = Lead(
            workspaceId=workspace_id,
            **lead_data.model_dump()
        )
        
        doc = lead.model_dump()
        doc['createdAt'] = doc['createdAt'].isoformat()
        await db.leads.insert_one(doc)
        
        # Log event
        event = IntelligenceEvent(
            workspaceId=workspace_id,
            userId=user_id,
            type="growth.lead_created",
            payload={"leadId": lead.id, "name": lead.name}
        )
        event_doc = event.model_dump()
        event_doc['occurredAt'] = event_doc['occurredAt'].isoformat()
        await db.intelligence_events.insert_one(event_doc)
        
        return lead.model_dump()
    
    @staticmethod
    async def update_lead(lead_id: str, lead_data: LeadUpdate, workspace_id: str) -> dict:
        """Update a lead"""
        db = get_database()
        
        update_data = {k: v for k, v in lead_data.model_dump().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No data to update")
        
        await db.leads.update_one(
            {"id": lead_id, "workspaceId": workspace_id},
            {"$set": update_data}
        )
        
        lead = await db.leads.find_one({"id": lead_id}, {"_id": 0})
        return lead
