# go2gg

Async Python SDK for the go2.gg Links API, built on `aiohttp`.

## Disclaimer

This library is community-maintained and is not affiliated with the go2.gg website authors.
Service bugs and issues with the go2.gg platform should be reported to the go2.gg service team,
not to this SDK's maintainers.

## Install

```bash
pip install go2gg
```

## Quickstart

```python
import asyncio
import os

from go2gg import Go2Client


async def main() -> None:
    # Uses GO2GG_API_KEY from the environment by default.
    async with Go2Client() as client:
        link = await client.links.create(
            destination_url="https://example.com/product",
            slug="summer-sale",
            title="Summer Sale Campaign",
            tags=["marketing", "summer-2024"],
            utm_source="email",
            utm_campaign="summer-sale",
        )
        print(link.short_url)

        stats = await client.links.stats(link.id)
        print(stats.total_clicks)


if __name__ == "__main__":
    asyncio.run(main())
```

## API

All `links` methods are async:

- `create(**params)`
- `list(page=..., per_page=..., search=..., domain=..., tag=..., archived=..., sort=...)`
- `get(link_id)`
- `update(link_id, **params)`
- `delete(link_id)`
- `stats(link_id)`

### Parameter naming

Method kwargs use `snake_case` and are translated to the API's `camelCase` fields.
For example, `destination_url` becomes `destinationUrl` and `click_limit` becomes
`clickLimit`.

### Errors

- HTTP/network failures raise `RequestError`.
- API errors raise `APIError` with `status_code`, `error_code`, and `message`.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
ruff check .
ruff format --check .
mypy
pytest --cov=go2gg --cov-report=term-missing
bandit -r src
pip-audit
```

## Security

Never commit API keys. Use environment variables such as `GO2GG_API_KEY`.

## Client Configuration

The client supports retries and timeouts. Retries and backoff are disabled by default.

```python
from go2gg import Go2Client

client = Go2Client(
    api_key="YOUR_API_KEY",
    timeout_total=30.0,
    timeout_connect=10.0,
    timeout_sock_read=30.0,
    timeout_sock_connect=10.0,
    retry_count=2,
    retry_delay=0.5,
    retry_backoff=True,
)
```
