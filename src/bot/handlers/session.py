"""Session generation handlers."""

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from src.bot.keyboards.session import (
    cancel_keyboard,
    framework_keyboard,
    main_menu_keyboard,
)
from src.services.session_service import session_service
from src.services.state import LoginStep

logger = logging.getLogger(__name__)

router = Router(name="session")


@router.callback_query(F.data == "generate_session")
async def on_generate_session(callback: CallbackQuery) -> None:
    """User pressed 'Generate String Session' — show framework selection."""
    user_id = callback.from_user.id if callback.from_user else None
    if user_id is None:
        await callback.answer("Unable to identify user.", show_alert=True)
        return

    # Enforce one active process per user
    if session_service.has_active_process(user_id):
        await callback.answer(
            "⚠️ You already have an active session generation.\n"
            "Finish or cancel the current process first.",
            show_alert=True,
        )
        return

    logger.info("session_generation_started user_id=%s", user_id)

    text = (
        "🔐 <b>Choose Framework</b>\n\n"
        "Select the framework you want to generate a session for."
    )
    await callback.message.edit_text(
        text,
        reply_markup=framework_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "framework:telethon")
async def on_framework_telethon(callback: CallbackQuery) -> None:
    """Telethon selected — create state (auth in Phase 3)."""
    await _handle_framework_selection(callback, "telethon")


@router.callback_query(F.data == "framework:pyrogram")
async def on_framework_pyrogram(callback: CallbackQuery) -> None:
    """Pyrogram v2 selected — create state (auth in Phase 4)."""
    await _handle_framework_selection(callback, "pyrogram")


async def _handle_framework_selection(callback: CallbackQuery, framework: str) -> None:
    user_id = callback.from_user.id if callback.from_user else None
    if user_id is None:
        await callback.answer("Unable to identify user.", show_alert=True)
        return

    if session_service.has_active_process(user_id):
        await callback.answer(
            "⚠️ You already have an active session generation.\n"
            "Finish or cancel the current process first.",
            show_alert=True,
        )
        return

    try:
        session_service.start_generation(user_id=user_id, framework=framework)
    except ValueError as exc:
        await callback.answer(str(exc), show_alert=True)
        return

    logger.info("framework_selected user_id=%s framework=%s", user_id, framework)

    label = "Telethon" if framework == "telethon" else "Pyrogram v2"
    await callback.message.edit_text(
        f"🔐 <b>{label}</b>\n\n"
        "Session generation for this framework will be available in the next phase.\n\n"
        "You can cancel the current process anytime.",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "cancel_generation")
async def on_cancel_callback(callback: CallbackQuery) -> None:
    """Cancel via inline button."""
    user_id = callback.from_user.id if callback.from_user else None
    if user_id is None:
        await callback.answer()
        return

    cancelled = await session_service.cancel_generation(user_id)
    if cancelled:
        text = "✅ Session generation cancelled.\n\nReturning to main menu."
    else:
        text = "No active session generation to cancel."

    await callback.message.edit_text(
        text,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(Command("cancel"))
async def cmd_cancel(message: Message) -> None:
    """Cancel via /cancel command."""
    user_id = message.from_user.id if message.from_user else None
    if user_id is None:
        return

    cancelled = await session_service.cancel_generation(user_id)
    if cancelled:
        text = "✅ Session generation cancelled.\n\nReturning to main menu."
    else:
        text = "No active session generation to cancel."

    await message.answer(
        text,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "main_menu")
async def on_main_menu(callback: CallbackQuery) -> None:
    """Return to main menu. Cancels any active process."""
    user_id = callback.from_user.id if callback.from_user else None
    if user_id is not None:
        await session_service.cancel_generation(user_id)

    text = (
        "🤖 <b>STRIDOLBot</b>\n\n"
        "Telegram String Session Generator\n\n"
        "Generate a session for your preferred Telegram framework.\n\n"
        "<b>Supported frameworks:</b>\n"
        "• Telethon\n"
        "• Pyrogram v2"
    )
    await callback.message.edit_text(
        text,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message()
async def fallback_message(message: Message) -> None:
    """Handle unexpected text messages."""
    user_id = message.from_user.id if message.from_user else None
    state = session_service.get_state(user_id) if user_id else None

    if state is not None:
        # User is in the middle of a flow (future phases will handle phone/code here)
        await message.answer(
            "Please follow the current instructions or press ❌ Cancel / send /cancel.",
            reply_markup=cancel_keyboard(),
        )
        return

    await message.answer(
        "Please use the buttons below or send /start to begin.",
        reply_markup=main_menu_keyboard(),
    )
