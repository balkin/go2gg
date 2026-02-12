from __future__ import annotations

"""Typed models for go2.gg API responses."""

from dataclasses import dataclass
from typing import Any

from go2gg.payloads import get_first


@dataclass(frozen=True)
class Link:
    """Represents a short link returned by the API."""
    id: str
    short_url: str | None = None
    destination_url: str | None = None
    slug: str | None = None
    domain: str | None = None
    title: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    has_password: bool | None = None
    expires_at: str | None = None
    click_count: int | None = None
    created_at: str | None = None
    updated_at: str | None = None
    raw: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Link":
        """Create a Link from an API response dictionary.

        Args:
            data: Parsed API response payload.

        Returns:
            A Link instance.
        """
        link_id = get_first(data, "id", "linkId")
        if link_id is None:
            raise ValueError("Link id is missing from the response.")
        return cls(
            id=str(link_id),
            short_url=get_first(data, "shortUrl", "short_url"),
            destination_url=get_first(data, "destinationUrl", "destination_url"),
            slug=get_first(data, "slug"),
            domain=get_first(data, "domain"),
            title=get_first(data, "title"),
            description=get_first(data, "description"),
            tags=get_first(data, "tags"),
            has_password=get_first(data, "hasPassword", "has_password"),
            expires_at=get_first(data, "expiresAt", "expires_at"),
            click_count=get_first(data, "clickCount", "click_count"),
            created_at=get_first(data, "createdAt", "created_at"),
            updated_at=get_first(data, "updatedAt", "updated_at"),
            raw=data,
        )


@dataclass(frozen=True)
class LinkListMeta:
    """Pagination metadata for link listings."""
    page: int | None = None
    per_page: int | None = None
    total: int | None = None
    has_more: bool | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LinkListMeta":
        """Create metadata from an API response dictionary.

        Args:
            data: Parsed API response payload.

        Returns:
            A LinkListMeta instance.
        """
        return cls(
            page=get_first(data, "page"),
            per_page=get_first(data, "perPage", "per_page"),
            total=get_first(data, "total"),
            has_more=get_first(data, "hasMore", "has_more"),
        )


@dataclass(frozen=True)
class LinkPage:
    """A page of links and optional pagination metadata."""
    data: list[Link]
    meta: LinkListMeta | None = None


@dataclass(frozen=True)
class CountByCountry:
    """Aggregated click counts by country code."""
    country: str
    count: int


@dataclass(frozen=True)
class CountByDevice:
    """Aggregated click counts by device type."""
    device: str
    count: int


@dataclass(frozen=True)
class CountByBrowser:
    """Aggregated click counts by browser name."""
    browser: str
    count: int


@dataclass(frozen=True)
class CountByReferrer:
    """Aggregated click counts by referrer."""
    referrer: str
    count: int


@dataclass(frozen=True)
class CountByDate:
    """Aggregated click counts by date."""
    date: str
    count: int


@dataclass(frozen=True)
class LinkStats:
    """Analytics data for a link."""
    total_clicks: int | None = None
    last_clicked_at: str | None = None
    by_country: list[CountByCountry] | None = None
    by_device: list[CountByDevice] | None = None
    by_browser: list[CountByBrowser] | None = None
    by_referrer: list[CountByReferrer] | None = None
    over_time: list[CountByDate] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LinkStats":
        """Create analytics data from an API response dictionary.

        Args:
            data: Parsed API response payload.

        Returns:
            A LinkStats instance.
        """
        by_country = None
        if isinstance(data.get("byCountry"), list):
            by_country = [
                CountByCountry(country=item["country"], count=item["count"])
                for item in data["byCountry"]
                if "country" in item and "count" in item
            ]

        by_device = None
        if isinstance(data.get("byDevice"), list):
            by_device = [
                CountByDevice(device=item["device"], count=item["count"])
                for item in data["byDevice"]
                if "device" in item and "count" in item
            ]

        by_browser = None
        if isinstance(data.get("byBrowser"), list):
            by_browser = [
                CountByBrowser(browser=item["browser"], count=item["count"])
                for item in data["byBrowser"]
                if "browser" in item and "count" in item
            ]

        by_referrer = None
        if isinstance(data.get("byReferrer"), list):
            by_referrer = [
                CountByReferrer(referrer=item["referrer"], count=item["count"])
                for item in data["byReferrer"]
                if "referrer" in item and "count" in item
            ]

        over_time = None
        if isinstance(data.get("overTime"), list):
            over_time = [
                CountByDate(date=item["date"], count=item["count"])
                for item in data["overTime"]
                if "date" in item and "count" in item
            ]

        return cls(
            total_clicks=get_first(data, "totalClicks", "total_clicks"),
            last_clicked_at=get_first(data, "lastClickedAt", "last_clicked_at"),
            by_country=by_country,
            by_device=by_device,
            by_browser=by_browser,
            by_referrer=by_referrer,
            over_time=over_time,
        )
