"""
CRUD operations for Asset items, including create, read, update, and delete functions.
Each function is decorated with a timing helper to measure execution time for performance monitoring.
"""
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.models import Asset
from app.models.asset import AssetType
from app.schemas.asset import AssetUpdate
from app.utils.helpers import timing


@timing
def get_assets(db: Session) -> list[type[Asset]]:
    return db.query(Asset).filter().all()


@timing
def get_asset_by_id(db: Session, asset_id: uuid.UUID) -> Optional[Asset]:
    return db.query(Asset).filter(Asset.id == asset_id).first()


@timing
def get_asset_by_ticker(db: Session, asset_ticker: str) -> Optional[Asset]:
    return db.query(Asset).filter(Asset.ticker == asset_ticker.upper()).first()


@timing
def create_asset(
        db: Session,
        ticker: str,
        name: str,
        asset_type: AssetType,
        sector_id: Optional[int] = None
) -> Asset:
    new_asset = Asset(
        ticker=ticker.upper(),
        name=name,
        asset_type=asset_type,
        sector_id=sector_id
    )
    db.add(new_asset)
    db.commit()
    return new_asset


@timing
def update_asset(
        db: Session,
        db_asset: Asset,
        asset_in: AssetUpdate
) -> Asset:
    update_data = asset_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_asset, field, value)
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset


@timing
def delete_asset_by_ticker(db: Session, asset_ticker: str) -> Optional[Asset]:
    asset = get_asset_by_ticker(db=db, asset_ticker=asset_ticker)
    if asset:
        db.delete(asset)
        db.commit()
        return asset
    return None


@timing
def delete_asset_by_id(db: Session, asset_id: uuid.UUID) -> Optional[Asset]:
    asset = get_asset_by_id(db=db, asset_id=asset_id)
    if asset:
        db.delete(asset)
        db.commit()
        return asset
    return None
