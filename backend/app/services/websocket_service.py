"""WebSocket Manager for Real-time Notifications"""
import asyncio
import json
from typing import Dict, Set, Optional
from datetime import datetime, timezone
from fastapi import WebSocket, WebSocketDisconnect
from app.core.database import get_db


class ConnectionManager:
    """
    Manages WebSocket connections for real-time notifications.
    Supports user-specific and workspace-wide broadcasts.
    """
    
    def __init__(self):
        # user_id -> set of websocket connections
        self.user_connections: Dict[str, Set[WebSocket]] = {}
        # workspace_id -> set of websocket connections
        self.workspace_connections: Dict[str, Set[WebSocket]] = {}
        # websocket -> (user_id, workspace_id)
        self.connection_info: Dict[WebSocket, tuple] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, workspace_id: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        # Add to user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)
        
        # Add to workspace connections
        if workspace_id not in self.workspace_connections:
            self.workspace_connections[workspace_id] = set()
        self.workspace_connections[workspace_id].add(websocket)
        
        # Store connection info
        self.connection_info[websocket] = (user_id, workspace_id)
        
        # Send connection confirmation
        await self.send_personal(websocket, {
            "type": "connection",
            "status": "connected",
            "message": "Real-time notifications enabled",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.connection_info:
            user_id, workspace_id = self.connection_info[websocket]
            
            # Remove from user connections
            if user_id in self.user_connections:
                self.user_connections[user_id].discard(websocket)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            
            # Remove from workspace connections
            if workspace_id in self.workspace_connections:
                self.workspace_connections[workspace_id].discard(websocket)
                if not self.workspace_connections[workspace_id]:
                    del self.workspace_connections[workspace_id]
            
            # Remove connection info
            del self.connection_info[websocket]
    
    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send message to a specific connection"""
        try:
            await websocket.send_json(message)
        except Exception:
            self.disconnect(websocket)
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send message to all connections of a specific user"""
        if user_id in self.user_connections:
            disconnected = []
            for websocket in self.user_connections[user_id]:
                try:
                    await websocket.send_json(message)
                except Exception:
                    disconnected.append(websocket)
            
            # Clean up disconnected sockets
            for ws in disconnected:
                self.disconnect(ws)
    
    async def send_to_workspace(self, workspace_id: str, message: dict):
        """Send message to all connections in a workspace"""
        if workspace_id in self.workspace_connections:
            disconnected = []
            for websocket in self.workspace_connections[workspace_id]:
                try:
                    await websocket.send_json(message)
                except Exception:
                    disconnected.append(websocket)
            
            # Clean up disconnected sockets
            for ws in disconnected:
                self.disconnect(ws)
    
    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        for websocket in list(self.connection_info.keys()):
            try:
                await websocket.send_json(message)
            except Exception:
                self.disconnect(websocket)
    
    def get_connected_users(self, workspace_id: Optional[str] = None) -> list:
        """Get list of connected user IDs"""
        if workspace_id:
            users = set()
            for ws in self.workspace_connections.get(workspace_id, set()):
                if ws in self.connection_info:
                    users.add(self.connection_info[ws][0])
            return list(users)
        return list(self.user_connections.keys())


# Global connection manager instance
manager = ConnectionManager()


class RealTimeNotificationService:
    """
    Service for sending real-time notifications via WebSocket.
    Integrates with the notification service for persistence.
    """
    
    @staticmethod
    async def notify_user(
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[dict] = None,
        workspace_id: Optional[str] = None,
        persist: bool = True
    ):
        """Send real-time notification to a user"""
        from app.services.notification_service import NotificationService
        
        notification = {
            "type": "notification",
            "notificationType": notification_type,
            "title": title,
            "message": message,
            "data": data or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Send via WebSocket
        await manager.send_to_user(user_id, notification)
        
        # Persist to database if requested
        if persist and workspace_id:
            await NotificationService.create_notification(
                workspace_id=workspace_id,
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                message=message,
                data=data
            )
    
    @staticmethod
    async def notify_workspace(
        workspace_id: str,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[dict] = None,
        exclude_user: Optional[str] = None
    ):
        """Send real-time notification to all users in a workspace"""
        notification = {
            "type": "notification",
            "notificationType": notification_type,
            "title": title,
            "message": message,
            "data": data or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Get all connections in workspace
        if workspace_id in manager.workspace_connections:
            for websocket in list(manager.workspace_connections[workspace_id]):
                if websocket in manager.connection_info:
                    user_id, _ = manager.connection_info[websocket]
                    if user_id != exclude_user:
                        try:
                            await websocket.send_json(notification)
                        except Exception:
                            manager.disconnect(websocket)
    
    @staticmethod
    async def notify_scheduled_action_executed(
        workspace_id: str,
        user_id: str,
        action: dict
    ):
        """Send notification when scheduled action is executed"""
        await RealTimeNotificationService.notify_user(
            user_id=user_id,
            notification_type="scheduled_action_executed",
            title="Scheduled Post Published",
            message=f"Your {action.get('platform', 'social')} post has been published!",
            data={"actionId": action.get("id"), "platform": action.get("platform")},
            workspace_id=workspace_id
        )
    
    @staticmethod
    async def notify_lead_captured(
        workspace_id: str,
        lead_data: dict
    ):
        """Send notification when a new lead is captured from website"""
        db = get_db()
        
        # Get workspace owner/admins
        members = await db.workspace_memberships.find({
            "workspace_id": workspace_id,
            "role": {"$in": ["owner", "admin"]}
        }).to_list(length=10)
        
        for member in members:
            await RealTimeNotificationService.notify_user(
                user_id=member.get("user_id"),
                notification_type="lead_captured",
                title="New Lead Captured!",
                message=f"New inquiry from {lead_data.get('name', 'Unknown')} via website",
                data={"leadId": lead_data.get("id"), "source": "website"},
                workspace_id=workspace_id
            )
    
    @staticmethod
    async def notify_team_activity(
        workspace_id: str,
        actor_id: str,
        activity_type: str,
        description: str,
        data: Optional[dict] = None
    ):
        """Send notification for team activities"""
        await RealTimeNotificationService.notify_workspace(
            workspace_id=workspace_id,
            notification_type="team_activity",
            title="Team Update",
            message=description,
            data={"activityType": activity_type, **(data or {})},
            exclude_user=actor_id
        )
    
    @staticmethod
    async def notify_ab_test_update(
        workspace_id: str,
        user_id: str,
        test_id: str,
        status: str,
        winner: Optional[dict] = None
    ):
        """Send notification for A/B test updates"""
        title = "A/B Test Update"
        if status == "completed":
            if winner:
                message = f"A/B test complete! Winner: {winner.get('name')} with {winner.get('conversionRate')}% conversion"
            else:
                message = "A/B test completed - no clear winner determined"
        else:
            message = f"A/B test status changed to: {status}"
        
        await RealTimeNotificationService.notify_user(
            user_id=user_id,
            notification_type="ab_test_update",
            title=title,
            message=message,
            data={"testId": test_id, "status": status, "winner": winner},
            workspace_id=workspace_id
        )
