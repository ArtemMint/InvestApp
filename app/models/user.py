import uuid
from datetime import datetime
from typing import List

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class User(Base):
    """
    User model representing a user of the portfolio management system.
    Each user can have multiple portfolios, but each portfolio belongs to only one user.
    The user's email must be unique across the system.
    When a user is deleted, all their portfolios will also be deleted to maintain data integrity.

    Attributes:
        id (uuid.UUID): Unique identifier for the user.
        email (str): Unique email address of the user.
        password_hash (str): Hashed password for authentication.
        created_at (datetime): Timestamp when the user was created.
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Connection to portfolios created by the user. When a user is deleted, all their portfolios will also be deleted.
    portfolios: Mapped[List["Portfolio"]] = relationship(back_populates="user", cascade="all, delete-orphan")
