#!/bin/bash

# LIHC Platform Production Deployment Script
# This script automates the deployment of the LIHC Multi-omics Analysis Platform

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PLATFORM_NAME="LIHC Platform"
VERSION="1.0.0"
DOCKER_COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
DATA_DIR="./data"
LOGS_DIR="./logs"
BACKUPS_DIR="./backups"

# Function to print colored output
print_status() {
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Docker
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check available disk space (minimum 10GB)
    available_space=$(df . | tail -1 | awk '{print $4}')
    if [ "$available_space" -lt 10485760 ]; then
        print_warning "Less than 10GB disk space available. Consider freeing up space."
    fi
    
    # Check available memory (minimum 4GB)
    total_mem=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    if [ "$total_mem" -lt 4096 ]; then
        print_warning "Less than 4GB RAM available. Performance may be affected."
    fi
    
    print_success "System requirements check completed"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p "$DATA_DIR"/{uploads,processed,exports,temp}
    mkdir -p "$LOGS_DIR"/{api,dashboard,database,nginx}
    mkdir -p "$BACKUPS_DIR"/{database,files}
    mkdir -p ./ssl/certs
    mkdir -p ./monitoring/{prometheus,grafana}
    
    print_success "Directories created successfully"
}

# Function to generate environment file
generate_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        print_status "Generating environment configuration file..."
        
        cat > "$ENV_FILE" << EOF
# LIHC Platform Environment Configuration
# Generated on $(date)

# Application Settings
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=$(openssl rand -hex 32)
API_KEY_SECRET=$(openssl rand -hex 32)

# Database Configuration
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=lihc_platform
POSTGRES_USER=lihc_user
POSTGRES_PASSWORD=$(openssl rand -base64 32)
DATABASE_URL=postgresql://lihc_user:$(openssl rand -base64 32)@postgres:5432/lihc_platform

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=$(openssl rand -base64 32)

# API Configuration
API_HOST=0.0.0.0
API_PORT=8050
API_WORKERS=4
API_TIMEOUT=300

# Dashboard Configuration
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8051

# File Storage
UPLOAD_MAX_SIZE=500MB
DATA_RETENTION_DAYS=365

# Security Settings
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
CORS_ORIGINS=*

# Monitoring
PROMETHEUS_RETENTION=15d
GRAFANA_ADMIN_PASSWORD=$(openssl rand -base64 16)

# Email Configuration (Optional)
SMTP_SERVER=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_USE_TLS=true

# External Services (Optional)
PUBMED_API_KEY=
ENRICHR_URL=https://maayanlab.cloud/Enrichr

# Performance Settings
CELERY_WORKERS=4
ANALYSIS_TIMEOUT=3600
MAX_CONCURRENT_ANALYSES=10

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_RETENTION_DAYS=30
EOF
        
        print_success "Environment file generated: $ENV_FILE"
        print_warning "Please review and update the configuration in $ENV_FILE"
    else
        print_status "Environment file already exists: $ENV_FILE"
    fi
}

# Function to generate SSL certificates (self-signed for development)
generate_ssl_certs() {
    if [ ! -f "./ssl/certs/lihc.crt" ]; then
        print_status "Generating SSL certificates..."
        
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ./ssl/certs/lihc.key \
            -out ./ssl/certs/lihc.crt \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        
        chmod 600 ./ssl/certs/lihc.key
        chmod 644 ./ssl/certs/lihc.crt
        
        print_success "SSL certificates generated"
        print_warning "Using self-signed certificates. Replace with proper certificates for production."
    else
        print_status "SSL certificates already exist"
    fi
}

# Function to build Docker images
build_images() {
    print_status "Building Docker images..."
    
    if command_exists docker-compose; then
        docker-compose build --parallel
    else
        docker compose build --parallel
    fi
    
    print_success "Docker images built successfully"
}

# Function to start services
start_services() {
    print_status "Starting LIHC Platform services..."
    
    if command_exists docker-compose; then
        docker-compose up -d
    else
        docker compose up -d
    fi
    
    print_success "Services started successfully"
}

# Function to check service health
check_health() {
    print_status "Checking service health..."
    
    # Wait for services to start
    sleep 30
    
    # Check database
    if docker exec lihc-postgres pg_isready -U lihc_user > /dev/null 2>&1; then
        print_success "Database is healthy"
    else
        print_error "Database health check failed"
        return 1
    fi
    
    # Check Redis
    if docker exec lihc-redis redis-cli ping | grep -q PONG; then
        print_success "Redis is healthy"
    else
        print_error "Redis health check failed"
        return 1
    fi
    
    # Check API
    if curl -f http://localhost:8050/health > /dev/null 2>&1; then
        print_success "API is healthy"
    else
        print_error "API health check failed"
        return 1
    fi
    
    # Check Dashboard
    if curl -f http://localhost:8051 > /dev/null 2>&1; then
        print_success "Dashboard is healthy"
    else
        print_error "Dashboard health check failed"
        return 1
    fi
    
    print_success "All services are healthy"
}

# Function to initialize database
init_database() {
    print_status "Initializing database..."
    
    # Run database migrations/initialization
    docker exec lihc-api python -c "
from src.database.models import init_db
init_db()
print('Database initialized successfully')
"
    
    print_success "Database initialization completed"
}

