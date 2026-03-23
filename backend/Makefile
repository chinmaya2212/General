.PHONY: run test lint format help

help:
	@echo "Available commands:"
	@echo "  make run    - Start the FastAPI application"
	@echo "  make test   - Run all backend tests with pytest"
	@echo "  make lint   - Check code quality with ruff"
	@echo "  make format - Format code with black and ruff"

run:
	uvicorn app.main:app --reload

test:
	pytest tests/ -v -s -rP

lint:
	ruff check .

format:
	black .
	ruff check --fix .
