from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base

class Item(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(index=True)
    description: Mapped[str | None] = mapped_column(default=None)
    media_url: Mapped[str | None] = mapped_column(default=None)
    created_at: Mapped[datetime | None] = mapped_column(server_default=func.now(), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=True)
