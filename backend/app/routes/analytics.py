"""Advanced Analytics routes"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.services.advanced_analytics_service import AdvancedAnalyticsService
from app.core.security import get_current_user, verify_workspace_access, get_workspace_id

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard")
async def get_dashboard_overview(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get comprehensive dashboard overview"""
    await verify_workspace_access(workspace_id, user)
    return await AdvancedAnalyticsService.get_dashboard_overview(workspace_id)


@router.get("/revenue-trends")
async def get_revenue_trends(
    days: int = Query(30, ge=7, le=365),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get revenue trends over time"""
    await verify_workspace_access(workspace_id, user)
    return await AdvancedAnalyticsService.get_revenue_trends(workspace_id, days)


@router.get("/lead-funnel")
async def get_lead_funnel(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get lead funnel analytics"""
    await verify_workspace_access(workspace_id, user)
    return await AdvancedAnalyticsService.get_lead_funnel(workspace_id)


@router.get("/campaign-performance")
async def get_campaign_performance(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get detailed campaign performance"""
    await verify_workspace_access(workspace_id, user)
    return await AdvancedAnalyticsService.get_campaign_performance(workspace_id)


@router.get("/social")
async def get_social_analytics(
    days: int = Query(30, ge=7, le=365),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get social media analytics"""
    await verify_workspace_access(workspace_id, user)
    return await AdvancedAnalyticsService.get_social_analytics(workspace_id, days)


@router.get("/report")
async def generate_business_report(
    report_type: str = Query("monthly", regex="^(weekly|monthly|quarterly)$"),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Generate comprehensive business report"""
    await verify_workspace_access(workspace_id, user)
    return await AdvancedAnalyticsService.generate_business_report(workspace_id, report_type)
