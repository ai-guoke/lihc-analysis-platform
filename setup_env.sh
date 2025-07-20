#!/bin/bash

# Environment Configuration Setup Script for LIHC Platform
# Helps set up the correct environment variables for different deployment scenarios

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

show_help() {
    cat << EOF
Environment Configuration Setup for LIHC Platform

Usage: $0 <environment>

Environments:
    development     Set up development environment
    production      Set up production environment
    testing         Set up testing environment

Examples:
    $0 development      # Setup for local development
    $0 production       # Setup for production deployment

EOF
}

setup_development() {
    print_info "Setting up development environment..."
    
    if [ -f ".env" ]; then
        print_warning "Existing .env file found. Creating backup..."
        cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    fi
    
    if [ -f ".env.development" ]; then
        cp .env.development .env
        print_success "Development environment configured!"
        print_info "Configuration loaded from .env.development"
    else
        print_error ".env.development file not found!"
        exit 1
    fi
}

setup_production() {
    print_info "Setting up production environment..."
    
    if [ -f ".env" ]; then
        print_warning "Existing .env file found. Creating backup..."
        cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    fi
    
    if [ -f ".env.production" ]; then
        cp .env.production .env
        print_warning "Production environment template configured!"
        print_error "⚠️  CRITICAL: You MUST change all default passwords and secrets before deployment!"
        print_info "Please edit .env file and replace all 'CHANGE_ME' values with secure credentials."
    else
        print_error ".env.production file not found!"
        exit 1
    fi
}

setup_testing() {
    print_info "Setting up testing environment..."
    
    # Create a minimal testing environment
    cat > .env << EOF
# Testing Environment Configuration
DATABASE_URL=sqlite:///test.db
REDIS_URL=redis://localhost:6379/15
SECRET_KEY=test-secret-key
ENVIRONMENT=testing
DEBUG=false
ENABLE_API_DOCS=false
LOG_LEVEL=WARNING
EOF
    
    print_success "Testing environment configured!"
}

validate_production_config() {
    print_info "Validating production configuration..."
    
    local issues=0
    
    # Check for default passwords
    if grep -q "CHANGE_ME" .env; then
        print_error "Default passwords/secrets found in .env file!"
        print_info "Please replace all 'CHANGE_ME' values with secure credentials."
        issues=$((issues + 1))
    fi
    
    # Check secret key length
    secret_key=$(grep "^SECRET_KEY=" .env | cut -d'=' -f2)
    if [ ${#secret_key} -lt 32 ]; then
        print_error "SECRET_KEY is too short (minimum 32 characters recommended)"
        issues=$((issues + 1))
    fi
    
    # Check if SSL certificates exist
    if [ ! -f "ssl/certs/lihc.crt" ] || [ ! -f "ssl/certs/lihc.key" ]; then
        print_warning "SSL certificates not found. Run ./generate_ssl.sh for development or obtain proper certificates for production."
    fi
    
    if [ $issues -eq 0 ]; then
        print_success "Production configuration validation passed!"
    else
        print_error "Production configuration has $issues issue(s) that must be fixed."
        return 1
    fi
}

# Main logic
case "${1:-help}" in
    "development")
        setup_development
        ;;
    "production")
        setup_production
        if [ -f ".env" ]; then
            validate_production_config
        fi
        ;;
    "testing")
        setup_testing
        ;;
    "validate")
        if [ -f ".env" ]; then
            validate_production_config
        else
            print_error ".env file not found!"
            exit 1
        fi
        ;;
    "help"|*)
        show_help
        ;;
esac