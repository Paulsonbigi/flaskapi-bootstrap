from functools import lru_cache

from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="app/.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = os.getenv("APP_NAME")
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = os.getenv("APP_ENVIRONMENT")

    # Database
    database_url: str = os.getenv("DATABASE_URL")
    database_pool_size: int = os.getenv("DATABASE_POOL_SIZE")
    database_max_overflow: int = os.getenv("DATABASE_MAX_FLOW")

    # Authentication
    secret_key: str = os.getenv("SECRET_KEY")
    access_token_expire_minutes: int = os.getenv("ACCESS_TOKEN_EXPIRATION")
    refresh_token_expire_days: int = os.getenv("REFRESH_TOKEN_EXPIRATION")

    # External Services
    redis_url: str = os.getenv("REDIS_URL")

    # CORS
    allowed_origins: list[str] = ["http://localhost:3000"]

    @property
    def async_database_url(self) -> str:
        return self.database_url.replace(
            "postgresql://", "postgresql+asyncpg://"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()