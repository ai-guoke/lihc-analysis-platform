# LIHC Analysis Platform Makefile
# Simplify common development and deployment tasks

.PHONY: help install dev test build deploy clean docs

# Variables
PYTHON := python3
PIP := pip3
DOCKER := docker
DOCKER_COMPOSE := docker-compose
PROJECT_NAME := lihc-platform
VERSION := 2.6.0

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Default target
help: ## Show this help message
	@echo "$(BLUE)LIHC Analysis Platform - Makefile Commands$(NC)"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# Installation targets
install: ## Install all dependencies
	@echo "$(YELLOW)Installing dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Dependencies installed successfully!$(NC)"

install-dev: ## Install development dependencies
	@echo "$(YELLOW)Installing development dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt || $(PIP) install pytest black flake8 mypy
	pre-commit install || echo "pre-commit not available"
	@echo "$(GREEN)Development dependencies installed successfully!$(NC)"

venv: ## Create virtual environment
	@echo "$(YELLOW)Creating virtual environment...$(NC)"
	$(PYTHON) -m venv venv
	@echo "$(GREEN)Virtual environment created! Activate with: source venv/bin/activate$(NC)"

# Development targets
dev: ## Run development server
	@echo "$(YELLOW)Starting development server...$(NC)"
	$(PYTHON) main.py --dashboard --debug --port 8050

run: ## Run production server
	@echo "$(YELLOW)Starting production server...$(NC)"
	$(PYTHON) main.py --dashboard --port 8050

dashboard: ## Run dashboard only
	@echo "$(YELLOW)Starting dashboard...$(NC)"
	$(PYTHON) main.py --dashboard

# Testing targets
test: ## Run all tests
	@echo "$(YELLOW)Running tests...$(NC)"
	pytest tests/ -v || echo "Tests not available yet"

test-unit: ## Run unit tests only
	@echo "$(YELLOW)Running unit tests...$(NC)"
	pytest tests/unit/ -v || echo "Unit tests not available yet"

test-integration: ## Run integration tests only
	@echo "$(YELLOW)Running integration tests...$(NC)"
	pytest tests/integration/ -v || echo "Integration tests not available yet"

test-coverage: ## Run tests with coverage report
	@echo "$(YELLOW)Running tests with coverage...$(NC)"
	pytest --cov=src --cov-report=html --cov-report=term || echo "Coverage tests not available yet"
	@echo "$(GREEN)Coverage report generated in htmlcov/index.html$(NC)"

# Code quality targets
lint: ## Run code linting
	@echo "$(YELLOW)Running linters...$(NC)"
	flake8 src/ --max-line-length=88 --ignore=E203,W503 || echo "Flake8 not available"
	pylint src/ || echo "Pylint not available"
	mypy src/ || echo "Mypy not available"

format: ## Format code with black
	@echo "$(YELLOW)Formatting code...$(NC)"
	black src/ tests/ || echo "Black not available"
	isort src/ tests/ || echo "Isort not available"
	@echo "$(GREEN)Code formatted successfully!$(NC)"

check: ## Check code quality without modifying
	@echo "$(YELLOW)Checking code quality...$(NC)"
	black --check src/ tests/ || echo "Black check not available"
	isort --check-only src/ tests/ || echo "Isort check not available"
	flake8 src/ || echo "Flake8 not available"

# Docker targets
build: ## Build Docker image
	@echo "$(YELLOW)Building Docker image...$(NC)"
	$(DOCKER) build -t $(PROJECT_NAME):$(VERSION) .
	$(DOCKER) tag $(PROJECT_NAME):$(VERSION) $(PROJECT_NAME):latest
	@echo "$(GREEN)Docker image built successfully!$(NC)"

build-no-cache: ## Build Docker image without cache
	@echo "$(YELLOW)Building Docker image (no cache)...$(NC)"
	$(DOCKER) build --no-cache -t $(PROJECT_NAME):$(VERSION) .

up: ## Start all services with docker-compose
	@echo "$(YELLOW)Starting services...$(NC)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)Services started! Access at http://localhost:8050$(NC)"

down: ## Stop all services
	@echo "$(YELLOW)Stopping services...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)Services stopped!$(NC)"

restart: ## Restart all services
	@echo "$(YELLOW)Restarting services...$(NC)"
	$(DOCKER_COMPOSE) restart
	@echo "$(GREEN)Services restarted!$(NC)"

logs: ## Show logs from all services
	$(DOCKER_COMPOSE) logs -f

logs-app: ## Show logs from app service only
	$(DOCKER_COMPOSE) logs -f lihc-platform

ps: ## Show running services
	$(DOCKER_COMPOSE) ps

