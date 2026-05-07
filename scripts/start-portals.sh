#!/bin/bash
#
# UI Portals Launch Script
# Starts the React development servers for all UI portals
# Currently: Customer Portal, Adjustor Portal (future: Executive, Admin)
#

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CUSTOMER_PORTAL_DIR="$PROJECT_ROOT/src/ui/customer"
ADJUSTOR_PORTAL_DIR="$PROJECT_ROOT/src/ui/adjustor"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  UI Portals Launcher${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if portal directories exist
if [ ! -d "$CUSTOMER_PORTAL_DIR" ]; then
    echo -e "${RED}ERROR: Customer portal directory not found at:${NC}"
    echo -e "${RED}  $CUSTOMER_PORTAL_DIR${NC}"
    exit 1
fi

if [ ! -d "$ADJUSTOR_PORTAL_DIR" ]; then
    echo -e "${RED}ERROR: Adjustor portal directory not found at:${NC}"
    echo -e "${RED}  $ADJUSTOR_PORTAL_DIR${NC}"
    exit 1
fi

echo -e "${BLUE}Starting Customer Portal and Adjustor Portal...${NC}"
echo -e "${YELLOW}(Executive and Admin portals coming in future phases)${NC}"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}ERROR: Node.js is not installed${NC}"
    echo -e "Please install Node.js (v18+) from: https://nodejs.org/"
    exit 1
fi

# Check Node version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo -e "${YELLOW}WARNING: Node.js version is $NODE_VERSION, but v18+ is recommended${NC}"
fi

echo -e "${GREEN}✓${NC} Node.js version: $(node -v)"
echo -e "${GREEN}✓${NC} npm version: $(npm -v)"
echo ""

# Check and setup Customer Portal
echo -e "${BLUE}Checking Customer Portal...${NC}"
cd "$CUSTOMER_PORTAL_DIR"
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠ Installing customer portal dependencies...${NC}"
    npm install
    echo -e "${GREEN}✓${NC} Customer portal dependencies installed"
fi
if [ ! -f "public/customer-portal-config.yaml" ]; then
    echo -e "${YELLOW}⚠ WARNING: customer-portal-config.yaml not found${NC}"
fi
echo -e "${GREEN}✓${NC} Customer portal ready"
echo ""

# Check and setup Adjustor Portal
echo -e "${BLUE}Checking Adjustor Portal...${NC}"
cd "$ADJUSTOR_PORTAL_DIR"
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠ Installing adjustor portal dependencies...${NC}"
    npm install
    echo -e "${GREEN}✓${NC} Adjustor portal dependencies installed"
fi
if [ ! -f "public/adjustor-portal-config.yaml" ]; then
    echo -e "${YELLOW}⚠ WARNING: adjustor-portal-config.yaml not found${NC}"
fi
echo -e "${GREEN}✓${NC} Adjustor portal ready"
echo ""

# Check if API server is running
echo -e "${BLUE}Checking API server...${NC}"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} API server is running at http://localhost:8000"
else
    echo -e "${YELLOW}⚠ WARNING: API server is not running at http://localhost:8000${NC}"
    echo -e "${YELLOW}  The portal requires the API server to function.${NC}"
    echo -e "${YELLOW}  Start it with: ./scripts/start_api.sh${NC}"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Starting Development Servers...${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Customer Portal:  ${GREEN}http://localhost:5173${NC}"
echo -e "Adjustor Portal:  ${GREEN}http://localhost:5174${NC}"
echo ""
echo -e "${YELLOW}Future portals:${NC}"
echo -e "  Executive Portal: http://localhost:5175 (coming soon)"
echo -e "  Admin Portal: http://localhost:5176 (coming soon)"
echo ""
echo -e "Press ${YELLOW}Ctrl+C${NC} to stop all servers"
echo ""

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping all portal servers...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

# Start Customer Portal in background
cd "$CUSTOMER_PORTAL_DIR"
echo -e "${BLUE}Starting Customer Portal on port 5173...${NC}"
npm run dev > /tmp/customer-portal.log 2>&1 &
CUSTOMER_PID=$!

# Start Adjustor Portal in background
cd "$ADJUSTOR_PORTAL_DIR"
echo -e "${BLUE}Starting Adjustor Portal on port 5174...${NC}"
npm run dev > /tmp/adjustor-portal.log 2>&1 &
ADJUSTOR_PID=$!

echo ""
echo -e "${GREEN}✓${NC} Both portals starting..."
echo -e "${YELLOW}Tip: Check logs at /tmp/customer-portal.log and /tmp/adjustor-portal.log${NC}"
echo ""

# Wait for both processes
wait
