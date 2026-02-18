from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pathlib import Path

from .api.v1.api import api_router
from .core.config import settings
from .db.session import engine
from app.db.base_class import Base

# Ensure DB tables are created (for small projects)
Base.metadata.create_all(bind=engine)

# Project root for optional static mounting
project_root = Path(__file__).resolve().parent.parent


def get_application() -> FastAPI:
    # Initializing FastAPI application
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # Optionally mount the frontend static files at /static (not required if nginx serves them)
    application.mount("/static", StaticFiles(directory=project_root / "frontend"), name="static")

    # Setting up CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Connecting API router
    application.include_router(api_router, prefix=settings.API_V1_STR)

    return application


app = get_application()

# Keep a simple JSON health endpoint
@app.get("/health")
async def health():
    return JSONResponse({"status": "ok", "message": "API is running"})

# Serve the stock chart page
@app.get("/")
async def read_index():
    return FileResponse(project_root / "frontend" / "stock.html")

# Serve the main index.html
@app.get("/item")
async def read_item():
    return FileResponse(project_root / "frontend" / "index.html")
