import uuid
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload

from app.models import Position


def get_position_for_portfolio_and_asset(
        db: Session,
        portfolio_id: uuid.UUID,
        asset_id: uuid.UUID,
) -> Position | None:
    """
    Get a position for a specific asset in a portfolio.
    """
    return db.query(Position).filter(
        Position.portfolio_id == portfolio_id,
        Position.asset_id == asset_id,
    ).first()


def get_position_for_portfolio(
        db: Session,
        portfolio_id: uuid.UUID
) -> Position | None:
    return db.query(Position).options(joinedload(Position.asset)).filter(
        Position.portfolio_id == portfolio_id
    ).first()


def get_positions_for_portfolio(
        db: Session,
        portfolio_id: uuid.UUID
) -> list[type[Position]]:
    return db.query(Position).options(joinedload(Position.asset)).filter(
        Position.portfolio_id == portfolio_id
    ).all() or []


def create_position_for_portfolio(
        db: Session,
        portfolio_id: uuid.UUID,
        asset_id: uuid.UUID,
        quantity: Decimal,
        average_buy_price: Decimal
) -> Position:
    db_position = Position(
        portfolio_id=portfolio_id,
        asset_id=asset_id,
        quantity=quantity,
        average_buy_price=average_buy_price
    )
    db.add(db_position)
    return db_position


def upsert_position_for_buy(
        db: Session,
        portfolio_id: uuid.UUID,
        asset_id: uuid.UUID,
        added_quantity: Decimal,
        buy_price: Decimal
) -> Position:
    """
    Upsert position for a buy transaction:
    1. If the asset already exists in the portfolio, update the quantity and recalculate the average buy price.
    2. If the asset does not exist, create a new position with the given quantity and buy price.
    """
    # 1. Searching for existing position
    position = get_position_for_portfolio_and_asset(
        db,
        portfolio_id=portfolio_id,
        asset_id=asset_id
    )

    if position:
        # 2. If asset is existing - calculate average price and quantity
        total_old_value = position.quantity * position.average_buy_price
        total_new_value = added_quantity * buy_price

        new_quantity = position.quantity + added_quantity

        # Check for devine by zero
        if new_quantity > Decimal('0'):
            new_average_price = (total_old_value + total_new_value) / new_quantity
            position.average_buy_price = new_average_price

        position.quantity = new_quantity
    else:
        # 3. If no asset in portfolio - create a new record
        create_position_for_portfolio(
            db,
            portfolio_id=portfolio_id,
            asset_id=asset_id,
            quantity=added_quantity,
            average_buy_price=buy_price
        )

    # 4. Save state for current transaction (WITHOUT commit)
    db.flush()

    return position
