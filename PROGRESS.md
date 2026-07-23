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

## Phase 3 — Dockerization (done)

- Made code Docker-ready:
  - `app/database.py` was already reading `DATABASE_URL` from env — no change needed
  - `streamlit_app.py` updated: `API_URL` now reads from `BACKEND_URL` env var
    (`os.getenv("BACKEND_URL", "http://127.0.0.1:8000")`) instead of a hardcoded
    `localhost` — required so the frontend container can reach the backend
    container by service name
- Generated `requirements.txt` via `pip freeze`
- Created `Dockerfile.backend` — builds FastAPI image, runs uvicorn on `0.0.0.0:8000`
- Created `Dockerfile.frontend` — builds Streamlit image, runs on `0.0.0.0:8501`
- Created `docker-compose.yml` with 3 services:
  - `db` — Postgres 16, with healthcheck; host port mapped to **5433** (not 5432)
    to avoid clashing with the native Windows Postgres install; data persisted
    via a named volume (`pgdata`)
  - `backend` — builds from `Dockerfile.backend`, waits for `db` to be healthy,
    connects via `DATABASE_URL=postgresql://livescore_user:livescore_pass@db:5432/livescore_db`
  - `frontend` — builds from `Dockerfile.frontend`, waits for `backend`,
    connects via `BACKEND_URL=http://backend:8000`
- Ran `docker compose up --build` successfully — all 3 containers
  (`db-1`, `backend-1`, `frontend-1`) came up healthy/running
- Verified both UIs work identically to the non-Docker version:
  - Backend docs: http://127.0.0.1:8000/docs
  - Frontend: http://localhost:8501
- Note: code changes require a rebuild (`docker compose up --build`) to take
  effect — no live-reload volume mount is set up yet (optional future step:
  mount `./streamlit_app.py` and `./app` into the containers for instant reload)

## Phase 4 — Delete match endpoint (done)

- Added `DELETE /matches/{match_id}` in `app/routers/matches.py`
  - Important: `match_id` must be typed as `UUID` (not `int`) — the `Match.id`
    column is a `UUID` primary key, so typing it as `int` causes a
    422 Unprocessable Entity error
  - Returns `404` if the match doesn't exist, otherwise deletes and returns `204`
- Added matching frontend support in `streamlit_app.py`:
  - `delete_match(match_id)` helper function (sends the DELETE request)
  - A "🗑️ Delete Match" button shown for **every** match card (not just
    completed ones — placed outside/after the status if/else block)
  - On success (`204`), shows a success message and calls `st.rerun()`
- Tested and confirmed working both via Swagger UI (`/docs`) and the
  Streamlit app — deleting a match removes it from the list immediately

## Phase 5 — Auto-refresh live scores (done)

- Added `streamlit-autorefresh` to `requirements.txt`
- Updated `streamlit_app.py`:
  - Added `from streamlit_autorefresh import st_autorefresh`
  - Added `st_autorefresh(interval=3000, key="score_autorefresh")` right
    after `st.title("🏏 LiveScore")` — triggers a full script rerun every
    3 seconds, so `get_matches()` is called automatically without any
    manual refresh or button click
- Rebuilt with `docker compose up --build` (new package needed installing)
- Confirmed working via backend logs — repeated automatic
  `GET /matches/ HTTP/1.1 200 OK` requests appearing every ~3 seconds
  on their own

## Notes / decisions made

- Docker was explored but not used for the real project — a separate folder
  (`C:\Users\Ashok\LiveScore`, capital L) had Docker + WSL setup as a learning
  exercise, with no real features built. That folder was deleted on 2026-07-16.
  The real project lives at `C:\Users\Ashok\AVSCODE\livescore`.
- Decision: finish core features first, containerize with Docker at the end,
  once the app is feature-complete — to avoid debugging code and infra at once.
  (Done — see Phase 3.)

## Next up (not started)

- [ ] Commit and push the auto-refresh changes:
  `git add . && git commit -m "Add 3-second auto-refresh to Streamlit frontend" && git push`
- [ ] Resume: add this project as a bullet point with GitHub link, once polished
- [ ] Optional/future: live-reload volume mounts for faster dev loop (skip
  rebuilds when only `streamlit_app.py` or `app/` changes)

## Automated Testing

- Added pytest test suite (tests/conftest.py, tests/test_matches.py)
- Uses a separate test Postgres database (livescore_test) for full isolation from real data
- 7 tests covering: create match, get match, get-not-found (404), list matches,
  score update moving status to LIVE, blocking score updates after COMPLETED
  (data integrity rule), and delete match
- All tests passing
- pytest.ini added with `pythonpath = .` to resolve app imports correctly

## Cloud Deployment (Render)

- Deployed full stack to Render's free tier (Singapore region)
- **Postgres database**: livescore-db (managed, free tier — expires ~Aug 20, 2026
  unless upgraded to a paid plan)
- **Backend**: livescore-backend (FastAPI, Dockerfile.backend)
  → https://livescore-backend-z0x4.onrender.com
