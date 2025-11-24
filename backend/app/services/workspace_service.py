"""Workspace service"""
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from uuid import UUID
from app.models.workspace import Workspace, WorkspaceMembership, BusinessProfile
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate
from app.schemas.enums import UserRole

class WorkspaceService:
    """Service for workspace management"""
    
    @staticmethod
    async def get_user_workspaces(db: AsyncSession, user_id: str) -> list:
        """Get all workspaces for a user"""
        user_uuid = UUID(user_id)
        
        # Get memberships with workspace data
        stmt = select(WorkspaceMembership).where(
            WorkspaceMembership.user_id == user_uuid
        ).options(selectinload(WorkspaceMembership.workspace))
        
        result = await db.execute(stmt)
        memberships = result.scalars().all()
        
        # Build response
        workspaces = []
        for membership in memberships:
            ws = membership.workspace
            workspaces.append({
                "id": str(ws.id),
                "name": ws.name,
                "slug": ws.slug,
                "country": ws.country,
                "industry": ws.industry,
                "stage": ws.stage,
                "ownerId": str(ws.owner_id),
                "createdAt": ws.created_at.isoformat(),
                "role": membership.role.value
            })
        
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
