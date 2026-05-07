#!/bin/bash
#
# Full Stack Launcher
# Starts both API server and Customer Portal
#

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Full Stack Launcher${NC}"
echo -e "${BLUE}  API + Customer Portal${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down servers...${NC}"
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null || true
        echo -e "${GREEN}✓${NC} API server stopped"
    fi
    if [ ! -z "$PORTAL_PID" ]; then
        kill $PORTAL_PID 2>/dev/null || true
        echo -e "${GREEN}✓${NC} UI Portals stopped"
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Check if API server is already running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ API server is already running at http://localhost:8000${NC}"
    echo -e "Using existing API server instance"
    API_ALREADY_RUNNING=true
else
    # Start API server
    echo -e "${BLUE}Starting API server...${NC}"
    cd "$PROJECT_ROOT"

    if command -v uv &> /dev/null; then
        nohup uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000 > logs/api-server.log 2>&1 &
        API_PID=$!
        echo -e "${GREEN}✓${NC} API server started (PID: $API_PID)"
        echo -e "  Logs: logs/api-server.log"
    else
        echo -e "${RED}ERROR: 'uv' command not found${NC}"
        echo -e "Please install uv or start API server manually"
        exit 1
    fi

    # Wait for API to be ready
    echo -e "${BLUE}Waiting for API server to be ready...${NC}"
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} API server is ready!"
            break
        fi
        if [ $i -eq 30 ]; then
            echo -e "${RED}ERROR: API server failed to start${NC}"
            echo -e "Check logs: logs/api-server.log"
            exit 1
        fi
        sleep 1
        echo -n "."
    done
    echo ""
fi

echo ""

# Start UI Portals
echo -e "${BLUE}Starting UI Portals (Customer)...${NC}"
cd "$PROJECT_ROOT/src/ui/customer"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing npm dependencies...${NC}"
    npm install
fi

# Start customer portal
nohup npm run dev > "$PROJECT_ROOT/logs/customer-portal.log" 2>&1 &
PORTAL_PID=$!
echo -e "${GREEN}✓${NC} Customer Portal started (PID: $PORTAL_PID)"
echo -e "  Logs: logs/customer-portal.log"

# Wait for portal to be ready
echo -e "${BLUE}Waiting for portal to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Portal is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${YELLOW}WARNING: Portal may still be starting...${NC}"
    fi
    sleep 1
    echo -n "."
done
echo ""

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✓ Full Stack is Running!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "API Server:       ${BLUE}http://localhost:8000${NC}"
echo -e "Customer Portal:  ${BLUE}http://localhost:5173${NC}"
echo -e "API Docs:         ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo -e "Logs:"
echo -e "  API:              logs/api-server.log"
echo -e "  Customer Portal:  logs/customer-portal.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"
echo ""

# Keep script running
wait
