from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    # Налаштування за замовчуванням (можуть бути перевизначені в .env)
    PROJECT_NAME: str = "FastAPI App 2026"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Список дозволених доменів для CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Параметри бази даних
    SQLITE_URL: str = "sqlite:///./sql_app.db"

    # Postgres / Docker settings (can be provided via .env or docker-compose)
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "webstore"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[str] = None

    # Налаштування завантаження з файлу .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True  # Змінні в .env мають бути великими літерами
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


# Створюємо один екземпляр для всього додатку
settings = Settings()
