# Real-Time Pair Programming Application
A collaborative code editor that allows two or more users to join a room, edit code in real-time, and receive mock AI autocomplete suggestions.

# Features
* Real-Time Collaboration: Instant code synchronization between users via WebSockets.
* Room Management: Unique room generation and persistent storage.
* AI Autocomplete: Simulated AI suggestions triggered by typing pauses.
* Persistence Strategy:
	* Hot State: Code updates are handled in-memory for millisecond latency.
	* Cold Storage: Data is synced to PostgreSQL on room exit.
	* Periodic Sync: A background task runs every 60 seconds to automatically save active room states to the database, preventing data loss in case of server failure.


 # Tech stack
 * **Backend** : Python, FastAPI, PostgreSQL (with SQLAlchemy ORM), WebSockets, REST API
 * **Frontend** : TypeScript,  React 18 (Vite), Redux Toolkit

## Installation & Setup
### Prerequisites :
* Python 3.9+
* Node.js & npm
* PostgreSQL (optional - defaults to SQLite if not configured)

### Backend Setup

Database Configuration: By default, the app uses SQLite (test.db) for zero-config testing.
To use PostgreSQL, create a .env file in /backend:
```
DATABASE_URL=postgresql://user:password@localhost:5432/pair_programming

```


FastAPI :
```
cd backend
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Server
uvicorn app.main:app --reload
```

The backend will run on http://127.0.0.1:8000

### Frontend Setup
```
cd frontend
npm install
npm run dev
```
The frontend will run on http://localhost:5173

## API Endpoints
| Method | Endpoint            | Description                                   |
|--------|----------------------|-----------------------------------------------|
| POST   | `/rooms`            | Create a new room. Returns `room_id`.         |
| POST   | `/autocomplete`     | Get AI code suggestions.                      |
| WS     | `/ws/{room_id}`     | WebSocket connection for real-time sync.      |


#  Architecture & Design Choices
* Hybrid Persistence Strategy : To balance speed and reliability, a hybrid storage approach is implemented:
	* In-Memory (RAM): All WebSocket keystrokes update a Python dictionary first. This ensures O(1) access time and zero database I/O lag during typing.
	* Periodic Background Sync: A standard asyncio background task runs every 60 seconds to flush dirty RAM state to the Database. This is managed via FastAPI's lifespan event handler.
	* Save-on-Disconnect: When the last user leaves a room, the state is immediately committed to the DB to ensure no data is lost.

* Concurrency : FastAPI's asynchronous nature (async def) allows handling multiple WebSocket connections concurrently without blocking the main thread, essential for a real-time app.
* Cursor Tracking: To prevent cursor jumping during collaborative edits, the frontend tracks the local cursor position relative to text changes and calculates a new position using a diff-based logic before re-rendering.


## Future Improvements
We can add following for more robust and scalable app:
* Containerization with Docker
* Add more process workers to utilize multi-core CPUs.
* Redis Layer: Instead of in-memory Python dictionaries, using Redis would allow the backend to scale across multiple server workers (horizontal scaling).
* Authentication: Adding JWT auth to restrict room access.
* Use CRDTs (Conflict-free Replicated Data Types) : Implement libraries like Yjs or Automerge to handle conflict resolution mathematically. This would also optimize network performance by broadcasting small deltas (operations) instead of the entire document snapshot.