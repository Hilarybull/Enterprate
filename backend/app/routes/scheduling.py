"""Scheduling routes for automated growth actions"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from app.services.scheduling_service import SchedulingService
from app.core.security import get_current_user, verify_workspace_access, get_workspace_id

router = APIRouter(prefix="/scheduling", tags=["scheduling"])


class ScheduleActionRequest(BaseModel):
    """Request to schedule an action"""
    actionType: str = "social_post"
    platform: str = "linkedin"
    content: str
    hashtags: Optional[List[str]] = []
    scheduledFor: Optional[str] = None
    source: Optional[str] = "manual"
    recommendationId: Optional[str] = None


class OptimalScheduleRequest(BaseModel):
    """Request for optimal schedule times"""
    platform: str
    actionType: str = "social_post"
    count: int = 5


@router.get("/optimal-times")
async def get_optimal_schedule(
    platform: str,
    count: int = Query(5, ge=1, le=20),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get optimal posting times for a platform"""
    await verify_workspace_access(workspace_id, user)
    return SchedulingService.get_optimal_schedule(platform, "social_post", count)


@router.post("/actions")
async def schedule_action(
    data: ScheduleActionRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Schedule a growth action for automatic execution"""
    await verify_workspace_access(workspace_id, user)
    
    action = {
        "type": data.actionType,
        "platform": data.platform,
        "content": data.content,
        "hashtags": data.hashtags,
        "source": data.source,
        "recommendationId": data.recommendationId
    }
    
    schedule_config = {"scheduledFor": data.scheduledFor} if data.scheduledFor else None
    
    return await SchedulingService.schedule_growth_action(
        workspace_id, user["id"], action, schedule_config
    )


@router.get("/actions")
async def get_scheduled_actions(
    status: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get scheduled actions for the workspace"""
    await verify_workspace_access(workspace_id, user)
    return await SchedulingService.get_scheduled_actions(workspace_id, status, platform)


@router.post("/actions/{action_id}/execute")
async def execute_action(
    action_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Manually execute a scheduled action"""
    await verify_workspace_access(workspace_id, user)
    return await SchedulingService.execute_scheduled_action(action_id, workspace_id)


@router.delete("/actions/{action_id}")
async def cancel_action(
    action_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Cancel a scheduled action"""
    await verify_workspace_access(workspace_id, user)
    cancelled = await SchedulingService.cancel_scheduled_action(action_id, workspace_id)
    return {"cancelled": cancelled}


@router.get("/analytics")
async def get_schedule_analytics(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get analytics about scheduled actions"""
    await verify_workspace_access(workspace_id, user)
    return await SchedulingService.get_schedule_analytics(workspace_id)


@router.post("/process-due")
async def process_due_actions(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Process all due scheduled actions (admin/cron endpoint)"""
    await verify_workspace_access(workspace_id, user)
    return await SchedulingService.process_due_actions()
