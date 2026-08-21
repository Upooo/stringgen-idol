"""Bot handlers."""

from aiogram import Router

from src.bot.handlers.start import router as start_router
from src.bot.handlers.session import router as session_router


def setup_routers() -> Router:
    """Assemble and return the root router with all handlers."""
    root = Router(name="root")
    root.include_router(start_router)
    root.include_router(session_router)
    return root
