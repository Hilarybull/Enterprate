"""Workspace service"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException
from app.core.database import get_db
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate

class WorkspaceService:
    """Service for workspace operations"""
    
    @staticmethod
    async def create_workspace(user_id: str, data: WorkspaceCreate) -> dict:
        """Create a new workspace"""
        db = get_db()
        
        workspace_id = str(uuid.uuid4())
        slug = data.name.lower().replace(' ', '-')
        
        workspace = {
            "id": workspace_id,
            "name": data.name,
            "slug": slug,
            "owner_id": user_id,
            "country": data.country,
            "industry": data.industry,
            "stage": data.stage,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.workspaces.insert_one(workspace)
        
        # Add owner as member
        membership = {
            "id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "user_id": user_id,
            "role": "OWNER",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.workspace_memberships.insert_one(membership)
        
        return {**workspace, "role": "OWNER"}
    
    @staticmethod
    async def get_user_workspaces(user_id: str) -> List[dict]:
        """Get all workspaces for a user"""
        db = get_db()
        
        # Find memberships
        memberships = await db.workspace_memberships.find(
            {"user_id": user_id}
        ).to_list(length=100)
        
        workspace_ids = [m["workspace_id"] for m in memberships]
        
        # Get workspaces
        workspaces = await db.workspaces.find(
            {"id": {"$in": workspace_ids}}
        ).to_list(length=100)
        
        # Add role to each workspace
        result = []
        for ws in workspaces:
            membership = next((m for m in memberships if m["workspace_id"] == ws["id"]), None)
            ws_dict = {k: v for k, v in ws.items() if k != '_id'}
            ws_dict["role"] = membership["role"] if membership else "MEMBER"
            result.append(ws_dict)
        
        return result
    
    @staticmethod
    async def get_workspace(workspace_id: str, user_id: str) -> dict:
        """Get a specific workspace"""
        db = get_db()
        
        workspace = await db.workspaces.find_one({"id": workspace_id})
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        
        # Check membership
        membership = await db.workspace_memberships.find_one({
            "workspace_id": workspace_id,
            "user_id": user_id
        })
        if not membership:
            raise HTTPException(status_code=403, detail="Access denied")
        
        ws_dict = {k: v for k, v in workspace.items() if k != '_id'}
        ws_dict["role"] = membership["role"]
        return ws_dict
    
    @staticmethod
    async def update_workspace(workspace_id: str, user_id: str, data: WorkspaceUpdate) -> dict:
        """Update a workspace"""
        db = get_db()
        
        # Check ownership
        workspace = await db.workspaces.find_one({"id": workspace_id})
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        
        membership = await db.workspace_memberships.find_one({
            "workspace_id": workspace_id,
            "user_id": user_id
        })
        if not membership:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update
        update_data = data.model_dump(exclude_unset=True)
        if update_data:
            await db.workspaces.update_one(
                {"id": workspace_id},
                {"$set": update_data}
            )
        
        # Return updated workspace
        updated = await db.workspaces.find_one({"id": workspace_id})
        ws_dict = {k: v for k, v in updated.items() if k != '_id'}
        ws_dict["role"] = membership["role"]
        return ws_dict
