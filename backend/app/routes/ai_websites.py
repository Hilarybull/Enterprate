"""AI Website Builder routes"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from pydantic import BaseModel
from app.services.ai_website_builder_service import AIWebsiteBuilderService
from app.core.security import get_current_user, verify_workspace_access, get_workspace_id

router = APIRouter(prefix="/ai-websites", tags=["ai-websites"])


class GenerateWebsiteRequest(BaseModel):
    userDescription: str
    brandPreferences: Optional[dict] = None
    logoUrl: Optional[str] = None
    contactMethod: str = "form"  # form, email, phone, link
    contactValue: Optional[str] = None
    language: str = "en"
    includeLeadForm: bool = True


class RefineWebsiteRequest(BaseModel):
    feedback: str


class DeployWebsiteRequest(BaseModel):
    siteName: Optional[str] = None
    platform: str = "netlify"  # netlify, vercel, railway


class LeadSubmissionRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    message: Optional[str] = None
    workspaceId: str
    source: str = "website_form"


@router.post("/generate")
async def generate_website(
    data: GenerateWebsiteRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """
    Generate a high-converting landing page from business description.
    Uses AIDA framework and AI content generation.
    """
    await verify_workspace_access(workspace_id, user)
    return await AIWebsiteBuilderService.generate_website(
        workspace_id=workspace_id,
        user_id=user["id"],
        user_description=data.userDescription,
        brand_preferences=data.brandPreferences,
        logo_url=data.logoUrl,
        contact_method=data.contactMethod,
        contact_value=data.contactValue
    )


@router.get("")
async def get_websites(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get all websites for the workspace"""
    await verify_workspace_access(workspace_id, user)
    return await AIWebsiteBuilderService.get_websites(workspace_id)


@router.get("/{website_id}")
async def get_website(
    website_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get website by ID"""
    await verify_workspace_access(workspace_id, user)
    website = await AIWebsiteBuilderService.get_website(website_id, workspace_id)
    if not website:
        return {"error": "Website not found"}
    return website


@router.post("/{website_id}/refine")
async def refine_website(
    website_id: str,
    data: RefineWebsiteRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Refine website based on user feedback"""
    await verify_workspace_access(workspace_id, user)
    return await AIWebsiteBuilderService.refine_website(
        website_id, workspace_id, user["id"], data.feedback
    )


@router.post("/{website_id}/deploy")
async def deploy_website(
    website_id: str,
    data: DeployWebsiteRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Deploy website to Netlify"""
    await verify_workspace_access(workspace_id, user)
    return await AIWebsiteBuilderService.deploy_to_netlify(
        website_id, workspace_id, user["id"], data.siteName
    )


@router.get("/{website_id}/download")
async def download_website(
    website_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Download website source code"""
    await verify_workspace_access(workspace_id, user)
    website = await AIWebsiteBuilderService.get_website(website_id, workspace_id)
    
    if not website:
        return {"error": "Website not found"}
    
    html_content = website.get("htmlContent", "")
    
    return Response(
        content=html_content,
        media_type="text/html",
        headers={
            "Content-Disposition": f'attachment; filename="website_{website_id}.html"'
        }
    )


@router.get("/{website_id}/preview")
async def preview_website(
    website_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get website HTML for preview"""
    await verify_workspace_access(workspace_id, user)
    website = await AIWebsiteBuilderService.get_website(website_id, workspace_id)
    
    if not website:
        return {"error": "Website not found"}
    
    return {
        "id": website_id,
        "htmlContent": website.get("htmlContent", ""),
        "version": website.get("version", 1),
        "status": website.get("status"),
        "deploymentUrl": website.get("deploymentUrl")
    }


@router.delete("/{website_id}")
async def delete_website(
    website_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Delete a website"""
    await verify_workspace_access(workspace_id, user)
    success = await AIWebsiteBuilderService.delete_website(website_id, workspace_id)
    return {"deleted": success}


@router.get("/color-schemes/list")
async def get_color_schemes():
    """Get available color schemes"""
    return AIWebsiteBuilderService.COLOR_SCHEMES
