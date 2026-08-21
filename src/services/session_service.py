"""Session generation service (stub for Phase 1)."""

from typing import Any


class SessionService:
    """Orchestrates session generation flow. Full implementation in Phase 2+."""

    def __init__(self) -> None:
        pass

    async def start_generation(self, user_id: int, framework: str) -> None:
        raise NotImplementedError("SessionService not fully implemented yet (Phase 2)")

    async def cancel_generation(self, user_id: int) -> None:
        raise NotImplementedError("SessionService not fully implemented yet (Phase 2)")

    def get_active_state(self, user_id: int) -> Any | None:
        return None
