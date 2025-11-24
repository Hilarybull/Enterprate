"""Growth service for CRM/Lead management"""
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.models.lead import Lead
from app.models.intelligence import IntelligenceEvent
from app.schemas.lead import LeadCreate, LeadUpdate

class GrowthService:
    """Service for Growth CRM features"""
    
    @staticmethod
    async def get_leads(db: AsyncSession, workspace_id: str) -> list:
        """Get all leads for a workspace"""
        workspace_uuid = UUID(workspace_id)
        
        stmt = select(Lead).where(Lead.workspace_id == workspace_uuid)
        result = await db.execute(stmt)
        leads = result.scalars().all()
        
        return [
            {
                "id": str(lead.id),
                "workspaceId": str(lead.workspace_id),
                "name": lead.name,
                "email": lead.email,
                "phone": lead.phone,
                "source": lead.source,
                "status": lead.status.value,
                "notes": lead.notes,
                "createdAt": lead.created_at.isoformat()
            }
            for lead in leads
        ]
    
    @staticmethod
    async def create_lead(db: AsyncSession, lead_data: LeadCreate, workspace_id: str, user_id: str) -> dict:
        """Create a new lead"""
        workspace_uuid = UUID(workspace_id)
        user_uuid = UUID(user_id)
        
        lead = Lead(
            workspace_id=workspace_uuid,
            name=lead_data.name,
            email=lead_data.email,
            phone=lead_data.phone,
            source=lead_data.source,
            notes=lead_data.notes
        )
        
        db.add(lead)
        await db.flush()
        
        # Log event
        event = IntelligenceEvent(
            workspace_id=workspace_uuid,
            user_id=user_uuid,
            type="growth.lead_created",
            payload={"leadId": str(lead.id), "name": lead.name}
        )
        db.add(event)
        await db.flush()
        
        return {
            "id": str(lead.id),
            "workspaceId": str(lead.workspace_id),
            "name": lead.name,
            "email": lead.email,
            "phone": lead.phone,
            "source": lead.source,
            "status": lead.status.value,
            "notes": lead.notes,
            "createdAt": lead.created_at.isoformat()
        }
    
    @staticmethod
    async def update_lead(db: AsyncSession, lead_id: str, lead_data: LeadUpdate, workspace_id: str) -> dict:
        """Update a lead"""
        lead_uuid = UUID(lead_id)
        workspace_uuid = UUID(workspace_id)
        
        update_data = {k: v for k, v in lead_data.model_dump().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No data to update")
        
        stmt = select(Lead).where(
            Lead.id == lead_uuid,
            Lead.workspace_id == workspace_uuid
        )
        result = await db.execute(stmt)
        lead = result.scalar_one_or_none()
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(lead, key):
                setattr(lead, key, value)
        
        await db.flush()
        
        return {
            "id": str(lead.id),
            "workspaceId": str(lead.workspace_id),
            "name": lead.name,
            "email": lead.email,
            "phone": lead.phone,
            "source": lead.source,
            "status": lead.status.value,
            "notes": lead.notes,
            "createdAt": lead.created_at.isoformat()
        }
