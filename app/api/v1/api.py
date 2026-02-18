# app/api/v1/api.py
from fastapi import APIRouter
from .endpoints import item, stock

api_router = APIRouter()
# Include the item router with the prefix "/items" so endpoints are under /api/v1/items
api_router.include_router(item.router, prefix="/items", tags=["item"])
# Include the stock router with the prefix "/stock" so endpoints are under /api/v1/stock
api_router.include_router(stock.router, prefix="/stock", tags=["stock"])
