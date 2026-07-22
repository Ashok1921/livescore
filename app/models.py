from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from sqlalchemy import Column, String, DateTime
from datetime import datetime, timezone
import uuid
from sqlalchemy.dialects.postgresql import UUID


from app.database import Base


class Match(Base):
    __tablename__ = "matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_a = Column(String(100), nullable=False)
    team_b = Column(String(100), nullable=False)
    status = Column(String(25), nullable=False, default="SCHEDULED")
    score_a = Column(Integer, default=0)
    score_b = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))    