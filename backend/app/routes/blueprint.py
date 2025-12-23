"""Business Blueprint routes"""
from typing import List
from fastapi import APIRouter, Depends
from app.services.blueprint_service import BlueprintService
from app.schemas.blueprint import (
    BlueprintCreate, BlueprintUpdate, BlueprintResponse,
    BlueprintSectionResponse, SWOTAnalysis, FinancialProjection
)
from app.core.security import get_current_user, verify_workspace_access, get_workspace_id

router = APIRouter(prefix="/blueprint", tags=["blueprint"])


@router.post("", response_model=BlueprintResponse)
async def create_blueprint(
    data: BlueprintCreate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Create a new business blueprint"""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.create_blueprint(workspace_id, user["id"], data)


@router.get("", response_model=List[BlueprintResponse])
async def get_blueprints(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get all blueprints for workspace"""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.get_blueprints(workspace_id)


@router.get("/{blueprint_id}", response_model=BlueprintResponse)
async def get_blueprint(
    blueprint_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get a specific blueprint"""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.get_blueprint(blueprint_id, workspace_id)


@router.post("/{blueprint_id}/generate-section/{section_type}")
async def generate_section(
    blueprint_id: str,
    section_type: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Generate a specific section using AI"""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.generate_section(workspace_id, blueprint_id, section_type)


@router.post("/{blueprint_id}/generate-swot")
async def generate_swot(
    blueprint_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Generate SWOT analysis using AI"""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.generate_swot(workspace_id, blueprint_id)


@router.post("/{blueprint_id}/generate-financials")
async def generate_financials(
    blueprint_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Generate financial projections"""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.generate_financials(workspace_id, blueprint_id)


@router.post("/{blueprint_id}/generate-full")
async def generate_full_blueprint(
    blueprint_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Generate complete blueprint with all sections"""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.generate_full_blueprint(workspace_id, blueprint_id)


@router.patch("/{blueprint_id}", response_model=BlueprintResponse)
async def update_blueprint(
    blueprint_id: str,
    data: BlueprintUpdate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Update a blueprint"""
    await verify_workspace_access(workspace_id, user)
    return await BlueprintService.update_blueprint(blueprint_id, workspace_id, data)


@router.delete("/{blueprint_id}")
async def delete_blueprint(
    blueprint_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Delete a blueprint"""
    await verify_workspace_access(workspace_id, user)
    deleted = await BlueprintService.delete_blueprint(blueprint_id, workspace_id)
    return {"deleted": deleted}
