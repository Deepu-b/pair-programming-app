from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  
from app.api import endpoints
from app.db.base import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pair Programming API")

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