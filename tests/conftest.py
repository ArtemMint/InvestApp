import os
from datetime import timedelta
from decimal import Decimal

from app.core.auth import create_access_token
from app.crud import create_user, create_portfolio
from app.crud.asset import create_asset
from app.models import Asset, Position, Transaction
from app.models.asset import AssetType
from app.models.transaction import TransactionType
from app.schemas import PortfolioCreate, UserRegister

# ---------------------------------------------------------------------------
# Override DATABASE_URL *before* any app module is imported so the app's
# session.py connects to an in-memory SQLite DB instead of Docker Postgres.
# Set TEST_DATABASE_URL env var to use a different test database.
# ---------------------------------------------------------------------------
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    "sqlite:///./test.db",
)
os.environ["POSTGRES_HOST"] = "localhost"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base_class import Base
from app.db.session import get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = os.environ["DATABASE_URL"]

_connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    _connect_args["check_same_thread"] = False

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=_connect_args)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables once per test session, drop after all tests finish."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    """
    Provide a transactional database session that rolls back after each test.
    This keeps tests isolated without leaving leftover data.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    """
    FastAPI TestClient with the DB dependency overridden to use the
    transactional *db_session* fixture.
    """

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def persisted_user(db_session, client):
    """
    Create a user in the test DB and set an authentication cookie on the TestClient.
    This lets tests use `client` as an authenticated user.
    """
    user = create_user(
        db=db_session,
        user_in=UserRegister(
            email="test_user@gmail.com",
            password="test_password"
        )
    )
    access_token = create_access_token(subject=user.email, expires_delta=timedelta(minutes=10))
    # Set cookie on TestClient so subsequent requests are authenticated
    client.cookies.set("access_token", f"Bearer {access_token}")
    return user


@pytest.fixture
def persisted_portfolio(db_session, persisted_user):
    portfolio = create_portfolio(
        db=db_session,
        portfolio_in=PortfolioCreate(
            name="Test Portfolio",
            currency="USD",
            is_imported=False
        ),
        user_id=persisted_user.id
    )
    # Save to DB
    db_session.add(portfolio)
    db_session.commit()
    db_session.refresh(portfolio)
    return portfolio


@pytest.fixture
def portfolio_with_assets(db_session, persisted_portfolio):
    """
    Фікстура, яка бере існуючий портфель і наповнює його
    тестовим активом (NVDA), позицією та транзакцією.
    """
    # 1. Create asset
    asset = Asset(
        ticker="NVDA",
        name="Nvidia Corp",
        asset_type=AssetType.STOCK
    )
    db_session.add(asset)
    db_session.flush()  # Getting asset.id

    # 2. Create positions
    position = Position(
        portfolio_id=persisted_portfolio.id,
        asset_id=asset.id,
        quantity=Decimal('10.0'),
        average_buy_price=Decimal('100.0')
    )
    db_session.add(position)

    # 3. Create transaction
    transaction = Transaction(
        portfolio_id=persisted_portfolio.id,
        asset_id=asset.id,
        type=TransactionType.BUY,
        quantity=Decimal('10.0'),
        price_per_share=Decimal('100.0')
    )
    db_session.add(transaction)

    # Commit the DB
    db_session.commit()

    return {
        "portfolio": persisted_portfolio,
        "asset": asset,
        "position": position,
        "transaction": transaction
    }


@pytest.fixture
def persisted_asset(db_session):
    db_asset = create_asset(
        db=db_session,
        ticker="GOOG",
        name="Google",
        asset_type=AssetType.STOCK,
    )
    return db_asset
