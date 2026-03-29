import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class TransactionBase(BaseModel):
    portfolio_id: uuid.UUID
    asset_id: uuid.UUID
    type: str
    quantity: Decimal
    price_per_share: Decimal


class TransactionResponse(TransactionBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
