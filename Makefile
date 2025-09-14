.PHONY: run test lint format typecheck precommit

run:
	poetry run uvicorn app.main:app --reload

test:
	poetry run pytest

lint:
	poetry run ruff check .

format:
	poetry run ruff format .

mypy:
	poetry run mypy app

precommit:
	pre-commit run --all-files
