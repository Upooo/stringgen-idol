"""In-memory session state management for login flow."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

# Default timeout for an active login session (10 minutes)
DEFAULT_STATE_TTL_SECONDS = 600


class LoginStep(str, Enum):
    """Current step in the login flow."""

    FRAMEWORK_SELECTED = "framework_selected"
    AWAITING_PHONE = "awaiting_phone"
    AWAITING_CODE = "awaiting_code"
    AWAITING_PASSWORD = "awaiting_password"
    COMPLETED = "completed"


@dataclass
class LoginState:
    """Temporary state for a single user's session generation process."""

    user_id: int
    framework: str  # "telethon" | "pyrogram"
    step: LoginStep = LoginStep.FRAMEWORK_SELECTED
    phone: str | None = None
    # Temporary client reference (Telethon/Pyrogram client). Cleared on cleanup.
    client: Any = field(default=None, repr=False)
    # Extra data needed by generators (e.g. phone_code_hash)
    extra: dict[str, Any] = field(default_factory=dict, repr=False)
    created_at: float = field(default_factory=time.time)
    expires_at: float = field(default=0.0)

    def __post_init__(self) -> None:
        if self.expires_at == 0.0:
            self.expires_at = self.created_at + DEFAULT_STATE_TTL_SECONDS

    @property
    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def touch(self, ttl: int = DEFAULT_STATE_TTL_SECONDS) -> None:
        """Extend expiration."""
        self.expires_at = time.time() + ttl


class StateManager:
    """In-memory store for LoginState, keyed by Telegram user ID.

    Guarantees:
    - One active state per user_id
    - Isolation between users
    - Automatic cleanup of expired states
    """

    def __init__(self) -> None:
        self._states: dict[int, LoginState] = {}

    def create(
        self,
        user_id: int,
        framework: str,
        ttl: int = DEFAULT_STATE_TTL_SECONDS,
    ) -> LoginState:
        """Create a new state. Raises if user already has an active non-expired state."""
        existing = self.get(user_id)
        if existing is not None and not existing.is_expired:
            raise ValueError("User already has an active session generation process")

        # Clean any leftover
        self.delete(user_id)

        state = LoginState(
            user_id=user_id,
            framework=framework,
            expires_at=time.time() + ttl,
        )
        self._states[user_id] = state
        logger.info(
            "session_generation_started user_id=%s framework=%s",
            user_id,
            framework,
        )
        return state

    def get(self, user_id: int) -> LoginState | None:
        """Return state if exists and not expired, else None (and cleanup)."""
        state = self._states.get(user_id)
        if state is None:
            return None
        if state.is_expired:
            logger.info("session_generation_timeout user_id=%s", user_id)
            self.delete(user_id)
            return None
        return state

    def update(self, user_id: int, **kwargs: Any) -> LoginState | None:
        """Update fields on an existing state. Returns None if no active state."""
        state = self.get(user_id)
        if state is None:
            return None
        for key, value in kwargs.items():
            if hasattr(state, key):
                setattr(state, key, value)
        state.touch()
        return state

    def delete(self, user_id: int) -> None:
        """Remove state and cleanup any temporary client."""
        state = self._states.pop(user_id, None)
        if state is None:
            return
        # Cleanup client if present
        client = state.client
        state.client = None
        state.extra.clear()
        if client is not None:
            try:
                # Best-effort disconnect (async clients handled by caller usually)
                if hasattr(client, "disconnect"):
                    # We cannot await here; caller should disconnect before delete when possible
                    pass
            except Exception:
                logger.exception("error during client cleanup user_id=%s", user_id)
        logger.debug("state deleted user_id=%s", user_id)

    def has_active(self, user_id: int) -> bool:
        return self.get(user_id) is not None

    def cleanup_expired(self) -> int:
        """Remove all expired states. Returns number of cleaned states."""
        now = time.time()
        expired_ids = [
            uid for uid, st in self._states.items() if st.expires_at <= now
        ]
        for uid in expired_ids:
            logger.info("session_generation_timeout user_id=%s", uid)
            self.delete(uid)
        return len(expired_ids)


# Global singleton for the bot process
state_manager = StateManager()
