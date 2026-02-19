# app/api/v1/api.py
from fastapi import APIRouter
from .endpoints import item, stock, financial_goals

api_router = APIRouter()
# Include the item router with the prefix "/items" so endpoints are under /api/v1/items
api_router.include_router(item.router, prefix="/items", tags=["item"])
# Include the stock router with the prefix "/stock" so endpoints are under /api/v1/stock
api_router.include_router(stock.router, prefix="/stock", tags=["stock"])
# Include the stock router with the prefix "/financial_goals" so endpoints are under /api/v1/financial_goals
api_router.include_router(financial_goals.router, prefix="/financial_goals", tags=["financial_goals"])