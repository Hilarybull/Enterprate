"""Intelligence Graph Routes - API for analytics and activity tracking"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from pydantic import BaseModel
from app.core.security import get_current_user, get_workspace_id, verify_workspace_access
from app.services.intelligence_service import IntelligenceGraphService, IntelligenceEvent

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


class LogEventRequest(BaseModel):
    eventType: str
    entityType: str
    entityId: Optional[str] = None
    data: dict = {}
    metadata: dict = {}


@router.get("/events")
async def get_events(
    entity_type: Optional[str] = Query(None, description="Filter by entity type (catalogue, invoice, document, etc.)"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    entity_id: Optional[str] = Query(None, description="Filter by specific entity ID"),
    start_date: Optional[str] = Query(None, description="Filter events after this date (ISO format)"),
    end_date: Optional[str] = Query(None, description="Filter events before this date (ISO format)"),
    limit: int = Query(100, ge=1, le=500),
    skip: int = Query(0, ge=0),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get intelligence events with optional filters"""
    await verify_workspace_access(workspace_id, user)
    
    return await IntelligenceGraphService.get_events(
        workspace_id=workspace_id,
        entity_type=entity_type,
        event_type=event_type,
        entity_id=entity_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        skip=skip
    )


@router.post("/events")
async def log_event(
    data: LogEventRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Manually log an intelligence event"""
    await verify_workspace_access(workspace_id, user)
    
    return await IntelligenceGraphService.log_event(
        workspace_id=workspace_id,
        user_id=user["id"],
        event_type=data.eventType,
        entity_type=data.entityType,
        entity_id=data.entityId,
        data=data.data,
        metadata=data.metadata
    )


@router.get("/summary")
async def get_activity_summary(
    period_type: str = Query("daily", enum=["daily", "monthly"]),
    periods: int = Query(7, ge=1, le=30),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get activity summary for dashboard"""
    await verify_workspace_access(workspace_id, user)
    
    return await IntelligenceGraphService.get_activity_summary(
        workspace_id=workspace_id,
        period_type=period_type,
        periods=periods
    )


@router.get("/insights")
async def get_insights(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get aggregated insights for dashboard"""
    await verify_workspace_access(workspace_id, user)
    
    return await IntelligenceGraphService.get_insights(workspace_id)


@router.get("/entity/{entity_type}/{entity_id}/timeline")
async def get_entity_timeline(
    entity_type: str,
    entity_id: str,
    limit: int = Query(50, ge=1, le=200),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get complete timeline for a specific entity"""
    await verify_workspace_access(workspace_id, user)
    
    return await IntelligenceGraphService.get_entity_timeline(
        workspace_id=workspace_id,
        entity_type=entity_type,
        entity_id=entity_id,
        limit=limit
    )


@router.get("/stats/{entity_type}")
async def get_entity_stats(
    entity_type: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get statistics for a specific entity type"""
    await verify_workspace_access(workspace_id, user)
    
    return await IntelligenceGraphService.get_entity_stats(
        workspace_id=workspace_id,
        entity_type=entity_type
    )
