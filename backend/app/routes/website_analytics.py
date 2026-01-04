"""Website Analytics routes"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from app.services.website_analytics_service import WebsiteAnalyticsService
from app.core.security import get_current_user, verify_workspace_access, get_workspace_id

router = APIRouter(prefix="/website-analytics", tags=["website-analytics"])


class RecordPageViewRequest(BaseModel):
    websiteId: str
    visitorId: str
    pagePath: str = "/"
    referrer: Optional[str] = None
    userAgent: Optional[str] = None
    country: Optional[str] = None
    deviceType: str = "desktop"


class RecordConversionRequest(BaseModel):
    websiteId: str
    visitorId: str
    leadId: str
    conversionType: str = "form_submit"


@router.get("/overview")
async def get_analytics_overview(
    days: int = Query(30, ge=1, le=365),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get analytics overview for all websites in workspace"""
    await verify_workspace_access(workspace_id, user)
    return await WebsiteAnalyticsService.get_all_websites_analytics(workspace_id, days)


@router.get("/website/{website_id}")
async def get_website_analytics(
    website_id: str,
    days: int = Query(30, ge=1, le=365),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get detailed analytics for a specific website"""
    await verify_workspace_access(workspace_id, user)
    return await WebsiteAnalyticsService.get_website_analytics(website_id, workspace_id, days)


@router.get("/website/{website_id}/realtime")
async def get_realtime_visitors(
    website_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get real-time visitor count for a website"""
    await verify_workspace_access(workspace_id, user)
    return await WebsiteAnalyticsService.get_realtime_visitors(website_id, workspace_id)


# Public tracking endpoints (called from deployed websites)
@router.post("/track/pageview")
async def track_page_view(data: RecordPageViewRequest):
    """Track a page view (public endpoint for embedded tracking)"""
    # Note: workspace_id would be derived from the website_id
    from app.core.database import get_db
    db = get_db()
    
    website = await db.ai_websites.find_one({"id": data.websiteId})
    if not website:
        return {"error": "Website not found"}
    
    workspace_id = website.get("workspace_id")
    
    return await WebsiteAnalyticsService.record_page_view(
        website_id=data.websiteId,
        workspace_id=workspace_id,
        visitor_id=data.visitorId,
        page_path=data.pagePath,
        referrer=data.referrer,
        user_agent=data.userAgent,
        ip_country=data.country,
        device_type=data.deviceType
    )


@router.post("/track/conversion")
async def track_conversion(data: RecordConversionRequest):
    """Track a conversion event (public endpoint)"""
    from app.core.database import get_db
    db = get_db()
    
    website = await db.ai_websites.find_one({"id": data.websiteId})
    if not website:
        return {"error": "Website not found"}
    
    workspace_id = website.get("workspace_id")
    
    return await WebsiteAnalyticsService.record_lead_conversion(
        website_id=data.websiteId,
        workspace_id=workspace_id,
        visitor_id=data.visitorId,
        lead_id=data.leadId,
        conversion_type=data.conversionType
    )
