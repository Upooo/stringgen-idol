"""Session generation handlers — full phone / OTP / 2FA flow."""

from __future__ import annotations

import logging
import re

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from src.bot.keyboards.session import (
    cancel_keyboard,
    framework_keyboard,
    main_menu_keyboard,
    success_keyboard,
)
from src.services.session_service import session_service
from src.services.state import LoginStep

logger = logging.getLogger(__name__)

router = Router(name="session")

# Simple phone validation (E.164-ish)
PHONE_RE = re.compile(r"^\+?[1-9]\d{6,14}$")


def _main_menu_text() -> str:
    return (
        "🤖 <b>STRIDOLBot</b>\n\n"
        "Telegram String Session Generator\n\n"
        "Generate a session for your preferred Telegram framework.\n\n"
        "<b>Supported frameworks:</b>\n"
        "• Telethon\n"
        "• Pyrogram v2"
    )


@router.callback_query(F.data == "generate_session")
async def on_generate_session(callback: CallbackQuery) -> None:
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
    await _handle_framework_selection(callback, "telethon", "Telethon")


@router.callback_query(F.data == "framework:pyrogram")
async def on_framework_pyrogram(callback: CallbackQuery) -> None:
    await _handle_framework_selection(callback, "pyrogram", "Pyrogram v2")


async def _handle_framework_selection(
    callback: CallbackQuery, framework: str, label: str
) -> None:
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

    await callback.message.edit_text(
        f"🔐 <b>{label}</b>\n\n"
        "Please send your phone number in international format.\n"
        "Example: <code>+6281234567890</code>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML",
    )
    # Move to awaiting phone
    session_service.get_state(user_id)  # ensure exists
    from src.services.state import state_manager
    state_manager.update(user_id, step=LoginStep.AWAITING_PHONE)
    await callback.answer()


@router.callback_query(F.data == "cancel_generation")
async def on_cancel_callback(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id if callback.from_user else None
    if user_id is None:
        await callback.answer()
        return

    cancelled = await session_service.cancel_generation(user_id)
    text = (
        "✅ Session generation cancelled.\n\nReturning to main menu."
        if cancelled
        else "No active session generation to cancel."
    )
    await callback.message.edit_text(
        text,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(Command("cancel"))
async def cmd_cancel(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else None
    if user_id is None:
        return

    cancelled = await session_service.cancel_generation(user_id)
    text = (
        "✅ Session generation cancelled.\n\nReturning to main menu."
        if cancelled
        else "No active session generation to cancel."
    )
    await message.answer(text, reply_markup=main_menu_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "main_menu")
async def on_main_menu(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id if callback.from_user else None
    if user_id is not None:
        await session_service.cancel_generation(user_id)

    await callback.message.edit_text(
        _main_menu_text(),
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "delete_message")
async def on_delete_message(callback: CallbackQuery) -> None:
    try:
        await callback.message.delete()
    except Exception:
        await callback.answer("Could not delete message.", show_alert=True)
        return
    await callback.answer()


@router.message()
async def on_text_message(message: Message) -> None:
    """Handle phone / OTP / 2FA password input based on current step."""
    user_id = message.from_user.id if message.from_user else None
    if user_id is None:
        return

    state = session_service.get_state(user_id)
    if state is None:
        await message.answer(
            "Please use the buttons below or send /start to begin.",
            reply_markup=main_menu_keyboard(),
        )
        return

    text = (message.text or "").strip()

    try:
        if state.step == LoginStep.AWAITING_PHONE:
            await _handle_phone(message, user_id, text)
        elif state.step == LoginStep.AWAITING_CODE:
            await _handle_code(message, user_id, text)
        elif state.step == LoginStep.AWAITING_PASSWORD:
            await _handle_password(message, user_id, text)
        else:
            await message.answer(
                "Please follow the current instructions or press ❌ Cancel.",
                reply_markup=cancel_keyboard(),
            )
    except ValueError as exc:
        # Safe user-facing error (no secrets)
        await message.answer(
            f"❌ {exc}\n\nYou can try again or press ❌ Cancel.",
            reply_markup=cancel_keyboard(),
        )
    except Exception:
        logger.exception("unexpected error in session flow user_id=%s", user_id)
        await session_service.cancel_generation(user_id)
        await message.answer(
            "❌ Authentication failed.\n\nPlease restart the process and try again.",
            reply_markup=main_menu_keyboard(),
        )


async def _handle_phone(message: Message, user_id: int, phone: str) -> None:
    # Normalize
    phone = phone.replace(" ", "").replace("-", "")
    if not phone.startswith("+"):
        phone = "+" + phone

    if not PHONE_RE.match(phone):
        await message.answer(
            "❌ Invalid phone number format.\n"
            "Please use international format, e.g. <code>+6281234567890</code>",
            reply_markup=cancel_keyboard(),
            parse_mode="HTML",
        )
        return

    await message.answer("⏳ Sending verification code...")
    await session_service.request_code(user_id, phone)

    await message.answer(
        "✅ Code sent!\n\n"
        "Please enter the verification code you received.",
        reply_markup=cancel_keyboard(),
    )


async def _handle_code(message: Message, user_id: int, code: str) -> None:
    code = code.replace(" ", "").replace("-", "")
    if not code.isdigit() or not (4 <= len(code) <= 8):
        await message.answer(
            "❌ Invalid verification code.\nPlease try again.",
            reply_markup=cancel_keyboard(),
        )
        return

    await message.answer("⏳ Verifying code...")
    needs_password = await session_service.submit_code(user_id, code)

    if needs_password:
        await message.answer(
            "🔐 Two-factor authentication is enabled.\n\n"
            "Please enter your 2FA password.",
            reply_markup=cancel_keyboard(),
        )
        return

    # Success — no 2FA
    await _deliver_session(message, user_id)


async def _handle_password(message: Message, user_id: int, password: str) -> None:
    if not password:
        await message.answer(
            "❌ Password cannot be empty.\nPlease try again.",
            reply_markup=cancel_keyboard(),
        )
        return

    await message.answer("⏳ Verifying 2FA password...")
    await session_service.submit_password(user_id, password)
    await _deliver_session(message, user_id)


async def _deliver_session(message: Message, user_id: int) -> None:
    """Generate session string, provide copy button, then cleanup."""
    try:
        session_str = await session_service.get_session_string(user_id)
    except Exception:
        logger.exception("failed to get session string user_id=%s", user_id)
        await session_service.cancel_generation(user_id)
        await message.answer(
            "❌ Failed to generate session.\n\nPlease restart and try again.",
            reply_markup=main_menu_keyboard(),
        )
        return

    # Deliver session (never log it)
    text = (
        "✅ <b>Session Generated</b>\n\n"
        "Your session has been generated successfully.\n\n"
        "📋 Use the button below to copy your session.\n\n"
        "⚠️ <b>SECURITY WARNING</b>\n"
        "This session is highly sensitive.\n"
        "Anyone who obtains it may be able to access your Telegram account.\n\n"
        "Never share it publicly."
    )

    await message.answer(
        text,
        reply_markup=success_keyboard(session_str),
        parse_mode="HTML",
    )

    # Cleanup immediately after delivery
    await session_service.finish_and_cleanup(user_id)
