from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import crud
import app.models as models
import app.schemas as schemas
from app.db.session import get_db
from app.utils.helpers import log_request

router = APIRouter()

@log_request
@router.get("/", response_model=List[schemas.Item], status_code=200)
async def list_items_api(db: Session = Depends(get_db)):
    items = crud.item.get_items(db)
    return [schemas.Item.model_validate(i) for i in items]

@log_request
@router.get("/{item_id}", response_model=schemas.Item, status_code=200)
async def get_item_api(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.item.get_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return schemas.Item.model_validate(db_item)

@log_request
@router.post("/", response_model=schemas.Item, status_code=201)
async def create_item_api(payload: schemas.ItemCreate, db: Session = Depends(get_db)):
    if payload.title is None or payload.description is None:
        raise HTTPException(status_code=400, detail="title and description are required")
    db_item = crud.item.create_item(db, item_in=payload)
    return schemas.Item.model_validate(db_item)

@log_request
@router.put("/", response_model=schemas.ItemUpdate, status_code=200)
async def update_item_api(payload: schemas.ItemUpdate, db: Session = Depends(get_db)):
    if payload.id is None:
        raise HTTPException(status_code=400, detail="id is required for update")
    db_item = db.query(models.Item).filter(models.Item.id == payload.id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db_item = crud.item.update_item(db, item_in=payload)
    return db_item

@log_request
@router.delete("/{item_id}", status_code=204)
async def delete_item_api(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.item.get_item(db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    crud.item.delete_item(db, item_id=item_id)
    return JSONResponse(status_code=204)
