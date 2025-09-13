"""
WebSocket Connection Manager for AI Excel Interviewer
Handles real-time communication between frontend and backend
"""

from fastapi import WebSocket
from typing import Dict, List
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for interview sessions"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_connections: Dict[str, str] = {}  # session_id -> connection_id
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Register a new WebSocket connection"""
        # WebSocket is already accepted in the endpoint
        connection_id = id(websocket)
        
        self.active_connections[connection_id] = websocket
        self.session_connections[session_id] = connection_id
        
        logger.info(f"WebSocket connected: {connection_id} for session {session_id}")
    
    def disconnect(self, session_id: str):
        """Disconnect a WebSocket connection"""
        if session_id in self.session_connections:
            connection_id = self.session_connections[session_id]
            
            if connection_id in self.active_connections:
                del self.active_connections[connection_id]
            
            del self.session_connections[session_id]
            
            logger.info(f"WebSocket disconnected: {connection_id} for session {session_id}")
    
    async def send_personal_message(self, session_id: str, message: str):
        """Send a message to a specific session"""
        if session_id in self.session_connections:
            connection_id = self.session_connections[session_id]
            
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                
                try:
                    await websocket.send_text(message)
                    logger.debug(f"Message sent to session {session_id}")
                except Exception as e:
                    logger.error(f"Error sending message to session {session_id}: {str(e)}")
                    # Clean up broken connection
                    self.disconnect(session_id)
            else:
                logger.warning(f"No active connection found for session {session_id}")
        else:
            logger.warning(f"No connection found for session {session_id}")
    
    async def broadcast_message(self, message: str):
        """Broadcast a message to all connected clients"""
        disconnected_sessions = []
        
        for session_id, connection_id in self.session_connections.items():
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to session {session_id}: {str(e)}")
                    disconnected_sessions.append(session_id)
        
        # Clean up disconnected sessions
        for session_id in disconnected_sessions:
            self.disconnect(session_id)
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return list(self.session_connections.keys())
    
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return len(self.active_connections)
