import uuid
from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.user import User  # Import for type checking to avoid circular imports
    from app.models.positions import Position  # Import for type checking to avoid circular imports
    from app.models.transaction import Transaction  # Import for type checking to avoid circular imports


class Portfolio(Base):
    """
    Portfolio model representing a user's investment portfolio.
    Each portfolio belongs to a single user and can contain multiple positions and transactions.
    The portfolio has a name, a base currency (defaulting to USD), and a flag indicating whether
    it was imported from an external source. When a portfolio is deleted, all its positions
    and transactions will also be deleted to maintain data integrity.

    Attributes:
        id (uuid.UUID): Unique identifier for the portfolio.
        user_id (uuid.UUID): Foreign key linking to the owning user.
        name (str): Name of the portfolio.
        currency (str): Base currency for the portfolio (default is "USD").
        is_imported (bool): Flag indicating if the portfolio was imported.
        created_at (datetime): Timestamp when the portfolio was created.
        updated_at (datetime): Timestamp when the portfolio was last updated.
    """
    __tablename__ = "portfolios"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    is_imported: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Connection to the user who owns the portfolio.
    user: Mapped["User"] = relationship(back_populates="portfolios")
    positions: Mapped[List["Position"]] = relationship(back_populates="portfolio", cascade="all, delete-orphan")
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="portfolio", cascade="all, delete-orphan")
