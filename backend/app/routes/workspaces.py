"""Workspace routes"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate
from app.services.workspace_service import WorkspaceService
from app.core.security import get_current_user, verify_workspace_access

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

@router.get("")
async def get_workspaces(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all workspaces for current user"""
    return await WorkspaceService.get_user_workspaces(db, user['id'])

@router.post("")
async def create_workspace(
    workspace_data: WorkspaceCreate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new workspace"""
    return await WorkspaceService.create_workspace(db, workspace_data, user['id'])

@router.get("/{workspace_id}")
async def get_workspace(
    workspace_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get workspace by ID"""
    await verify_workspace_access(workspace_id, user, db)
    return await WorkspaceService.get_workspace(db, workspace_id)

@router.patch("/{workspace_id}")
async def update_workspace(
    workspace_id: str,
    workspace_data: WorkspaceUpdate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update workspace"""
    await verify_workspace_access(workspace_id, user, db)
    return await WorkspaceService.update_workspace(db, workspace_id, workspace_data)
