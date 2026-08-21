"""Session generation service — orchestrates state and generators."""

from __future__ import annotations

import logging
from typing import Any

from src.config import get_settings
from src.generators.base import BaseSessionGenerator
from src.generators.pyrogram import PyrogramSessionGenerator
from src.generators.telethon import TelethonSessionGenerator
from src.services.state import LoginState, LoginStep, state_manager

logger = logging.getLogger(__name__)


class SessionService:
    """High-level API for the login / session generation flow."""

    def __init__(self) -> None:
        self._state_manager = state_manager

    def has_active_process(self, user_id: int) -> bool:
        return self._state_manager.has_active(user_id)

    def start_generation(self, user_id: int, framework: str) -> LoginState:
        """Start a new generation process. Raises ValueError if already active."""
        if framework not in ("telethon", "pyrogram"):
            raise ValueError(f"Unsupported framework: {framework}")
        return self._state_manager.create(user_id=user_id, framework=framework)

    def get_state(self, user_id: int) -> LoginState | None:
        return self._state_manager.get(user_id)

    def _build_generator(self, framework: str) -> BaseSessionGenerator:
        settings = get_settings()
        if framework == "telethon":
            if not settings.telethon_api_id or not settings.telethon_api_hash:
                raise ValueError(
                    "Telethon API credentials are not configured. "
                    "Set TELETHON_API_ID and TELETHON_API_HASH."
                )
            return TelethonSessionGenerator(
                api_id=settings.telethon_api_id,
                api_hash=settings.telethon_api_hash,
            )
        if framework == "pyrogram":
            if not settings.pyrogram_api_id or not settings.pyrogram_api_hash:
                raise ValueError(
                    "Pyrogram API credentials are not configured. "
                    "Set PYROGRAM_API_ID and PYROGRAM_API_HASH."
                )
            return PyrogramSessionGenerator(
                api_id=settings.pyrogram_api_id,
                api_hash=settings.pyrogram_api_hash,
            )
        raise ValueError(f"Unsupported framework: {framework}")

    async def request_code(self, user_id: int, phone: str) -> None:
        """Start login: send OTP to phone."""
        state = self._state_manager.get(user_id)
        if state is None:
            raise ValueError("No active session generation.")

        generator = self._build_generator(state.framework)
        result = await generator.start_login(phone)

        self._state_manager.update(
            user_id,
            phone=phone,
            step=LoginStep.AWAITING_CODE,
            client=generator,
        )
        # store phone_code_hash inside generator; also mirror in extra if needed
        state = self._state_manager.get(user_id)
        if state:
            state.extra["phone_code_hash"] = result.get("phone_code_hash")

    async def submit_code(self, user_id: int, code: str) -> bool:
        """Submit OTP. Returns True if 2FA is still needed."""
        state = self._state_manager.get(user_id)
        if state is None or state.client is None:
            raise ValueError("No active session generation.")

        generator: BaseSessionGenerator = state.client
        result = await generator.submit_code(code)

        if result.get("needs_password"):
            self._state_manager.update(user_id, step=LoginStep.AWAITING_PASSWORD)
            return True

        # No 2FA — session is ready
        self._state_manager.update(user_id, step=LoginStep.COMPLETED)
        return False

    async def submit_password(self, user_id: int, password: str) -> None:
        """Submit 2FA password."""
        state = self._state_manager.get(user_id)
        if state is None or state.client is None:
            raise ValueError("No active session generation.")

        generator: BaseSessionGenerator = state.client
        await generator.submit_password(password)
        self._state_manager.update(user_id, step=LoginStep.COMPLETED)

    async def get_session_string(self, user_id: int) -> str:
        """Return session string and mark completed."""
        state = self._state_manager.get(user_id)
        if state is None or state.client is None:
            raise ValueError("No active session generation.")
        if state.step != LoginStep.COMPLETED:
            raise ValueError("Login not completed yet.")

        generator: BaseSessionGenerator = state.client
        session_str = await generator.get_session_string()
        return session_str

    async def finish_and_cleanup(self, user_id: int) -> None:
        """Cleanup after successful generation."""
        state = self._state_manager.get(user_id)
        if state and state.client is not None:
            try:
                await state.client.cleanup()
            except Exception:
                logger.debug("cleanup error user_id=%s", user_id, exc_info=True)
        self._state_manager.delete(user_id)
        logger.info("session_generation_completed user_id=%s", user_id)

    async def cancel_generation(self, user_id: int) -> bool:
        """Cancel active process, disconnect client, clear state."""
        state = self._state_manager.get(user_id)
        if state is None:
            return False

        if state.client is not None:
            try:
                await state.client.cleanup()
            except Exception:
                logger.exception(
                    "error during cancel cleanup user_id=%s", user_id
                )

        self._state_manager.delete(user_id)
        logger.info("session_generation_cancelled user_id=%s", user_id)
        return True

    def cleanup_expired(self) -> int:
        return self._state_manager.cleanup_expired()


session_service = SessionService()
