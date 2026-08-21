"""Tests for in-memory session state management."""

import time
from unittest.mock import AsyncMock

import pytest

from src.services.state import (
    DEFAULT_STATE_TTL_SECONDS,
    LoginState,
    LoginStep,
    StateManager,
)
from src.services.session_service import SessionService


class TestLoginState:
    def test_default_expiration(self) -> None:
        state = LoginState(user_id=1, framework="telethon")
        assert state.expires_at > state.created_at
        assert not state.is_expired

    def test_is_expired(self) -> None:
        state = LoginState(
            user_id=1,
            framework="telethon",
            created_at=time.time() - 1000,
            expires_at=time.time() - 10,
        )
        assert state.is_expired

    def test_touch_extends_expiration(self) -> None:
        state = LoginState(user_id=1, framework="telethon")
        old_exp = state.expires_at
        time.sleep(0.01)
        state.touch(ttl=DEFAULT_STATE_TTL_SECONDS + 100)  # longer than default
        assert state.expires_at > old_exp


class TestStateManager:
    def setup_method(self) -> None:
        self.mgr = StateManager()

    def test_create_and_get(self) -> None:
        state = self.mgr.create(user_id=42, framework="telethon")
        assert state.user_id == 42
        assert state.framework == "telethon"
        assert state.step == LoginStep.FRAMEWORK_SELECTED

        got = self.mgr.get(42)
        assert got is not None
        assert got.user_id == 42

    def test_user_isolation(self) -> None:
        self.mgr.create(user_id=1, framework="telethon")
        self.mgr.create(user_id=2, framework="pyrogram")

        s1 = self.mgr.get(1)
        s2 = self.mgr.get(2)
        assert s1 is not None and s1.framework == "telethon"
        assert s2 is not None and s2.framework == "pyrogram"
        assert s1 is not s2

    def test_cannot_create_second_active_state(self) -> None:
        self.mgr.create(user_id=1, framework="telethon")
        with pytest.raises(ValueError, match="already has an active"):
            self.mgr.create(user_id=1, framework="pyrogram")

    def test_delete_clears_state(self) -> None:
        self.mgr.create(user_id=1, framework="telethon")
        self.mgr.delete(1)
        assert self.mgr.get(1) is None

    def test_expired_state_is_cleaned_on_get(self) -> None:
        state = self.mgr.create(user_id=1, framework="telethon", ttl=1)
        state.expires_at = time.time() - 1  # force expire
        assert self.mgr.get(1) is None
        assert 1 not in self.mgr._states

    def test_cleanup_expired(self) -> None:
        self.mgr.create(user_id=1, framework="telethon", ttl=1)
        self.mgr.create(user_id=2, framework="pyrogram", ttl=9999)
        self.mgr._states[1].expires_at = time.time() - 1

        cleaned = self.mgr.cleanup_expired()
        assert cleaned == 1
        assert self.mgr.get(1) is None
        assert self.mgr.get(2) is not None

    def test_update(self) -> None:
        self.mgr.create(user_id=1, framework="telethon")
        updated = self.mgr.update(1, step=LoginStep.AWAITING_PHONE, phone="+123")
        assert updated is not None
        assert updated.step == LoginStep.AWAITING_PHONE
        assert updated.phone == "+123"

    def test_has_active(self) -> None:
        assert self.mgr.has_active(1) is False
        self.mgr.create(user_id=1, framework="telethon")
        assert self.mgr.has_active(1) is True
        self.mgr.delete(1)
        assert self.mgr.has_active(1) is False


class TestSessionService:
    def setup_method(self) -> None:
        # Use a fresh StateManager for isolation
        self.svc = SessionService()
        self.svc._state_manager = StateManager()

    def test_start_and_get(self) -> None:
        state = self.svc.start_generation(10, "telethon")
        assert state.framework == "telethon"
        assert self.svc.get_state(10) is not None

    def test_unsupported_framework(self) -> None:
        with pytest.raises(ValueError, match="Unsupported"):
            self.svc.start_generation(10, "gramjs")

    def test_one_active_per_user(self) -> None:
        self.svc.start_generation(10, "telethon")
        with pytest.raises(ValueError, match="already has an active"):
            self.svc.start_generation(10, "pyrogram")

    @pytest.mark.asyncio
    async def test_cancel_generation(self) -> None:
        self.svc.start_generation(10, "telethon")
        mock_client = AsyncMock()
        self.svc.set_client(10, mock_client)

        cancelled = await self.svc.cancel_generation(10)
        assert cancelled is True
        assert self.svc.get_state(10) is None
        mock_client.disconnect.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_cancel_when_none(self) -> None:
        cancelled = await self.svc.cancel_generation(999)
        assert cancelled is False
