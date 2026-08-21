"""Keyboards related to session generation flow."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu with Generate String Session button."""
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
    """Framework selection keyboard."""
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
