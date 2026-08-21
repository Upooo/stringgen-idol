"""Start command and main menu handlers."""

import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.bot.keyboards.session import main_menu_keyboard

logger = logging.getLogger(__name__)

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Handle /start — show welcome message and main menu."""
    user_id = message.from_user.id if message.from_user else None
    logger.info("bot_started user_id=%s", user_id)

    text = (
        "🤖 <b>STRIDOLBot</b>\n\n"
        "Telegram String Session Generator\n\n"
        "Generate a session for your preferred Telegram framework.\n\n"
        "<b>Supported frameworks:</b>\n"
        "• Telethon\n"
        "• Pyrogram v2"
    )
    await message.answer(
        text,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )
