"""Application settings loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Centralized configuration for the FastAPI backend."""

    app_name: str = "Mental Health Assistant API"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    environment: str = "development"
    debug: bool = False

    database_url: str = Field(..., alias="DATABASE_URL")

    secret_key: str = Field(..., alias="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    password_reset_token_expire_minutes: int = 30

    backend_cors_origins: list[str] = Field(default_factory=list)
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-5-mini", alias="OPENAI_MODEL")
    openai_max_output_tokens: int = 420
    assistant_max_context_messages: int = 12
    scheduler_enabled: bool = True
    scheduler_run_in_debug: bool = False
    azure_demo_mode: bool = False
    appointment_reminder_interval_minutes: int = 15
    appointment_reminder_lead_hours: int = 24
    appointment_booking_min_notice_hours: int = 2
    appointment_cancellation_cutoff_hours: int = 2
    appointment_reschedule_cutoff_hours: int = 4
    critical_alert_suggestion_lookahead_days: int = 7
    critical_alert_suggestion_limit: int = 5
    critical_alert_slots_per_specialist: int = 2
    critical_alert_recent_window_hours: int = 72

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("debug", mode="before")
    @classmethod
    def normalize_debug_value(cls, value: object) -> object:
        """Treat leaked logging-level env vars as disabled debug mode."""

        if not isinstance(value, str):
            return value

        normalized = value.strip().lower()
        if normalized in {"warn", "warning", "info", "error", "critical"}:
            return False
        if normalized == "debug":
            return True
        return value


@lru_cache
def get_settings() -> Settings:
    """Build and cache application settings from the environment."""

    return Settings()  # pyright: ignore[reportCallIssue]


settings = get_settings()
