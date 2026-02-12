import asyncio

import aiohttp
import pytest
from aioresponses import aioresponses

from go2gg import Go2Client
from go2gg.exceptions import APIError

BASE_URL = "https://api.go2.gg/api/v1"


@pytest.mark.asyncio
async def test_default_timeouts_applied() -> None:
    async with Go2Client(api_key="test-key") as client:
        timeout = client._session.timeout
        assert timeout.total == 30.0
        assert timeout.connect == 10.0
        assert timeout.sock_read == 30.0
        assert timeout.sock_connect == 10.0


@pytest.mark.asyncio
async def test_custom_timeouts_override_defaults() -> None:
    async with Go2Client(
        api_key="test-key",
        timeout_total=5.0,
        timeout_connect=1.0,
        timeout_sock_read=2.0,
        timeout_sock_connect=3.0,
    ) as client:
        timeout = client._session.timeout
        assert timeout.total == 5.0
        assert timeout.connect == 1.0
        assert timeout.sock_read == 2.0
        assert timeout.sock_connect == 3.0


@pytest.mark.asyncio
async def test_no_retries_by_default() -> None:
    error_payload = {"success": False, "code": "SLUG_EXISTS", "message": "Already used"}

    with aioresponses() as mock:
        mock.post(f"{BASE_URL}/links", status=409, payload=error_payload)

        async with Go2Client(api_key="test-key") as client:
            with pytest.raises(APIError):
                await client.links.create(destination_url="https://example.com", slug="summer-sale")

        assert len(mock.requests[("POST", f"{BASE_URL}/links")]) == 1


@pytest.mark.asyncio
async def test_retries_enabled_success_after_failure() -> None:
    error_payload = {"message": "server error"}
    ok_payload = {
        "success": True,
        "data": {"id": "lnk_ok", "shortUrl": "https://go2.gg/ok"},
    }

    with aioresponses() as mock:
        mock.post(f"{BASE_URL}/links", status=500, payload=error_payload)
        mock.post(f"{BASE_URL}/links", status=200, payload=ok_payload)

        async with Go2Client(api_key="test-key", retry_count=1, retry_delay=0) as client:
            link = await client.links.create(destination_url="https://example.com")

        assert link.id == "lnk_ok"
        assert len(mock.requests[("POST", f"{BASE_URL}/links")]) == 2


@pytest.mark.asyncio
async def test_retry_backoff_increases_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    delays: list[float] = []

    async def fake_sleep(delay: float) -> None:
        delays.append(delay)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    error_payload = {"message": "server error"}
    ok_payload = {"success": True, "data": {"id": "lnk_ok", "shortUrl": "https://go2.gg/ok"}}

    with aioresponses() as mock:
        mock.post(f"{BASE_URL}/links", status=500, payload=error_payload)
        mock.post(f"{BASE_URL}/links", status=500, payload=error_payload)
        mock.post(f"{BASE_URL}/links", status=200, payload=ok_payload)

        async with Go2Client(
            api_key="test-key",
            retry_count=2,
            retry_delay=0.5,
            retry_backoff=True,
        ) as client:
            await client.links.create(destination_url="https://example.com")

    assert delays == [0.5, 1.0]


@pytest.mark.asyncio
async def test_retry_on_network_error() -> None:
    ok_payload = {
        "success": True,
        "data": {"id": "lnk_ok", "shortUrl": "https://go2.gg/ok"},
    }

    with aioresponses() as mock:
        mock.post(
            f"{BASE_URL}/links",
            exception=aiohttp.ClientConnectionError("boom"),
        )
        mock.post(f"{BASE_URL}/links", status=200, payload=ok_payload)

        async with Go2Client(api_key="test-key", retry_count=1, retry_delay=0) as client:
            link = await client.links.create(destination_url="https://example.com")

        assert link.id == "lnk_ok"
