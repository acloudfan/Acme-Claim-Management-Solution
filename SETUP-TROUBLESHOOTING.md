# Setup Troubleshooting Guide

This guide helps resolve common issues when setting up the ACME Insurance Claims Management System.

---

## Quick Fix Checklist

If you're experiencing issues, try these steps in order:

1. **Fix Database Configuration**
   ```bash
   # Edit api-config.yaml and ensure database URL is set to SQLite
   # Change line 8 to: url: sqlite:///./test_insurance.db
   ```

2. **Clean Install UI Dependencies**
   ```bash
   ./scripts/install-ui-dependencies.sh --clean
   ```

3. **Start API Server**
   ```bash
   ./scripts/start-api-server.sh --clean
   ```

4. **Start UI Portals**
   ```bash
   ./scripts/start-portals.sh
   ```

---

## Common Errors and Solutions

### Error: "Can't load plugin: sqlalchemy.dialects:sqlanywhere"

**Cause:** The `api-config.yaml` file has an incorrect database URL pointing to SQL Anywhere instead of SQLite.

**Solution:**
```bash
# Open api-config.yaml
nano api-config.yaml  # or use your preferred editor

# Find the database section (around line 7-8) and change to:
database:
  url: sqlite:///./test_insurance.db
  pool_size: 5
  max_overflow: 10
  echo: false
```

Save the file and restart the API server.

---

### Error: "Cannot find module 'vite/dist/node/cli.js'"

**Cause:** npm dependencies are incomplete or corrupted. The Vite package installed but its dist folder is missing.

**Solution 1 - Use the installation script (Recommended):**
```bash
./scripts/install-ui-dependencies.sh --clean
```

**Solution 2 - Manual cleanup:**
```bash
# Go to each portal directory and clean install
cd src/ui/admin
rm -rf node_modules package-lock.json
npm install
cd ../../..

cd src/ui/customer
rm -rf node_modules package-lock.json
npm install
cd ../../..

cd src/ui/adjustor
rm -rf node_modules package-lock.json
npm install
cd ../../..

cd src/ui/executive
rm -rf node_modules package-lock.json
npm install
cd ../../..
```

**Why this happens:** Sometimes npm install completes but doesn't fully extract all package files, especially when there are network interruptions or cache issues.

---

### Error: API server won't start / Database errors

**Solution:**
```bash
# Clean restart with fresh database
./scripts/start-api-server.sh --clean

# This will:
# - Delete existing database
# - Create new database with schema
# - Seed with demo data
```

---

### Error: "No module named 'anthropic'" or similar Python import errors

**Cause:** Python dependencies not installed.

**Solution:**
```bash
# Install Python dependencies using uv
uv sync

# Or if using pip
pip install -r requirements.txt
```

---

### Error: Portals start but can't connect to API (Network errors in browser)

**Cause:** API server is not running or CORS configuration issue.

**Solution:**
```bash
# 1. Check if API server is running
curl http://localhost:8000/api/health

# 2. If not running, start it
./scripts/start-api-server.sh

# 3. Check the API logs
tail -f logs/api.log
```

---

## Complete Reset Procedure

If nothing else works, start completely fresh:

```bash
# 1. Stop all running processes
pkill -f "uvicorn"
pkill -f "vite"

# 2. Clean Python environment
rm -rf .venv
uv sync

# 3. Clean database
rm -f test_insurance.db claims-warehouse.db

# 4. Clean UI dependencies
./scripts/install-ui-dependencies.sh --clean

# 5. Start fresh
./scripts/start-api-server.sh --clean
./scripts/start-portals.sh
```

---

## Verification Steps

After setup, verify everything is working:

### 1. Check API Server
```bash
curl http://localhost:8000/api/health
# Should return: {"status":"healthy"}
```

### 2. Check API Documentation
Open in browser: http://localhost:8000/docs
- Should see FastAPI Swagger UI with all endpoints

### 3. Check Portals
- Customer Portal: http://localhost:5173
- Adjustor Portal: http://localhost:5174
- Admin Portal: http://localhost:5170
- Executive Portal: http://localhost:5175

All should load without errors in the browser console.

---

## Still Having Issues?

### Check System Requirements

**Node.js:**
```bash
node --version  # Should be v18.x or higher
npm --version   # Should be 9.x or higher
```

**Python:**
```bash
python3 --version  # Should be 3.11 or higher
```

**uv (Python package manager):**
```bash
uv --version  # Should be installed
```

If missing, install:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Check Log Files

**API Logs:**
```bash
tail -f logs/api.log
```

**Portal Logs:**
```bash
tail -f /tmp/customer-portal.log
tail -f /tmp/adjustor-portal.log
tail -f /tmp/admin-portal.log
tail -f /tmp/executive-portal.log
```

### Report an Issue

If you're still stuck, please report the issue at:
https://github.com/your-repo/issues

Include:
- Error message (full stack trace)
- Output of `node --version` and `python3 --version`
- Relevant log files
- Steps you've already tried

---

## Tips for Smooth Setup

1. **Always use --clean flag on first run**
   ```bash
   ./scripts/install-ui-dependencies.sh --clean
   ./scripts/start-api-server.sh --clean
   ```

2. **Check your .env file**
   - Copy `.env.example` to `.env`
   - Add at least one LLM provider API key
   - AWS Bedrock users: configure `aws configure` or add AWS keys to `.env`

3. **Don't mix package managers**
   - Use `npm` consistently (not yarn/pnpm)
   - Use `uv` for Python (not pip/poetry)

4. **Check port conflicts**
   ```bash
   # If ports are in use, find and kill the processes
   lsof -i :8000  # API server
   lsof -i :5173  # Customer portal
   lsof -i :5174  # Adjustor portal
   lsof -i :5170  # Admin portal
   lsof -i :5175  # Executive portal
   ```

---

## Environment-Specific Notes

### WSL (Windows Subsystem for Linux)
- File permissions may need adjustment: `chmod +x scripts/*.sh`
- Ensure Windows Defender isn't blocking npm operations

### macOS
- May need to install Xcode Command Line Tools: `xcode-select --install`

### Linux
- Ensure you have build essentials: `sudo apt-get install build-essential`

---

**Last Updated:** 2026-05-08
