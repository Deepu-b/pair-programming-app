from pydantic import BaseModel
from typing import Optional

class RoomCreate(BaseModel):
    pass

class RoomResponse(BaseModel):
    room_id: str

class AutoCompleteRequest(BaseModel):
    code: str
    cursorPosition: int
    language: str = "python"

class AutoCompleteResponse(BaseModel):
    suggestion: str