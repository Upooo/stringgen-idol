"""Tests for configuration loading and validation."""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.config import Settings, get_settings


class TestSettings:
    """Unit tests for Settings / get_settings."""

    def test_valid_configuration(self) -> None:
        """Settings load successfully with required BOT_TOKEN."""
        env = {
            "BOT_TOKEN": "123456:ABC-DEF",
            "ENVIRONMENT": "development",
            "LOG_LEVEL": "INFO",
        }
        with patch.dict(os.environ, env, clear=True):
            get_settings.cache_clear()
            settings = Settings(_env_file=None)  # type: ignore[call-arg]
            assert settings.bot_token == "123456:ABC-DEF"
            assert settings.environment == "development"
            assert settings.log_level == "INFO"
            assert settings.is_development is True
            assert settings.is_production is False

    def test_missing_bot_token_raises(self) -> None:
        """Missing BOT_TOKEN must raise ValidationError."""
        with patch.dict(os.environ, {}, clear=True):
            get_settings.cache_clear()
            with pytest.raises(ValidationError) as exc_info:
                Settings(_env_file=None)  # type: ignore[call-arg]
            assert "bot_token" in str(exc_info.value).lower()

    def test_empty_bot_token_raises(self) -> None:
        """Empty BOT_TOKEN must raise ValidationError."""
        with patch.dict(os.environ, {"BOT_TOKEN": "   "}, clear=True):
            get_settings.cache_clear()
            with pytest.raises(ValidationError):
                Settings(_env_file=None)  # type: ignore[call-arg]

    def test_optional_api_credentials_default_to_none(self) -> None:
        """API ID/Hash are optional at config load time."""
        env = {"BOT_TOKEN": "123456:ABC-DEF"}
        with patch.dict(os.environ, env, clear=True):
            get_settings.cache_clear()
            settings = Settings(_env_file=None)  # type: ignore[call-arg]
            assert settings.telethon_api_id is None
            assert settings.telethon_api_hash is None
            assert settings.pyrogram_api_id is None
            assert settings.pyrogram_api_hash is None

    def test_api_credentials_loaded_when_present(self) -> None:
        """API credentials are loaded when provided."""
        env = {
            "BOT_TOKEN": "123456:ABC-DEF",
            "TELETHON_API_ID": "12345",
            "TELETHON_API_HASH": "abcdef0123456789",
            "PYROGRAM_API_ID": "54321",
            "PYROGRAM_API_HASH": "fedcba9876543210",
        }
        with patch.dict(os.environ, env, clear=True):
            get_settings.cache_clear()
            settings = Settings(_env_file=None)  # type: ignore[call-arg]
            assert settings.telethon_api_id == 12345
            assert settings.telethon_api_hash == "abcdef0123456789"
            assert settings.pyrogram_api_id == 54321
            assert settings.pyrogram_api_hash == "fedcba9876543210"

    def test_log_level_and_environment_defaults(self) -> None:
        """Defaults for LOG_LEVEL and ENVIRONMENT are applied."""
        env = {"BOT_TOKEN": "123456:ABC-DEF"}
        with patch.dict(os.environ, env, clear=True):
            get_settings.cache_clear()
            settings = Settings(_env_file=None)  # type: ignore[call-arg]
            assert settings.log_level == "INFO"
            assert settings.environment == "development"
