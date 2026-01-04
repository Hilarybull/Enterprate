"""Campaign Automation routes"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from app.services.campaign_automation_service import CampaignAutomationService
from app.core.security import get_current_user, verify_workspace_access, get_workspace_id

router = APIRouter(prefix="/automation", tags=["automation"])


class CreateRuleRequest(BaseModel):
    name: str
    description: str
    trigger: dict
    conditions: List[dict] = []
    actions: List[dict]
    isActive: bool = True
    priority: int = 0


class UpdateRuleRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    trigger: Optional[dict] = None
    conditions: Optional[List[dict]] = None
    actions: Optional[List[dict]] = None
    isActive: Optional[bool] = None
    priority: Optional[int] = None


@router.get("/triggers")
async def get_available_triggers():
    """Get all available automation triggers"""
    return CampaignAutomationService.get_available_triggers()


@router.get("/actions")
async def get_available_actions():
    """Get all available automation actions"""
    return CampaignAutomationService.get_available_actions()


@router.get("/operators")
async def get_available_operators():
    """Get all available condition operators"""
    return CampaignAutomationService.get_available_operators()


@router.post("/rules")
async def create_automation_rule(
    data: CreateRuleRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Create a new automation rule"""
    await verify_workspace_access(workspace_id, user)
    return await CampaignAutomationService.create_rule(
        workspace_id=workspace_id,
        user_id=user["id"],
        name=data.name,
        description=data.description,
        trigger=data.trigger,
        conditions=data.conditions,
        actions=data.actions,
        is_active=data.isActive,
        priority=data.priority
    )


@router.get("/rules")
async def get_automation_rules(
    isActive: Optional[bool] = Query(None),
    triggerType: Optional[str] = Query(None),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get all automation rules"""
    await verify_workspace_access(workspace_id, user)
    return await CampaignAutomationService.get_rules(workspace_id, isActive, triggerType)


@router.get("/rules/{rule_id}")
async def get_automation_rule(
    rule_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get a specific automation rule"""
    await verify_workspace_access(workspace_id, user)
    rule = await CampaignAutomationService.get_rule(rule_id, workspace_id)
    if not rule:
        return {"error": "Rule not found"}
    return rule


@router.patch("/rules/{rule_id}")
async def update_automation_rule(
    rule_id: str,
    data: UpdateRuleRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Update an automation rule"""
    await verify_workspace_access(workspace_id, user)
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    return await CampaignAutomationService.update_rule(rule_id, workspace_id, updates)


@router.delete("/rules/{rule_id}")
async def delete_automation_rule(
    rule_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Delete an automation rule"""
    await verify_workspace_access(workspace_id, user)
    success = await CampaignAutomationService.delete_rule(rule_id, workspace_id)
    return {"deleted": success}


@router.post("/rules/{rule_id}/toggle")
async def toggle_automation_rule(
    rule_id: str,
    isActive: bool = Query(...),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Toggle rule active status"""
    await verify_workspace_access(workspace_id, user)
    return await CampaignAutomationService.toggle_rule(rule_id, workspace_id, isActive)


@router.get("/logs")
async def get_execution_logs(
    limit: int = Query(50, ge=1, le=200),
    actionType: Optional[str] = Query(None),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get automation execution logs"""
    await verify_workspace_access(workspace_id, user)
    return await CampaignAutomationService.get_execution_logs(workspace_id, limit, actionType)
