# 🏏 LiveScore

A full-stack live cricket score tracking application built with **FastAPI**, **PostgreSQL**, and **Streamlit** — fully containerized with **Docker**. Inspired by the architecture of the open-source [CricScore](https://github.com) project.

## Features

- Create matches between two teams
- Track live scores with auto status transitions (`SCHEDULED` → `LIVE` → `COMPLETED`)
- Update scores in real time via a simple web UI
- Mark matches as completed (locks further score updates)
- Delete matches
- Auto-refreshing scoreboard (updates every 3 seconds, no manual refresh needed)
- Fully containerized — one command spins up the database, API, and frontend

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI, SQLAlchemy |
| Database | PostgreSQL 16 |
| Frontend | Streamlit |
| Containerization | Docker, Docker Compose |

## Architecture

```
┌─────────────┐      HTTP      ┌─────────────┐      SQL      ┌──────────────┐
│  Streamlit  │ ─────────────▶ │   FastAPI   │ ────────────▶ │  PostgreSQL  │
│  Frontend   │ ◀───────────── │   Backend   │ ◀──────────── │   Database   │
└─────────────┘                └─────────────┘                └──────────────┘
   port 8501                      port 8000                     port 5432
```

Each layer runs in its own Docker container, connected via a shared Docker Compose network.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/matches/` | Create a new match |
| `GET` | `/matches/` | List all matches |
| `GET` | `/matches/{match_id}` | Get a single match |
| `PATCH` | `/matches/{match_id}/score` | Update a match's score |
| `PATCH` | `/matches/{match_id}/complete` | Mark a match as completed |
| `DELETE` | `/matches/{match_id}` | Delete a match |

Interactive API docs available at `/docs` (Swagger UI) once the backend is running.

## Getting Started

### Run with Docker (recommended)

```bash
git clone https://github.com/Ashok1921/livescore.git
cd livescore
docker compose up --build
```

- Frontend: http://localhost:8501
- Backend docs: http://127.0.0.1:8000/docs

### Run locally without Docker

```bash
# Terminal 1 — backend
python -m venv venv
venv\Scripts\Activate.ps1        # or `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload

# Terminal 2 — frontend
venv\Scripts\Activate.ps1
streamlit run streamlit_app.py
```

You'll need a local PostgreSQL instance and a `.env` file with a `DATABASE_URL` connection string.

## Project Structure

```
livescore/
├── app/
│   ├── database.py       # DB connection/session setup
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic request/response schemas
│   └── routers/
│       └── matches.py    # Match API endpoints
├── streamlit_app.py       # Frontend UI
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── requirements.txt
└── PROGRESS.md            # Development log
```

## Roadmap

- [ ] Match filtering/search
- [ ] Ball-by-ball scoring detail
- [ ] User authentication for match creation
- [ ] Deployment to a cloud host

## License

This project is open source and available for learning purposes.
