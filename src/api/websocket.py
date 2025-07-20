"""
WebSocket endpoints for real-time progress tracking
"""

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from typing import Dict, List, Any
import json
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, analysis_id: str = None):
        """Connect a WebSocket client"""
        await websocket.accept()
        
        # Track by user
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(websocket)
        
        # Track by analysis if specified
        if analysis_id:
            if analysis_id not in self.active_connections:
                self.active_connections[analysis_id] = []
            self.active_connections[analysis_id].append(websocket)
        
        logger.info(f"WebSocket connected: user={user_id}, analysis={analysis_id}")
    
    def disconnect(self, websocket: WebSocket, user_id: str, analysis_id: str = None):
        """Disconnect a WebSocket client"""
        # Remove from user connections
        if user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # Remove from analysis connections
        if analysis_id and analysis_id in self.active_connections:
            if websocket in self.active_connections[analysis_id]:
                self.active_connections[analysis_id].remove(websocket)
            if not self.active_connections[analysis_id]:
                del self.active_connections[analysis_id]
        
        logger.info(f"WebSocket disconnected: user={user_id}, analysis={analysis_id}")
    
    async def send_personal_message(self, websocket: WebSocket, message: dict):
        """Send message to specific WebSocket"""
        if websocket.client_state == WebSocketState.CONNECTED:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send WebSocket message: {e}")
    
    async def broadcast_to_analysis(self, analysis_id: str, message: dict):
        """Broadcast message to all clients following an analysis"""
        if analysis_id in self.active_connections:
            disconnected = []
            
            for connection in self.active_connections[analysis_id]:
                try:
                    if connection.client_state == WebSocketState.CONNECTED:
                        await connection.send_text(json.dumps(message))
                    else:
                        disconnected.append(connection)
                except Exception as e:
                    logger.error(f"Failed to broadcast to analysis {analysis_id}: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected clients
            for conn in disconnected:
                self.active_connections[analysis_id].remove(conn)
    
    async def broadcast_to_user(self, user_id: str, message: dict):
        """Broadcast message to all connections for a user"""
        if user_id in self.user_connections:
            disconnected = []
            
            for connection in self.user_connections[user_id]:
                try:
                    if connection.client_state == WebSocketState.CONNECTED:
                        await connection.send_text(json.dumps(message))
                    else:
                        disconnected.append(connection)
                except Exception as e:
                    logger.error(f"Failed to broadcast to user {user_id}: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected clients
            for conn in disconnected:
                self.user_connections[user_id].remove(conn)
    
    async def broadcast_system_message(self, message: dict):
        """Broadcast system message to all connected users"""
        all_connections = []
        
        for user_connections in self.user_connections.values():
            all_connections.extend(user_connections)
        
        for connection in all_connections:
            try:
                if connection.client_state == WebSocketState.CONNECTED:
                    await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to broadcast system message: {e}")

# Global connection manager
manager = ConnectionManager()

class ProgressTracker:
    """Real-time progress tracking"""
    
    def __init__(self):
        self.analysis_progress = {}
    
    async def update_progress(self, analysis_id: str, progress: float, message: str, 
                            details: Dict[str, Any] = None):
        """Update analysis progress"""
        progress_data = {
            "analysis_id": analysis_id,
            "progress": progress,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        # Store progress
        self.analysis_progress[analysis_id] = progress_data
        
        # Broadcast to WebSocket clients
        await manager.broadcast_to_analysis(analysis_id, {
            "type": "progress_update",
            "data": progress_data
        })
    
    async def complete_analysis(self, analysis_id: str, success: bool, 
                              results: Dict[str, Any] = None, error: str = None):
        """Mark analysis as complete"""
        completion_data = {
            "analysis_id": analysis_id,
            "success": success,
            "completed_at": datetime.now().isoformat(),
            "results": results,
            "error": error
        }
        
        # Broadcast completion
        await manager.broadcast_to_analysis(analysis_id, {
            "type": "analysis_complete",
            "data": completion_data
        })
        
        # Clean up progress tracking
        if analysis_id in self.analysis_progress:
            del self.analysis_progress[analysis_id]
    
    def get_progress(self, analysis_id: str) -> Dict[str, Any]:
        """Get current progress for analysis"""
        return self.analysis_progress.get(analysis_id)

# Global progress tracker
progress_tracker = ProgressTracker()

async def websocket_endpoint(websocket: WebSocket, user_id: str, analysis_id: str = None):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket, user_id, analysis_id)
    
    try:
        # Send initial connection confirmation
        await manager.send_personal_message(websocket, {
            "type": "connection_established",
            "user_id": user_id,
            "analysis_id": analysis_id,
            "timestamp": datetime.now().isoformat()
        })
        
        # Send current progress if analysis is specified
        if analysis_id:
            current_progress = progress_tracker.get_progress(analysis_id)
            if current_progress:
                await manager.send_personal_message(websocket, {
                    "type": "current_progress",
                    "data": current_progress
                })
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    await manager.send_personal_message(websocket, {
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                elif message.get("type") == "subscribe_analysis":
                    # Subscribe to different analysis
                    new_analysis_id = message.get("analysis_id")
                    if new_analysis_id:
                        if new_analysis_id not in manager.active_connections:
                            manager.active_connections[new_analysis_id] = []
                        manager.active_connections[new_analysis_id].append(websocket)
                        
                        # Send current progress if available
                        current_progress = progress_tracker.get_progress(new_analysis_id)
                        if current_progress:
                            await manager.send_personal_message(websocket, {
                                "type": "current_progress",
                                "data": current_progress
                            })
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
    
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, user_id, analysis_id)

async def send_notification(user_id: str, notification_type: str, message: str, 
                          data: Dict[str, Any] = None):
    """Send notification to user"""
    notification = {
        "type": "notification",
        "notification_type": notification_type,
        "message": message,
        "data": data or {},
        "timestamp": datetime.now().isoformat()
    }
    
    await manager.broadcast_to_user(user_id, notification)

async def send_system_alert(alert_type: str, message: str, data: Dict[str, Any] = None):
    """Send system-wide alert"""
    alert = {
        "type": "system_alert",
        "alert_type": alert_type,
        "message": message,
        "data": data or {},
        "timestamp": datetime.now().isoformat()
    }
    
    await manager.broadcast_system_message(alert)