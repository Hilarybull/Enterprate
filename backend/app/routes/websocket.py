"""WebSocket routes for real-time notifications"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.services.websocket_manager import manager
from app.core.security import decode_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(...),
    workspace_id: str = Query(...)
):
    """
    WebSocket endpoint for real-time notifications.
    
    Connect with: ws://host/api/ws/notifications?token=<jwt>&workspace_id=<workspace_id>
    
    Message types received:
    - connected: Connection confirmed
    - notification: Real-time notification
    - ping/pong: Keep-alive
    """
    # Verify token
    try:
        payload = decode_token(token)
        user_id = payload.get("user_id") or payload.get("sub")
        if not user_id:
            await websocket.close(code=4001, reason="Invalid token")
            return
    except Exception as e:
        logger.error(f"WebSocket auth failed: {e}")
        await websocket.close(code=4001, reason="Authentication failed")
        return
    
    # Connect
    await manager.connect(websocket, user_id, workspace_id)
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_json()
            
            # Handle different message types
            if data.get("type") == "ping":
                await manager.send_personal_message({"type": "pong"}, websocket)
            elif data.get("type") == "subscribe":
                # Future: handle topic subscriptions
                pass
            elif data.get("type") == "mark_read":
                # Mark notification as read
                notification_id = data.get("notification_id")
                if notification_id:
                    from app.core.database import get_db
                    db = get_db()
                    await db.notifications.update_one(
                        {"id": notification_id, "user_id": user_id},
                        {"$set": {"read": True}}
                    )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.get("/ws/status")
async def websocket_status():
    """Get WebSocket service status"""
    total_connections = sum(len(conns) for conns in manager.active_connections.values())
    return {
        "status": "online",
        "total_connections": total_connections,
        "active_users": len(manager.active_connections),
        "active_workspaces": len(manager.workspace_users)
    }
