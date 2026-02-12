"""Async Python SDK for the go2.gg Links API."""

from go2gg.client import Go2Client
from go2gg.exceptions import APIError, Go2Error, RequestError
from go2gg.types import (
    CountByBrowser,
    CountByCountry,
    CountByDate,
    CountByDevice,
    CountByReferrer,
    Link,
    LinkListMeta,
    LinkPage,
    LinkStats,
)

__all__ = [
    "Go2Client",
    "Go2Error",
    "APIError",
    "RequestError",
    "Link",
    "LinkListMeta",
    "LinkPage",
    "LinkStats",
    "CountByCountry",
    "CountByDevice",
    "CountByBrowser",
    "CountByReferrer",
    "CountByDate",
]
