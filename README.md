# InvestApp

Minimal FastAPI InvestApp application with real-time stock chart visualization.

## Features

- 📊 **Item Management** - CRUD operations for items
- 📈 **Stock Chart** - Interactive candlestick charts with real-time stock data
- 🔐 **User Management** - User authentication and management
- 🗄️ **PostgreSQL Database** - Persistent data storage
- 🐳 **Docker Support** - Easy deployment with Docker Compose

## Stock Chart Feature

The application includes a powerful stock chart visualization tool:

- **Interactive candlestick charts** using Lightweight Charts
- **Real-time data** from Yahoo Finance API
- **Multiple timeframes** (1 minute to 1 week intervals)
- **Volume histogram** with color-coded bars
- **Statistics dashboard** showing price, change, high, low, and volume

### Quick Start for Stock Charts

```bash
# Start the development server
uvicorn app.main:app --reload

# Access the stock chart
http://localhost:8000/stock.html
```

## Docker Compose

This repository includes a `docker-compose.yml` which brings up three services:

- `backend` — your FastAPI app built from the provided `Dockerfile` (exposes port 8000)
- `frontend` — a minimal static frontend served by Nginx (exposes port 8080)
- `postgres` — Postgres 15 with a persistent volume (exposes port 5432)

Quick start:

1. Copy the example environment file and adjust secrets if needed:

```bash
cp .env.test .env
```

2. Build and start the stack:

```bash
docker compose up --build
```

3. Open the frontend at http://localhost:8080 and the backend at http://localhost:8000

Notes:
- The backend reads `DATABASE_URL` from the environment. `docker-compose.yml` uses `.env` to populate this value.
- Do not commit your real `.env` with secrets to version control. Keep `.env.example` as a template.
