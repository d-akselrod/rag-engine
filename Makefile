.PHONY: help dev test db-up db-down db-init db-seed lint clean

PYTHON ?= .venv/bin/python
UVICORN ?= .venv/bin/uvicorn
PYTEST ?= .venv/bin/pytest

help:
	@echo "Available commands:"
	@echo "  make dev       Run local FastAPI development server with auto-reload"
	@echo "  make test      Run unit and integration test suite with pytest"
	@echo "  make db-up     Start PostgreSQL pgvector container in background"
	@echo "  make db-down   Stop PostgreSQL pgvector container"
	@echo "  make db-init   Initialize database schema and pgvector extension"
	@echo "  make db-seed   Seed sample documents into pgvector"
	@echo "  make clean     Clean up Python cache files and temporary artifacts"

dev:
	$(UVICORN) src.main:app --reload --host 0.0.0.0 --port 8000

test:
	$(PYTEST) tests/ -v

db-up:
	docker compose up -d

db-down:
	docker compose down

db-init:
	$(PYTHON) scripts/init_db.py

db-seed:
	$(PYTHON) scripts/seed_sample.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache
