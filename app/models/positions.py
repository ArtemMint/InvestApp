import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.portfolio import Portfolio  # Import for type checking to avoid circular imports
    from app.models.asset import Asset  # Import for type checking to avoid circular imports


class Position(Base):
    """
    Position model representing a specific holding of an asset within a portfolio.
    Each position is associated with one portfolio and one asset, and it tracks the quantity of the
    asset held and the average buy price. The quantity is stored as a Decimal for financial precision,
    allowing up to 18 digits total with 8 digits after the decimal point.
    The average buy price is also stored as a Decimal with 4 digits after the decimal point.
    When a portfolio or asset is deleted, all related positions will also be deleted to maintain
    data integrity. Additionally, there is a unique constraint to ensure that each portfolio can
    only have one position per asset.

    Attributes:
        id (uuid.UUID): Unique identifier for the position.
        portfolio_id (uuid.UUID): Foreign key linking to the associated portfolio.
        asset_id (uuid.UUID): Foreign key linking to the associated asset.
        quantity (Decimal): The quantity of the asset held in the position.
        average_buy_price (Decimal): The average price at which the asset was bought.
        updated_at (datetime): Timestamp when the position was last updated.
    """
    __tablename__ = "positions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    portfolio_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("portfolios.id"), nullable=False)
    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id"), nullable=False)

    # User Numeric for financial precision. 18 digits total, 8 of which are after the decimal point.
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False, default=0)
    average_buy_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)

    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now())

    # Connection to the portfolio and asset. When a portfolio or asset is deleted, all related positions will also be deleted.
    portfolio: Mapped["Portfolio"] = relationship(back_populates="positions")
    asset: Mapped["Asset"] = relationship(back_populates="positions")

    # Guarantee that each portfolio can only have one position per asset
    __table_args__ = (
        UniqueConstraint('portfolio_id', 'asset_id', name='_portfolio_asset_uc'),
    )
