import enum
import uuid
from typing import List
from typing import Optional

from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.positions import Position


class AssetType(str, enum.Enum):
    """AssetType enumeration representing the type of financial asset."""
    STOCK = "STOCK"
    CRYPTO = "CRYPTO"
    BOND = "BOND"
    ETF = "ETF"


class Asset(Base):
    """
    Asset model representing a financial asset that can be held in a portfolio.
    Each asset has a unique ticker symbol, a name, an asset type (e.g., stock, crypto, bond, ETF), and an optional sector classification.
    The ticker symbol is unique across the system and is indexed for fast lookup. The asset type is stored as an enumeration to ensure data integrity.
    The sector field is optional and can be used to classify assets into different sectors (e.g., technology, healthcare) for reporting and analysis purposes.
    Each asset can be associated with multiple positions in different portfolios, allowing users to track their holdings across various assets.

    Attributes:
        id (uuid.UUID): Unique identifier for the asset.
        ticker (str): Unique ticker symbol for the asset (e.g., AAPL, BTC).
        name (str): Name of the asset (e.g., Apple Inc., Bitcoin).
        asset_type (AssetType): Type of the asset (e.g., STOCK, CRYPTO, BOND, ETF).
        sector (Optional[str]): Optional sector classification for the asset (e.g., technology, healthcare).
        positions (List[Position]): List of positions associated with this asset.
    """
    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ticker: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_type: Mapped[AssetType] = mapped_column(Enum(AssetType), nullable=False)
    sector: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Connection to positions and transactions.
    positions: Mapped[List["Position"]] = relationship(back_populates="asset")