# Function to create monitoring configuration
setup_monitoring() {
    print_status "Setting up monitoring configuration..."
    
    # Create Grafana configuration
    mkdir -p ./monitoring/grafana/provisioning/{dashboards,datasources}
    
    cat > ./monitoring/grafana/provisioning/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF

    # Create basic dashboard configuration
    cat > ./monitoring/grafana/provisioning/dashboards/dashboard.yml << EOF
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
EOF

    print_success "Monitoring configuration created"
}

# Function to run tests
run_tests() {
    print_status "Running system tests..."
    
    # Basic API tests
    docker exec lihc-api python -m pytest tests/ -v --tb=short || {
        print_warning "Some tests failed. Check logs for details."
    }
    
    print_success "System tests completed"
}

# Function to show deployment summary
show_summary() {
    echo
    echo "==============================================="
    echo -e "${GREEN}${PLATFORM_NAME} v${VERSION} Deployment Complete!${NC}"
    echo "==============================================="
    echo
    echo "Services:"
    echo "  🌐 Web Dashboard:    https://localhost"
    echo "  🔧 API:              https://localhost/api/v1"
    echo "  📊 API Docs:         http://localhost:8080/docs"
    echo "  📈 Monitoring:       https://localhost/monitoring"
    echo "  🗄️  Database:         localhost:5432"
    echo "  🔄 Redis:            localhost:6379"
    echo
    echo "Default Credentials:"
    echo "  Admin Username: admin"
    echo "  Admin Password: admin123"
    echo "  (Change immediately after first login)"
    echo
    echo "Important Files:"
    echo "  📁 Data Directory:   $DATA_DIR"
    echo "  📋 Logs Directory:   $LOGS_DIR"
    echo "  💾 Backups:          $BACKUPS_DIR"
    echo "  ⚙️  Configuration:    $ENV_FILE"
    echo
    echo "Management Commands:"
    echo "  Stop services:       ./deploy.sh stop"
    echo "  View logs:           ./deploy.sh logs"
    echo "  Backup data:         ./deploy.sh backup"
    echo "  Update platform:     ./deploy.sh update"
    echo
    echo "Next Steps:"
    echo "  1. Review configuration in $ENV_FILE"
    echo "  2. Change default passwords"
    echo "  3. Configure SSL certificates for production"
    echo "  4. Set up regular backups"
    echo "  5. Configure monitoring alerts"
    echo
    print_warning "This deployment uses self-signed SSL certificates."
    print_warning "Replace with proper certificates for production use."
    echo
}

# Function to stop services
stop_services() {
    print_status "Stopping LIHC Platform services..."
    
    if command_exists docker-compose; then
        docker-compose down
    else
        docker compose down
    fi
    
    print_success "Services stopped"
}

# Function to show logs
show_logs() {
    if command_exists docker-compose; then
        docker-compose logs -f
    else
        docker compose logs -f
    fi
}

# Function to backup data
backup_data() {
    print_status "Creating backup..."
    
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_name="lihc_backup_$timestamp"
    
    # Create backup directory
    mkdir -p "$BACKUPS_DIR/$backup_name"
    
    # Backup database
    docker exec lihc-postgres pg_dump -U lihc_user lihc_platform > "$BACKUPS_DIR/$backup_name/database.sql"
    
    # Backup data files
    tar -czf "$BACKUPS_DIR/$backup_name/data_files.tar.gz" -C "$DATA_DIR" .
    
    # Backup configuration
    cp "$ENV_FILE" "$BACKUPS_DIR/$backup_name/"
    
    print_success "Backup created: $BACKUPS_DIR/$backup_name"
}

# Function to update platform
update_platform() {
    print_status "Updating LIHC Platform..."
    
    # Pull latest images
    if command_exists docker-compose; then
        docker-compose pull
        docker-compose up -d --force-recreate
    else
        docker compose pull
        docker compose up -d --force-recreate
    fi
    
    print_success "Platform updated successfully"
}

# Main deployment function
deploy() {
    echo
    echo "==============================================="
    echo -e "${BLUE}${PLATFORM_NAME} v${VERSION} Deployment${NC}"
    echo "==============================================="
    echo
    
    check_requirements
    create_directories
    generate_env_file
    generate_ssl_certs
    setup_monitoring
    build_images
    start_services
    check_health
    init_database
    run_tests
    show_summary
}

# Parse command line arguments
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "stop")
        stop_services
        ;;
    "logs")
        show_logs
        ;;
    "backup")
        backup_data
        ;;
    "update")
        update_platform
        ;;
    "health")
        check_health
        ;;
    "restart")
        stop_services
        sleep 5
        start_services
        check_health
        ;;
    *)
        echo "Usage: $0 {deploy|stop|logs|backup|update|health|restart}"
        echo
        echo "Commands:"
        echo "  deploy   - Full deployment (default)"
        echo "  stop     - Stop all services"
        echo "  logs     - Show service logs"
        echo "  backup   - Create data backup"
        echo "  update   - Update to latest version"
        echo "  health   - Check service health"
        echo "  restart  - Restart all services"
        exit 1
        ;;
esac