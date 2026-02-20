import asyncio
import json
import logging
from typing import Dict, Any, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.agents.nexus.weaver.agent import WeaverAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BridgeServer")

app = FastAPI(title="BRIDGE WebSocket Server")
weaver = WeaverAgent()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for prototype
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    """
    Manages WebSocket connections and broadcasting.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected. Active connections: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        """
        Broadcasts a JSON message to all connected clients.
        """
        payload = json.dumps(message)
        for connection in self.active_connections:
            try:
                await connection.send_text(payload)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                # We might want to disconnect broken connections here
                # but let's leave it to the disconnect handler for now

manager = ConnectionManager()

@app.websocket("/ws/bridge")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for client messages (e.g. pings)
            data = await websocket.receive_text()
            
            # Simple Echo/Ping handling
            try:
                msg = json.loads(data)
                msg_type = msg.get("type")
                
                if msg_type == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                
                elif msg_type == "ingest":
                    # Handle context ingestion request
                    context_type = msg.get("context_type", "unknown")
                    content = msg.get("content", "")
                    
                    # Ingest via Weaver
                    result = await weaver.ingest_context(context_type, content)
                    
                    # Send acknowledgment
                    ack = {
                        "type": "ack",
                        "request_id": msg.get("id"),
                        "status": result.get("status"),
                        "entry_id": result.get("id"),
                        "message": result.get("message")
                    }
                    await websocket.send_text(json.dumps(ack))
                    
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "connections": len(manager.active_connections)}

# Mock method to inject messages from other agents (for testing/prototyping)
@app.post("/api/inject-message")
async def inject_message(message: Dict[str, Any]):
    """
    Internal API to trigger a broadcast from the backend agents.
    """
    await manager.broadcast(message)
    return {"status": "broadcasted"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
