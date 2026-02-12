from __future__ import annotations

"""Custom exceptions for the go2.gg SDK."""

from dataclasses import dataclass
from typing import Any


class Go2Error(Exception):
    """Base error for the go2.gg SDK."""


@dataclass
class APIError(Go2Error):
    """HTTP error returned by the API."""

    status_code: int
    message: str
    error_code: str | None = None
    details: dict[str, Any] | None = None

    def __str__(self) -> str:
        code = f" ({self.error_code})" if self.error_code else ""
        return f"HTTP {self.status_code}{code}: {self.message}"


class RequestError(Go2Error):
    """Network/transport error when calling the API."""
