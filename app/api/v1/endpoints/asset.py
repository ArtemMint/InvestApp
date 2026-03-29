import uuid
from typing import List

from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session

from app.crud.asset import get_asset_by_ticker, get_assets, delete_asset_by_ticker, create_asset, update_asset, \
    get_asset_by_id, delete_asset_by_id
from app.db.session import get_db
from app.models.asset import AssetType
from app.schemas.asset import AssetResponse, AssetCreate, AssetUpdate

router = APIRouter()


@router.get("/", response_model=List[AssetResponse], status_code=status.HTTP_200_OK)
async def read_assets(
        db: Session = Depends(get_db),
) -> List[AssetResponse]:
    db_assets = get_assets(db=db)
    if not db_assets:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assets not found")
    return [AssetResponse.model_validate(i) for i in db_assets]


@router.get("/{ticker}", response_model=AssetResponse, status_code=status.HTTP_200_OK)
async def read_asset_by_ticker(
        ticker: str,
        db: Session = Depends(get_db),
) -> AssetResponse:
    db_asset = get_asset_by_ticker(db, asset_ticker=ticker)
    if not db_asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    return AssetResponse.model_validate(db_asset)


@router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def add_asset(
        asset: AssetCreate,
        db: Session = Depends(get_db),
) -> AssetResponse:
    db_asset = get_asset_by_ticker(db, asset_ticker=asset.ticker)
    if db_asset:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Asset already created")
    db_asset = create_asset(
        db=db,
        ticker=asset.ticker,
        name=asset.ticker,  # Заглушка
        asset_type=AssetType.STOCK  # Заглушка
    )
    return AssetResponse.model_validate(db_asset)


@router.put("/ticker/{asset_ticker}", response_model=AssetResponse, status_code=status.HTTP_200_OK)
async def update_asset_by_ticker(
        asset_ticker: str,
        payload: AssetUpdate,
        db: Session = Depends(get_db),
) -> AssetResponse:
    db_asset = get_asset_by_ticker(db, asset_ticker=asset_ticker)
    if not db_asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Asset {asset_ticker} not found")
    db_asset = update_asset(db, db_asset=db_asset, asset_in=payload)
    return AssetResponse.model_validate(db_asset)


@router.put("/id/{asset_id}", response_model=AssetResponse, status_code=status.HTTP_200_OK)
async def update_asset_by_id(
        asset_id: uuid.UUID,
        payload: AssetUpdate,
        db: Session = Depends(get_db),
) -> AssetResponse:
    db_asset = get_asset_by_id(db, asset_id=asset_id)
    if not db_asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Asset {asset_id} not found")
    db_asset = update_asset(db, db_asset=db_asset, asset_in=payload)
    return AssetResponse.model_validate(db_asset)


@router.delete("/id/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_asset_by_id(
        asset_id: uuid.UUID,
        db: Session = Depends(get_db),
) -> Response:
    delete_asset_by_id(db=db, asset_id=asset_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/ticker/{asset_ticker}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_asset_by_ticker(
        asset_ticker: str,
        db: Session = Depends(get_db),
) -> Response:
    delete_asset_by_ticker(db=db, asset_ticker=asset_ticker)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
