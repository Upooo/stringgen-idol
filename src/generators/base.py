"""Base interface for session generators."""

from abc import ABC, abstractmethod
from typing import Any


class BaseSessionGenerator(ABC):
    """Abstract base class for framework-specific session generators."""

    framework_name: str

    @abstractmethod
    async def start_login(self, phone: str) -> Any:
        """Initiate login with the given phone number."""
        ...

    @abstractmethod
    async def submit_code(self, code: str) -> Any:
        """Submit the OTP / login code."""
        ...

    @abstractmethod
    async def submit_password(self, password: str) -> Any:
        """Submit 2FA password if required."""
        ...

    @abstractmethod
    async def get_session_string(self) -> str:
        """Return the generated session string."""
        ...

    @abstractmethod
    async def cleanup(self) -> None:
        """Disconnect client and clear sensitive data."""
        ...
