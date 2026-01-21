import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Determine DB URL
DATABASE_URL = settings.SQLALCHEMY_DATABASE_URL

# Helper to know if this is sqlite (so we can pass check_same_thread)
is_sqlite = DATABASE_URL.startswith("sqlite")

# Try to create engine with a small retry loop to allow postgres container to become ready
last_err = None
engine = None
for attempt in range(1, 11):
    try:
        if is_sqlite:
            engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        else:
            # For Postgres and others, enable pool_pre_ping to avoid stale connections
            engine = create_engine(DATABASE_URL, pool_pre_ping=True)

        # Try a quick test connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        last_err = None
        break
    except Exception as e:
        last_err = e
        # If DB not ready, wait and retry
        time.sleep(1)

if engine is None:
    # If we were unable to create a working engine, raise the last error for visibility
    raise last_err

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
