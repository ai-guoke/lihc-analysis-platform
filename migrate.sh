#!/bin/bash

# Database Migration Management Script for LIHC Platform

set -e

# Configuration
DB_CONTAINER="lihc-postgres"
DB_USER="lihc_user"
DB_NAME="lihc_platform"

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

check_database() {
    print_info "Checking database connection..."
    if docker exec $DB_CONTAINER pg_isready -U $DB_USER -d $DB_NAME > /dev/null 2>&1; then
        print_success "Database is ready"
        return 0
    else
        print_error "Database is not ready"
        return 1
    fi
}

init_alembic() {
    print_info "Initializing Alembic..."
    if [ ! -f "alembic.ini" ]; then
        print_error "alembic.ini not found. Please run this script from the project root."
        exit 1
    fi
    
    # Create initial migration if versions directory is empty
    if [ -z "$(ls -A alembic/versions/ 2>/dev/null)" ]; then
        print_info "Creating initial migration..."
        python -m alembic revision --autogenerate -m "Initial database schema"
    fi
    
    print_success "Alembic initialized"
}

migrate_up() {
    print_info "Running database migrations..."
    if check_database; then
        python -m alembic upgrade head
        print_success "Migrations completed successfully"
    else
        print_error "Cannot run migrations - database not available"
        exit 1
    fi
}

migrate_down() {
    local steps=${1:-1}
    print_warning "Rolling back $steps migration(s)..."
    if check_database; then
        python -m alembic downgrade -$steps
        print_success "Rollback completed"
    else
        print_error "Cannot rollback - database not available"
        exit 1
    fi
}

create_migration() {
    local message="$1"
    if [ -z "$message" ]; then
        print_error "Migration message is required"
        echo "Usage: $0 create-migration \"Your migration message\""
        exit 1
    fi
    
    print_info "Creating new migration: $message"
    python -m alembic revision --autogenerate -m "$message"
    print_success "Migration created"
}

show_current() {
    print_info "Current migration status:"
    python -m alembic current
}

show_history() {
    print_info "Migration history:"
    python -m alembic history --verbose
}

reset_database() {
    print_warning "This will reset the entire database!"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Resetting database..."
        python -m alembic downgrade base
        python -m alembic upgrade head
        print_success "Database reset completed"
    else
        print_info "Database reset cancelled"
    fi
}

show_help() {
    cat << EOF
Database Migration Management Script for LIHC Platform

Usage: $0 <command> [arguments]

Commands:
    init                    Initialize Alembic (run once)
    up                      Run all pending migrations
    down [steps]           Rollback N migrations (default: 1)
    create-migration "msg"  Create new migration with message
    current                Show current migration version
    history                Show migration history
    reset                  Reset database (down to base, then up to head)
    check                  Check database connection
    help                   Show this help message

Examples:
    $0 init
    $0 up
    $0 down 2
    $0 create-migration "Add user preferences table"
    $0 current
    $0 history
    $0 reset

EOF
}

# Main command handling
case "${1:-help}" in
    "init")
        init_alembic
        ;;
    "up")
        migrate_up
        ;;
    "down")
        migrate_down "$2"
        ;;
    "create-migration")
        create_migration "$2"
        ;;
    "current")
        show_current
        ;;
    "history")
        show_history
        ;;
    "reset")
        reset_database
        ;;
    "check")
        check_database
        ;;
    "help"|*)
        show_help
        ;;
esac