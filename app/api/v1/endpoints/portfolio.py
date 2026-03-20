from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.crud.portfolio import get_portfolio, get_portfolios, create_portfolio, update_portfolio, delete_portfolio
from app.db.session import get_db
from app.models import User, Portfolio
from app.schemas.portfolio import PortfolioResponse, PortfolioCreate, PortfolioUpdate
from app.utils.helpers import log_request

router = APIRouter()


@log_request
@router.get("/{portfolio_id}", response_model=PortfolioResponse, status_code=200)
async def read_portfolio(
        portfolio_id: str,
        db: Session = Depends(get_db)
) -> PortfolioResponse:
    portfolio = get_portfolio(db, portfolio_id=portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return PortfolioResponse.model_validate(portfolio)


@log_request
@router.get("/", response_model=List[PortfolioResponse], status_code=200)
async def read_portfolios(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> List[PortfolioResponse]:
    portfolios = get_portfolios(db, current_user_id=current_user.id)
    return [PortfolioResponse.model_validate(i) for i in portfolios]


@log_request
@router.post("/", response_model=PortfolioResponse, status_code=201)
async def add_portfolio(
        payload: PortfolioCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> PortfolioResponse:
    db_item = create_portfolio(db, portfolio_in=payload, user_id=current_user.id)
    return PortfolioResponse.model_validate(db_item)


@log_request
@router.put("/", response_model=PortfolioResponse, status_code=200)
async def edit_portfolio(
        payload: PortfolioUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> PortfolioResponse:
    db_item = db.query(Portfolio).filter(Portfolio.id == current_user.id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    db_item = update_portfolio(db, item_in=payload)
    return db_item


@log_request
@router.delete("/{portfolio_id}", status_code=204)
async def remove_portfolio(
        portfolio_id: str,
        db: Session = Depends(get_db)
) -> Response:
    db_item = get_portfolio(db, portfolio_id=portfolio_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    delete_portfolio(db, portfolio_id=portfolio_id)
    return Response(status_code=204)
