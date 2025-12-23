"""Marketing/Growth routes - Campaigns, Social, Analytics"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.services.marketing_service import MarketingService
from app.schemas.marketing import (
    CampaignCreate, CampaignUpdate, CampaignResponse,
    SocialPostCreate, SocialPostUpdate, SocialPostResponse,
    SocialPostGenerateRequest, GrowthAnalyticsResponse
)
from app.core.security import get_current_user, verify_workspace_access, get_workspace_id

router = APIRouter(prefix="/marketing", tags=["marketing"])


# === CAMPAIGN ENDPOINTS ===

@router.post("/campaigns", response_model=CampaignResponse)
async def create_campaign(
    data: CampaignCreate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Create a marketing campaign"""
    await verify_workspace_access(workspace_id, user)
    return await MarketingService.create_campaign(workspace_id, user["id"], data)


@router.get("/campaigns", response_model=List[CampaignResponse])
async def get_campaigns(
    status: Optional[str] = Query(None),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get campaigns for workspace"""
    await verify_workspace_access(workspace_id, user)
    return await MarketingService.get_campaigns(workspace_id, status)


@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get a specific campaign"""
    await verify_workspace_access(workspace_id, user)
    return await MarketingService.get_campaign(campaign_id, workspace_id)


@router.patch("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    data: CampaignUpdate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Update a campaign"""
    await verify_workspace_access(workspace_id, user)
    return await MarketingService.update_campaign(campaign_id, workspace_id, data)


@router.delete("/campaigns/{campaign_id}")
async def delete_campaign(
    campaign_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Delete a campaign"""
    await verify_workspace_access(workspace_id, user)
    deleted = await MarketingService.delete_campaign(campaign_id, workspace_id)
    return {"deleted": deleted}


@router.patch("/campaigns/{campaign_id}/metrics", response_model=CampaignResponse)
async def update_campaign_metrics(
    campaign_id: str,
    metrics: dict,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Update campaign metrics"""
    await verify_workspace_access(workspace_id, user)
    return await MarketingService.update_campaign_metrics(campaign_id, workspace_id, metrics)


# === SOCIAL MEDIA POST ENDPOINTS ===

@router.post("/social-posts", response_model=SocialPostResponse)
async def create_social_post(
    data: SocialPostCreate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Create a social media post"""
    await verify_workspace_access(workspace_id, user)
    return await MarketingService.create_social_post(workspace_id, user["id"], data)


@router.get("/social-posts", response_model=List[SocialPostResponse])
async def get_social_posts(
    platform: Optional[str] = Query(None),
    campaign_id: Optional[str] = Query(None),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get social posts"""
    await verify_workspace_access(workspace_id, user)
    return await MarketingService.get_social_posts(workspace_id, platform, campaign_id)


@router.patch("/social-posts/{post_id}", response_model=SocialPostResponse)
async def update_social_post(
    post_id: str,
    data: SocialPostUpdate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Update a social post"""
    await verify_workspace_access(workspace_id, user)
    return await MarketingService.update_social_post(post_id, workspace_id, data)


@router.delete("/social-posts/{post_id}")
async def delete_social_post(
    post_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Delete a social post"""
    await verify_workspace_access(workspace_id, user)
    deleted = await MarketingService.delete_social_post(post_id, workspace_id)
    return {"deleted": deleted}


@router.post("/social-posts/generate")
async def generate_social_post(
    data: SocialPostGenerateRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Generate social post content with AI"""
    await verify_workspace_access(workspace_id, user)
    return await MarketingService.generate_social_post(workspace_id, data)


# === ANALYTICS ENDPOINTS ===

@router.get("/analytics", response_model=GrowthAnalyticsResponse)
async def get_growth_analytics(
    period: str = Query("month"),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get comprehensive growth analytics"""
    await verify_workspace_access(workspace_id, user)
    return await MarketingService.get_growth_analytics(workspace_id, period)


@router.get("/analytics/lead-trends")
async def get_lead_trends(
    days: int = Query(30, le=365),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get lead trends over time"""
    await verify_workspace_access(workspace_id, user)
    return await MarketingService.get_lead_trends(workspace_id, days)
