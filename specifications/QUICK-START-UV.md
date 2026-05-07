# Quick Start with UV

## 🚀 One-Command Setup

```bash
./scripts/setup_uv.sh && ./scripts/start_api.sh
```

That's it! The API will be running at http://localhost:8000

---

## 📖 Step-by-Step Guide

### 1. Install UV

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Verify installation:**
```bash
uv --version
```

### 2. Setup Project

```bash
# Automated setup
./scripts/setup_uv.sh

# Or manually
uv sync                              # Install dependencies
cp api-config.example.yaml api-config.yaml
mkdir -p uploads logs
```

### 3. Start API

```bash
# Using the start script
./scripts/start_api.sh

# Start with clean database (deletes existing data)
./scripts/start_api.sh --clean

# Or manually
uv run uvicorn src.api.main:app --reload
```

### 4. Access API

Open your browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 🛠️ Common Commands

### Using Make (Recommended)

```bash
make help          # Show all commands
make init          # Complete initialization
make run           # Start API server
make test          # Run tests
make format        # Format code with black
make lint          # Lint with ruff
make clean         # Clean generated files
```

### Using UV Directly

```bash
# Install dependencies
uv sync                          # Core dependencies
uv sync --extra dev              # + dev tools
uv sync --extra ai               # + AI packages
uv sync --all-extras             # Everything

# Run commands
uv run <command>                 # Run any command
uv run python script.py          # Run Python script
uv run pytest                    # Run tests
uv run black src/api             # Format code
uv run ruff check src/api        # Lint code

# Start API
uv run uvicorn src.api.main:app --reload
```

---

## 📦 What Gets Installed

### Core Dependencies
- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **sqlalchemy** - ORM
- **pydantic** - Data validation
- **python-multipart** - File uploads
- **pyyaml** - Config parsing

### Dev Dependencies (optional: `--extra dev`)
- **pytest** - Testing framework
- **pytest-cov** - Coverage reporting
- **httpx** - API testing
- **faker** - Test data
- **black** - Code formatter
- **ruff** - Linter

### AI Dependencies (optional: `--extra ai`)
- **ultralytics** - YOLOv8
- **pillow** - Image processing
- **numpy** - Numerical computing

---

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/api --cov-report=html

# Run specific test
uv run pytest src/api/tests/test_claims.py

# Using Make
make test
make test-cov
```

---

## 🎨 Code Quality

```bash
# Format code
uv run black src/api

# Check formatting
uv run black --check src/api

# Lint code
uv run ruff check src/api

# Fix linting issues
uv run ruff check --fix src/api

# Using Make
make format
make lint
make lint-fix
```

---

## 🗄️ Database

The API uses **SQLite by default** for development.

**Reset database:**
```bash
rm test_insurance.db
# Database will be recreated on next startup

# Or with Make
make db-reset
```

**Switch to SQLAnywhere:**
Edit `api-config.yaml`:
```yaml
database:
  url: "sqlanywhere://user:password@localhost:2638/insurance_db"
```

---

## 📝 Configuration

Configuration is in `api-config.yaml`.

**Key settings:**
```yaml
api:
  host: "0.0.0.0"
  port: 8000
  debug: true

database:
  url: "sqlite:///./test_insurance.db"

storage:
  images_root_folder: "uploads"
  max_upload_size_mb: 10
  max_images_per_claim: 20

logging:
  level: "INFO"
  file: "logs/api.log"
```

---

## 🐛 Troubleshooting

### UV not found
```bash
# Restart shell or source profile
source ~/.bashrc  # or ~/.zshrc

# Or add to PATH manually
export PATH="$HOME/.cargo/bin:$PATH"
```

### Import errors
```bash
# Ensure dependencies are installed
uv sync

# Verify installation
uv run python -c "import fastapi"
```

### Permission denied on scripts
```bash
chmod +x setup_uv.sh start_api.sh
```

### Port already in use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uv run uvicorn src.api.main:app --reload --port 8001
```

---

## 📚 Additional Resources

- **API Documentation**: `specifications/README-API.md`
- **Implementation Details**: `specifications/API-IMPLEMENTATION-SUMMARY.md`
- **Project Overview**: `CLAUDE.md`
- **Design Spec**: `specifications/API-BACKEND-DESIGN.md`

---

## 🎯 Quick Test

```bash
# 1. Start API
./scripts/start_api.sh

# 2. In another terminal, test health endpoint
curl http://localhost:8000/health

# 3. Open Swagger UI in browser
open http://localhost:8000/docs  # macOS
xdg-open http://localhost:8000/docs  # Linux

# 4. Try creating a claim via Swagger UI
```

---

## 💡 Pro Tips

1. **Use Make for everything** - `make help` shows all commands
2. **Install dev tools early** - `uv sync --extra dev`
3. **Enable hot reload** - It's on by default with `--reload`
4. **Check logs** - `tail -f logs/api.log` or `make logs`
5. **Reset database often** - `make db-reset` for clean slate
6. **Format before committing** - `make format lint`

---

## 🆘 Need Help?

```bash
# Show available make commands
make help

# Show uv help
uv --help

# Validate project structure
uv run python scripts/validate_api.py

# Check API health
curl http://localhost:8000/health
```

---

**Ready to build!** 🚀
