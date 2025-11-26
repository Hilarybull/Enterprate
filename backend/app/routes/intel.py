"""Intelligence Graph routes"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.services.intel_service import IntelService
from app.schemas.intelligence import EventCreate, EventResponse
from app.core.security import get_current_user, verify_workspace_access, get_workspace_id

router = APIRouter(prefix="/intel", tags=["intelligence"])

@router.post("/events", response_model=EventResponse)
async def create_event(
    data: EventCreate,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Create a new event"""
    await verify_workspace_access(workspace_id, user)
    return await IntelService.create_event(workspace_id, data)

@router.get("/events", response_model=List[EventResponse])
async def get_events(
    event_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get events for workspace"""
    await verify_workspace_access(workspace_id, user)
    return await IntelService.get_events(workspace_id, event_type, limit)
