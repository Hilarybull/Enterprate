"""Project service"""
from app.core.database import get_database
from app.schemas.project import Project, ProjectCreate

class ProjectService:
    """Service for project management"""
    
    @staticmethod
    async def get_workspace_projects(workspace_id: str) -> list:
        """Get all projects for a workspace"""
        db = get_database()
        projects = await db.projects.find({"workspaceId": workspace_id}, {"_id": 0}).to_list(100)
        return projects
    
    @staticmethod
    async def create_project(workspace_id: str, project_data: ProjectCreate) -> dict:
        """Create a new project"""
        db = get_database()
        
        project = Project(
            workspaceId=workspace_id,
            type=project_data.type,
            name=project_data.name,
            config=project_data.config
        )
        
        doc = project.model_dump()
        doc['createdAt'] = doc['createdAt'].isoformat()
        await db.projects.insert_one(doc)
        
        return project.model_dump()
