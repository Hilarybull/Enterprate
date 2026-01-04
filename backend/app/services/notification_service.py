"""Real-time Notifications Service for scheduled actions and system events"""
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from app.core.database import get_db


class NotificationService:
    """
    Service for real-time notifications.
    Handles scheduled action notifications, team updates, and system alerts.
    """
    
    # Notification types
    TYPES = {
        "scheduled_action_due": "Scheduled action is due for execution",
        "scheduled_action_executed": "Scheduled action has been executed",
        "scheduled_action_failed": "Scheduled action failed to execute",
        "campaign_started": "Campaign has started",
        "campaign_completed": "Campaign has completed",
        "campaign_milestone": "Campaign reached a milestone",
        "lead_converted": "Lead has been converted",
        "team_invite": "You have been invited to a team",
        "team_member_joined": "A new member joined the team",
        "comment_added": "New comment on your item",
        "ab_test_winner": "A/B test winner has been determined",
        "website_deployed": "Website has been deployed",
        "growth_alert": "Growth Agent detected an alert",
        "system_announcement": "System announcement"
    }
    
    @staticmethod
    async def create_notification(
        workspace_id: str,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[dict] = None,
        priority: str = "normal",
        action_url: Optional[str] = None
    ) -> dict:
        """Create a new notification"""
        db = get_db()
        
        notification_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        
        notification = {
            "id": notification_id,
            "workspace_id": workspace_id,
            "user_id": user_id,
            "type": notification_type,
            "title": title,
            "message": message,
            "data": data or {},
            "priority": priority,  # low, normal, high, urgent
            "actionUrl": action_url,
            "read": False,
            "readAt": None,
            "createdAt": now
        }
        
        await db.notifications.insert_one(notification)
        return {k: v for k, v in notification.items() if k != '_id'}
    
    @staticmethod
    async def get_notifications(
        workspace_id: str,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[dict]:
        """Get notifications for a user"""
        db = get_db()
        
        query = {
            "workspace_id": workspace_id,
            "user_id": user_id
        }
        
        if unread_only:
            query["read"] = False
        
        notifications = await db.notifications.find(query)\
            .sort("createdAt", -1)\
            .limit(limit)\
            .to_list(length=limit)
        
        return [{k: v for k, v in n.items() if k != '_id'} for n in notifications]
    
    @staticmethod
    async def mark_as_read(notification_id: str, user_id: str) -> bool:
        """Mark a notification as read"""
        db = get_db()
        
        result = await db.notifications.update_one(
            {"id": notification_id, "user_id": user_id},
            {
                "$set": {
                    "read": True,
                    "readAt": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return result.modified_count > 0
    
    @staticmethod
    async def mark_all_as_read(workspace_id: str, user_id: str) -> int:
        """Mark all notifications as read for a user"""
        db = get_db()
        
        result = await db.notifications.update_many(
            {"workspace_id": workspace_id, "user_id": user_id, "read": False},
            {
                "$set": {
                    "read": True,
                    "readAt": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return result.modified_count
    
    @staticmethod
    async def get_unread_count(workspace_id: str, user_id: str) -> int:
        """Get count of unread notifications"""
        db = get_db()
        return await db.notifications.count_documents({
            "workspace_id": workspace_id,
            "user_id": user_id,
            "read": False
        })
    
    @staticmethod
    async def delete_notification(notification_id: str, user_id: str) -> bool:
        """Delete a notification"""
        db = get_db()
        result = await db.notifications.delete_one({
            "id": notification_id,
            "user_id": user_id
        })
        return result.deleted_count > 0
    
    @staticmethod
    async def notify_scheduled_action_executed(
        workspace_id: str,
        user_id: str,
        action: dict
    ):
        """Send notification when scheduled action is executed"""
        platform = action.get("platform", "social")
        return await NotificationService.create_notification(
            workspace_id=workspace_id,
            user_id=user_id,
            notification_type="scheduled_action_executed",
            title="Scheduled Post Published",
            message=f"Your {platform.title()} post has been published successfully.",
            data={"actionId": action.get("id"), "platform": platform},
            priority="normal",
            action_url="/growth?tab=social"
        )
    
    @staticmethod
    async def notify_scheduled_action_failed(
        workspace_id: str,
        user_id: str,
        action: dict,
        error: str
    ):
        """Send notification when scheduled action fails"""
        return await NotificationService.create_notification(
            workspace_id=workspace_id,
            user_id=user_id,
            notification_type="scheduled_action_failed",
            title="Scheduled Action Failed",
            message=f"Failed to execute scheduled action: {error}",
            data={"actionId": action.get("id"), "error": error},
            priority="high",
            action_url="/growth?tab=agent"
        )
    
    @staticmethod
    async def notify_growth_alert(
        workspace_id: str,
        user_id: str,
        alert: dict
    ):
        """Send notification for growth agent alerts"""
        return await NotificationService.create_notification(
            workspace_id=workspace_id,
            user_id=user_id,
            notification_type="growth_alert",
            title=alert.get("title", "Growth Alert"),
            message=alert.get("message", "New alert from Growth Agent"),
            data={"alertId": alert.get("id"), "alertType": alert.get("type")},
            priority="high" if alert.get("severity") == "critical" else "normal",
            action_url="/growth?tab=agent"
        )
    
    @staticmethod
    async def notify_ab_test_winner(
        workspace_id: str,
        user_id: str,
        test: dict,
        winner: dict
    ):
        """Send notification when A/B test winner is determined"""
        notification = await NotificationService.create_notification(
            workspace_id=workspace_id,
            user_id=user_id,
            notification_type="ab_test_winner",
            title="A/B Test Complete",
            message=f"Variant '{winner.get('name')}' won with {winner.get('conversionRate')}% conversion rate.",
            data={"testId": test.get("id"), "winnerId": winner.get("id")},
            priority="normal",
            action_url="/growth?tab=campaigns"
        )
        
        # Broadcast via WebSocket
        try:
            from app.services.websocket_manager import NotificationBroadcaster
            import asyncio
            asyncio.create_task(NotificationBroadcaster.notify_ab_test_winner(
                workspace_id, test.get("name", "Test"), winner.get("name", "Winner")
            ))
        except Exception:
            pass
        
        return notification
    
    @staticmethod
    async def notify_website_deployed(
        workspace_id: str,
        user_id: str,
        site_url: str,
        site_name: str
    ):
        """Send notification when website is deployed"""
        notification = await NotificationService.create_notification(
            workspace_id=workspace_id,
            user_id=user_id,
            notification_type="website_deployed",
            title="Website Deployed!",
            message=f"Your website '{site_name}' is now live at {site_url}",
            data={"siteUrl": site_url, "siteName": site_name},
            priority="high",
            action_url=site_url
        )
        
        # Broadcast via WebSocket
        try:
            from app.services.websocket_manager import NotificationBroadcaster
            import asyncio
            asyncio.create_task(NotificationBroadcaster.notify_website_deployed(
                workspace_id, user_id, site_url, site_name
            ))
        except Exception:
            pass  # WebSocket failure shouldn't break the notification
        
        return notification
    
    @staticmethod
    async def notify_team_invite(
        workspace_id: str,
        invitee_id: str,
        inviter_name: str,
        workspace_name: str
    ):
        """Send notification for team invite"""
        return await NotificationService.create_notification(
            workspace_id=workspace_id,
            user_id=invitee_id,
            notification_type="team_invite",
            title="Team Invitation",
            message=f"{inviter_name} invited you to join '{workspace_name}'",
            data={"workspaceId": workspace_id, "inviterName": inviter_name},
            priority="high",
            action_url="/settings/team"
        )
    
    @staticmethod
    async def notify_new_lead(workspace_id: str, lead: dict):
        """Send notification when a new lead is captured"""
        # Get workspace owner/admins to notify
        db = get_db()
        team_members = await db.team_members.find({
            "workspace_id": workspace_id,
            "role": {"$in": ["owner", "admin"]}
        }).to_list(length=10)
        
        lead_name = lead.get("name", "Unknown")
        lead_email = lead.get("email", "")
        
        # Create notifications for each admin/owner
        for member in team_members:
            await NotificationService.create_notification(
                workspace_id=workspace_id,
                user_id=member.get("user_id"),
                notification_type="lead_converted",
                title="New Lead Captured!",
                message=f"New lead: {lead_name} ({lead_email})",
                data={
                    "leadId": lead.get("id"),
                    "leadName": lead_name,
                    "leadEmail": lead_email,
                    "source": lead.get("source", "website_form")
                },
                priority="high",
                action_url="/growth?tab=leads"
            )
        
        # Broadcast via WebSocket
        try:
            from app.services.websocket_manager import NotificationBroadcaster
            import asyncio
            asyncio.create_task(NotificationBroadcaster.notify_new_lead(workspace_id, lead))
        except Exception:
            pass  # WebSocket failure shouldn't break the lead capture
