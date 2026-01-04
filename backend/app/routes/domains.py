"""Custom Domain routes"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.custom_domain_service import CustomDomainService
from app.core.security import get_current_user, verify_workspace_access, get_workspace_id

router = APIRouter(prefix="/domains", tags=["domains"])


class AddDomainRequest(BaseModel):
    websiteId: str
    domain: str


@router.post("")
async def add_custom_domain(
    data: AddDomainRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Add a custom domain to a deployed website"""
    await verify_workspace_access(workspace_id, user)
    return await CustomDomainService.add_custom_domain(
        website_id=data.websiteId,
        workspace_id=workspace_id,
        domain=data.domain,
        user_id=user["id"]
    )


@router.get("/website/{website_id}")
async def get_website_domains(
    website_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get all custom domains for a website"""
    await verify_workspace_access(workspace_id, user)
    return await CustomDomainService.get_website_domains(website_id, workspace_id)


@router.get("/{domain_id}")
async def get_domain(
    domain_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get domain details"""
    await verify_workspace_access(workspace_id, user)
    return await CustomDomainService.get_domain(domain_id, workspace_id)


@router.post("/{domain_id}/verify")
async def verify_domain(
    domain_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Verify DNS configuration for a custom domain"""
    await verify_workspace_access(workspace_id, user)
    return await CustomDomainService.verify_domain(domain_id, workspace_id)


@router.delete("/{domain_id}")
async def remove_domain(
    domain_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Remove a custom domain"""
    await verify_workspace_access(workspace_id, user)
    return await CustomDomainService.remove_domain(domain_id, workspace_id)
