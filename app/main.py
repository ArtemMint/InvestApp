from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from .api.v1.api import api_router
from .core.config import settings
from .db.session import engine
from app.db.base_class import Base

# Ensure DB tables are created (for small projects)
Base.metadata.create_all(bind=engine)

# Templates (Jinja2) and static files mounting
# Use an absolute path derived from the project root so templates load from frontend/templates
project_root = Path(__file__).resolve().parent.parent
templates_dir = project_root / "frontend" / "templates"
# Fallback: if frontend/templates doesn't exist, fall back to app/templates
if not templates_dir.exists():
    templates_dir = Path(__file__).resolve().parent / "templates"

templates = Jinja2Templates(directory=str(templates_dir))


def get_application() -> FastAPI:
    # Initializing FastAPI application
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # Mount the frontend static files (optional)
    # This allows the backend to serve assets from ./frontend at the /static path
    application.mount("/static", StaticFiles(directory=project_root / "frontend"), name="static")

    # Setting up CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Connecting API роутер
    application.include_router(api_router, prefix=settings.API_V1_STR)

    return application


app = get_application()

# Serve the frontend index page from templates/index.html
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Return the frontend index page rendered by Jinja2 templates."""
    # If you want to pass DB-driven items to the template, you can query here and pass them
    return templates.TemplateResponse("index.html", {"request": request})

# Keep a simple JSON health endpoint if desired
@app.get("/health")
async def health():
    return {"status": "ok", "message": "API is running"}
