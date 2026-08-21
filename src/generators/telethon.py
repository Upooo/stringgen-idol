"""Telethon session generator."""

from __future__ import annotations

import logging
from typing import Any

from telethon import TelegramClient
from telethon.errors import (
    FloodWaitError,
    PasswordHashInvalidError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
)
from telethon.sessions import StringSession

from src.generators.base import BaseSessionGenerator

logger = logging.getLogger(__name__)


class TelethonSessionGenerator(BaseSessionGenerator):
    """Generate Telethon StringSession via phone login."""

    framework_name = "telethon"

    def __init__(self, api_id: int, api_hash: str) -> None:
        self._api_id = api_id
        self._api_hash = api_hash
        self._client: TelegramClient | None = None
        self._phone: str | None = None
        self._phone_code_hash: str | None = None

    async def start_login(self, phone: str) -> dict[str, Any]:
        """Send login code to the given phone number."""
        self._phone = phone
        self._client = TelegramClient(
            StringSession(),
            self._api_id,
            self._api_hash,
        )
        await self._client.connect()

        try:
            result = await self._client.send_code_request(phone)
            self._phone_code_hash = result.phone_code_hash
            return {"phone_code_hash": result.phone_code_hash}
        except PhoneNumberInvalidError as exc:
            await self.cleanup()
            raise ValueError("Invalid phone number.") from exc
        except FloodWaitError as exc:
            await self.cleanup()
            raise ValueError(
                f"Too many requests. Please wait {exc.seconds} seconds."
            ) from exc
        except Exception:
            await self.cleanup()
            logger.exception("telethon start_login failed")
            raise ValueError("Failed to send login code. Please try again.") from None

    async def submit_code(self, code: str) -> dict[str, Any]:
        """Submit the OTP. May raise if 2FA is required."""
        if not self._client or not self._phone or not self._phone_code_hash:
            raise ValueError("Login not started.")

        try:
            await self._client.sign_in(
                phone=self._phone,
                code=code,
                phone_code_hash=self._phone_code_hash,
            )
            return {"needs_password": False}
        except SessionPasswordNeededError:
            return {"needs_password": True}
        except PhoneCodeInvalidError as exc:
            raise ValueError("Invalid verification code.") from exc
        except PhoneCodeExpiredError as exc:
            await self.cleanup()
            raise ValueError("Verification code has expired. Please restart.") from exc
        except FloodWaitError as exc:
            raise ValueError(
                f"Too many requests. Please wait {exc.seconds} seconds."
            ) from exc
        except Exception:
            logger.exception("telethon submit_code failed")
            raise ValueError("Authentication failed. Please try again.") from None

    async def submit_password(self, password: str) -> dict[str, Any]:
        """Submit 2FA password."""
        if not self._client:
            raise ValueError("Login not started.")

        try:
            await self._client.sign_in(password=password)
            return {"ok": True}
        except PasswordHashInvalidError as exc:
            raise ValueError("Invalid 2FA password.") from exc
        except Exception:
            logger.exception("telethon submit_password failed")
            raise ValueError("Authentication failed. Please try again.") from None

    async def get_session_string(self) -> str:
        """Return the generated StringSession."""
        if not self._client or not self._client.is_connected():
            raise ValueError("Client not connected.")
        return self._client.session.save()

    async def cleanup(self) -> None:
        """Disconnect and clear sensitive data."""
        if self._client is not None:
            try:
                if self._client.is_connected():
                    await self._client.disconnect()
            except Exception:
                logger.debug("telethon cleanup disconnect error", exc_info=True)
            finally:
                self._client = None
        self._phone = None
        self._phone_code_hash = None
