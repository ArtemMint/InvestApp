import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.schemas import AssetResponse


class PositionBase(BaseModel):
    portfolio_id: uuid.UUID
    asset_id: uuid.UUID
    quantity: Decimal
    average_buy_price: Decimal


class PositionResponse(PositionBase):
    id: uuid.UUID
    asset: AssetResponse

    model_config = ConfigDict(from_attributes=True)