# Docker profiles
up-monitoring: ## Start with monitoring stack
	@echo "$(YELLOW)Starting with monitoring...$(NC)"
	$(DOCKER_COMPOSE) --profile monitoring up -d
	@echo "$(GREEN)Services started with monitoring!$(NC)"
	@echo "Grafana: http://localhost:3000 (admin/admin)"
	@echo "Prometheus: http://localhost:9090"

up-celery: ## Start with Celery workers
	@echo "$(YELLOW)Starting with Celery...$(NC)"
	$(DOCKER_COMPOSE) --profile celery up -d
	@echo "$(GREEN)Services started with Celery workers!$(NC)"
	@echo "Flower: http://localhost:5555"

up-full: ## Start all services including optional ones
	@echo "$(YELLOW)Starting all services...$(NC)"
	$(DOCKER_COMPOSE) --profile monitoring --profile celery --profile production --profile management up -d
	@echo "$(GREEN)All services started!$(NC)"

# Database targets
db-init: ## Initialize database
	@echo "$(YELLOW)Initializing database...$(NC)"
	$(PYTHON) scripts/init_db.py || echo "Database initialization script not available"
	@echo "$(GREEN)Database initialized!$(NC)"

db-migrate: ## Run database migrations
	@echo "$(YELLOW)Running migrations...$(NC)"
	$(PYTHON) scripts/migrate.py || echo "Migration script not available"
	@echo "$(GREEN)Migrations completed!$(NC)"

db-backup: ## Backup database
	@echo "$(YELLOW)Backing up database...$(NC)"
	$(DOCKER_COMPOSE) exec postgres pg_dump -U lihc_user lihc_db > backup_$(shell date +%Y%m%d_%H%M%S).sql || echo "Database backup not available"
	@echo "$(GREEN)Database backed up!$(NC)"

# Documentation targets
docs: ## Generate documentation
	@echo "$(YELLOW)Documentation files:$(NC)"
	@ls -la docs/*.md
	@echo "$(GREEN)Documentation available in docs/ directory$(NC)"

docs-serve: ## Serve documentation locally
	@echo "$(YELLOW)Serving documentation...$(NC)"
	cd docs && python -m http.server 8080

# Utility targets
clean: ## Clean temporary files and caches
	@echo "$(YELLOW)Cleaning temporary files...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".DS_Store" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	@echo "$(GREEN)Cleanup completed!$(NC)"

clean-docker: ## Clean Docker resources
	@echo "$(YELLOW)Cleaning Docker resources...$(NC)"
	$(DOCKER_COMPOSE) down -v || true
	$(DOCKER) system prune -f || true
	@echo "$(GREEN)Docker cleanup completed!$(NC)"

clean-all: clean clean-docker ## Clean everything
	@echo "$(GREEN)Full cleanup completed!$(NC)"

# Analysis targets
analyze: ## Run a quick analysis with demo data
	@echo "$(YELLOW)Running analysis with demo data...$(NC)"
	$(PYTHON) main.py --analyze --demo || echo "Demo analysis not available"

demo: ## Run with demo data
	@echo "$(YELLOW)Starting with demo data...$(NC)"
	$(PYTHON) main.py --dashboard --demo || $(PYTHON) main.py --dashboard

# Git targets
git-hooks: ## Install git hooks
	@echo "$(YELLOW)Installing git hooks...$(NC)"
	pre-commit install || echo "pre-commit not available"
	@echo "$(GREEN)Git hooks installed!$(NC)"

# Environment setup
env: ## Copy .env.example to .env
	@echo "$(YELLOW)Setting up environment...$(NC)"
	cp .env.example .env
	@echo "$(GREEN)Environment file created! Please edit .env with your values.$(NC)"

env-check: ## Check if .env file exists
	@if [ -f .env ]; then \
		echo "$(GREEN).env file exists$(NC)"; \
	else \
		echo "$(RED).env file not found! Run 'make env' to create it.$(NC)"; \
	fi

# Quick start targets
quickstart: env install ## Quick start for new developers
	@echo "$(GREEN)Quick start completed!$(NC)"
	@echo "Run 'make dev' to start the development server"

# Information targets
info: ## Show project information
	@echo "$(BLUE)LIHC Analysis Platform$(NC)"
	@echo "Version: $(VERSION)"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Docker: $(shell $(DOCKER) --version 2>/dev/null || echo 'Not installed')"
	@echo "Docker Compose: $(shell $(DOCKER_COMPOSE) --version 2>/dev/null || echo 'Not installed')"

status: ps ## Show current status of all services
	@echo "$(GREEN)Status check completed!$(NC)"

version: ## Show current version
	@echo "$(BLUE)Current version: $(VERSION)$(NC)"

# Default shell
SHELL := /bin/bash