- **Frontend**: livescore-frontend (Streamlit, Dockerfile.frontend)
  → https://livescore-frontend-ziwp.onrender.com
- Confirmed working end-to-end: create, live score update, mark completed, delete
- Note: free tier instances spin down after inactivity (~50s wake-up delay on first request)

## Authentication (Stage 1 — Users table + password hashing) ✅ Complete

**Date:** 2026-07-22

**Goal:** Single-admin-user authentication foundation, designed so multi-user/admin roles can be added later without a rewrite.

**What was built:**

- `User` model added in `app/models.py` (id: UUID, username, hashed_password, created_at)
- `app/auth.py` created with:
  - `hash_password()` / `verify_password()` using `passlib` + `bcrypt`
  - `seed_admin_user(db)` — auto-creates one admin user on startup from `ADMIN_USERNAME` / `ADMIN_PASSWORD` env vars, if the `users` table is empty
- Startup hook wired in `app/main.py` (`@app.on_event("startup")`) to call `seed_admin_user()`
- `.env` updated with `ADMIN_USERNAME` / `ADMIN_PASSWORD`
- `docker-compose.yml` updated to pass those two env vars into the `backend` service (`${ADMIN_USERNAME}` / `${ADMIN_PASSWORD}` syntax) — **critical**: Compose does NOT auto-forward local `.env` into containers unless explicitly declared here
- `requirements.txt`: added `passlib[bcrypt]`, `python-jose[cryptography]`, `python-multipart`, and pinned `bcrypt==4.0.1` (newer bcrypt versions break passlib's version-detection, causing a "password cannot be longer than 72 bytes" false error)
- `Dockerfile.backend`: added `ENV PYTHONUNBUFFERED=1` so `print()` output shows up in `docker compose logs` (Python buffers stdout by default when not attached to a real terminal)

**Bugs hit + fixed along the way (for reference if they recur):**

1. `ModuleNotFoundError: No module named 'database'` — `main.py` had inconsistent import style; some imports used `app.database`, others used bare `database`. Fixed by making all intra-package imports consistently use the `app.` prefix.
2. `auth.py` was accidentally created at the project root instead of inside `app/` — moved into `app/` to match `main.py`, `database.py`, `models.py`.
3. bcrypt/passlib version incompatibility (see above) — fixed by pinning `bcrypt==4.0.1`.
4. `docker compose up` (without `-d`) runs in the foreground — closing/losing that terminal session stops all containers. Switched to `docker compose up --build -d` (detached) for day-to-day work, `docker compose logs backend` to check logs afterward.

**Verified:** Queried `users` table directly via `docker exec -it livescore-db-1 psql -U livescore_user -d livescore_db -c "SELECT * FROM users;"` — confirmed one row (`ashok`) with a properly bcrypt-hashed password (`$2b$12$...`), not plaintext.

**Next (Stage 2):** `/auth/login` endpoint — JWT token generation/verification, protecting match create/update/delete endpoints while keeping list/get public



## Stage 2: Authentication (JWT) — COMPLETE

- Added JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES as env vars (docker-compose.yml + .env)
- Added python-jose[cryptography]==3.3.0 to requirements.txt
- app/auth.py: added create_access_token() / decode_access_token() helpers
- app/routers/auth.py (new): POST /auth/login — verifies credentials, returns JWT access_token
- Registered auth.router in main.py alongside matches.router
- app/auth.py: added get_current_user() dependency using HTTPBearer
  (switched from OAuth2PasswordBearer — its form-encoded flow didn't match
  our JSON-based /auth/login and caused 422 errors in Swagger's Authorize dialog)
- app/routers/matches.py: protected write endpoints with
  current_user: User = Depends(get_current_user):
  - POST   /matches/
  - PATCH  /matches/{match_id}/score
  - PATCH  /matches/{match_id}/complete
  - DELETE /matches/{match_id}
    Left public (no auth required):
  - GET /matches/
  - GET /matches/{match_id}
- Verified end-to-end via Swagger UI (/docs):
  - Login returns valid token
  - Authorize + paste token → protected POST succeeds (200)
  - Logout → same POST returns 401 (confirms protection is enforced, not decorative)
- Committed and pushed to GitHub: commit 7289543
  "Add JWT authentication: login endpoint and protected write routes"

## Next: Stage 3 — Streamlit frontend integration

- Add login form + session state to store JWT
- Attach Authorization: Bearer <token></token> header on create/update/delete calls
- Leave list/view calls unauthenticated




xt up

- Authentication (JWT)
- WebSockets (deferred — Streamlit's rerun model makes this a bigger architectural change than a simple swap)
- 

## How to resume a session

Run the app with Docker (recommended, matches current setup):

```powershell
cd C:\Users\Ashok\AVSCODE\livescore
docker compose up --build
```

- Backend docs: http://127.0.0.1:8000/docs
- Frontend: http://localhost:8501

Or run natively (two terminals, without Docker):

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

To pick up with Claude next time: paste this file's contents, or say
"here's my LiveScore PROGRESS.md" and share what you want to work on next.
