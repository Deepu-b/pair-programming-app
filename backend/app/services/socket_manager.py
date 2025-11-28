from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # Store active connections: room_id -> List of WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Store current code state: room_id -> str (code)
        self.room_state: Dict[str, Any] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
            self.room_state[room_id] = {"code": "", "cursor": 0}
        self.active_connections[room_id].append(websocket)
        
        # Send current code state to the newly connected user
        await websocket.send_json({
            "type": "INIT",
            "payload": self.room_state[room_id]
        })

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
                if room_id in self.room_state:
                    del self.room_state[room_id]

    async def broadcast(self, data: dict, room_id: str, sender: WebSocket):        
        """
        Expects data to be a dictionary like: 
        { "type": "CODE_UPDATE", "payload": { "code": "...", "cursor": 12 } }
        """

        msg_type = data.get("type")
        payload = data.get("payload")

        if msg_type == "CODE_UPDATE" and payload is not None:
            self.room_state[room_id] = data["payload"]

        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                if connection != sender:
                    await connection.send_json(data)

manager = ConnectionManager()