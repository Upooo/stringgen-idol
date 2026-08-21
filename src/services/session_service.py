"""Session generation service — orchestrates state and generators."""

from __future__ import annotations

import logging
from typing import Any

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

    def set_step(self, user_id: int, step: LoginStep) -> LoginState | None:
        return self._state_manager.update(user_id, step=step)

    def set_phone(self, user_id: int, phone: str) -> LoginState | None:
        return self._state_manager.update(
            user_id, phone=phone, step=LoginStep.AWAITING_CODE
        )

    def set_client(self, user_id: int, client: Any) -> LoginState | None:
        return self._state_manager.update(user_id, client=client)

    def set_extra(self, user_id: int, **kwargs: Any) -> LoginState | None:
        state = self._state_manager.get(user_id)
        if state is None:
            return None
        state.extra.update(kwargs)
        state.touch()
        return state

    async def cancel_generation(self, user_id: int) -> bool:
        """Cancel active process, disconnect client, clear state.

        Returns True if a process was cancelled, False if none was active.
        """
        state = self._state_manager.get(user_id)
        if state is None:
            return False

        client = state.client
        if client is not None:
            try:
                if hasattr(client, "disconnect"):
                    await client.disconnect()
            except Exception:
                logger.exception(
                    "error disconnecting client on cancel user_id=%s", user_id
                )

        self._state_manager.delete(user_id)
        logger.info("session_generation_cancelled user_id=%s", user_id)
        return True

    def cleanup_expired(self) -> int:
        return self._state_manager.cleanup_expired()


# Convenience singleton
session_service = SessionService()
