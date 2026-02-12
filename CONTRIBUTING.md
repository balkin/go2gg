# Contributing

Thanks for helping improve the go2gg SDK.

## Disclaimer

This library is community-maintained and is not affiliated with the go2.gg website authors.
Service bugs and issues with the go2.gg platform should be reported to the go2.gg service team,
not to this SDK's maintainers.

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Quality Checks

```bash
ruff check .
ruff format --check .
mypy
pytest --cov=go2gg --cov-report=term-missing
bandit -r src
pip-audit
```

## Testing Principles

We follow TDD:
1. Write the smallest failing test that captures behavior.
2. Run tests to confirm failure.
3. Implement the minimal change to pass.
4. Refactor for clarity and re-run tests.

## Code Style

- Line length: 120
- Absolute imports within the package (e.g., `from go2gg.exceptions import APIError`)
- Google-style docstrings for public APIs
