import uuid
from typing import List

from app.models import Transaction
from app.models.transaction import TransactionType
from app.schemas.asset import AddPositionToPortfolioRequest


def get_transactions_for_portfolio(db, portfolio_id: uuid.UUID) -> List[Transaction]:
    return db.query(Transaction).filter(
        Transaction.portfolio_id == portfolio_id).all()


def create_transaction(
        db,
        portfolio_id: uuid.UUID,
        asset_id: uuid.UUID,
        asset_data: AddPositionToPortfolioRequest
) -> Transaction:
    new_transaction = Transaction(
        portfolio_id=portfolio_id,
        asset_id=asset_id,
        type=TransactionType.BUY,
        quantity=asset_data.quantity,
        price_per_share=asset_data.price_per_share
    )
    db.add(new_transaction)
    return new_transaction
