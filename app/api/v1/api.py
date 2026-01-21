# app/api/v1/api.py
from fastapi import APIRouter
from .endpoints import item

api_router = APIRouter()
# Include the item router with the prefix "/items" so endpoints are under /api/v1/items
api_router.include_router(item.router, prefix="/items", tags=["item"])
