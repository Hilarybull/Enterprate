"""WebSocket Manager for Real-time Notifications"""
import json
import asyncio
from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time notifications"""
    
    def __init__(self):
        # user_id -> set of websocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # workspace_id -> set of user_ids
        self.workspace_users: Dict[str, Set[str]] = {}
        # websocket -> (user_id, workspace_id)
        self.connection_info: Dict[WebSocket, tuple] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, workspace_id: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        # Add to user connections
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        
        # Add to workspace users
        if workspace_id not in self.workspace_users:
            self.workspace_users[workspace_id] = set()
        self.workspace_users[workspace_id].add(user_id)
        
        # Store connection info
        self.connection_info[websocket] = (user_id, workspace_id)
        
        logger.info(f"WebSocket connected: user={user_id}, workspace={workspace_id}")
        
        # Send connection confirmation
        await self.send_personal_message({
            "type": "connected",
            "message": "Connected to notification service",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.connection_info:
            user_id, workspace_id = self.connection_info[websocket]
            
            # Remove from user connections
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
                    # Remove from workspace users if no more connections
                    if workspace_id in self.workspace_users:
                        self.workspace_users[workspace_id].discard(user_id)
                        if not self.workspace_users[workspace_id]:
                            del self.workspace_users[workspace_id]
            
            del self.connection_info[websocket]
            logger.info(f"WebSocket disconnected: user={user_id}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send a message to all connections of a specific user"""
        if user_id in self.active_connections:
            disconnected = []
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_json(message)
                except Exception:
                    disconnected.append(websocket)
            
            # Clean up disconnected sockets
            for ws in disconnected:
                self.disconnect(ws)
    
    async def broadcast_to_workspace(self, workspace_id: str, message: dict, exclude_user: Optional[str] = None):
        """Broadcast a message to all users in a workspace"""
        if workspace_id in self.workspace_users:
            for user_id in self.workspace_users[workspace_id]:
                if user_id != exclude_user:
                    await self.send_to_user(user_id, message)
    
    async def broadcast_all(self, message: dict):
        """Broadcast a message to all connected users"""
        for user_id in list(self.active_connections.keys()):
            await self.send_to_user(user_id, message)
    
    def get_online_users(self, workspace_id: str) -> Set[str]:
        """Get list of online users in a workspace"""
        return self.workspace_users.get(workspace_id, set())
    
    def is_user_online(self, user_id: str) -> bool:
        """Check if a user is currently connected"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0


# Global connection manager instance
manager = ConnectionManager()


class NotificationBroadcaster:
    """Helper class to broadcast notifications via WebSocket"""
    
    @staticmethod
    async def notify_new_lead(workspace_id: str, lead: dict):
        """Broadcast new lead notification"""
        await manager.broadcast_to_workspace(workspace_id, {
            "type": "notification",
            "category": "lead",
            "action": "new_lead",
            "data": {
                "leadId": lead.get("id"),
                "name": lead.get("name"),
                "email": lead.get("email"),
                "source": lead.get("source")
            },
            "message": f"New lead captured: {lead.get('name')}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    @staticmethod
    async def notify_website_deployed(workspace_id: str, user_id: str, site_url: str, site_name: str):
        """Broadcast website deployment notification"""
        await manager.broadcast_to_workspace(workspace_id, {
            "type": "notification",
            "category": "website",
            "action": "deployed",
            "data": {
                "siteUrl": site_url,
                "siteName": site_name
            },
            "message": f"Website '{site_name}' deployed successfully!",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    @staticmethod
    async def notify_ab_test_winner(workspace_id: str, test_name: str, winner_name: str):
        """Broadcast A/B test winner notification"""
        await manager.broadcast_to_workspace(workspace_id, {
            "type": "notification",
            "category": "ab_test",
            "action": "winner",
            "data": {
                "testName": test_name,
                "winnerName": winner_name
            },
            "message": f"A/B Test '{test_name}' has a winner: {winner_name}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    @staticmethod
    async def notify_automation_executed(workspace_id: str, rule_name: str, action_type: str, success: bool):
        """Broadcast automation execution notification"""
        status = "completed" if success else "failed"
        await manager.broadcast_to_workspace(workspace_id, {
            "type": "notification",
            "category": "automation",
            "action": "executed",
            "data": {
                "ruleName": rule_name,
                "actionType": action_type,
                "success": success
            },
            "message": f"Automation '{rule_name}' {status}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    @staticmethod
    async def notify_team_activity(workspace_id: str, user_name: str, activity: str, exclude_user: Optional[str] = None):
        """Broadcast team activity notification"""
        await manager.broadcast_to_workspace(workspace_id, {
            "type": "notification",
            "category": "team",
            "action": "activity",
            "data": {
                "userName": user_name,
                "activity": activity
            },
            "message": f"{user_name} {activity}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, exclude_user=exclude_user)
    
    @staticmethod
    async def notify_scheduled_action(workspace_id: str, action_type: str, platform: str):
        """Broadcast scheduled action execution notification"""
        await manager.broadcast_to_workspace(workspace_id, {
            "type": "notification",
            "category": "scheduling",
            "action": "executed",
            "data": {
                "actionType": action_type,
                "platform": platform
            },
            "message": f"Scheduled {action_type} posted to {platform}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
