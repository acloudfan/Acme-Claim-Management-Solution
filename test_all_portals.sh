#!/bin/bash
# Test All Portals Script
# Checks if all 5 services are running and accessible

echo "=========================================="
echo "ACME Claims - Portal Status Check"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if service is running
check_service() {
    local name=$1
    local url=$2

    if curl -s --head --request GET "$url" | grep "200\|301\|302" > /dev/null; then
        echo -e "${GREEN}✓${NC} $name is running at $url"
        return 0
    else
        echo -e "${RED}✗${NC} $name is NOT running at $url"
        return 1
    fi
}

# Check API Server
echo "Checking Backend Services..."
check_service "API Server" "http://localhost:8000/health"
api_status=$?
echo ""

# Check Frontend Portals
echo "Checking Frontend Portals..."
check_service "Customer Portal" "http://localhost:5173"
customer_status=$?

check_service "Adjustor Portal" "http://localhost:5174"
adjustor_status=$?

check_service "Admin Portal" "http://localhost:5170"
admin_status=$?

check_service "Executive Portal" "http://localhost:5176"
executive_status=$?
echo ""

# Summary
echo "=========================================="
echo "Summary"
echo "=========================================="

total=5
running=0

[ $api_status -eq 0 ] && ((running++))
[ $customer_status -eq 0 ] && ((running++))
[ $adjustor_status -eq 0 ] && ((running++))
[ $admin_status -eq 0 ] && ((running++))
[ $executive_status -eq 0 ] && ((running++))

echo "$running / $total services running"
echo ""

if [ $running -eq $total ]; then
    echo -e "${GREEN}✓ All services are running!${NC}"
    echo ""
    echo "Quick Links:"
    echo "  • API Docs:       http://localhost:8000/docs"
    echo "  • Customer:       http://localhost:5173"
    echo "  • Adjustor:       http://localhost:5174"
    echo "  • Admin:          http://localhost:5170"
    echo "  • Executive:      http://localhost:5176"
    echo ""
    echo "To test cross-portal navigation:"
    echo "  1. Open Admin Portal: http://localhost:5170"
    echo "  2. Click Quick Access buttons to open other portals"
    exit 0
else
    echo -e "${YELLOW}⚠ Some services are not running${NC}"
    echo ""
    echo "To start missing services:"

    if [ $api_status -ne 0 ]; then
        echo "  • API Server:      python -m src.api.main"
    fi
    if [ $customer_status -ne 0 ]; then
        echo "  • Customer Portal: cd src/ui/customer && npm run dev"
    fi
    if [ $adjustor_status -ne 0 ]; then
        echo "  • Adjustor Portal: cd src/ui/adjustor && npm run dev"
    fi
    if [ $admin_status -ne 0 ]; then
        echo "  • Admin Portal:    cd src/ui/admin && npm run dev"
    fi
    if [ $executive_status -ne 0 ]; then
        echo "  • Executive Portal: cd src/ui/executive && npm run dev"
    fi
    exit 1
fi
