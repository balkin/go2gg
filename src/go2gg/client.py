from __future__ import annotations

"""Async client for the go2.gg Links API."""

import asyncio
import os
from types import TracebackType
from typing import Any

import aiohttp

from go2gg.exceptions import APIError, RequestError
from go2gg.resources import LinksAPI

DEFAULT_BASE_URL = "https://api.go2.gg/api/v1"
DEFAULT_TIMEOUT_TOTAL = 30.0
DEFAULT_TIMEOUT_CONNECT = 10.0
DEFAULT_TIMEOUT_SOCK_READ = 30.0
DEFAULT_TIMEOUT_SOCK_CONNECT = 10.0
DEFAULT_RETRY_DELAY = 0.5
DEFAULT_RETRY_STATUS_CODES = {429, 500, 502, 503, 504}


class Go2Client:
    """Async client for go2.gg API access.

    Args:
        api_key: API key for authentication. If omitted, uses GO2GG_API_KEY.
        base_url: API base URL.
        session: Optional shared aiohttp session.
        timeout: Optional aiohttp timeout for a managed session. Overrides individual timeout values.
        timeout_total: Total request timeout in seconds.
        timeout_connect: Connection timeout in seconds.
        timeout_sock_read: Socket read timeout in seconds.
        timeout_sock_connect: Socket connect timeout in seconds.
        user_agent: Optional User-Agent header.
        retry_count: Number of retry attempts for retryable failures.
        retry_delay: Base delay in seconds between retries.
        retry_backoff: Whether to apply exponential backoff to retry delays.
        retry_status_codes: HTTP status codes that should trigger retries.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        session: aiohttp.ClientSession | None = None,
        timeout: aiohttp.ClientTimeout | None = None,
        timeout_total: float = DEFAULT_TIMEOUT_TOTAL,
        timeout_connect: float = DEFAULT_TIMEOUT_CONNECT,
        timeout_sock_read: float = DEFAULT_TIMEOUT_SOCK_READ,
        timeout_sock_connect: float = DEFAULT_TIMEOUT_SOCK_CONNECT,
        user_agent: str | None = None,
        retry_count: int = 0,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        retry_backoff: bool = False,
        retry_status_codes: set[int] | None = None,
    ) -> None:
        """Initialize the client and configure authentication."""
        resolved_key = api_key or os.getenv("GO2GG_API_KEY")
        if not resolved_key:
            raise ValueError(
                "API key is required. Provide api_key or set GO2GG_API_KEY in the environment."
            )
        if not base_url:
            raise ValueError("base_url is required")

        self._api_key = resolved_key
        self._base_url = base_url.rstrip("/")
        resolved_timeout = timeout or aiohttp.ClientTimeout(
            total=timeout_total,
            connect=timeout_connect,
            sock_read=timeout_sock_read,
            sock_connect=timeout_sock_connect,
        )
        self._session = session or aiohttp.ClientSession(timeout=resolved_timeout)
        self._owns_session = session is None
        self._user_agent = user_agent
        self._retry_count = retry_count
        self._retry_delay = retry_delay
        self._retry_backoff = retry_backoff
        self._retry_status_codes = retry_status_codes or DEFAULT_RETRY_STATUS_CODES

        self.links = LinksAPI(self)

    async def __aenter__(self) -> "Go2Client":
        """Enter the async context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Exit the async context manager and close the session."""
        await self.close()

    async def close(self) -> None:
        """Close the underlying session if owned by this client."""
        if self._owns_session and not self._session.closed:
            await self._session.close()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send an HTTP request and return the decoded response payload."""
        url = f"{self._base_url}/{path.lstrip('/')}"
        headers = {"Authorization": f"Bearer {self._api_key}"}
        if self._user_agent:
            headers["User-Agent"] = self._user_agent

        for attempt in range(self._retry_count + 1):
            try:
                async with self._session.request(
                    method,
                    url,
                    params=params,
                    json=json,
                    headers=headers,
                ) as response:
                    if response.status == 204:
                        return {}

                    payload: Any
                    try:
                        payload = await response.json(content_type=None)
                    except aiohttp.ContentTypeError:
                        payload = {"message": await response.text()}

                    if response.status >= 400:
                        error = self._to_api_error(response.status, payload)
                        if self._should_retry(response.status, attempt):
                            await self._sleep_before_retry(attempt)
                            continue
                        raise error

                    if isinstance(payload, dict) and payload.get("success") is False:
                        raise self._to_api_error(response.status, payload)

                    if not isinstance(payload, dict):
                        return {"data": payload}

                    return payload
            except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
                if self._should_retry(None, attempt):
                    await self._sleep_before_retry(attempt)
                    continue
                raise RequestError(str(exc)) from exc

        raise RequestError("Request failed after retries.")

    def _should_retry(self, status_code: int | None, attempt: int) -> bool:
        if attempt >= self._retry_count:
            return False
        if status_code is None:
            return True
        return status_code in self._retry_status_codes

    async def _sleep_before_retry(self, attempt: int) -> None:
        if self._retry_delay <= 0:
            return
        delay = self._retry_delay
        if self._retry_backoff:
            delay *= 2 ** attempt
        await asyncio.sleep(delay)

    @staticmethod
    def _to_api_error(status: int, payload: Any) -> APIError:
        """Normalize API error payloads into APIError."""
        if isinstance(payload, dict):
            error = payload.get("error")
            message = (
                payload.get("message")
                or (error.get("message") if isinstance(error, dict) else None)
                or payload.get("error_description")
                or "Request failed"
            )
            code = (
                payload.get("code")
                or payload.get("errorCode")
                or (error.get("code") if isinstance(error, dict) else None)
            )
            details = (
                payload.get("details") if isinstance(payload.get("details"), dict) else None
            )
            return APIError(status_code=status, message=str(message), error_code=code, details=details)

        return APIError(status_code=status, message=str(payload), error_code=None, details=None)
