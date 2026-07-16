from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/matches", tags=["matches"])

# LIST all matches
@router.get("/", response_model=list[schemas.MatchResponse])
def list_matches(db: Session = Depends(get_db)):
    matches = db.query(models.Match).order_by(models.Match.created_at.desc()).all()
    return matches


# CREATE a new match
@router.post("/", response_model=schemas.MatchResponse)
def create_match(match: schemas.MatchCreate, db: Session = Depends(get_db)):
    new_match = models.Match(team_a=match.team_a, team_b=match.team_b)
    db.add(new_match)
    db.commit()
    db.refresh(new_match)  # reloads it from DB so we get the generated id/created_at
    return new_match


# GET a single match by id
@router.get("/{match_id}", response_model=schemas.MatchResponse)
def get_match(match_id: UUID, db: Session = Depends(get_db)):
    match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match


# UPDATE a match's score
@router.patch("/{match_id}/score", response_model=schemas.MatchResponse)
def update_score(match_id: UUID, score: schemas.ScoreUpdate, db: Session = Depends(get_db)):
    match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    if match.status == "COMPLETED":
        raise HTTPException(status_code=400, detail="Cannot update score of a completed match")
    match.score_a = score.score_a
    match.score_b = score.score_b
    if match.status == "SCHEDULED":
        match.status = "LIVE"
    db.commit()
    db.refresh(match)
    return match


# MARK a match as completed
@router.patch("/{match_id}/complete", response_model=schemas.MatchResponse)
def complete_match(match_id: UUID, db: Session = Depends(get_db)):
    match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    match.status = "COMPLETED"
    db.commit()
    db.refresh(match)
    return match