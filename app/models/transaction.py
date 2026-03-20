import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, DateTime, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class TransactionType(str, enum.Enum):
    """TransactionType enumeration representing the type of transaction."""
    BUY = "BUY"
    SELL = "SELL"
    DIVIDEND = "DIVIDEND"


class Transaction(Base):
    """
    Transaction model representing a buy, sell, or dividend transaction for an asset within a portfolio.
    Each transaction is associated with one portfolio and one asset, and it tracks the type of transaction (buy, sell, dividend),
    the quantity of the asset involved, the price per share at the time of the transaction, and the timestamp of when
    the transaction occurred. The quantity is stored as a Decimal for financial precision, allowing up to 18 digits total
    with 8 digits after the decimal point. The price per share is also stored as a Decimal with 4 digits after the decimal point.
    When a portfolio or asset is deleted, all related transactions will also be deleted to maintain data integrity.

    Attributes:
        id (uuid.UUID): Unique identifier for the transaction.
        portfolio_id (uuid.UUID): Foreign key linking to the associated portfolio.
        asset_id (uuid.UUID): Foreign key linking to the associated asset.
        transaction_type (TransactionType): The type of transaction (BUY, SELL, DIVIDEND).
        quantity (Decimal): The quantity of the asset involved in the transaction.
        price_per_share (Decimal): The price per share at the time of the transaction.
        timestamp (datetime): Timestamp when the transaction occurred.
    """
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    portfolio_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("portfolios.id"), nullable=False)
    asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.id"), nullable=False)

    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    price_per_share: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Connection to the portfolio and asset.
    portfolio: Mapped["Portfolio"] = relationship(back_populates="transactions")
    asset: Mapped["Asset"] = relationship()
