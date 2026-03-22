import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.db.base_class import Base
from .api.v1.api import api_router
from .core.auth import is_token_valid
from .core.config import settings
from .db.session import engine

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


# Create tables on startup when appropriate (useful for local/dev).
@app.on_event("startup")
def create_tables_on_startup():
    if os.getenv("TESTING") == "1":
        return
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass


# Keep a simple JSON health endpoint
@app.get("/health")
async def health():
    return JSONResponse({"status": "ok", "message": "API is running"})


# Serve the main index.html
@app.get("/")
async def read_index():
    return FileResponse(project_root / "frontend" / "index.html")


# Serve the stock.html at /stock
@app.get("/stock")
async def read_stock(request: Request):
    redirect = is_token_valid(request)
    if redirect:
        return redirect
    return FileResponse(project_root / "frontend" / "stock.html")


# Serve the investment_calc.html
@app.get("/investment_calc")
async def read_investment_calc(request: Request):
    redirect = is_token_valid(request)
    if redirect:
        return redirect
    return FileResponse(project_root / "frontend" / "investment_calc.html")


# Serve the portfolio.html
@app.get("/portfolio")
async def read_portfolio(request: Request):
    redirect = is_token_valid(request)
    if redirect:
        return redirect
    return FileResponse(project_root / "frontend" / "portfolio.html")


# Serve the login and register pages
@app.get("/login")
async def read_login():
    return FileResponse(project_root / "frontend" / "login.html")


@app.get("/register")
async def read_register():
    return FileResponse(project_root / "frontend" / "register.html")
