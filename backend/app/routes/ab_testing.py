"""A/B Testing routes"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from app.services.ab_testing_service import ABTestingService
from app.core.security import get_current_user, verify_workspace_access, get_workspace_id

router = APIRouter(prefix="/ab-tests", tags=["ab-testing"])


class CreateTestRequest(BaseModel):
    name: str
    description: str
    testType: str  # campaign, landing_page, email, social_post, cta
    variants: List[dict]
    trafficSplit: Optional[List[float]] = None
    durationDays: int = 14
    goalMetric: str = "conversion_rate"


class RecordEventRequest(BaseModel):
    variantId: str
    eventType: str  # impression, click, conversion, revenue, engagement
    value: float = 1.0


@router.post("")
async def create_ab_test(
    data: CreateTestRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Create a new A/B test"""
    await verify_workspace_access(workspace_id, user)
    return await ABTestingService.create_ab_test(
        workspace_id=workspace_id,
        user_id=user["id"],
        name=data.name,
        description=data.description,
        test_type=data.testType,
        variants=data.variants,
        traffic_split=data.trafficSplit,
        duration_days=data.durationDays,
        goal_metric=data.goalMetric
    )


@router.get("")
async def get_ab_tests(
    status: Optional[str] = Query(None),
    testType: Optional[str] = Query(None),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get all A/B tests"""
    await verify_workspace_access(workspace_id, user)
    return await ABTestingService.get_tests(workspace_id, status, testType)


@router.get("/{test_id}")
async def get_ab_test(
    test_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get A/B test by ID"""
    await verify_workspace_access(workspace_id, user)
    test = await ABTestingService.get_test(test_id, workspace_id)
    if not test:
        return {"error": "Test not found"}
    return test


@router.post("/{test_id}/start")
async def start_ab_test(
    test_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Start an A/B test"""
    await verify_workspace_access(workspace_id, user)
    return await ABTestingService.start_test(test_id, workspace_id)


@router.post("/{test_id}/pause")
async def pause_ab_test(
    test_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Pause an A/B test"""
    await verify_workspace_access(workspace_id, user)
    return await ABTestingService.pause_test(test_id, workspace_id)


@router.post("/{test_id}/resume")
async def resume_ab_test(
    test_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Resume a paused A/B test"""
    await verify_workspace_access(workspace_id, user)
    return await ABTestingService.resume_test(test_id, workspace_id)


@router.get("/{test_id}/analyze")
async def analyze_ab_test(
    test_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Analyze A/B test results"""
    await verify_workspace_access(workspace_id, user)
    return await ABTestingService.analyze_test(test_id, workspace_id)


@router.post("/{test_id}/complete")
async def complete_ab_test(
    test_id: str,
    winner_id: Optional[str] = None,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Complete an A/B test and optionally set winner"""
    await verify_workspace_access(workspace_id, user)
    return await ABTestingService.complete_test(test_id, workspace_id, winner_id)


@router.post("/{test_id}/event")
async def record_test_event(
    test_id: str,
    data: RecordEventRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Record an event for A/B test tracking"""
    await verify_workspace_access(workspace_id, user)
    await ABTestingService.record_event(
        test_id, data.variantId, data.eventType, data.value
    )
    return {"success": True}


@router.get("/{test_id}/variant")
async def get_variant_for_visitor(
    test_id: str,
    visitor_id: str = Query(...),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get which variant to show a visitor"""
    await verify_workspace_access(workspace_id, user)
    variant = await ABTestingService.get_variant_for_visitor(test_id, visitor_id)
    return variant or {"error": "Test not running or not found"}


@router.delete("/{test_id}")
async def delete_ab_test(
    test_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Delete an A/B test"""
    await verify_workspace_access(workspace_id, user)
    success = await ABTestingService.delete_test(test_id, workspace_id)
    return {"deleted": success}
