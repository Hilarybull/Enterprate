"""Growth/Marketing routes"""
from typing import List
from fastapi import APIRouter, Depends
from app.services.growth_service import GrowthService
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse
from app.core.security import get_current_user, verify_workspace_access, get_workspace_id

router = APIRouter(prefix="/growth", tags=["growth"])

@router.post("/leads", response_model=LeadResponse)
async def create_lead(
    data: LeadCreate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Create a new lead"""
    await verify_workspace_access(workspace_id, user)
    return await GrowthService.create_lead(workspace_id, user["id"], data)

@router.get("/leads", response_model=List[LeadResponse])
async def get_leads(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get all leads"""
    await verify_workspace_access(workspace_id, user)
    return await GrowthService.get_leads(workspace_id)

@router.patch("/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str,
    data: LeadUpdate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Update a lead"""
    await verify_workspace_access(workspace_id, user)
    return await GrowthService.update_lead(lead_id, workspace_id, data)
