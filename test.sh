#!/bin/bash

# Test Runner Script for LIHC Platform
# Provides convenient commands for running different types of tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    print_info "Checking test dependencies..."
    
    if ! command -v python &> /dev/null; then
        print_error "Python is not installed"
        exit 1
    fi
    
    if ! python -c "import pytest" &> /dev/null; then
        print_error "pytest is not installed. Installing..."
        pip install pytest pytest-cov pytest-xdist pytest-timeout
    fi
    
    print_success "Dependencies check passed"
}

run_unit_tests() {
    print_info "Running unit tests..."
    python -m pytest tests/ -m "unit" -v --tb=short
}

run_integration_tests() {
    print_info "Running integration tests..."
    python -m pytest tests/ -m "integration" -v --tb=short
}

run_api_tests() {
    print_info "Running API tests..."
    python -m pytest tests/ -m "api" -v --tb=short
}

run_all_tests() {
    print_info "Running all tests..."
    python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html
}

run_fast_tests() {
    print_info "Running fast tests (excluding slow tests)..."
    python -m pytest tests/ -m "not slow" -v --tb=short
}

run_coverage() {
    print_info "Running tests with coverage analysis..."
    python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html --cov-report=xml --cov-fail-under=80
    print_success "Coverage report generated in htmlcov/ directory"
}

run_parallel() {
    local workers=${1:-auto}
    print_info "Running tests in parallel with $workers workers..."
    python -m pytest tests/ -n $workers -v --tb=short
}

run_load_tests() {
    print_info "Running load tests..."
    if [ -f "tests/load_testing.py" ]; then
        python tests/load_testing.py
    else
        print_warning "Load tests not found"
    fi
}

lint_code() {
    print_info "Running code linting..."
    
    # Black formatting check
    print_info "Checking code formatting with Black..."
    python -m black --check src/ tests/ || {
        print_warning "Code formatting issues found. Run 'black src/ tests/' to fix."
    }
    
    # isort import sorting check
    print_info "Checking import sorting with isort..."
    python -m isort --check-only src/ tests/ || {
        print_warning "Import sorting issues found. Run 'isort src/ tests/' to fix."
    }
    
    # flake8 linting
    print_info "Running flake8 linting..."
    python -m flake8 src/ tests/ --max-line-length=100 --extend-ignore=E203,W503
    
    print_success "Linting completed"
}

type_check() {
    print_info "Running type checking with mypy..."
    python -m mypy src/ --ignore-missing-imports --no-strict-optional
    print_success "Type checking completed"
}

security_check() {
    print_info "Running security checks..."
    
    # Install bandit if not available
    if ! command -v bandit &> /dev/null; then
        print_info "Installing bandit for security scanning..."
        pip install bandit
    fi
    
    bandit -r src/ -f json -o bandit-report.json || true
    print_info "Security report generated: bandit-report.json"
    
    # Install safety if not available
    if ! command -v safety &> /dev/null; then
        print_info "Installing safety for dependency scanning..."
        pip install safety
    fi
    
    safety check --json --output safety-report.json || true
    print_info "Safety report generated: safety-report.json"
}

clean_test_artifacts() {
    print_info "Cleaning test artifacts..."
    
    # Remove coverage files
    rm -f .coverage coverage.xml
    rm -rf htmlcov/
    
    # Remove pytest cache
    rm -rf .pytest_cache/
    
    # Remove test databases
    rm -f test*.db
    
    # Remove log files
    rm -f *.log
    
    print_success "Test artifacts cleaned"
}

run_ci_tests() {
    print_info "Running CI test suite..."
    
    check_dependencies
    lint_code
    type_check
    security_check
    run_coverage
    
    print_success "CI test suite completed successfully"
}

show_help() {
    cat << EOF
Test Runner for LIHC Platform

Usage: $0 <command> [arguments]

Commands:
    unit                Run unit tests only
    integration         Run integration tests only
    api                 Run API tests only
    all                 Run all tests
    fast                Run fast tests (exclude slow tests)
    coverage            Run tests with coverage analysis
    parallel [workers]  Run tests in parallel (default: auto)
    load                Run load tests
    lint                Run code linting (black, isort, flake8)
    type-check          Run type checking with mypy
    security            Run security checks (bandit, safety)
    clean               Clean test artifacts
    ci                  Run complete CI test suite
    help                Show this help message

Examples:
    $0 unit                 # Run unit tests
    $0 coverage             # Run tests with coverage
    $0 parallel 4           # Run tests with 4 workers
    $0 ci                   # Run complete CI suite

EOF
}

# Main command handling
case "${1:-help}" in
    "unit")
        check_dependencies
        run_unit_tests
        ;;
    "integration")
        check_dependencies
        run_integration_tests
        ;;
    "api")
        check_dependencies
        run_api_tests
        ;;
    "all")
        check_dependencies
        run_all_tests
        ;;
    "fast")
        check_dependencies
        run_fast_tests
        ;;
    "coverage")
        check_dependencies
        run_coverage
        ;;
    "parallel")
        check_dependencies
        run_parallel "$2"
        ;;
    "load")
        run_load_tests
        ;;
    "lint")
        lint_code
        ;;
    "type-check")
        type_check
        ;;
    "security")
        security_check
        ;;
    "clean")
        clean_test_artifacts
        ;;
    "ci")
        run_ci_tests
        ;;
    "help"|*)
        show_help
        ;;
esac