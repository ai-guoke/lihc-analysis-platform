#!/bin/bash

# Start Celery workers for LIHC Analysis Platform
# Usage: ./start_celery.sh [all|quick|standard|heavy|batch|flower]

COMMAND=${1:-all}
LOGLEVEL=${LOGLEVEL:-info}

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting Celery components for LIHC Analysis Platform...${NC}"

# Function to start a worker
start_worker() {
    local queue=$1
    local concurrency=$2
    local name=$3
    
    echo -e "${GREEN}Starting $name worker (Queue: $queue, Concurrency: $concurrency)...${NC}"
    celery -A src.analysis.task_queue worker \
        --loglevel=$LOGLEVEL \
        -Q $queue \
        -n $name@%h \
        -c $concurrency \
        --detach \
        --pidfile=/tmp/celery-$name.pid \
        --logfile=/tmp/celery-$name.log
}

# Function to start flower
start_flower() {
    echo -e "${GREEN}Starting Flower monitoring dashboard...${NC}"
    celery -A src.analysis.task_queue flower \
        --port=5555 \
        --detach \
        --pidfile=/tmp/celery-flower.pid \
        --logfile=/tmp/celery-flower.log
    echo -e "${BLUE}Flower dashboard available at: http://localhost:5555${NC}"
}

# Function to start beat
start_beat() {
    echo -e "${GREEN}Starting Celery Beat scheduler...${NC}"
    celery -A src.analysis.task_queue beat \
        --loglevel=$LOGLEVEL \
        --detach \
        --pidfile=/tmp/celery-beat.pid \
        --logfile=/tmp/celery-beat.log
}

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${RED}Error: Redis is not running. Please start Redis first.${NC}"
    echo "You can start Redis with: redis-server"
    exit 1
fi

# Start components based on command
case $COMMAND in
    all)
        start_worker quick 4 worker-quick
        start_worker standard 2 worker-standard
        start_worker heavy 1 worker-heavy
        start_worker batch 2 worker-batch
        start_beat
        start_flower
        ;;
    quick)
        start_worker quick 4 worker-quick
        ;;
    standard)
        start_worker standard 2 worker-standard
        ;;
    heavy)
        start_worker heavy 1 worker-heavy
        ;;
    batch)
        start_worker batch 2 worker-batch
        ;;
    flower)
        start_flower
        ;;
    beat)
        start_beat
        ;;
    *)
        echo -e "${RED}Usage: $0 [all|quick|standard|heavy|batch|flower|beat]${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}Celery components started successfully!${NC}"
echo -e "${BLUE}Check logs in /tmp/celery-*.log${NC}"
echo -e "${BLUE}To stop all workers: ./stop_celery.sh${NC}"