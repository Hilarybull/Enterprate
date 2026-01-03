"""Growth/Marketing routes with Proactive Growth Agent"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.services.growth_service import GrowthService
from app.services.proactive_growth_service import ProactiveGrowthService
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse
from app.schemas.growth import (
    PerformanceAnalysisResponse,
    GenerateRecommendationRequest,
    ApproveRecommendationRequest,
    RejectRecommendationRequest,
    RecommendationResponse,
    GrowthRecommendation
)
from app.core.security import get_current_user, verify_workspace_access, get_workspace_id

router = APIRouter(prefix="/growth", tags=["growth"])


# === LEAD ENDPOINTS ===

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


# === PROACTIVE GROWTH AGENT ENDPOINTS ===

@router.get("/agent/analyze")
async def analyze_business_performance(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """
    Analyze business performance metrics.
    Returns health score, trends, and alerts for leads, revenue, and campaigns.
    """
    await verify_workspace_access(workspace_id, user)
    return await ProactiveGrowthService.analyze_business_performance(workspace_id)


@router.post("/agent/recommend")
async def generate_growth_recommendation(
    data: GenerateRecommendationRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """
    Generate AI-powered growth recommendation based on detected alert.
    Returns a proposed action plan for user approval.
    """
    await verify_workspace_access(workspace_id, user)
    return await ProactiveGrowthService.generate_growth_recommendation(
        workspace_id, data.alertType
    )


@router.post("/agent/approve")
async def approve_recommendation(
    data: ApproveRecommendationRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """
    Approve and execute a growth recommendation.
    Human-in-the-loop approval before any action is taken.
    """
    await verify_workspace_access(workspace_id, user)
    return await ProactiveGrowthService.approve_recommendation(
        data.recommendationId, workspace_id, user["id"]
    )


@router.post("/agent/reject")
async def reject_recommendation(
    data: RejectRecommendationRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Reject a growth recommendation"""
    await verify_workspace_access(workspace_id, user)
    return await ProactiveGrowthService.reject_recommendation(
        data.recommendationId, workspace_id, user["id"], data.reason
    )


@router.get("/agent/recommendations")
async def get_recommendations(
    status: Optional[str] = Query(None, description="Filter by status: pending, approved, rejected"),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get all growth recommendations for the workspace"""
    await verify_workspace_access(workspace_id, user)
    return await ProactiveGrowthService.get_recommendations(workspace_id, status)
