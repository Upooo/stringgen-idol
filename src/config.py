"""Centralized configuration using pydantic-settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Required
    bot_token: str = Field(..., description="Telegram Bot API token")

    # Environment
    environment: Literal["development", "production"] = Field(
        default="development",
        description="Runtime environment",
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )

    # Telethon credentials
    telethon_api_id: int | None = Field(default=None, description="Telegram API ID for Telethon")
    telethon_api_hash: str | None = Field(
        default=None, description="Telegram API Hash for Telethon"
    )

    # Pyrogram credentials
    pyrogram_api_id: int | None = Field(default=None, description="Telegram API ID for Pyrogram")
    pyrogram_api_hash: str | None = Field(
        default=None, description="Telegram API Hash for Pyrogram"
    )

    @field_validator("bot_token")
    @classmethod
    def bot_token_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("BOT_TOKEN must not be empty")
        return v.strip()

    @field_validator("telethon_api_id", "pyrogram_api_id", mode="before")
    @classmethod
    def empty_str_to_none_int(cls, v: object) -> object:
        if v == "" or v is None:
            return None
        return v

    @field_validator("telethon_api_hash", "pyrogram_api_hash", mode="before")
    @classmethod
    def empty_str_to_none_str(cls, v: object) -> object:
        if v == "" or v is None:
            return None
        return v

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
