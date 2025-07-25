#!/bin/bash

# Stop Celery workers for LIHC Analysis Platform

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Stopping Celery components...${NC}"

# Function to stop a component
stop_component() {
    local name=$1
    local pidfile="/tmp/celery-$name.pid"
    
    if [ -f "$pidfile" ]; then
        PID=$(cat "$pidfile")
        if ps -p $PID > /dev/null; then
            echo -e "${GREEN}Stopping $name (PID: $PID)...${NC}"
            kill $PID
            rm -f "$pidfile"
        else
            echo -e "${RED}$name not running (stale PID file)${NC}"
            rm -f "$pidfile"
        fi
    else
        echo -e "${RED}$name not found${NC}"
    fi
}

# Stop all components
stop_component "worker-quick"
stop_component "worker-standard"
stop_component "worker-heavy"
stop_component "worker-batch"
stop_component "beat"
stop_component "flower"

# Clean up any remaining processes
echo -e "${BLUE}Cleaning up any remaining Celery processes...${NC}"
pkill -f "celery -A src.analysis.task_queue" || true

echo -e "${GREEN}All Celery components stopped!${NC}"