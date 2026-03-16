"""Team Collaboration Service for workspace management"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from app.core.database import get_db


class TeamCollaborationService:
    """
    Service for team collaboration features.
    Manages team members, roles, activity feeds, and comments.
    """
    
    # Available roles
    ROLES = {
        "owner": {"level": 100, "label": "Owner", "permissions": ["*"]},
        "admin": {"level": 80, "label": "Admin", "permissions": ["manage_team", "manage_content", "view_analytics"]},
        "editor": {"level": 60, "label": "Editor", "permissions": ["manage_content", "view_analytics"]},
        "viewer": {"level": 20, "label": "Viewer", "permissions": ["view_content", "view_analytics"]},
        "guest": {"level": 10, "label": "Guest", "permissions": ["view_content"]}
    }
    
    @staticmethod
    async def invite_member(
        workspace_id: str,
        inviter_id: str,
        email: str,
        role: str = "editor",
        message: Optional[str] = None
    ) -> dict:
        """Invite a new member to the workspace"""
        db = get_db()
        
        if role not in TeamCollaborationService.ROLES:
            raise HTTPException(status_code=400, detail="Invalid role")
        
        # Check if already a member
        existing = await db.workspace_memberships.find_one({
            "workspace_id": workspace_id,
            "email": email
        })
        
        if existing:
            raise HTTPException(status_code=400, detail="User is already a member or has pending invite")
        
        # Check if user exists
        user = await db.users.find_one({"email": email})
        if user and user.get("id"):
            already_has_workspace = await db.workspace_memberships.find_one(
                {"user_id": user.get("id")},
                {"_id": 0},
            )
            if already_has_workspace:
                raise HTTPException(status_code=409, detail="This user already belongs to a workspace")
        
        invite_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        invite = {
            "id": invite_id,
            "workspace_id": workspace_id,
            "email": email,
            "user_id": user.get("id") if user else None,
            "role": role,
            "status": "pending",  # pending, accepted, declined, expired
            "message": message,
            "invitedBy": inviter_id,
            "createdAt": now,
            "expiresAt": None  # Could add expiration
        }
        
        await db.team_invites.insert_one(invite)
        
        # Log activity
        await TeamCollaborationService.log_activity(
            workspace_id=workspace_id,
            user_id=inviter_id,
            activity_type="member_invited",
            description=f"Invited {email} as {role}",
            data={"email": email, "role": role}
        )
        
        return {k: v for k, v in invite.items() if k != '_id'}
    
    @staticmethod
    async def accept_invite(invite_id: str, user_id: str) -> dict:
        """Accept a team invite"""
        db = get_db()
        
        invite = await db.team_invites.find_one({"id": invite_id, "status": "pending"})
        if not invite:
            raise HTTPException(status_code=404, detail="Invite not found or already processed")
        
        user = await db.users.find_one({"id": user_id})
        if not user or user.get("email") != invite.get("email"):
            raise HTTPException(status_code=403, detail="This invite is not for you")

        already_has_workspace = await db.workspace_memberships.find_one(
            {"user_id": user_id},
            {"_id": 0},
        )
        if already_has_workspace:
            raise HTTPException(status_code=409, detail="Only one workspace is allowed per user")
        
        now = datetime.now(timezone.utc).isoformat()
        
        # Create membership
        membership = {
            "workspace_id": invite.get("workspace_id"),
            "user_id": user_id,
            "email": user.get("email"),
            "name": user.get("name"),
            "role": invite.get("role", "editor"),
            "joinedAt": now,
            "invitedBy": invite.get("invitedBy")
        }
        
        await db.workspace_memberships.insert_one(membership)
        
        # Update invite status
        await db.team_invites.update_one(
            {"id": invite_id},
            {"$set": {"status": "accepted", "acceptedAt": now}}
        )
        
        # Log activity
        await TeamCollaborationService.log_activity(
            workspace_id=invite.get("workspace_id"),
            user_id=user_id,
            activity_type="member_joined",
            description=f"{user.get('name')} joined the team",
            data={"role": invite.get("role")}
        )
        
        return {k: v for k, v in membership.items() if k != '_id'}
    
    @staticmethod
    async def decline_invite(invite_id: str, user_id: str) -> bool:
        """Decline a team invite"""
        db = get_db()
        
        result = await db.team_invites.update_one(
            {"id": invite_id, "status": "pending"},
            {"$set": {"status": "declined", "declinedAt": datetime.now(timezone.utc).isoformat()}}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    async def get_team_members(workspace_id: str) -> List[dict]:
        """Get all team members for a workspace"""
        db = get_db()
        
        members = await db.workspace_memberships.find({
            "workspace_id": workspace_id
        }).to_list(length=100)
        
        return [{k: v for k, v in m.items() if k != '_id'} for m in members]
    
    @staticmethod
    async def get_pending_invites(workspace_id: str) -> List[dict]:
        """Get pending invites for a workspace"""
        db = get_db()
        
        invites = await db.team_invites.find({
            "workspace_id": workspace_id,
            "status": "pending"
        }).to_list(length=50)
        
        return [{k: v for k, v in i.items() if k != '_id'} for i in invites]
    
    @staticmethod
    async def update_member_role(
        workspace_id: str,
        member_user_id: str,
        new_role: str,
        updater_id: str
    ) -> dict:
        """Update a team member's role"""
        db = get_db()
        
        if new_role not in TeamCollaborationService.ROLES:
            raise HTTPException(status_code=400, detail="Invalid role")
        
        result = await db.workspace_memberships.update_one(
            {"workspace_id": workspace_id, "user_id": member_user_id},
            {"$set": {"role": new_role, "roleUpdatedAt": datetime.now(timezone.utc).isoformat()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Member not found")
        
        # Log activity
        await TeamCollaborationService.log_activity(
            workspace_id=workspace_id,
            user_id=updater_id,
            activity_type="role_updated",
            description=f"Changed role to {new_role}",
            data={"memberId": member_user_id, "newRole": new_role}
        )
        
        updated = await db.workspace_memberships.find_one({
            "workspace_id": workspace_id,
            "user_id": member_user_id
        })
        return {k: v for k, v in updated.items() if k != '_id'}
    
    @staticmethod
    async def remove_member(
        workspace_id: str,
        member_user_id: str,
        remover_id: str
    ) -> bool:
        """Remove a team member"""
        db = get_db()
        
        # Can't remove owner
        member = await db.workspace_memberships.find_one({
            "workspace_id": workspace_id,
            "user_id": member_user_id
        })
        
        if member and member.get("role") == "owner":
            raise HTTPException(status_code=400, detail="Cannot remove workspace owner")
        
        result = await db.workspace_memberships.delete_one({
            "workspace_id": workspace_id,
            "user_id": member_user_id
        })
        
        if result.deleted_count > 0:
            await TeamCollaborationService.log_activity(
                workspace_id=workspace_id,
                user_id=remover_id,
                activity_type="member_removed",
                description="Member removed from team",
                data={"memberId": member_user_id}
            )
        
        return result.deleted_count > 0
    
    @staticmethod
    async def log_activity(
        workspace_id: str,
        user_id: str,
        activity_type: str,
        description: str,
        data: Optional[dict] = None
    ) -> dict:
        """Log a team activity"""
        db = get_db()
        
        activity_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        # Get user name
        user = await db.users.find_one({"id": user_id})
        user_name = user.get("name", "Unknown") if user else "System"
        
        activity = {
            "id": activity_id,
            "workspace_id": workspace_id,
            "user_id": user_id,
            "user_name": user_name,
            "type": activity_type,
            "description": description,
            "data": data or {},
            "createdAt": now
        }
        
        await db.team_activities.insert_one(activity)
        return {k: v for k, v in activity.items() if k != '_id'}
    
    @staticmethod
    async def get_activity_feed(
        workspace_id: str,
        limit: int = 50,
        activity_types: Optional[List[str]] = None
    ) -> List[dict]:
        """Get activity feed for workspace"""
        db = get_db()
        
        query = {"workspace_id": workspace_id}
        if activity_types:
            query["type"] = {"$in": activity_types}
        
        activities = await db.team_activities.find(query)\
            .sort("createdAt", -1)\
            .limit(limit)\
            .to_list(length=limit)
        
        return [{k: v for k, v in a.items() if k != '_id'} for a in activities]
    
    @staticmethod
    async def add_comment(
        workspace_id: str,
        user_id: str,
        entity_type: str,
        entity_id: str,
        content: str,
        parent_id: Optional[str] = None
    ) -> dict:
        """Add a comment to an entity (campaign, lead, task, etc.)"""
        db = get_db()
        
        user = await db.users.find_one({"id": user_id})
        
        comment_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        comment = {
            "id": comment_id,
            "workspace_id": workspace_id,
            "entityType": entity_type,
            "entityId": entity_id,
            "parentId": parent_id,
            "content": content,
            "userId": user_id,
            "userName": user.get("name", "Unknown") if user else "Unknown",
            "createdAt": now,
            "updatedAt": now,
            "isEdited": False
        }
        
        await db.comments.insert_one(comment)
        
        # Log activity
        await TeamCollaborationService.log_activity(
            workspace_id=workspace_id,
            user_id=user_id,
            activity_type="comment_added",
            description=f"Commented on {entity_type}",
            data={"entityType": entity_type, "entityId": entity_id}
        )
        
        return {k: v for k, v in comment.items() if k != '_id'}
    
    @staticmethod
    async def get_comments(
        workspace_id: str,
        entity_type: str,
        entity_id: str
    ) -> List[dict]:
        """Get comments for an entity"""
        db = get_db()
        
        comments = await db.comments.find({
            "workspace_id": workspace_id,
            "entityType": entity_type,
            "entityId": entity_id
        }).sort("createdAt", 1).to_list(length=200)
        
        return [{k: v for k, v in c.items() if k != '_id'} for c in comments]
    
    @staticmethod
    async def update_comment(
        comment_id: str,
        user_id: str,
        content: str
    ) -> dict:
        """Update a comment"""
        db = get_db()
        
        result = await db.comments.update_one(
            {"id": comment_id, "userId": user_id},
            {
                "$set": {
                    "content": content,
                    "updatedAt": datetime.now(timezone.utc).isoformat(),
                    "isEdited": True
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Comment not found or not authorized")
        
        updated = await db.comments.find_one({"id": comment_id})
        return {k: v for k, v in updated.items() if k != '_id'}
    
    @staticmethod
    async def delete_comment(comment_id: str, user_id: str) -> bool:
        """Delete a comment"""
        db = get_db()
        
        result = await db.comments.delete_one({
            "id": comment_id,
            "userId": user_id
        })
        
        return result.deleted_count > 0
