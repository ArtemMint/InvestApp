from typing import Optional
from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    title: str = Field(..., max_length=100, min_length=1, description="Title of the item")
    description: str = Field(..., max_length=300, min_length=1, description="Description of the item")
    media_url: Optional[bytes] = Field(None, description="Optional media_url associated with the item")

class Item(ItemBase):
    id: int = Field(..., description="ID of the item item")

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    title: Optional[str] = Field(None, max_length=100, min_length=1, description="Title of the item item")
    description: Optional[str] = Field(None, max_length=300, min_length=1, description="Description of the item item")
    media_url: Optional[bytes] = Field(None, description="Optional media_url associated with the item")
