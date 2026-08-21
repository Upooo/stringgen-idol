"""Tests for session generators (stubs in Phase 1)."""

import pytest

from src.generators.base import BaseSessionGenerator
from src.generators.pyrogram import PyrogramSessionGenerator
from src.generators.telethon import TelethonSessionGenerator


class TestBaseGenerator:
    def test_telethon_is_subclass(self) -> None:
        assert issubclass(TelethonSessionGenerator, BaseSessionGenerator)

    def test_pyrogram_is_subclass(self) -> None:
        assert issubclass(PyrogramSessionGenerator, BaseSessionGenerator)

    def test_framework_names(self) -> None:
        assert TelethonSessionGenerator.framework_name == "telethon"
        assert PyrogramSessionGenerator.framework_name == "pyrogram"


class TestTelethonStub:
    @pytest.mark.asyncio
    async def test_start_login_not_implemented(self) -> None:
        gen = TelethonSessionGenerator()
        with pytest.raises(NotImplementedError):
            await gen.start_login("+1234567890")

    @pytest.mark.asyncio
    async def test_submit_code_not_implemented(self) -> None:
        gen = TelethonSessionGenerator()
        with pytest.raises(NotImplementedError):
            await gen.submit_code("12345")

    @pytest.mark.asyncio
    async def test_submit_password_not_implemented(self) -> None:
        gen = TelethonSessionGenerator()
        with pytest.raises(NotImplementedError):
            await gen.submit_password("secret")

    @pytest.mark.asyncio
    async def test_get_session_string_not_implemented(self) -> None:
        gen = TelethonSessionGenerator()
        with pytest.raises(NotImplementedError):
            await gen.get_session_string()

    @pytest.mark.asyncio
    async def test_cleanup_is_noop(self) -> None:
        gen = TelethonSessionGenerator()
        await gen.cleanup()


class TestPyrogramStub:
    @pytest.mark.asyncio
    async def test_start_login_not_implemented(self) -> None:
        gen = PyrogramSessionGenerator()
        with pytest.raises(NotImplementedError):
            await gen.start_login("+1234567890")

    @pytest.mark.asyncio
    async def test_cleanup_is_noop(self) -> None:
        gen = PyrogramSessionGenerator()
        await gen.cleanup()
