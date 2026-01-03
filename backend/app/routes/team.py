"""Team Collaboration routes"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from app.services.team_collaboration_service import TeamCollaborationService
from app.core.security import get_current_user, verify_workspace_access, get_workspace_id

router = APIRouter(prefix="/team", tags=["team"])


class InviteMemberRequest(BaseModel):
    email: str
    role: str = "editor"
    message: Optional[str] = None


class UpdateRoleRequest(BaseModel):
    role: str


class AddCommentRequest(BaseModel):
    entityType: str
    entityId: str
    content: str
    parentId: Optional[str] = None


class UpdateCommentRequest(BaseModel):
    content: str


@router.get("/members")
async def get_team_members(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get all team members"""
    await verify_workspace_access(workspace_id, user)
    return await TeamCollaborationService.get_team_members(workspace_id)


@router.post("/invite")
async def invite_member(
    data: InviteMemberRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Invite a new team member"""
    await verify_workspace_access(workspace_id, user)
    return await TeamCollaborationService.invite_member(
        workspace_id, user["id"], data.email, data.role, data.message
    )


@router.get("/invites/pending")
async def get_pending_invites(
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get pending team invites"""
    await verify_workspace_access(workspace_id, user)
    return await TeamCollaborationService.get_pending_invites(workspace_id)


@router.post("/invites/{invite_id}/accept")
async def accept_invite(
    invite_id: str,
    user: dict = Depends(get_current_user)
):
    """Accept a team invite"""
    return await TeamCollaborationService.accept_invite(invite_id, user["id"])


@router.post("/invites/{invite_id}/decline")
async def decline_invite(
    invite_id: str,
    user: dict = Depends(get_current_user)
):
    """Decline a team invite"""
    success = await TeamCollaborationService.decline_invite(invite_id, user["id"])
    return {"declined": success}


@router.patch("/members/{member_id}/role")
async def update_member_role(
    member_id: str,
    data: UpdateRoleRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Update a team member's role"""
    await verify_workspace_access(workspace_id, user)
    return await TeamCollaborationService.update_member_role(
        workspace_id, member_id, data.role, user["id"]
    )


@router.delete("/members/{member_id}")
async def remove_member(
    member_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Remove a team member"""
    await verify_workspace_access(workspace_id, user)
    success = await TeamCollaborationService.remove_member(
        workspace_id, member_id, user["id"]
    )
    return {"removed": success}


@router.get("/roles")
async def get_available_roles():
    """Get available team roles"""
    return TeamCollaborationService.ROLES


# Activity Feed
@router.get("/activity")
async def get_activity_feed(
    limit: int = Query(50, ge=1, le=100),
    types: Optional[str] = Query(None, description="Comma-separated activity types"),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get team activity feed"""
    await verify_workspace_access(workspace_id, user)
    activity_types = types.split(",") if types else None
    return await TeamCollaborationService.get_activity_feed(
        workspace_id, limit, activity_types
    )


# Comments
@router.post("/comments")
async def add_comment(
    data: AddCommentRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Add a comment to an entity"""
    await verify_workspace_access(workspace_id, user)
    return await TeamCollaborationService.add_comment(
        workspace_id, user["id"], data.entityType, data.entityId, 
        data.content, data.parentId
    )


@router.get("/comments")
async def get_comments(
    entityType: str = Query(...),
    entityId: str = Query(...),
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Get comments for an entity"""
    await verify_workspace_access(workspace_id, user)
    return await TeamCollaborationService.get_comments(
        workspace_id, entityType, entityId
    )


@router.patch("/comments/{comment_id}")
async def update_comment(
    comment_id: str,
    data: UpdateCommentRequest,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Update a comment"""
    await verify_workspace_access(workspace_id, user)
    return await TeamCollaborationService.update_comment(
        comment_id, user["id"], data.content
    )


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: str,
    user: dict = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id)
):
    """Delete a comment"""
    await verify_workspace_access(workspace_id, user)
    success = await TeamCollaborationService.delete_comment(comment_id, user["id"])
    return {"deleted": success}
