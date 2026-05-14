#!/bin/bash
# Quick start script for Insurance Claims API

# Parse arguments
CLEAN_MODE=false
if [ "$1" = "--clean" ]; then
    CLEAN_MODE=true
fi

echo "========================================"
echo "Insurance Claims API - Quick Start"
echo "========================================"
echo ""

# Clean mode: Delete database and uploads
if [ "$CLEAN_MODE" = true ]; then
    echo "🧹 CLEAN MODE ENABLED"
    echo ""

    # Run the seed-data.py --clean command
    echo "Running: uv run python scripts/seed-data.py --clean"
    uv run python scripts/seed-data.py --clean

    echo ""
    echo "✅ Clean complete!"
    echo ""
fi

# Check if config exists
if [ ! -f "api-config.yaml" ]; then
    echo "⚠️  Configuration file not found!"
    echo "Creating default configuration..."
    cp api-config.example.yaml api-config.yaml
    echo "✅ Created api-config.yaml"
    echo ""
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p uploads logs
echo "✅ Created uploads/ and logs/ directories"
echo ""

# Check if uv is installed
echo "Checking uv installation..."
if ! command -v uv &> /dev/null; then
    echo "⚠️  uv is not installed!"
    echo ""
    echo "Install uv with:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    echo "Or on Windows:"
    echo "  powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\""
    echo ""
    exit 1
fi

echo "✅ uv is installed"
echo ""

# Sync dependencies with uv
echo "Syncing dependencies with uv..."
uv sync
echo "✅ Dependencies synced"
echo ""

# Seed database if clean mode was used
if [ "$CLEAN_MODE" = true ]; then
    echo "Seeding database..."
    uv run python scripts/seed-data.py
    echo ""
fi

# Start the API
echo "Starting API server..."
echo "========================================"
echo ""
echo "API will be available at:"
echo "  - Swagger UI: http://localhost:8000/docs"
echo "  - ReDoc:      http://localhost:8000/redoc"
echo "  - Health:     http://localhost:8000/health"
echo ""
if [ "$CLEAN_MODE" = true ]; then
    echo "NOTE: Started with fresh database (cleaned and reseeded)"
    echo ""
fi
echo "Press Ctrl+C to stop the server"
echo ""
echo "========================================"
echo ""

# Run with uv
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
