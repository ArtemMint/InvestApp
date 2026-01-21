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
async def create_item_api(payload: schemas.ItemCreate, db: Session = Depends(get_db)):
    if payload.title is None or payload.description is None:
        raise HTTPException(status_code=400, detail="title and description are required")
    db_item = models.Item(
        title=payload.title,
        description=payload.description,
        media_url=payload.media_url,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return JSONResponse({"id": db_item.id, "title": db_item.title, "description": db_item.description, "media_url": db_item.media_url})

# JSON API: update item via JSON body
@router.put("/", response_model=schemas.ItemUpdate, status_code=200)
async def update_item_api(payload: schemas.Item, db: Session = Depends(get_db)):
    if payload.id is None:
        raise HTTPException(status_code=400, detail="id is required for update")
    db_item = db.query(models.Item).filter(models.Item.id == payload.id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    if payload.title is not None:
        db_item.title = payload.title
    if payload.description is not None:
        db_item.description = payload.description
    if payload.media_url is not None:
        db_item.media_url = payload.media_url
    db.commit()
    db.refresh(db_item)
    return JSONResponse({"id": db_item.id, "title": db_item.title, "description": db_item.description, "media_url": db_item.media_url})

# JSON API: delete item by ID
@router.delete("/{item_id}", status_code=204)
async def delete_item_api(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return JSONResponse(status_code=204, content={})
