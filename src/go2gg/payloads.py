from __future__ import annotations

"""Helpers for request/response payload shaping."""

from typing import Any


def snake_to_camel(value: str) -> str:
    """Convert a snake_case string to camelCase."""
    parts = value.split("_")
    return parts[0] + "".join(part[:1].upper() + part[1:] for part in parts[1:])


def map_snake_keys(data: dict[str, Any]) -> dict[str, Any]:
    """Convert snake_case keys to camelCase and drop None values."""
    return {snake_to_camel(key): value for key, value in data.items() if value is not None}


def get_first(data: dict[str, Any], *keys: str) -> Any:
    """Return the first matching key's value from a dict, or None."""
    for key in keys:
        if key in data:
            return data[key]
    return None
