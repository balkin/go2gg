import aiohttp
import pytest
from aioresponses import aioresponses

from go2gg import Go2Client
from go2gg.exceptions import APIError, RequestError

BASE_URL = "https://api.go2.gg/api/v1"


@pytest.mark.asyncio
async def test_client_raises_api_error() -> None:
    error_payload = {
        "success": False,
        "code": "SLUG_EXISTS",
        "message": "The slug is already in use.",
    }

    with aioresponses() as mock:
        mock.post(f"{BASE_URL}/links", status=409, payload=error_payload)

        async with Go2Client(api_key="test-key") as client:
            with pytest.raises(APIError) as excinfo:
                await client.links.create(destination_url="https://example.com", slug="summer-sale")

        error = excinfo.value
        assert error.status_code == 409
        assert error.error_code == "SLUG_EXISTS"


@pytest.mark.asyncio
async def test_client_raises_request_error() -> None:
    with aioresponses() as mock:
        mock.get(
            f"{BASE_URL}/links/lnk_abc123",
            exception=aiohttp.ClientConnectionError("boom"),
        )

        async with Go2Client(api_key="test-key") as client:
            with pytest.raises(RequestError):
                await client.links.get("lnk_abc123")
