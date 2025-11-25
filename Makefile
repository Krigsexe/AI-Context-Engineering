# =============================================================================
# ODIN v7.0 - Makefile
# =============================================================================

.PHONY: help install start stop restart logs status clean test build

# Default target
help:
	@echo "ODIN v7.0 - Available commands:"
	@echo ""
	@echo "  make install    - First-time installation"
	@echo "  make start      - Start all services"
	@echo "  make stop       - Stop all services"
	@echo "  make restart    - Restart all services"
	@echo "  make logs       - View logs (all services)"
	@echo "  make status     - Check service status"
	@echo "  make clean      - Remove containers and volumes"
	@echo "  make test       - Run tests"
	@echo "  make build      - Build all images"
	@echo ""
	@echo "  make start-local  - Start with local LLM (Ollama)"
	@echo "  make start-cloud  - Start without local LLM"
	@echo "  make start-full   - Start all services including Neo4j"
	@echo ""
	@echo "  make cli        - Open CLI shell"
	@echo "  make pull-models - Download LLM models"
	@echo ""

# -----------------------------------------------------------------------------
# Installation
# -----------------------------------------------------------------------------

install:
	@./install.sh

# -----------------------------------------------------------------------------
# Service Management
# -----------------------------------------------------------------------------

start:
	docker compose up -d

start-local:
	docker compose --profile local-llm up -d

start-cloud:
	docker compose up -d postgres redis orchestrator api agent-intake agent-retrieval agent-dev agent-mcp agent-approbation agent-oracle-code

start-full:
	docker compose --profile local-llm --profile knowledge-graph up -d

stop:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

logs-orchestrator:
	docker compose logs -f orchestrator

logs-api:
	docker compose logs -f api

logs-agents:
	docker compose logs -f agent-intake agent-retrieval agent-dev agent-mcp agent-approbation agent-oracle-code

status:
	docker compose ps

# -----------------------------------------------------------------------------
# Build
# -----------------------------------------------------------------------------

build:
	docker compose build

build-no-cache:
	docker compose build --no-cache

# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

cli:
	docker compose run --rm cli

# -----------------------------------------------------------------------------
# LLM Models
# -----------------------------------------------------------------------------

pull-models:
	@echo "Pulling LLM models..."
	docker compose --profile local-llm up -d ollama
	@sleep 5
	docker exec odin-ollama ollama pull qwen2.5:7b
	@echo "Qwen 2.5 7B downloaded."
	@read -p "Download Llama 3.1 8B? (y/N) " yn; \
	if [ "$$yn" = "y" ]; then docker exec odin-ollama ollama pull llama3.1:8b; fi
	@read -p "Download DeepSeek Coder? (y/N) " yn; \
	if [ "$$yn" = "y" ]; then docker exec odin-ollama ollama pull deepseek-coder:6.7b; fi

# -----------------------------------------------------------------------------
# Testing
# -----------------------------------------------------------------------------

test:
	@echo "Running tests..."
	cd agents && python -m pytest ../tests/unit/agents -v
	cd orchestrator && go test ./... -v
	cd api && npm test

test-unit:
	cd agents && python -m pytest ../tests/unit -v

test-integration:
	cd tests/integration && python -m pytest -v

test-e2e:
	cd tests/e2e && python -m pytest -v

# -----------------------------------------------------------------------------
# Development
# -----------------------------------------------------------------------------

dev-setup:
	@./scripts/dev_setup.sh

lint:
	cd agents && pylint --rcfile=../.pylintrc agents/
	cd api && npm run lint
	cd orchestrator && golangci-lint run

format:
	cd agents && black .
	cd api && npm run format
	cd orchestrator && gofmt -w .

# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------

db-migrate:
	@./scripts/setup_db.sh

db-reset:
	docker compose down -v postgres_data
	docker compose up -d postgres
	@sleep 5
	@./scripts/setup_db.sh

# -----------------------------------------------------------------------------
# Cleanup
# -----------------------------------------------------------------------------

clean:
	docker compose down -v
	docker system prune -f

clean-all:
	docker compose down -v --rmi all
	docker system prune -af

# -----------------------------------------------------------------------------
# Health Check
# -----------------------------------------------------------------------------

health:
	@./scripts/health_check.sh

# -----------------------------------------------------------------------------
# Documentation
# -----------------------------------------------------------------------------

docs:
	@echo "Documentation available at: docs/"
	@echo ""
	@echo "  - ARCHITECTURE.md    - System architecture"
	@echo "  - LLM_PROVIDERS.md   - Supported providers"
	@echo "  - USER_CONFIGURATION.md - Configuration guide"
	@echo "  - VISION.md          - Project philosophy"
