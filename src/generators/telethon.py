"""Telethon session generator (stub for Phase 1)."""

from src.generators.base import BaseSessionGenerator


class TelethonSessionGenerator(BaseSessionGenerator):
    """Telethon StringSession generator. Full implementation in Phase 3."""

    framework_name = "telethon"

    async def start_login(self, phone: str) -> None:
        raise NotImplementedError("Telethon generator not implemented yet (Phase 3)")

    async def submit_code(self, code: str) -> None:
        raise NotImplementedError("Telethon generator not implemented yet (Phase 3)")

    async def submit_password(self, password: str) -> None:
        raise NotImplementedError("Telethon generator not implemented yet (Phase 3)")

    async def get_session_string(self) -> str:
        raise NotImplementedError("Telethon generator not implemented yet (Phase 3)")

    async def cleanup(self) -> None:
        """No-op cleanup for stub."""
        pass
