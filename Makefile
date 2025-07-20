# Makefile for LIHC Platform Development

.PHONY: help install install-dev test test-cov lint format type-check clean setup-hooks run-demo run-dashboard docker-build docker-run

# Default target
help:
	@echo "Available targets:"
	@echo "  install          Install production dependencies"
	@echo "  install-dev      Install development dependencies"
	@echo "  test            Run tests"
	@echo "  test-cov        Run tests with coverage"
	@echo "  lint            Run linting (flake8)"
	@echo "  format          Format code (black + isort)"
	@echo "  type-check      Run type checking (mypy)"
	@echo "  clean           Clean up generated files"
	@echo "  setup-hooks     Install pre-commit hooks"
	@echo "  run-demo        Run demo analysis"
	@echo "  run-dashboard   Run dashboard"
	@echo "  docker-build    Build Docker image"
	@echo "  docker-run      Run Docker container"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -e .

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

# Code quality
lint:
	flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,E266,E501,W503

format:
	black src/ tests/ --line-length=88
	isort src/ tests/ --profile=black

type-check:
	mypy src/ --ignore-missing-imports

# Pre-commit hooks
setup-hooks:
	pre-commit install
	pre-commit install --hook-type pre-push

# Running the application
run-demo:
	python main.py --setup-demo --run-analysis

run-dashboard:
	python main.py --dashboard

run-full:
	python main.py --setup-demo --run-analysis --dashboard

# Docker
docker-build:
	docker build -t lihc-platform:latest .

docker-run:
	docker run -p 8050:8050 lihc-platform:latest

docker-compose-up:
	docker-compose up -d

docker-compose-down:
	docker-compose down

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/
	rm -rf build/ dist/

# Development workflow
dev-setup: install-dev setup-hooks
	@echo "Development environment setup complete!"

dev-check: format lint type-check test
	@echo "All development checks passed!"

# Documentation
docs:
	@echo "Generating documentation..."
	@echo "Current documentation files:"
	@ls -la *.md

# Performance profiling
profile:
	python -m cProfile -o profile_output.prof main.py --setup-demo --run-analysis
	@echo "Profile saved to profile_output.prof"

# Database operations (if applicable)
reset-data:
	rm -rf data/processed/*
	rm -rf results/user_analyses/*
	@echo "Processed data and user analyses cleared"

# Monitoring
check-logs:
	@echo "Recent log files:"
	@ls -la logs/ || echo "No logs directory found"

# CI/CD helpers
ci-test: install-dev
	pytest tests/ -v --cov=src --cov-report=xml

ci-lint:
	flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,E266,E501,W503 --output-file=flake8-report.txt

# Release helpers
version:
	@echo "Current version info:"
	@python -c "import sys; print(f'Python: {sys.version}')"
	@python -c "import pandas; print(f'Pandas: {pandas.__version__}')"
	@python -c "import numpy; print(f'NumPy: {numpy.__version__}')"

# Security
security-check:
	pip list --format=freeze | grep -E "(django|flask|tornado|twisted)" || echo "No known web frameworks found"
	@echo "Run 'pip-audit' if available for security scanning"