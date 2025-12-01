from typing import Dict, List
from fastapi import WebSocket
from sqlalchemy.orm import Session
from app.db.models import Room


# For saving room state to db, we will save code when last disconnect happens (also fetch the room code when room data is not present in memory)
# wanted some periodic function to save data to db everything 30 or 60 sec. Will look into this later
class ConnectionManager:
    def __init__(self):
        # Store active connections: room_id -> List of WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Store current code state: room_id -> str (code)
        self.room_state: Dict[str, Any] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str, db : Session):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []

            # check if we have this room in db
            db_room = db.query(Room).filter(Room.room_id == room_id).first()
            saved_code = db_room.code if db_room and db_room.code else ""

            self.room_state[room_id] = {"code": saved_code, "cursor": 0}

        self.active_connections[room_id].append(websocket)
        
        await websocket.send_json({
            "type": "INIT",
            "payload": self.room_state[room_id]
        })

    def disconnect(self, websocket: WebSocket, room_id: str, db : Session):
        if room_id in self.active_connections:
            if websocket in self.active_connections[room_id]:
                self.active_connections[room_id].remove(websocket)

            if not self.active_connections[room_id]:
                # save to db
                current_code = self.room_state[room_id].get("code", "")
                db_room = db.query(Room).filter(Room.room_id == room_id).first()
                if db_room:
                    db_room.code = current_code
                    db.commit() 

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