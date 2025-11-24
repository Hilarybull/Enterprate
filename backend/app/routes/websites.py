"""Website builder routes"""
from fastapi import APIRouter, Depends
from app.schemas.website import WebsiteCreate, WebsitePageCreate
from app.services.website_service import WebsiteService
from app.core.security import get_current_user, get_workspace_id, verify_workspace_access

router = APIRouter(prefix="/websites", tags=["website-builder"])

@router.get("")
async def get_websites(
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    """Get all websites for a workspace"""
    await verify_workspace_access(workspace_id, user)
    return await WebsiteService.get_websites(workspace_id)

@router.post("")
async def create_website(
    website_data: WebsiteCreate,
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    """Create a new website"""
    await verify_workspace_access(workspace_id, user)
    return await WebsiteService.create_website(website_data, workspace_id)

@router.get("/{website_id}")
async def get_website(
    website_id: str,
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    """Get a website by ID"""
    await verify_workspace_access(workspace_id, user)
    return await WebsiteService.get_website(website_id, workspace_id)

@router.get("/{website_id}/pages")
async def get_website_pages(
    website_id: str,
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    """Get all pages for a website"""
    await verify_workspace_access(workspace_id, user)
    return await WebsiteService.get_website_pages(website_id)

@router.post("/{website_id}/pages")
async def create_website_page(
    website_id: str,
    page_data: WebsitePageCreate,
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    """Create a new website page"""
    await verify_workspace_access(workspace_id, user)
    return await WebsiteService.create_website_page(website_id, page_data, workspace_id)

@router.patch("/{website_id}/pages/{page_id}")
async def update_website_page(
    website_id: str,
    page_id: str,
    page_data: WebsitePageCreate,
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    """Update a website page"""
    await verify_workspace_access(workspace_id, user)
    return await WebsiteService.update_website_page(page_id, website_id, page_data)
