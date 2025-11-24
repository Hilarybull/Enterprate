"""Growth (CRM/Lead) routes"""
from fastapi import APIRouter, Depends
from app.schemas.lead import LeadCreate, LeadUpdate
from app.services.growth_service import GrowthService
from app.core.security import get_current_user, get_workspace_id, verify_workspace_access

router = APIRouter(prefix="/growth", tags=["growth"])

@router.get("/leads")
async def get_leads(
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    """Get all leads for a workspace"""
    await verify_workspace_access(workspace_id, user)
    return await GrowthService.get_leads(workspace_id)

@router.post("/leads")
async def create_lead(
    lead_data: LeadCreate,
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    """Create a new lead"""
    await verify_workspace_access(workspace_id, user)
    return await GrowthService.create_lead(lead_data, workspace_id, user['id'])

@router.patch("/leads/{lead_id}")
async def update_lead(
    lead_id: str,
    lead_data: LeadUpdate,
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    """Update a lead"""
    await verify_workspace_access(workspace_id, user)
    return await GrowthService.update_lead(lead_id, lead_data, workspace_id)
