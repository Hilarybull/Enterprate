"""Intelligence graph routes"""
from fastapi import APIRouter, Depends, Query
from app.schemas.intelligence import IntelligenceEventCreate
from app.services.intel_service import IntelService
from app.core.security import get_current_user, get_workspace_id, verify_workspace_access

router = APIRouter(prefix="/intel", tags=["intelligence"])

@router.get("/events")
async def get_events(
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100)
):
    """Get intelligence events for a workspace"""
    await verify_workspace_access(workspace_id, user)
    return await IntelService.get_events(workspace_id, limit)

@router.post("/events")
async def create_event(
    event_data: IntelligenceEventCreate,
    workspace_id: str = Depends(get_workspace_id),
    user: dict = Depends(get_current_user)
):
    """Create an intelligence event"""
    await verify_workspace_access(workspace_id, user)
    return await IntelService.create_event(event_data, workspace_id, user['id'])
