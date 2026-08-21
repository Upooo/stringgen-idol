"""Session generation handlers (framework selection stub for Phase 1)."""

import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from src.bot.keyboards.session import (
    framework_keyboard,
    main_menu_keyboard,
)

logger = logging.getLogger(__name__)

router = Router(name="session")


@router.callback_query(F.data == "generate_session")
async def on_generate_session(callback: CallbackQuery) -> None:
    """User pressed 'Generate String Session' — show framework selection."""
    user_id = callback.from_user.id if callback.from_user else None
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
    """Telethon selected (Phase 1: placeholder only)."""
    user_id = callback.from_user.id if callback.from_user else None
    logger.info("framework_selected user_id=%s framework=telethon", user_id)

    await callback.message.edit_text(
        "🔐 <b>Telethon</b>\n\n"
        "Telethon session generation will be available in the next phase.\n\n"
        "Please check back later.",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "framework:pyrogram")
async def on_framework_pyrogram(callback: CallbackQuery) -> None:
    """Pyrogram v2 selected (Phase 1: placeholder only)."""
    user_id = callback.from_user.id if callback.from_user else None
    logger.info("framework_selected user_id=%s framework=pyrogram", user_id)

    await callback.message.edit_text(
        "🔐 <b>Pyrogram v2</b>\n\n"
        "Pyrogram v2 session generation will be available in the next phase.\n\n"
        "Please check back later.",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "main_menu")
async def on_main_menu(callback: CallbackQuery) -> None:
    """Return to main menu."""
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
    """Handle unexpected text messages during Phase 1."""
    await message.answer(
        "Please use the buttons below or send /start to begin.",
        reply_markup=main_menu_keyboard(),
    )
