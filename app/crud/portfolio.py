"""
CRUD operations for Portfolio items, including create, read, update, and delete functions.
Each function is decorated with a timing helper to measure execution time for performance monitoring.
"""
import uuid

from sqlalchemy.orm import Session

from app.models import Portfolio, User
from app.schemas import PortfolioCreate, PortfolioUpdate
from app.utils.helpers import timing


@timing
def get_portfolio_for_user(db: Session, portfolio_id: uuid.UUID = None, user_id: uuid.UUID = None):
    """Retrieve a single portfolio by its ID."""
    return db.query(Portfolio).filter(Portfolio.id == portfolio_id, User.id == user_id).first()


@timing
def get_portfolios_for_user(db: Session, current_user_id: uuid.UUID = None):
    """Retrieve a list of portfolios with pagination support."""
    return db.query(Portfolio).filter(Portfolio.user_id == current_user_id).all()


@timing
def create_portfolio(db: Session, portfolio_in: PortfolioCreate = None, user_id: uuid.UUID = None):
    """Create a new portfolio item in the database."""
    portfolio_item = Portfolio(
        name=portfolio_in.name,
        currency=portfolio_in.currency,
        is_imported=portfolio_in.is_imported,
        user_id=user_id
    )
    db.add(portfolio_item)
    db.commit()
    db.refresh(portfolio_item)
    return portfolio_item


@timing
def update_portfolio(
        db: Session,
        db_portfolio: Portfolio,
        portfolio_in: PortfolioUpdate
) -> Portfolio:
    update_data = portfolio_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_portfolio, field, value)
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)

    return db_portfolio


@timing
def delete_portfolio(db: Session, portfolio_item):
    """Delete a portfolio item from the database by its ID."""
    if portfolio_item:
        db.delete(portfolio_item)
        db.commit()
    return portfolio_item
