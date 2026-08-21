"""Pyrogram v2 session generator (stub for Phase 1)."""

from src.generators.base import BaseSessionGenerator


class PyrogramSessionGenerator(BaseSessionGenerator):
    """Pyrogram v2 session generator. Full implementation in Phase 4."""

    framework_name = "pyrogram"

    async def start_login(self, phone: str) -> None:
        raise NotImplementedError("Pyrogram generator not implemented yet (Phase 4)")

    async def submit_code(self, code: str) -> None:
        raise NotImplementedError("Pyrogram generator not implemented yet (Phase 4)")

    async def submit_password(self, password: str) -> None:
        raise NotImplementedError("Pyrogram generator not implemented yet (Phase 4)")

    async def get_session_string(self) -> str:
        raise NotImplementedError("Pyrogram generator not implemented yet (Phase 4)")

    async def cleanup(self) -> None:
        """No-op cleanup for stub."""
        pass
