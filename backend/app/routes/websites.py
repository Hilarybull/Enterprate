"""Website routes"""
from typing import List
from fastapi import APIRouter, Depends
from app.services.website_service import WebsiteService
from app.schemas.website import WebsiteCreate, WebsiteUpdate, WebsiteResponse
from app.core.security import get_current_user, verify_workspace_access, get_workspace_id

router = APIRouter(prefix="/websites", tags=["websites"])

@router.post("", response_model=WebsiteResponse)
async def create_website(
    data: WebsiteCreate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Create a new website"""
    await verify_workspace_access(workspace_id, user)
    return await WebsiteService.create_website(workspace_id, user["id"], data)

@router.get("", response_model=List[WebsiteResponse])
async def get_websites(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get all websites"""
    await verify_workspace_access(workspace_id, user)
    return await WebsiteService.get_websites(workspace_id)

@router.get("/{website_id}", response_model=WebsiteResponse)
async def get_website(
    website_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get a specific website"""
    await verify_workspace_access(workspace_id, user)
    return await WebsiteService.get_website(website_id, workspace_id)

@router.delete("/{website_id}")
async def delete_website(
    website_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Delete a website"""
    await verify_workspace_access(workspace_id, user)
    await WebsiteService.delete_website(website_id, workspace_id)
    return {"message": "Website deleted"}
