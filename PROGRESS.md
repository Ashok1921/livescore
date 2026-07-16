
# LiveScore — Progress Log

Project: FastAPI + PostgreSQL + Streamlit full-stack app, inspired by the open-source CricScore project.
Repo: https://github.com/Ashok1921/livescore

---

## Phase 1 (done)

- Set up venv, installed FastAPI, SQLAlchemy, psycopg2, python-dotenv
- PostgreSQL installed locally on Windows (not Docker), running on port 5432
- Built backend structure:
  - `app/database.py` — DB connection/session setup
  - `app/models.py` — SQLAlchemy `Match` model
  - `app/schemas.py` — Pydantic schemas (MatchCreate, MatchResponse, ScoreUpdate)
  - `app/routers/matches.py` — match endpoints
- Endpoints: `POST /matches/` (create), `GET /matches/{id}` (get one)
- Git initialized, pushed to GitHub (commit `99011c7`)

## Phase 2 (done)

- Added `GET /matches/` — list all matches, newest first
- Added match lifecycle logic in `update_score`:
  - Auto-flips status `SCHEDULED -> LIVE` when score is updated
  - Blocks score updates once status is `COMPLETED` (returns 400 error)
- Added `PATCH /matches/{id}/complete` — marks match as `COMPLETED`
- Built `streamlit_app.py` — frontend with:
  - Form to create a new match
  - List of all matches with live status/score
  - Update score + mark completed buttons (hidden once completed)
- Tested full round trip: Postgres <-> FastAPI <-> Streamlit, all working
- Committed and pushed to GitHub (commit `c729517`)

## Notes / decisions made

- Docker was explored but not used for the real project — a separate folder
  (`C:\Users\Ashok\LiveScore`, capital L) had Docker + WSL setup as a learning
  exercise, with no real features built. That folder was deleted on 2026-07-16.
  The real project lives at `C:\Users\Ashok\AVSCODE\livescore` and currently
  uses local (non-Docker) PostgreSQL.
- Decision: finish core features first, containerize with Docker at the end,
  once the app is feature-complete — to avoid debugging code and infra at once.

## Next up (not started yet)

- [ ] Docker setup (Dockerfile + docker-compose.yml) for the real project folder
- [ ] Delete match endpoint
- [ ] Auto-refresh live scores in Streamlit (currently manual button clicks)
- [ ] Resume: add this project as a bullet point with GitHub link once polished

## How to resume a session

Run the app locally with two terminals:

```powershell
# Terminal 1 - backend
cd C:\Users\Ashok\AVSCODE\livescore
venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

# Terminal 2 - frontend
cd C:\Users\Ashok\AVSCODE\livescore
venv\Scripts\Activate.ps1
streamlit run streamlit_app.py
```

Backend docs: http://127.0.0.1:8000/docs
Frontend: http://localhost:8501

To pick up with Claude next time: paste this file's contents, or say
"here's my LiveScore PROGRESS.md" and share what you want to work on next.

# LIST all matches

@router.get("/", response_model=list[schemas.MatchResponse])
def list_matches(db: Session = Depends(get_db)):
    matches = db.query(models.Match).order_by(models.Match.created_at.desc()).all()
    return matches
