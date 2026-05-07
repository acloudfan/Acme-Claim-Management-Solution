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

    # Get database file from config
    DB_FILE="test_insurance.db"
    if [ -f "api-config.yaml" ]; then
        # Extract database filename from config (simple grep)
        DB_PATH=$(grep -oP 'url:.*sqlite:///\./\K[^"]+' api-config.yaml 2>/dev/null || echo "test_insurance.db")
        DB_FILE="${DB_PATH%.db}.db"
    fi

    # Delete database
    if [ -f "$DB_FILE" ]; then
        echo "🗑️  Deleting database: $DB_FILE"
        rm -f "$DB_FILE"
        echo "✅ Database deleted"
    else
        echo "ℹ️  Database file not found: $DB_FILE"
    fi

    # Delete all files from uploads folder
    UPLOAD_DIR="uploads"
    if [ -f "api-config.yaml" ]; then
        # Extract uploads folder from config
        UPLOAD_DIR=$(grep -oP 'images_root_folder:\s*"\K[^"]+' api-config.yaml 2>/dev/null || echo "uploads")
    fi

    if [ -d "$UPLOAD_DIR" ]; then
        FILE_COUNT=$(find "$UPLOAD_DIR" -type f 2>/dev/null | wc -l)
        if [ "$FILE_COUNT" -gt 0 ]; then
            echo "🗑️  Deleting $FILE_COUNT file(s) from: $UPLOAD_DIR"
            find "$UPLOAD_DIR" -type f -delete
            echo "✅ Upload files deleted"
        else
            echo "ℹ️  Upload folder is empty: $UPLOAD_DIR"
        fi
    else
        echo "ℹ️  Upload folder not found: $UPLOAD_DIR"
    fi

    echo ""
    echo "✅ Clean complete! Starting with fresh database..."
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
    echo "NOTE: Started with clean database"
    echo ""
fi
echo "Press Ctrl+C to stop the server"
echo ""
echo "========================================"
echo ""

# Run with uv
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
