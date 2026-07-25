from fastapi import FastAPI

from app.database import engine, Base
from app.routers import matches, auth
from app.database import SessionLocal
from app.auth import seed_admin_user

from fastapi import WebSocket, WebSocketDisconnect
from app.ws_manager import manager



# Creates all tables defined in models.py (if they don't already exist)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LiveScore API")

# Wire in the matches endpoints
app.include_router(matches.router)

# Wire in the auth endpoints
app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "LiveScore API is running"}


@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        seed_admin_user(db)
    finally:
        db.close()
        
@app.websocket("/ws/matches")
async def websocket_matches(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We don't expect clients to send anything meaningful,
            # but we need to keep the connection alive by listening.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)        