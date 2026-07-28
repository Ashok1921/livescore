# 🏏 LiveScore

A full-stack, production-style live match scoring application — built end-to-end with a FastAPI backend, PostgreSQL database, and a Streamlit frontend with real-time updates over WebSockets.

**🔗 Live app:** https://livescore-frontend-ziwp.onrender.com
**⚙️ API:** https://livescore-backend-z0x4.onrender.com

> Note: hosted on Render's free tier, so the backend may take ~30–50 seconds to spin up on first load after a period of inactivity.

---

## Features

- **Create, update, and complete matches** — track two teams and their live scores
- **Real-time sync across clients** — score updates push instantly to every open browser tab via a custom WebSocket-based Streamlit component (no polling)
- **JWT authentication** — admin login required to create/update/complete/delete matches; anyone can view live scores without logging in
- **Match lifecycle rules** — scores lock automatically once a match is marked completed
- **Automated test suite** — pytest coverage for all endpoints, including auth-protected routes and unauthenticated-access rejection
- **Containerized & cloud-deployed** — Docker Compose for local development, deployed as separate services on Render

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy |
| Database | PostgreSQL |
| Frontend | Streamlit |
| Real-time | Custom Streamlit component using the WebSocket API + Streamlit's component postMessage protocol |
| Auth | JWT (python-jose) + bcrypt password hashing |
| Testing | pytest |
| Infra | Docker, Docker Compose, Render (cloud deployment) |

---

## Architecture

```
┌─────────────┐         HTTP (REST)         ┌──────────────┐
│  Streamlit  │ ──────────────────────────▶ │   FastAPI    │
│  Frontend   │ ◀────────────────────────── │   Backend    │
│             │                              │              │
│             │        WebSocket (wss)       │              │
│             │ ◀──────────────────────────▶ │              │
└─────────────┘                              └──────┬───────┘
                                                     │
                                                     ▼
                                              ┌──────────────┐
                                              │  PostgreSQL  │
                                              └──────────────┘
```

- The frontend calls the backend over standard REST for reads/writes.
- On any match action (create/update/complete/delete), the backend broadcasts the change to all connected clients over a WebSocket, and each Streamlit client triggers a live UI refresh — without a manual reload or fixed polling interval.

---

## Running Locally

**Prerequisites:** Docker and Docker Compose installed.

```bash
git clone https://github.com/Ashok1921/livescore.git
cd livescore
docker compose up --build
```

- Frontend: http://localhost:8501
- Backend API docs (Swagger): http://localhost:8000/docs

Set the following environment variables (see `docker-compose.yml`):
- `DATABASE_URL`
- `ADMIN_USERNAME`, `ADMIN_PASSWORD` — seeds an admin user on first startup
- `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_EXPIRE_MINUTES`

## Running Tests

```bash
pytest
```

---

## What This Project Demonstrates

This was built as a hands-on learning project to go deep on a full production-style workflow rather than just a CRUD demo:

- REST API design with proper resource lifecycle handling
- Real-time communication over WebSockets, including handling browser sandboxing constraints in Streamlit and building a custom component from scratch
- JWT-based authentication with protected vs public routes
- Automated testing with authenticated and unauthenticated test cases
- Dockerizing a multi-service app (backend, frontend, database)
- Debugging and resolving real cloud-deployment issues: environment-specific networking (Docker-internal hostnames vs public URLs), missing production environment variables, and dependency version conflicts (bcrypt/passlib)

---

## Author

Ashok — Generative AI & Agentic AI Developer
