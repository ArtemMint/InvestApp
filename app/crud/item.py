from datetime import datetime

from sqlalchemy.orm import Session

import app.models as models
from app.models.item import Item
from app.utils.helpers import timing


@timing
def get_item(db: Session, item_id: int):
    return db.query(Item).filter(Item.id == item_id).first()

@timing
def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Item).offset(skip).limit(limit).all()

@timing
def create_item(db: Session, item_in):
    db_item = models.Item(
        title=item_in.title,
        description=item_in.description,
        media_url=item_in.media_url,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@timing
def delete_item(db: Session, item_id: int):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item

@timing
def update_item(db: Session, item_in):
    db_item = db.query(Item).filter(Item.id == item_in.id).first()
    if db_item:
        update_data = item_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)
        db_item.uploaded_at = datetime.now()
        db.commit()
        db.refresh(db_item)
    return db_item
