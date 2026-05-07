.PHONY: help setup install sync run dev test format lint clean validate

help: ## Show this help message
	@echo "Insurance Claims API - Available Commands"
	@echo "=========================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Initial project setup (installs uv and dependencies)
	@./scripts/setup_uv.sh

install: ## Install dependencies with uv
	uv sync

sync: ## Sync dependencies (same as install)
	uv sync

install-dev: ## Install with dev dependencies
	uv sync --extra dev

install-ai: ## Install with AI dependencies
	uv sync --extra ai

install-all: ## Install all dependencies
	uv sync --all-extras

run: ## Start the API server
	@./scripts/start_api.sh

dev: ## Start the API server in development mode
	uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests
	uv run pytest

test-cov: ## Run tests with coverage
	uv run pytest --cov=src/api --cov-report=term-missing --cov-report=html

test-watch: ## Run tests in watch mode
	uv run pytest-watch

format: ## Format code with black
	uv run black src/api

format-check: ## Check code formatting
	uv run black --check src/api

lint: ## Lint code with ruff
	uv run ruff check src/api

lint-fix: ## Lint and fix issues
	uv run ruff check --fix src/api

validate: ## Validate project structure
	uv run python scripts/validate_api.py

clean: ## Clean up generated files
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf .ruff_cache
	rm -rf src/**/__pycache__
	rm -rf test_insurance.db
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

clean-all: clean ## Clean everything including uv cache
	rm -rf .venv
	uv cache clean

config: ## Create config from example
	@if [ ! -f api-config.yaml ]; then \
		cp api-config.example.yaml api-config.yaml; \
		echo "✅ Created api-config.yaml"; \
	else \
		echo "⚠️  api-config.yaml already exists"; \
	fi

dirs: ## Create necessary directories
	mkdir -p uploads logs

db-reset: ## Reset SQLite database (development only)
	rm -f test_insurance.db
	@echo "✅ Database reset"

logs: ## Tail API logs
	tail -f logs/api.log

check: validate lint format-check test ## Run all checks

init: setup config dirs ## Complete initialization
	@echo "✅ Project initialized!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Review api-config.yaml"
	@echo "  2. Run: make run"

# Docker commands (future)
docker-build: ## Build docker image
	docker build -t insurance-claims-api:latest .

docker-run: ## Run docker container
	docker run -p 8000:8000 insurance-claims-api:latest

# Development helpers
shell: ## Open uv shell
	uv run python

repl: ## Open Python REPL with project loaded
	uv run python -i -c "from src.api import *"

info: ## Show project info
	@echo "Project: Insurance Claims API"
	@echo "Python: $$(python --version)"
	@echo "UV: $$(uv --version)"
	@echo "Location: $$(pwd)"
	@echo ""
	@echo "Dependencies:"
	@uv pip list 2>/dev/null || echo "  Run 'make install' first"
