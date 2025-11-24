"""Workspace service"""
from fastapi import HTTPException
from app.core.database import get_database
from app.schemas.workspace import Workspace, WorkspaceCreate, WorkspaceUpdate, WorkspaceMembership, BusinessProfile
from app.schemas.enums import UserRole

class WorkspaceService:
    """Service for workspace management"""
    
    @staticmethod
    async def get_user_workspaces(user_id: str) -> list:
        """Get all workspaces for a user"""
        db = get_database()
        
        memberships = await db.workspace_memberships.find({"userId": user_id}, {"_id": 0}).to_list(100)
        workspace_ids = [m['workspaceId'] for m in memberships]
        
        workspaces = await db.workspaces.find({"id": {"$in": workspace_ids}}, {"_id": 0}).to_list(100)
        
        # Add membership info
        for ws in workspaces:
            membership = next((m for m in memberships if m['workspaceId'] == ws['id']), None)
            ws['role'] = membership['role'] if membership else None
        
        return workspaces
    
    @staticmethod
    async def create_workspace(workspace_data: WorkspaceCreate, user_id: str) -> dict:
        """Create a new workspace"""
        db = get_database()
        
        # Generate slug from name
        slug = workspace_data.name.lower().replace(' ', '-')
        
        workspace = Workspace(
            name=workspace_data.name,
            slug=slug,
            country=workspace_data.country,
            industry=workspace_data.industry,
            stage=workspace_data.stage,
            ownerId=user_id
        )
        
        doc = workspace.model_dump()
        doc['createdAt'] = doc['createdAt'].isoformat()
        await db.workspaces.insert_one(doc)
        
        # Create membership
        membership = WorkspaceMembership(
            userId=user_id,
            workspaceId=workspace.id,
            role=UserRole.OWNER
        )
        
        mem_doc = membership.model_dump()
        mem_doc['createdAt'] = mem_doc['createdAt'].isoformat()
        await db.workspace_memberships.insert_one(mem_doc)
        
        # Create business profile
        profile = BusinessProfile(
            workspaceId=workspace.id,
            businessName=workspace_data.name
        )
        
        profile_doc = profile.model_dump()
        profile_doc['createdAt'] = profile_doc['createdAt'].isoformat()
        await db.business_profiles.insert_one(profile_doc)
        
        return workspace.model_dump()
    
    @staticmethod
    async def get_workspace(workspace_id: str) -> dict:
        """Get workspace by ID"""
        db = get_database()
        
        workspace = await db.workspaces.find_one({"id": workspace_id}, {"_id": 0})
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        
        # Get business profile
        profile = await db.business_profiles.find_one({"workspaceId": workspace_id}, {"_id": 0})
        workspace['businessProfile'] = profile
        
        return workspace
    
    @staticmethod
    async def update_workspace(workspace_id: str, workspace_data: WorkspaceUpdate) -> dict:
        """Update workspace"""
        db = get_database()
        
        update_data = {k: v for k, v in workspace_data.model_dump().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No data to update")
        
        await db.workspaces.update_one({"id": workspace_id}, {"$set": update_data})
        
        workspace = await db.workspaces.find_one({"id": workspace_id}, {"_id": 0})
        return workspace
