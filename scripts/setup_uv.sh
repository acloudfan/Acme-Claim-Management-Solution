#!/bin/bash
# Setup script for uv package manager

echo "========================================"
echo "Insurance Claims API - UV Setup"
echo "========================================"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed"
    echo ""
    echo "Installing uv..."
    echo ""

    # Detect OS and install accordingly
    if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
        # Linux or macOS
        curl -LsSf https://astral.sh/uv/install.sh | sh
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        # Windows (Git Bash or similar)
        echo "On Windows, please run:"
        echo "  powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\""
        exit 1
    else
        echo "Unknown OS. Please install uv manually:"
        echo "  https://github.com/astral-sh/uv"
        exit 1
    fi

    echo ""
    echo "✅ uv installed successfully"
else
    echo "✅ uv is already installed"
fi

echo ""
echo "uv version:"
uv --version
echo ""

# Initialize project
echo "Initializing project with uv..."
echo ""

# Sync dependencies
echo "Syncing dependencies..."
uv sync
echo ""
echo "✅ Dependencies synced"
echo ""

# Create necessary directories
echo "Creating project directories..."
mkdir -p uploads logs
echo "✅ Created uploads/ and logs/ directories"
echo ""

# Create config if not exists
if [ ! -f "api-config.yaml" ]; then
    echo "Creating default configuration..."
    cp api-config.example.yaml api-config.yaml
    echo "✅ Created api-config.yaml"
    echo ""
fi

# Verify installation
echo "Verifying installation..."
if uv run python -c "import fastapi, sqlalchemy, pydantic; from src.api import config" 2>/dev/null; then
    echo "✅ All core dependencies installed correctly"
    echo "✅ Package imports working"
else
    echo "❌ Some dependencies failed to install"
    exit 1
fi

echo ""
echo "========================================"
echo "Setup Complete! 🎉"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Review api-config.yaml"
echo "  2. Start the API: ./start_api.sh"
echo "  3. Or run manually: uv run uvicorn src.api.main:app --reload"
echo ""
echo "Optional - Install dev dependencies:"
echo "  uv sync --extra dev"
echo ""
echo "Optional - Install AI dependencies:"
echo "  uv sync --extra ai"
echo ""
