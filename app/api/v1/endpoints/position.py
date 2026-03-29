import uuid
from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.crud.position import get_positions_for_portfolio
from app.db.session import get_db
from app.schemas import PositionResponse

router = APIRouter()


@router.get("/{portfolio_id}", response_model=List[PositionResponse], status_code=status.HTTP_200_OK)
def read_positions_for_portfolio(
        portfolio_id: uuid.UUID,
        db: Session = Depends(get_db),
) -> List[PositionResponse]:
    db_positions = get_positions_for_portfolio(
        db=db,
        portfolio_id=portfolio_id,
    )
    if not db_positions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Positions not found")
    return [PositionResponse.model_validate(position) for position in db_positions]
