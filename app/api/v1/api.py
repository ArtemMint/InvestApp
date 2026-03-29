# app/api/v1/api.py
from fastapi import APIRouter

from .endpoints import portfolio, stock, financial_goals, user, asset, transaction, position

api_router = APIRouter()
# Include the user router with the prefix "/users" so endpoints are under /api/v1/users
api_router.include_router(user.router, prefix="/users", tags=["users"])

# Include the stock router with the prefix "/stock" so endpoints are under /api/v1/stock
api_router.include_router(stock.router, prefix="/stock", tags=["stock"])

# Include the item router with the prefix "/portfolio" so endpoints are under /api/v1/portfolio
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])

# Include the stock router with the prefix "/financial_goals" so endpoints are under /api/v1/financial_goals
api_router.include_router(financial_goals.router, prefix="/financial_goals", tags=["financial_goals"])

# Include the asset router with the prefix "/assets" so endpoints are under /api/v1/assets
api_router.include_router(asset.router, prefix="/assets", tags=["assets"])

# Include the transaction router with the prefix "/transactions" so endpoints are under /api/v1/transaction
api_router.include_router(transaction.router, prefix="/transactions", tags=["transactions"])

# Include the position router with the prefix "/positions" so endpoints are under /api/v1/transaction
api_router.include_router(position.router, prefix="/positions", tags=["positions"])
