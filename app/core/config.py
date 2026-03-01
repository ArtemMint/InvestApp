import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI App 2026"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    SQLITE_URL: str = "sqlite:///./sql_app.db"

    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "invest_db")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = os.getenv("POSTGRES_PORT", 5432)
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL",
                                            "postgresql://postgres:postgres@localhost:5432/invest_db")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        """Return the SQLAlchemy database URL to use.

        Priority:
        1. Explicit DATABASE_URL environment variable
        2. Built from POSTGRES_* settings
        3. SQLITE_URL fallback
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL

        # If POSTGRES_HOST is not the default 'localhost' or POSTGRES_DB is set,
        # build a postgres URL
        if self.POSTGRES_HOST and self.POSTGRES_DB:
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

        return self.SQLITE_URL


settings = Settings()
