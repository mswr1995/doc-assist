.PHONY: run test lint

run:
	uvicorn src.main:app --reload

test:
	pytest

lint:
	ruff src tests