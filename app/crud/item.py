from sqlalchemy.orm import Session
from app.models.item import Item
from app.schemas.item import ItemCreate

def create_item(db: Session, item_in: ItemCreate):
    db_item = Item(**item_in.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Item).offset(skip).limit(limit).all()
