from typing import List, TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.asset import Asset  # Import for type checking to avoid circular imports


class Sector(Base):
    """
    Sector model
    """
    __tablename__ = "sectors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    assets: Mapped[List["Asset"]] = relationship(back_populates="sector")
