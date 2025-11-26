"""Workspace routes"""
from typing import List
from fastapi import APIRouter, Depends
from app.services.workspace_service import WorkspaceService
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

@router.post("", response_model=WorkspaceResponse)
async def create_workspace(
    data: WorkspaceCreate,
    user: dict = Depends(get_current_user)
):
    """Create a new workspace"""
    return await WorkspaceService.create_workspace(user["id"], data)

@router.get("", response_model=List[WorkspaceResponse])
async def get_workspaces(user: dict = Depends(get_current_user)):
    """Get all workspaces for current user"""
    return await WorkspaceService.get_user_workspaces(user["id"])

@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: str,
    user: dict = Depends(get_current_user)
):
    """Get a specific workspace"""
    return await WorkspaceService.get_workspace(workspace_id, user["id"])

@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: str,
    data: WorkspaceUpdate,
    user: dict = Depends(get_current_user)
):
    """Update a workspace"""
    return await WorkspaceService.update_workspace(workspace_id, user["id"], data)
