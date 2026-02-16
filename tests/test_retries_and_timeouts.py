import asyncio
from typing import Any, cast

import aiohttp
import pytest
from aioresponses import aioresponses

from go2gg import Go2Client
from go2gg.exceptions import APIError, RequestError

BASE_URL = "https://api.go2.gg/api/v1"


def _calls_for(mock: Any, method: str, url: str) -> list[Any]:
    """Find captured requests by HTTP method and base URL."""
    for (recorded_method, recorded_url), calls in mock.requests.items():
        if recorded_method == method and str(recorded_url).split("?", maxsplit=1)[0] == url:
            return cast(list[Any], calls)
    return []


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

        assert len(_calls_for(mock, "POST", f"{BASE_URL}/links")) == 1


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
        assert len(_calls_for(mock, "POST", f"{BASE_URL}/links")) == 2


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


@pytest.mark.asyncio
async def test_close_does_not_close_external_session() -> None:
    session = aiohttp.ClientSession()
    client = Go2Client(api_key="test-key", session=session)
    await client.close()
    assert not session.closed
    await session.close()


@pytest.mark.asyncio
async def test_retry_without_backoff_uses_fixed_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    delays: list[float] = []

    async def fake_sleep(delay: float) -> None:
        delays.append(delay)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    with aioresponses() as mock:
        mock.post(f"{BASE_URL}/links", status=500, payload={"message": "server error"})
        mock.post(
            f"{BASE_URL}/links",
            status=200,
            payload={"success": True, "data": {"id": "lnk_ok", "shortUrl": "https://go2.gg/ok"}},
        )

        async with Go2Client(api_key="test-key", retry_count=1, retry_delay=0.25, retry_backoff=False) as client:
            await client.links.create(destination_url="https://example.com")

    assert delays == [0.25]


def test_client_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GO2GG_API_KEY", raising=False)
    with pytest.raises(ValueError, match="API key is required"):
        Go2Client(api_key=None)


def test_client_requires_base_url() -> None:
    with pytest.raises(ValueError, match="base_url is required"):
        Go2Client(api_key="test-key", base_url="")


@pytest.mark.asyncio
async def test_api_success_false_raises_error() -> None:
    payload = {"success": False, "code": "INVALID_INPUT", "message": "Bad payload"}

    with aioresponses() as mock:
        mock.post(f"{BASE_URL}/links", status=200, payload=payload)

        async with Go2Client(api_key="test-key") as client:
            with pytest.raises(APIError) as excinfo:
                await client.links.create(destination_url="https://example.com")

        assert excinfo.value.error_code == "INVALID_INPUT"


@pytest.mark.asyncio
async def test_non_dict_json_payload_wrapped_in_data() -> None:
    with aioresponses() as mock:
        mock.get(f"{BASE_URL}/links/non-dict", payload=[{"id": "one"}])

        async with Go2Client(api_key="test-key") as client:
            payload = await client._request("GET", "/links/non-dict")

        assert payload == {"data": [{"id": "one"}]}


@pytest.mark.asyncio
async def test_error_with_non_dict_payload_is_wrapped_as_api_error() -> None:
    with aioresponses() as mock:
        mock.get(f"{BASE_URL}/links/non-dict", status=500, payload=["boom"])

        async with Go2Client(api_key="test-key") as client:
            with pytest.raises(APIError) as excinfo:
                await client._request("GET", "/links/non-dict")

        assert excinfo.value.status_code == 500


@pytest.mark.asyncio
async def test_request_failed_after_retries_defensive_path(monkeypatch: pytest.MonkeyPatch) -> None:
    with aioresponses() as mock:
        mock.post(f"{BASE_URL}/links", exception=aiohttp.ClientConnectionError("boom"))
        mock.post(f"{BASE_URL}/links", exception=aiohttp.ClientConnectionError("boom"))

        async with Go2Client(api_key="test-key", retry_count=1, retry_delay=0) as client:
            monkeypatch.setattr(client, "_should_retry", lambda _status_code, _attempt: True)
            with pytest.raises(RequestError, match="Request failed after retries."):
                await client.links.create(destination_url="https://example.com")
