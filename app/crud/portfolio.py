"""
CRUD operations for Portfolio items, including create, read, update, and delete functions.
Each function is decorated with a timing helper to measure execution time for performance monitoring.
"""

from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Portfolio
from app.schemas import PortfolioCreate
from app.utils.helpers import timing


@timing
def get_portfolio(db: Session, portfolio_id: str):
    """Retrieve a single portfolio by its ID."""
    return db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()


@timing
def get_portfolios(db: Session, current_user_id=None):
    """Retrieve a list of portfolios with pagination support."""
    return db.query(Portfolio).filter(Portfolio.user_id == current_user_id).all()


@timing
def create_portfolio(db: Session, portfolio_in: PortfolioCreate, user_id):
    """Create a new portfolio item in the database."""
    db_item = Portfolio(
        name=portfolio_in.name,
        currency=portfolio_in.currency,
        is_imported=portfolio_in.is_imported,
        user_id=user_id
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@timing
def update_portfolio(db: Session, portfolio_id):
    """Update an existing portfolio item in the database."""
    db_item = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if db_item:
        update_data = portfolio_id.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)
        db_item.uploaded_at = datetime.now()
        db.commit()
        db.refresh(db_item)
    return db_item


@timing
def delete_portfolio(db: Session, portfolio_id: str):
    """Delete a portfolio item from the database by its ID."""
    db_item = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item
