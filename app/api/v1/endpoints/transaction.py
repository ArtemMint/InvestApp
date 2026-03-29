import uuid
from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.crud.transaction import get_transactions_for_portfolio
from app.db.session import get_db
from app.schemas.transaction import TransactionResponse

router = APIRouter()


@router.get("/{portfolio_id}", response_model=List[TransactionResponse], status_code=status.HTTP_200_OK)
def read_transactions_for_portfolio(
        portfolio_id: uuid.UUID,
        db: Session = Depends(get_db),
) -> List[TransactionResponse]:
    db_transactions = get_transactions_for_portfolio(db=db, portfolio_id=portfolio_id)
    if not db_transactions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assets not found")
    return [TransactionResponse.model_validate(i) for i in db_transactions]
