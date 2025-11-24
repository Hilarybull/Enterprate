"""Project routes"""
from fastapi import APIRouter, Depends
from app.schemas.project import ProjectCreate
from app.services.project_service import ProjectService
from app.core.security import get_current_user, verify_workspace_access

router = APIRouter(prefix="/workspaces", tags=["projects"])

@router.get("/{workspace_id}/projects")
async def get_projects(workspace_id: str, user: dict = Depends(get_current_user)):
    """Get all projects for a workspace"""
    await verify_workspace_access(workspace_id, user)
    return await ProjectService.get_workspace_projects(workspace_id)

@router.post("/{workspace_id}/projects")
async def create_project(
    workspace_id: str,
    project_data: ProjectCreate,
    user: dict = Depends(get_current_user)
):
    """Create a new project"""
    await verify_workspace_access(workspace_id, user)
    return await ProjectService.create_project(workspace_id, project_data)
