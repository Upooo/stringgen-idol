"""Pyrogram v2 session generator."""

from __future__ import annotations

import logging
from typing import Any

from pyrogram import Client
from pyrogram.errors import (
    FloodWait,
    PhoneCodeExpired,
    PhoneCodeInvalid,
    PhoneNumberInvalid,
    SessionPasswordNeeded,
)

from src.generators.base import BaseSessionGenerator

logger = logging.getLogger(__name__)


class PyrogramSessionGenerator(BaseSessionGenerator):
    """Generate Pyrogram session string via phone login."""

    framework_name = "pyrogram"

    def __init__(self, api_id: int, api_hash: str) -> None:
        self._api_id = api_id
        self._api_hash = api_hash
        self._client: Client | None = None
        self._phone: str | None = None
        self._phone_code_hash: str | None = None

    async def start_login(self, phone: str) -> dict[str, Any]:
        """Send login code to the given phone number."""
        self._phone = phone
        self._client = Client(
            name="stridol_temp",
            api_id=self._api_id,
            api_hash=self._api_hash,
            in_memory=True,
        )
        await self._client.connect()

        try:
            sent = await self._client.send_code(phone)
            self._phone_code_hash = sent.phone_code_hash
            return {"phone_code_hash": sent.phone_code_hash}
        except PhoneNumberInvalid as exc:
            await self.cleanup()
            raise ValueError("Invalid phone number.") from exc
        except FloodWait as exc:
            await self.cleanup()
            raise ValueError(
                f"Too many requests. Please wait {exc.value} seconds."
            ) from exc
        except Exception:
            await self.cleanup()
            logger.exception("pyrogram start_login failed")
            raise ValueError("Failed to send login code. Please try again.") from None

    async def submit_code(self, code: str) -> dict[str, Any]:
        """Submit the OTP. May indicate 2FA is required."""
        if not self._client or not self._phone or not self._phone_code_hash:
            raise ValueError("Login not started.")

        try:
            await self._client.sign_in(
                phone_number=self._phone,
                phone_code_hash=self._phone_code_hash,
                phone_code=code,
            )
            return {"needs_password": False}
        except SessionPasswordNeeded:
            return {"needs_password": True}
        except PhoneCodeInvalid as exc:
            raise ValueError("Invalid verification code.") from exc
        except PhoneCodeExpired as exc:
            await self.cleanup()
            raise ValueError("Verification code has expired. Please restart.") from exc
        except FloodWait as exc:
            raise ValueError(
                f"Too many requests. Please wait {exc.value} seconds."
            ) from exc
        except Exception:
            logger.exception("pyrogram submit_code failed")
            raise ValueError("Authentication failed. Please try again.") from None

    async def submit_password(self, password: str) -> dict[str, Any]:
        """Submit 2FA password."""
        if not self._client:
            raise ValueError("Login not started.")

        try:
            await self._client.check_password(password)
            return {"ok": True}
        except Exception:
            # Pyrogram raises various errors; treat as invalid password
            logger.exception("pyrogram submit_password failed")
            raise ValueError("Invalid 2FA password.") from None

    async def get_session_string(self) -> str:
        """Return the generated session string."""
        if not self._client:
            raise ValueError("Client not connected.")
        return await self._client.export_session_string()

    async def cleanup(self) -> None:
        """Disconnect and clear sensitive data."""
        if self._client is not None:
            try:
                await self._client.disconnect()
            except Exception:
                logger.debug("pyrogram cleanup disconnect error", exc_info=True)
            finally:
                self._client = None
        self._phone = None
        self._phone_code_hash = None
