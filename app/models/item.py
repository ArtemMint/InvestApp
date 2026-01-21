from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base

class Item(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(index=True)
    description: Mapped[str | None] = mapped_column(default=None)
    media_url: Mapped[str | None] = mapped_column(default=None)
