from fastapi import FastAPI

from app.database import engine, Base
from app.routers import matches, auth
from app.database import SessionLocal
from app.auth import seed_admin_user

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