"""Notifications routes"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.services.notification_service import NotificationService
from app.core.security import get_current_user, verify_workspace_access, get_workspace_id

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
async def get_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=100),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get notifications for the current user"""
    await verify_workspace_access(workspace_id, user)
    return await NotificationService.get_notifications(
        workspace_id, user["id"], unread_only, limit
    )


@router.get("/unread-count")
async def get_unread_count(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get count of unread notifications"""
    await verify_workspace_access(workspace_id, user)
    count = await NotificationService.get_unread_count(workspace_id, user["id"])
    return {"unreadCount": count}


@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Mark a notification as read"""
    await verify_workspace_access(workspace_id, user)
    success = await NotificationService.mark_as_read(notification_id, user["id"])
    return {"success": success}


@router.post("/read-all")
async def mark_all_as_read(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Mark all notifications as read"""
    await verify_workspace_access(workspace_id, user)
    count = await NotificationService.mark_all_as_read(workspace_id, user["id"])
    return {"markedAsRead": count}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Delete a notification"""
    await verify_workspace_access(workspace_id, user)
    success = await NotificationService.delete_notification(notification_id, user["id"])
    return {"deleted": success}
