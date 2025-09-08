.PHONY: run test lint

run:
	uv run uvicorn src.main:app --reload

test:
	uv run pytest

lint:
	uv run ruff src tests