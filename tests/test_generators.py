"""Tests for session generators."""

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


class TestTelethonGenerator:
    def test_init(self) -> None:
        gen = TelethonSessionGenerator(api_id=12345, api_hash="hash")
        assert gen.framework_name == "telethon"

    @pytest.mark.asyncio
    async def test_cleanup_without_client(self) -> None:
        gen = TelethonSessionGenerator(api_id=12345, api_hash="hash")
        await gen.cleanup()  # should not raise


class TestPyrogramGenerator:
    def test_init(self) -> None:
        gen = PyrogramSessionGenerator(api_id=12345, api_hash="hash")
        assert gen.framework_name == "pyrogram"

    @pytest.mark.asyncio
    async def test_cleanup_without_client(self) -> None:
        gen = PyrogramSessionGenerator(api_id=12345, api_hash="hash")
        await gen.cleanup()  # should not raise
