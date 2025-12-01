from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  
from app.api import endpoints
from app.db.base import Base, engine
import asyncio
from contextlib import asynccontextmanager

from app.db.base import Base, engine, SessionLocal
from app.services.socket_manager import manager
from app.db.models import Room


async def periodic_db_sync():
    """
    Runs every 60 seconds.
    Iterates through active rooms in memory and flushes state to Postgres.
    """

    while True:
        await asyncio.sleep(60)

        db = SessionLocal()
        try:
            active_rooms = list(manager.room_state.keys())
            print(active_rooms)
            for room_id in active_rooms:
                room_data = manager.room_state.get(room_id)
                if not room_data: 
                    continue
                db_room = db.query(Room).filter(Room.room_id == room_id).first()
                if db_room:
                    db_room.code = current_code
                
            db.commit()
        except Exception as e:
            db.rollback()
        finally:
            db.close()

@asynccontextmanager
async def lifespan(app :FastAPI):
    Base.metadata.create_all(bind=engine)
    sync_task = asyncio.create_task(periodic_db_sync())

    yield

    sync_task.cancel()
    try:
        await sync_task
    except asyncio.CancelledError:
        pass

app = FastAPI(title="Pair Programming API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router)

@app.get("/")
def read_root():
    return {"message": "Server is running"}