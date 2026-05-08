#!/bin/bash
#
# UI Dependencies Installation Script
# Installs npm dependencies for all UI portals
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

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  UI Dependencies Installer${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}ERROR: npm is not installed${NC}"
    echo -e "${YELLOW}Please install Node.js and npm first:${NC}"
    echo "  https://nodejs.org/"
    exit 1
fi

echo -e "${GREEN}✓${NC} npm found: $(npm --version)"
echo -e "${GREEN}✓${NC} node found: $(node --version)"
echo ""

# Array of portals to install
PORTALS=(
    "customer:src/ui/customer"
    "adjustor:src/ui/adjustor"
    "admin:src/ui/admin"
    "executive:src/ui/executive"
)

FAILED_PORTALS=()
SUCCESS_COUNT=0

# Install dependencies for each portal
for portal_info in "${PORTALS[@]}"; do
    IFS=':' read -r portal_name portal_path <<< "$portal_info"
    PORTAL_DIR="$PROJECT_ROOT/$portal_path"

    echo -e "${BLUE}Installing ${portal_name} portal dependencies...${NC}"

    if [ ! -d "$PORTAL_DIR" ]; then
        echo -e "${RED}ERROR: Portal directory not found: $PORTAL_DIR${NC}"
        FAILED_PORTALS+=("$portal_name (directory not found)")
        continue
    fi

    cd "$PORTAL_DIR"

    # Check if package.json exists
    if [ ! -f "package.json" ]; then
        echo -e "${RED}ERROR: package.json not found in $PORTAL_DIR${NC}"
        FAILED_PORTALS+=("$portal_name (no package.json)")
        continue
    fi

    # Remove existing node_modules if --clean flag is provided
    if [ "$1" = "--clean" ]; then
        if [ -d "node_modules" ]; then
            echo -e "${YELLOW}  Removing existing node_modules...${NC}"
            rm -rf node_modules
        fi
        if [ -f "package-lock.json" ]; then
            echo -e "${YELLOW}  Removing package-lock.json...${NC}"
            rm -f package-lock.json
        fi
    fi

    # Install dependencies
    if npm install; then
        # Verify critical dependency (vite) was installed correctly
        if [ ! -d "node_modules/vite/dist" ]; then
            echo -e "${RED}✗${NC} ${portal_name} portal installation incomplete (vite dist missing)"
            echo -e "${YELLOW}  Retrying with clean install...${NC}"
            rm -rf node_modules package-lock.json
            if npm install; then
                if [ -d "node_modules/vite/dist" ]; then
                    echo -e "${GREEN}✓${NC} ${portal_name} portal dependencies installed (after retry)"
                    ((SUCCESS_COUNT++))
                else
                    echo -e "${RED}✗${NC} ${portal_name} portal still incomplete after retry"
                    FAILED_PORTALS+=("$portal_name (vite corrupted)")
                fi
            else
                echo -e "${RED}✗${NC} Failed to install ${portal_name} portal dependencies (retry failed)"
                FAILED_PORTALS+=("$portal_name")
            fi
        else
            echo -e "${GREEN}✓${NC} ${portal_name} portal dependencies installed"
            ((SUCCESS_COUNT++))
        fi
    else
        echo -e "${RED}✗${NC} Failed to install ${portal_name} portal dependencies"
        FAILED_PORTALS+=("$portal_name")
    fi

    echo ""
done

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Installation Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Successful:${NC} $SUCCESS_COUNT/${#PORTALS[@]} portals"

if [ ${#FAILED_PORTALS[@]} -gt 0 ]; then
    echo -e "${RED}Failed:${NC}"
    for failed in "${FAILED_PORTALS[@]}"; do
        echo -e "  ${RED}✗${NC} $failed"
    done
    echo ""
    echo -e "${YELLOW}TIP: Try running with --clean flag to remove existing node_modules:${NC}"
    echo -e "  ./scripts/install-ui-dependencies.sh --clean"
    exit 1
else
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  All dependencies installed!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "Next steps:"
    echo -e "  1. Start API server:    ${BLUE}./scripts/start-api-server.sh${NC}"
    echo -e "  2. Start UI portals:    ${BLUE}./scripts/start-portals.sh${NC}"
    echo ""
fi
