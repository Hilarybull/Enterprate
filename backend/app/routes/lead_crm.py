"""Lead CRM Integration Routes"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from pydantic import BaseModel
from app.core.security import get_current_user, get_workspace_id, verify_workspace_access
from app.services.lead_crm_service import LeadCRMService

router = APIRouter(prefix="/leads", tags=["lead-crm"])


class WebsiteLeadSubmission(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    message: Optional[str] = None
    websiteId: Optional[str] = None


@router.get("")
async def get_website_leads(
    website_id: Optional[str] = Query(None, description="Filter by website"),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get all website leads for the workspace"""
    await verify_workspace_access(workspace_id, user)
    return await LeadCRMService.get_website_leads(workspace_id, website_id)


@router.post("")
async def submit_website_lead(
    data: WebsiteLeadSubmission,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Submit a website lead and sync to CRM"""
    await verify_workspace_access(workspace_id, user)
    return await LeadCRMService.process_website_lead(
        workspace_id=workspace_id,
        website_id=data.websiteId or "manual",
        lead_data={
            "name": data.name,
            "email": data.email,
            "phone": data.phone,
            "company": data.company,
            "message": data.message
        }
    )


@router.post("/{contact_id}/convert")
async def convert_to_customer(
    contact_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Convert a lead to a customer"""
    await verify_workspace_access(workspace_id, user)
    return await LeadCRMService.convert_lead_to_customer(contact_id, workspace_id, user["id"])


@router.get("/analytics")
async def get_lead_analytics(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get lead analytics for dashboard"""
    await verify_workspace_access(workspace_id, user)
    return await LeadCRMService.get_lead_analytics(workspace_id)
