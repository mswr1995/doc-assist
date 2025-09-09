.PHONY: help install run docker-up docker-down docker-setup clean

install:
	uv sync

run:
	uv run uvicorn src.main:app --reload

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

docker-setup:
	docker-compose up --build -d
	docker-compose exec ollama ollama pull llama3.2:1b

clean:
	del /s /q __pycache__ 2>nul || true
	del /s /q *.pyc 2>nul || true