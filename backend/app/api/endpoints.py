from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
import asyncio

from app.services.socket_manager import manager
from app.schemas.room import RoomResponse, AutoCompleteRequest, AutoCompleteResponse
from app.db.base import get_db
from app.db.models import Room

router = APIRouter()


@router.post("/rooms", response_model=RoomResponse)
def create_room(db: Session = Depends(get_db)):
    new_room_id = str(uuid.uuid4())[:8]
    
    new_room = Room(room_id=new_room_id)
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    
    return {"room_id": new_room_id}

@router.post("/autocomplete", response_model=AutoCompleteResponse)
async def autocomplete(payload: AutoCompleteRequest):

    # (Frontend usually handles the delay, but we simulate API latency here slightly)
    await asyncio.sleep(0.5) 
    
    suggestion = ""
    lines = payload.code.split('\n')
    last_line = lines[-1].strip() if lines else ""

    if last_line.startswith("def "):
        suggestion = "\n    # TODO: Implement function logic\n    pass"
    elif last_line.startswith("if "):
        suggestion = "\n    pass"
    elif "print" in last_line:
        suggestion = "('Hello World')"
    else:
        suggestion = " # AI suggestion"
        
    return {"suggestion": suggestion}


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.room_id == room_id).first()
    if not room:
        await websocket.accept()
        print(f"Connection rejected: Room {room_id} not found.")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Room not found")
        return
    
    try:
        # 2. Connect
        await manager.connect(websocket, room_id)
        
        # 3. Listen for messages
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(data, room_id, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
    except json.JSONDecodeError:
        print(f"Error decoding JSON in room {room_id}")