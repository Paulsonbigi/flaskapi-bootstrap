import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        # env_file_encoding="utf-8",
        # case_sensitive=False,
    )
    # alpha_vantage_base_url: str

    # Application
    app_name: str
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str

    # Database
    database_url: str
    database_pool_size: int
    database_max_overflow: int

    # Authentication
    secret_key: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    # External Services
    redis_url: str

    # CORS
    allowed_origins: list[str] = ["http://localhost:3000"]

    # integrations
    alpha_vantage_base_url: str 
    alpha_vantage_api_key: str = os.getenv('ALPHA_VANTAGE_API_KEY')

    @property
    def async_database_url(self) -> str:
        return self.database_url.replace(
            "postgresql://", "postgresql+asyncpg://"
        )


# @lru_cache
def get_settings() -> Settings:
    return Settings()