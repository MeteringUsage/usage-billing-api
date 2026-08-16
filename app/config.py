"""Runtime settings for the HTTP service."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

DbBackend = Literal["sql", "sqlite", "postgres", "postgresql"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="USAGE_BILLING_",
        env_file=".env",
        extra="ignore",
    )

    db_backend: DbBackend = "sql"
    database: str = "usage_billing.db"
    database_url: str | None = None
    ensure_schema: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    invoice_files: str = "invoice_files"


@lru_cache
def get_settings() -> Settings:
    return Settings()
