#!/bin/bash
#
# Warehouse Database Diagnostic Script
# Run this on your Mac to troubleshoot Executive Portal issues
#

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================="
echo "Warehouse Database Diagnostic"
echo "========================================="
echo ""

# Check current directory
echo "Current directory: $(pwd)"
echo ""

# Check if warehouse database exists
if [ -f "claims-warehouse.db" ]; then
    echo -e "${GREEN}✓${NC} claims-warehouse.db found"
    echo "  Size: $(ls -lh claims-warehouse.db | awk '{print $5}')"
    echo "  Location: $(pwd)/claims-warehouse.db"

    # Check if it has data
    CLAIM_COUNT=$(sqlite3 claims-warehouse.db "SELECT COUNT(*) FROM claims_warehouse" 2>/dev/null || echo "0")
    if [ "$CLAIM_COUNT" -gt 0 ]; then
        echo -e "  ${GREEN}✓${NC} Contains $CLAIM_COUNT claims"
    else
        echo -e "  ${RED}✗${NC} Database is empty or corrupted"
    fi
else
    echo -e "${RED}✗${NC} claims-warehouse.db NOT found in $(pwd)"
    echo ""
    echo "Searching for warehouse database..."
    find . -name "claims-warehouse.db" -type f 2>/dev/null || echo "  No warehouse database found"
fi

echo ""

# Check if API server is running
echo "Checking API server..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} API server is running on port 8000"

    # Test executive endpoint
    echo ""
    echo "Testing executive API endpoint..."
    RESPONSE=$(curl -s http://localhost:8000/api/v1/executive/kpis?time_period=last_6_months 2>&1)

    if echo "$RESPONSE" | grep -q "detail"; then
        echo -e "${RED}✗${NC} Executive API error:"
        echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    elif echo "$RESPONSE" | grep -q "total_claims"; then
        echo -e "${GREEN}✓${NC} Executive API working correctly"
        echo "  Sample response: $(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"total_claims={d.get('total_claims', 'N/A')}\")" 2>/dev/null || echo "$RESPONSE" | head -c 100)"
    else
        echo -e "${YELLOW}⚠${NC} Unexpected response:"
        echo "$RESPONSE" | head -c 200
    fi
else
    echo -e "${RED}✗${NC} API server is NOT running"
    echo "  Start it with: ./scripts/start-api-server.sh"
fi

echo ""
echo "========================================="
