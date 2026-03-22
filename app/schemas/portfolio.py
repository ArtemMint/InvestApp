import uuid
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class PortfolioBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    currency: str = Field("USD", max_length=3)
    is_imported: bool = False


class PortfolioCreate(PortfolioBase):
    pass


class PortfolioUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    currency: str | None = Field(None, max_length=3)
    updated_at: datetime | None = Field(default_factory=datetime.now)


class PortfolioResponse(PortfolioBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
