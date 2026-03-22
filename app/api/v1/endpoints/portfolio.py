import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.crud.portfolio import get_portfolio_for_user, get_portfolios_for_user, create_portfolio, update_portfolio, \
    delete_portfolio
from app.db.session import get_db
from app.models import User
from app.schemas.portfolio import PortfolioResponse, PortfolioCreate, PortfolioUpdate
from app.utils.helpers import log_request

router = APIRouter()


@log_request
@router.get("/{portfolio_id}", response_model=PortfolioResponse, status_code=status.HTTP_200_OK)
async def read_user_portfolio(
        portfolio_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> PortfolioResponse:
    db_portfolio = get_portfolio_for_user(db, portfolio_id=portfolio_id, user_id=current_user.id)
    if not db_portfolio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    return PortfolioResponse.model_validate(db_portfolio)


@log_request
@router.get("/", response_model=List[PortfolioResponse], status_code=status.HTTP_200_OK)
async def read_user_portfolios(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> List[PortfolioResponse]:
    portfolios = get_portfolios_for_user(db, current_user_id=current_user.id)
    return [PortfolioResponse.model_validate(i) for i in portfolios]


@log_request
@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def add_user_portfolio(
        payload: PortfolioCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> PortfolioResponse:
    db_portfolio = create_portfolio(db, portfolio_in=payload, user_id=current_user.id)
    return PortfolioResponse.model_validate(db_portfolio)


@log_request
@router.put("/{portfolio_id}", response_model=PortfolioResponse, status_code=status.HTTP_200_OK)
async def edit_user_portfolio(
        portfolio_id: uuid.UUID,
        payload: PortfolioUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> PortfolioResponse:
    db_portfolio = get_portfolio_for_user(db, portfolio_id=portfolio_id, user_id=current_user.id)
    if not db_portfolio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    db_portfolio = update_portfolio(db, db_portfolio=db_portfolio, portfolio_in=payload)
    return PortfolioResponse.model_validate(db_portfolio)


@log_request
@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_portfolio(
        portfolio_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> Response:
    db_portfolio = get_portfolio_for_user(db, portfolio_id=portfolio_id, user_id=current_user.id)
    if not db_portfolio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")
    delete_portfolio(db, portfolio_item=db_portfolio)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
