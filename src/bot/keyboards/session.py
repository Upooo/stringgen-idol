"""Keyboards related to session generation flow."""

from aiogram.types import (
    CopyTextButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔐 Generate String Session",
                    callback_data="generate_session",
                )
            ]
        ]
    )


def framework_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Telethon",
                    callback_data="framework:telethon",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Pyrogram v2",
                    callback_data="framework:pyrogram",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Main Menu",
                    callback_data="main_menu",
                )
            ],
        ]
    )


def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Cancel",
                    callback_data="cancel_generation",
                )
            ]
        ]
    )


def success_keyboard(session_string: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📋 Copy Session",
                    copy_text=CopyTextButton(
                        text=session_string,
                    ),
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Delete Message",
                    callback_data="delete_message",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Generate Another",
                    callback_data="generate_session",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Main Menu",
                    callback_data="main_menu",
                )
            ],
        ]
    )
