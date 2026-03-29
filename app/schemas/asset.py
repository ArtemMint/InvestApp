import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.asset import AssetType


class AssetBase(BaseModel):
    ticker: str
    name: str
    asset_type: AssetType


class AssetResponse(BaseModel):
    id: uuid.UUID
    ticker: str
    name: str
    asset_type: AssetType
    # sector_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    ticker: str | None = None
    name: str | None = None
    asset_type: AssetType | None = None

    model_config = ConfigDict(extra="forbid")


class AddPositionToPortfolioRequest(BaseModel):
    ticker: str = Field(..., description="Ticker of investment, for example AAPL")
    quantity: Decimal = Field(..., gt=0, description="Quantity of stocks")
    price_per_share: Decimal = Field(..., gt=0, description="Price for one")
