from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    title: str = Field(..., max_length=100, min_length=1, description="Title of the item")
    description: str = Field(..., max_length=300, min_length=1, description="Description of the item")
    media_url: Optional[str] = Field(None, max_length=500, description="Optional media_url associated with the item")

class Item(ItemBase):
    id: int = Field(..., description="ID of the item")
    created_at: datetime = Field(..., description="Date and time when the item was created")
    updated_at: datetime = Field(..., description="Date and time when the item was last updated")

    class Config:
        from_attributes = True

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    id: int = Field(..., description="ID of the item")
    title: Optional[str] = Field(None, max_length=100, min_length=1, description="Title of the item")
    description: Optional[str] = Field(None, max_length=300, min_length=1, description="Description of the item")
    media_url: Optional[str] = Field(None, max_length=500, description="Optional media_url associated with the item")
    created_at: Optional[datetime] = Field(None, description="Date and time when the item was created")
    updated_at: Optional[datetime] = Field(None, description="Date and time when the item was last updated")
