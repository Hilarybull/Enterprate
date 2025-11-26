"""Project service"""
import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import HTTPException
from app.core.database import get_db
from app.schemas.project import ProjectCreate

class ProjectService:
    """Service for project operations"""
    
    @staticmethod
    async def create_project(workspace_id: str, user_id: str, data: ProjectCreate) -> dict:
        """Create a new project"""
        db = get_db()
        
        project_id = str(uuid.uuid4())
        project = {
            "id": project_id,
            "workspace_id": workspace_id,
            "name": data.name,
            "description": data.description,
            "type": data.type,
            "status": "ACTIVE",
            "created_by": user_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.projects.insert_one(project)
        return {k: v for k, v in project.items() if k != '_id'}
    
    @staticmethod
    async def get_workspace_projects(workspace_id: str) -> List[dict]:
        """Get all projects for a workspace"""
        db = get_db()
        
        projects = await db.projects.find(
            {"workspace_id": workspace_id}
        ).to_list(length=100)
        
        return [{k: v for k, v in p.items() if k != '_id'} for p in projects]
    
    @staticmethod
    async def get_project(project_id: str, workspace_id: str) -> dict:
        """Get a specific project"""
        db = get_db()
        
        project = await db.projects.find_one({
            "id": project_id,
            "workspace_id": workspace_id
        })
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {k: v for k, v in project.items() if k != '_id'}
