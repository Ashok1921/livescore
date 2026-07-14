from fastapi import FastAPI

from app.database import engine, Base
from app.routers import matches

# Creates all tables defined in models.py (if they don't already exist)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LiveScore API")

# Wire in the matches endpoints
app.include_router(matches.router)


@app.get("/")
def root():
    return {"message": "LiveScore API is running"}