import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.crud.asset import get_asset_by_ticker, create_asset
from app.crud.portfolio import get_portfolio_for_user, get_portfolios_for_user, create_portfolio, update_portfolio, \
    delete_portfolio
from app.crud.position import upsert_position_for_buy, get_positions_for_portfolio
from app.crud.transaction import create_transaction, get_transactions_for_portfolio
from app.db.session import get_db
from app.models import User
from app.models.asset import AssetType
from app.schemas import TransactionResponse, PositionResponse
from app.schemas.asset import AddPositionToPortfolioRequest
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Portfolio {portfolio_id} not found")
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Portfolio {portfolio_id} not found")
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Portfolio {portfolio_id} not found")
    delete_portfolio(db, portfolio_item=db_portfolio)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{portfolio_id}/position", status_code=status.HTTP_201_CREATED)
def add_position_to_portfolio(
        portfolio_id: uuid.UUID,
        asset_data: AddPositionToPortfolioRequest,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    ticker_upper = asset_data.ticker.upper()

    # 1. Check if the portfolio exists and belongs to the current user
    asset = get_asset_by_ticker(db, asset_ticker=ticker_upper)

    # 2. If the asset does not exist, create it (with placeholder data)
    if not asset:
        asset = create_asset(
            db=db,
            ticker=ticker_upper,
            name=ticker_upper,  # Заглушка
            asset_type=AssetType.STOCK  # Заглушка
        )

    # 3. Verify portfolio is existing for user.
    db_portfolio = get_portfolio_for_user(db, portfolio_id=portfolio_id, user_id=current_user.id)
    if not db_portfolio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Portfolio {portfolio_id} not found")

    # 4. Create a new transaction for buying the asset
    create_transaction(db, portfolio_id=portfolio_id, asset_id=asset.id, asset_data=asset_data)

    # 5. Upsert the position in the portfolio for this asset
    upsert_position_for_buy(
        db=db,
        portfolio_id=portfolio_id,
        asset_id=asset.id,
        added_quantity=asset_data.quantity,
        buy_price=asset_data.price_per_share
    )

    # Finally, commit the transaction to save all changes to the database
    db.commit()
    return {"message": f"Asset {ticker_upper} added to the portfolio {portfolio_id}."}


@router.get("/{portfolio_id}/positions", response_model=List[PositionResponse], status_code=status.HTTP_200_OK)
def read_positions_for_portfolio(
        portfolio_id: uuid.UUID,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
) -> List[PositionResponse]:
    db_portfolio = get_portfolio_for_user(db, portfolio_id=portfolio_id, user_id=current_user.id)
    if not db_portfolio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")

    db_positions = get_positions_for_portfolio(
        db=db,
        portfolio_id=db_portfolio.id,
    )
    return [PositionResponse.model_validate(position) for position in db_positions]


@router.get("/{portfolio_id}/transactions", response_model=List[TransactionResponse], status_code=status.HTTP_200_OK)
def read_transactions_for_portfolio(
        portfolio_id: uuid.UUID,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
) -> List[TransactionResponse]:
    db_portfolio = get_portfolio_for_user(db, portfolio_id=portfolio_id, user_id=current_user.id)
    if not db_portfolio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found")

    db_transactions = get_transactions_for_portfolio(db=db, portfolio_id=portfolio_id)
    return [TransactionResponse.model_validate(i) for i in db_transactions]
