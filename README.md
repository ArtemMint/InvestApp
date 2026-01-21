# WebStore

Minimal FastAPI WebStore application.

## Docker Compose

This repository includes a `docker-compose.yml` which brings up three services:

- `backend` — your FastAPI app built from the provided `Dockerfile` (exposes port 8000)
- `frontend` — a minimal static frontend served by Nginx (exposes port 8080)
- `postgres` — Postgres 15 with a persistent volume (exposes port 5432)

Quick start:

1. Copy the example environment file and adjust secrets if needed:

```bash
cp .env.example .env
```

2. Build and start the stack:

```bash
docker compose up --build
```

3. Open the frontend at http://localhost:8080 and the backend at http://localhost:8000

Notes:
- The backend reads `DATABASE_URL` from the environment. `docker-compose.yml` uses `.env` to populate this value.
- Do not commit your real `.env` with secrets to version control. Keep `.env.example` as a template.
