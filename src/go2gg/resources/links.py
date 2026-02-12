from __future__ import annotations

"""Links API resource methods."""

from typing import TYPE_CHECKING

from go2gg.payloads import map_snake_keys
from go2gg.types import Link, LinkListMeta, LinkPage, LinkStats


if TYPE_CHECKING:
    from go2gg.client import Go2Client


class LinksAPI:
    """Links API operations."""

    def __init__(self, client: "Go2Client") -> None:
        """Create a Links API accessor.

        Args:
            client: Authenticated Go2Client instance.
        """
        self._client = client

    async def create(
        self,
        *,
        destination_url: str,
        slug: str | None = None,
        domain: str | None = None,
        title: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        password: str | None = None,
        expires_at: str | None = None,
        click_limit: int | None = None,
        geo_targets: dict[str, str] | None = None,
        device_targets: dict[str, str] | None = None,
        ios_url: str | None = None,
        android_url: str | None = None,
        utm_source: str | None = None,
        utm_medium: str | None = None,
        utm_campaign: str | None = None,
        utm_term: str | None = None,
        utm_content: str | None = None,
    ) -> Link:
        """Create a new short link.

        Args:
            destination_url: Target URL to redirect to.
            slug: Optional custom slug.
            domain: Optional custom domain.
            title: Optional link title.
            description: Optional link description.
            tags: Optional tags for filtering.
            password: Optional password for protection.
            expires_at: Optional ISO 8601 expiration date.
            click_limit: Optional maximum number of clicks.
            geo_targets: Optional country-specific redirect URLs.
            device_targets: Optional device-specific redirect URLs.
            ios_url: Optional iOS deep link URL.
            android_url: Optional Android deep link URL.
            utm_source: Optional UTM source.
            utm_medium: Optional UTM medium.
            utm_campaign: Optional UTM campaign.
            utm_term: Optional UTM term.
            utm_content: Optional UTM content.

        Returns:
            The created Link.
        """
        payload = map_snake_keys(
            {
                "destination_url": destination_url,
                "slug": slug,
                "domain": domain,
                "title": title,
                "description": description,
                "tags": tags,
                "password": password,
                "expires_at": expires_at,
                "click_limit": click_limit,
                "geo_targets": geo_targets,
                "device_targets": device_targets,
                "ios_url": ios_url,
                "android_url": android_url,
                "utm_source": utm_source,
                "utm_medium": utm_medium,
                "utm_campaign": utm_campaign,
                "utm_term": utm_term,
                "utm_content": utm_content,
            }
        )
        response = await self._client._request("POST", "/links", json=payload)
        data = response.get("data", response)
        return Link.from_dict(data)

    async def list(
        self,
        *,
        page: int | None = None,
        per_page: int | None = None,
        search: str | None = None,
        domain: str | None = None,
        tag: str | None = None,
        archived: bool | None = None,
        sort: str | None = None,
    ) -> LinkPage:
        """List links for the authenticated account.

        Args:
            page: Page number.
            per_page: Items per page (max 100).
            search: Search by slug, URL, or title.
            domain: Filter by domain.
            tag: Filter by tag.
            archived: Include archived links.
            sort: Sort by created, clicks, or updated.

        Returns:
            A page of links plus pagination metadata.
        """
        params = map_snake_keys(
            {
                "page": page,
                "per_page": per_page,
                "search": search,
                "domain": domain,
                "tag": tag,
                "archived": archived,
                "sort": sort,
            }
        )
        response = await self._client._request("GET", "/links", params=params)
        data = response.get("data", [])
        meta = response.get("meta")
        links = [Link.from_dict(item) for item in data] if isinstance(data, list) else []
        meta_obj = LinkListMeta.from_dict(meta) if isinstance(meta, dict) else None
        return LinkPage(data=links, meta=meta_obj)

    async def get(self, link_id: str) -> Link:
        """Fetch a single link by ID.

        Args:
            link_id: Link identifier.

        Returns:
            The requested Link.
        """
        response = await self._client._request("GET", f"/links/{link_id}")
        data = response.get("data", response)
        return Link.from_dict(data)

    async def update(
        self,
        link_id: str,
        *,
        destination_url: str | None = None,
        slug: str | None = None,
        domain: str | None = None,
        title: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        password: str | None = None,
        expires_at: str | None = None,
        click_limit: int | None = None,
        geo_targets: dict[str, str] | None = None,
        device_targets: dict[str, str] | None = None,
        ios_url: str | None = None,
        android_url: str | None = None,
        utm_source: str | None = None,
        utm_medium: str | None = None,
        utm_campaign: str | None = None,
        utm_term: str | None = None,
        utm_content: str | None = None,
        is_archived: bool | None = None,
    ) -> Link:
        """Update fields for an existing link.

        Args:
            link_id: Link identifier.
            destination_url: Optional updated destination URL.
            slug: Optional updated slug.
            domain: Optional updated domain.
            title: Optional updated title.
            description: Optional updated description.
            tags: Optional updated tags.
            password: Optional updated password.
            expires_at: Optional updated expiration date.
            click_limit: Optional updated click limit.
            geo_targets: Optional updated geo targets.
            device_targets: Optional updated device targets.
            ios_url: Optional updated iOS deep link URL.
            android_url: Optional updated Android deep link URL.
            utm_source: Optional updated UTM source.
            utm_medium: Optional updated UTM medium.
            utm_campaign: Optional updated UTM campaign.
            utm_term: Optional updated UTM term.
            utm_content: Optional updated UTM content.
            is_archived: Archive or restore the link.

        Returns:
            The updated Link.
        """
        payload = map_snake_keys(
            {
                "destination_url": destination_url,
                "slug": slug,
                "domain": domain,
                "title": title,
                "description": description,
                "tags": tags,
                "password": password,
                "expires_at": expires_at,
                "click_limit": click_limit,
                "geo_targets": geo_targets,
                "device_targets": device_targets,
                "ios_url": ios_url,
                "android_url": android_url,
                "utm_source": utm_source,
                "utm_medium": utm_medium,
                "utm_campaign": utm_campaign,
                "utm_term": utm_term,
                "utm_content": utm_content,
                "is_archived": is_archived,
            }
        )
        response = await self._client._request("PATCH", f"/links/{link_id}", json=payload)
        data = response.get("data", response)
        return Link.from_dict(data)

    async def delete(self, link_id: str) -> None:
        """Archive (soft delete) a link.

        Args:
            link_id: Link identifier.
        """
        await self._client._request("DELETE", f"/links/{link_id}")
        return None

    async def stats(self, link_id: str) -> LinkStats:
        """Retrieve analytics for a link.

        Args:
            link_id: Link identifier.

        Returns:
            Analytics for the link.
        """
        response = await self._client._request("GET", f"/links/{link_id}/stats")
        data = response.get("data", response)
        if isinstance(data, dict):
            return LinkStats.from_dict(data)
        return LinkStats()
