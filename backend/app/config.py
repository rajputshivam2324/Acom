"""
Application configuration loaded from environment variables.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://acom:acom_secret@localhost:5432/acom_db"
    SYNC_DATABASE_URL: str = "postgresql://acom:acom_secret@localhost:5432/acom_db"

    # AI Provider
    AI_PROVIDER: str = "openai"
    AI_BASE_URL: str = "https://api.openai.com/v1"
    AI_API_KEY: str = "sk-placeholder"
    AI_DEFAULT_MODEL: str = "gpt-4-turbo-preview"

    # App
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Security
    SECRET_KEY: str = "change-me-in-production"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
