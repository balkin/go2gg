import pytest

from go2gg.types import Link, LinkStats


def test_link_from_dict_parses_fields() -> None:
    payload = {
        "id": "lnk_abc123",
        "shortUrl": "https://go2.gg/summer-sale",
        "destinationUrl": "https://example.com/landing",
        "slug": "summer-sale",
        "domain": "go2.gg",
        "title": "Summer Sale Campaign",
        "tags": ["marketing", "summer-2024"],
        "hasPassword": False,
        "expiresAt": "2024-09-01T00:00:00Z",
        "clickCount": 42,
        "createdAt": "2024-06-01T10:30:00Z",
        "updatedAt": "2024-06-01T10:30:00Z",
    }
    link = Link.from_dict(payload)
    assert link.id == "lnk_abc123"
    assert link.short_url == "https://go2.gg/summer-sale"
    assert link.destination_url == "https://example.com/landing"
    assert link.slug == "summer-sale"
    assert link.tags == ["marketing", "summer-2024"]
    assert link.click_count == 42


def test_link_from_dict_missing_id_raises() -> None:
    with pytest.raises(ValueError):
        Link.from_dict({"shortUrl": "https://go2.gg/test"})


def test_link_stats_parsing() -> None:
    payload = {
        "totalClicks": 1542,
        "lastClickedAt": "2024-06-15T14:22:00Z",
        "byCountry": [{"country": "US", "count": 823}],
        "byDevice": [{"device": "desktop", "count": 892}],
        "byBrowser": [{"browser": "Chrome", "count": 756}],
        "byReferrer": [{"referrer": "twitter.com", "count": 412}],
        "overTime": [{"date": "2024-06-01", "count": 45}],
    }
    stats = LinkStats.from_dict(payload)
    assert stats.total_clicks == 1542
    assert stats.by_country and stats.by_country[0].country == "US"
    assert stats.by_device and stats.by_device[0].device == "desktop"
    assert stats.by_browser and stats.by_browser[0].browser == "Chrome"
    assert stats.by_referrer and stats.by_referrer[0].referrer == "twitter.com"
    assert stats.over_time and stats.over_time[0].date == "2024-06-01"
