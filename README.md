# Message Broker

Async message broker built with FastAPI.  
Senders publish JSON messages to named channels; receivers fetch messages in order, independently tracked.

## Features

- **Send messages:** Publish JSON to any channel.
- **Fetch new messages:** Receivers get unread messages since last fetch.
- **Fetch by index:** Receivers fetch up to X messages from index Y.

## Prerequisites

- [Poetry](https://python-poetry.org/) for dependency management

## Quickstart

```bash
poetry install
poetry run uvicorn app.main:app --reload
# API docs: http://localhost:8000/docs
```

### Reset database (optional, destructive)

```bash
rm broker.db
# or use a GUI like DB Browser for SQLite
```

## Testing

Run all tests:

```bash
poetry run pytest
```

## Development

### Makefile commands

This project includes a `Makefile` with common developer tasks:

- `make lint` – Run Ruff (lint & format check).
- `make typecheck` – Run mypy for type checking.
- `make test` – Run the test suite with pytest.
- `make precommit` – Run all pre-commit hooks (lint, format, typecheck).

### Linting & Formatting

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and autoformatting.

Check for issues:

```bash
poetry run ruff check .
```

Format code (like Black):

```bash
poetry run ruff format .
```

### Typing

This project uses [mypy](https://mypy.readthedocs.io/) for static type checking.

Run type checks:

```bash
poetry run mypy app
```

### Pre-commit hooks

To install git hooks locally so they run on every commit:

```bash
poetry run pre-commit install
```

## Notes

- Multiple senders/receivers supported.  
- No authentication is implemented. For this demo, receiver IDs are passed directly in the URL for simplicity.
