import uuid

from pydantic import BaseModel, ConfigDict

from app.models.asset import AssetType


class AssetResponse(BaseModel):
    id: uuid.UUID
    ticker: str
    name: str
    asset_type: AssetType
    sector: str | None = None

    model_config = ConfigDict(from_attributes=True)
