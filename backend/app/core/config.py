from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import PostgresDsn, RedisDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "RegWatch"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    api_prefix: str = "/api/v1"
    allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    api_key: SecretStr = SecretStr("regwatch-dev-key-change-in-production")
    jwt_secret: SecretStr = SecretStr("change-me-in-production")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    database_url: PostgresDsn = PostgresDsn(
        "postgresql+asyncpg://regwatch:regwatch@localhost:5432/regwatch"
    )
    database_sync_url: str = "postgresql://regwatch:regwatch@localhost:5432/regwatch"

    redis_url: RedisDsn = RedisDsn("redis://localhost:6379/0")

    anthropic_api_key: SecretStr | None = None
    anthropic_model: str = "claude-sonnet-4-20250514"

    pinecone_api_key: SecretStr | None = None
    pinecone_environment: str | None = None
    pinecone_index_name: str = "regwatch"
    pinecone_dimension: int = 1536

    resend_api_key: SecretStr | None = None
    slack_webhook_url: str | None = None
    notification_email_from: str = "regwatch@example.com"

    playwright_headless: bool = True
    scrapyd_timeout_seconds: int = 30
    max_concurrent_scrapes: int = 5

    scheduler_watcher_interval_hours: int = 24
    scheduler_full_pipeline_interval_hours: int = 168

    log_level: str = "INFO"
    sentry_dsn: str | None = None

    @field_validator("database_url", mode="before")
    @classmethod
    def validate_db_url(cls, v: str | object) -> str:
        if isinstance(v, str):
            if not v.startswith("postgresql"):
                v = f"postgresql+asyncpg://{v.split('://')[1]}"
            return v
        return str(v)


settings = Settings()
