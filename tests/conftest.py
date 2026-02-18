import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import get_db
from app.db.base_class import Base
from fastapi.testclient import TestClient

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/postgres"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create tables for tests."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    """Create database session."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    """Create client for tests."""
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    # Перевизначаємо залежність get_db на нашу тестову
    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as c:
        yield c
    # Прибираємо перевизначення після тесту
    app.dependency_overrides.clear()
