#!/bin/bash
#
# Force restart API server with full cleanup
# Use this when configuration changes aren't taking effect
#

set -e

echo "========================================="
echo "Force Restart API Server"
echo "========================================="
echo ""

# Kill all uvicorn processes
echo "1. Stopping all uvicorn processes..."
pkill -9 -f uvicorn || echo "  No uvicorn processes found"
sleep 2

# Clear Python cache
echo "2. Clearing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Verify API is stopped
echo "3. Verifying API server is stopped..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "  ERROR: API server is still running!"
    exit 1
else
    echo "  ✓ API server stopped"
fi

echo ""
echo "4. Starting API server with fresh configuration..."
echo ""

# Start API server
./scripts/start-api-server.sh
