import re
from typing import Any, cast

import pytest
from aioresponses import aioresponses

from go2gg import Go2Client

BASE_URL = "https://api.go2.gg/api/v1"


def _calls_for(mock: Any, method: str, url: str) -> list[Any]:
    """Find captured requests by HTTP method and base URL."""
    for (recorded_method, recorded_url), calls in mock.requests.items():
        if recorded_method == method and str(recorded_url).split("?", maxsplit=1)[0] == url:
            return cast(list[Any], calls)
    return []


@pytest.mark.asyncio
async def test_links_create_happy_path() -> None:
    response_payload = {
        "success": True,
        "data": {
            "id": "lnk_abc123",
            "shortUrl": "https://go2.gg/summer-sale",
            "destinationUrl": "https://example.com/landing",
            "slug": "summer-sale",
            "title": "Summer Sale Campaign",
            "tags": ["marketing", "summer-2024"],
        },
    }

    with aioresponses() as mock:
        mock.post(f"{BASE_URL}/links", payload=response_payload)

        async with Go2Client(api_key="test-key", user_agent="go2gg-sdk-tests/1.0") as client:
            link = await client.links.create(
                destination_url="https://example.com/landing",
                slug="summer-sale",
                title="Summer Sale Campaign",
                tags=["marketing", "summer-2024"],
                utm_source="email",
                utm_campaign="summer-sale",
            )

        calls = _calls_for(mock, "POST", f"{BASE_URL}/links")
        assert calls
        request = calls[0]
        assert request.kwargs["json"] == {
            "destinationUrl": "https://example.com/landing",
            "slug": "summer-sale",
            "title": "Summer Sale Campaign",
            "tags": ["marketing", "summer-2024"],
            "utmSource": "email",
            "utmCampaign": "summer-sale",
        }
        assert request.kwargs["headers"]["User-Agent"] == "go2gg-sdk-tests/1.0"
        assert link.id == "lnk_abc123"
        assert link.short_url == "https://go2.gg/summer-sale"


@pytest.mark.asyncio
async def test_links_list_with_pagination() -> None:
    response_payload = {
        "success": True,
        "data": [
            {
                "id": "lnk_abc123",
                "shortUrl": "https://go2.gg/summer-sale",
                "destinationUrl": "https://example.com/landing",
                "clickCount": 1542,
                "createdAt": "2024-06-01T10:30:00Z",
            }
        ],
        "meta": {"page": 1, "perPage": 10, "total": 47, "hasMore": True},
    }

    with aioresponses() as mock:
        mock.get(
            re.compile(rf"^{re.escape(BASE_URL)}/links(?:\?.*)?$"),
            payload=response_payload,
        )

        async with Go2Client(api_key="test-key") as client:
            page = await client.links.list(per_page=10, sort="clicks")

        calls = _calls_for(mock, "GET", f"{BASE_URL}/links")
        assert calls
        request = calls[0]
        assert request.kwargs["params"] == {"perPage": 10, "sort": "clicks"}
        assert page.meta and page.meta.total == 47
        assert page.data[0].id == "lnk_abc123"


@pytest.mark.asyncio
async def test_links_stats_parsing() -> None:
    response_payload = {
        "success": True,
        "data": {
            "totalClicks": 1542,
            "lastClickedAt": "2024-06-15T14:22:00Z",
            "byCountry": [{"country": "US", "count": 823}],
            "byDevice": [{"device": "desktop", "count": 892}],
        },
    }

    with aioresponses() as mock:
        mock.get(f"{BASE_URL}/links/lnk_abc123/stats", payload=response_payload)

        async with Go2Client(api_key="test-key") as client:
            stats = await client.links.stats("lnk_abc123")

        assert stats.total_clicks == 1542
        assert stats.by_country and stats.by_country[0].country == "US"
        assert stats.by_device and stats.by_device[0].device == "desktop"


@pytest.mark.asyncio
async def test_links_update_delete_and_get() -> None:
    get_payload = {
        "success": True,
        "data": {"id": "lnk_abc123", "shortUrl": "https://go2.gg/summer-sale"},
    }
    update_payload = {
        "success": True,
        "data": {"id": "lnk_abc123", "title": "Updated title"},
    }

    with aioresponses() as mock:
        mock.get(f"{BASE_URL}/links/lnk_abc123", payload=get_payload)
        mock.patch(f"{BASE_URL}/links/lnk_abc123", payload=update_payload)
        mock.delete(f"{BASE_URL}/links/lnk_abc123", status=204)

        async with Go2Client(api_key="test-key") as client:
            fetched = await client.links.get("lnk_abc123")
            updated = await client.links.update("lnk_abc123", title="Updated title")
            await client.links.delete("lnk_abc123")

        assert fetched.id == "lnk_abc123"
        assert updated.id == "lnk_abc123"


@pytest.mark.asyncio
async def test_links_stats_returns_empty_model_for_non_dict_payload() -> None:
    response_payload = {"success": True, "data": []}

    with aioresponses() as mock:
        mock.get(f"{BASE_URL}/links/lnk_abc123/stats", payload=response_payload)

        async with Go2Client(api_key="test-key") as client:
            stats = await client.links.stats("lnk_abc123")

        assert stats.total_clicks is None
        assert stats.by_country is None
