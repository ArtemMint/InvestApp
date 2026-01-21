from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app import crud
import app.models as models
import app.schemas as schemas

router = APIRouter()

# JSON API: list items
@router.get("/", response_model=List[schemas.Item], status_code=200)
async def list_items_api(db: Session = Depends(get_db)):
    items = crud.item.get_items(db)
    result = [
        {"id": i.id, "title": i.title, "description": i.description, "media_url": i.media_url}
        for i in items
    ]
    return JSONResponse(result)

# JSON API: create item via JSON body
@router.post("/", response_model=schemas.Item, status_code=201)
async def create_item_api(payload: dict, db: Session = Depends(get_db)):
    if "title" not in payload or "description" not in payload:
        raise HTTPException(status_code=400, detail="title and description are required")
    db_item = models.Item(**{k: v for k, v in payload.items() if k in ("title", "description", "media_url")})
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return JSONResponse({"id": db_item.id, "title": db_item.title, "description": db_item.description, "media_url": db_item.media_url})
