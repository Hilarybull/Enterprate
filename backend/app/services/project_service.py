"""Project service"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.models.project import Project
from app.schemas.project import ProjectCreate

class ProjectService:
    """Service for project management"""
    
    @staticmethod
    async def get_workspace_projects(db: AsyncSession, workspace_id: str) -> list:
        """Get all projects for a workspace"""
        workspace_uuid = UUID(workspace_id)
        
        stmt = select(Project).where(Project.workspace_id == workspace_uuid)
        result = await db.execute(stmt)
        projects = result.scalars().all()
        
        return [
            {
                "id": str(p.id),
                "workspaceId": str(p.workspace_id),
                "type": p.type.value,
                "name": p.name,
                "status": p.status.value,
                "config": p.config,
                "createdAt": p.created_at.isoformat()
            }
            for p in projects
        ]
    
    @staticmethod
    async def create_project(db: AsyncSession, workspace_id: str, project_data: ProjectCreate) -> dict:
        """Create a new project"""
        workspace_uuid = UUID(workspace_id)
        
        project = Project(
            workspace_id=workspace_uuid,
            type=project_data.type,
            name=project_data.name,
            config=project_data.config
        )
        
        db.add(project)
        await db.flush()
        
        return {
            "id": str(project.id),
            "workspaceId": str(project.workspace_id),
            "type": project.type.value,
            "name": project.name,
            "status": project.status.value,
            "config": project.config,
            "createdAt": project.created_at.isoformat()
        }
