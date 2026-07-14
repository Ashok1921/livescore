from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Load variables from .env into environment
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# The engine manages the actual connection pool to Postgres
engine = create_engine(DATABASE_URL)

# Each request will get its own "session" (a working conversation with the DB)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that our table models will inherit from
Base = declarative_base()

# Dependency function FastAPI will use to get a DB session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()