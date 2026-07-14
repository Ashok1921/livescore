from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


# Shape of data required when CREATING a match (client sends this)
class MatchCreate(BaseModel):
    team_a: str
    team_b: str


# Shape of data required when UPDATING a score (client sends this)
class ScoreUpdate(BaseModel):
    score_a: int
    score_b: int


# Shape of data returned back to the client (API response)
class MatchResponse(BaseModel):
    id: UUID
    team_a: str
    team_b: str
    status: str
    score_a: int
    score_b: int
    created_at: datetime

    class Config:
        from_attributes = True  # allows Pydantic to read data straight from SQLAlchemy objects