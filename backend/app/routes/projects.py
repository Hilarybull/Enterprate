"""Project routes"""
from typing import List
from fastapi import APIRouter, Depends, Header
from app.services.project_service import ProjectService
from app.schemas.project import ProjectCreate, ProjectResponse
from app.core.security import get_current_user, verify_workspace_access

router = APIRouter(prefix="/workspaces/{workspace_id}/projects", tags=["projects"])

@router.post("", response_model=ProjectResponse)
async def create_project(
    workspace_id: str,
    data: ProjectCreate,
    user: dict = Depends(get_current_user)
):
    """Create a new project in workspace"""
    await verify_workspace_access(workspace_id, user)
    return await ProjectService.create_project(workspace_id, user["id"], data)

@router.get("", response_model=List[ProjectResponse])
async def get_projects(
    workspace_id: str,
    user: dict = Depends(get_current_user)
):
    """Get all projects for a workspace"""
    await verify_workspace_access(workspace_id, user)
    return await ProjectService.get_workspace_projects(workspace_id)

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    workspace_id: str,
    project_id: str,
    user: dict = Depends(get_current_user)
):
    """Get a specific project"""
    await verify_workspace_access(workspace_id, user)
    return await ProjectService.get_project(project_id, workspace_id)
