# Scripts Directory

This directory contains utility scripts for launching and managing the Insurance Claims system.

---

## Available Scripts

### 🚀 Full Stack Launcher

**Start both API server and Customer Portal with one command:**

```bash
./scripts/start-full-stack.sh
```

**What it does:**
- Checks if API server is already running
- Starts API server at http://localhost:8000
- Starts Customer Portal at http://localhost:5173
- Installs dependencies if needed (first time)
- Displays access URLs and log locations
- Gracefully shuts down both on Ctrl+C

**Recommended for:** First-time users, development, demos

---

### 🎨 UI Portals Launcher

**Start all UI portals (currently Customer Portal, more coming soon):**

```bash
./scripts/start-portals.sh
```

**What it does:**
- Checks Node.js installation and version
- Installs npm dependencies if needed
- Verifies API server is running (warns if not)
- Starts Customer Portal at http://localhost:5173
- (Future: Will start Adjustor, Executive, Admin portals)

**Recommended for:** UI-only development, when API is already running

---

### 🔧 API Server Launcher

**Start only the API server (FastAPI):**

```bash
./scripts/start-api-server.sh
# Or use the existing script:
./scripts/start_api.sh
```

**What it does:**
- Checks uv installation
- Starts uvicorn server with auto-reload
- Opens API at http://localhost:8000
- API docs available at http://localhost:8000/docs

**Recommended for:** Backend development, API testing

---

## Prerequisites

### For Customer Portal Scripts

- **Node.js** v18+ ([Download](https://nodejs.org/))
- **npm** (comes with Node.js)

Check versions:
```bash
node --version  # Should be v18.0.0 or higher
npm --version
```

### For API Server Scripts

- **Python** 3.13+ 
- **uv** package manager ([Install](https://github.com/astral-sh/uv))

Check installation:
```bash
uv --version
python3 --version
```

---

## Script Details

### start-full-stack.sh

**Location:** `scripts/start-full-stack.sh`

**Features:**
- ✅ Automatic dependency installation
- ✅ Health checks before proceeding
- ✅ Log output to `logs/api-server.log` and `logs/portal.log`
- ✅ Graceful shutdown (Ctrl+C)
- ✅ Colored output for easy reading

**Ports Used:**
- 8000 - API Server
- 5173 - Customer Portal (Vite dev server)

**Logs:**
- API: `logs/api-server.log`
- Portal: `logs/portal.log`

---

### start-portals.sh

**Location:** `scripts/start-portals.sh`

**Features:**
- ✅ Node.js version check (warns if < v18)
- ✅ Dependency installation check
- ✅ Configuration file validation
- ✅ API server availability check
- ✅ Interactive confirmation if API not running
- ✅ Future-ready for multiple portals (Adjustor, Executive, Admin)

**Current Portals:**
- Customer Portal: http://localhost:5173

**Future Portals:**
- Adjustor Portal: http://localhost:5174 (coming soon)
- Executive Portal: http://localhost:5175 (coming soon)
- Admin Portal: http://localhost:5176 (coming soon)

**Configuration:**
- Reads: `src/ui/customer/public/customer-portal-config.yaml`
- Falls back to defaults if config missing

---

### start-api-server.sh (or start_api.sh)

**Location:** `scripts/start_api.sh`

**Features:**
- ✅ uv installation check
- ✅ Database connection check
- ✅ Auto-reload on code changes
- ✅ Comprehensive error messages

**Configuration:**
- Reads: `api-config.yaml`

---

## Troubleshooting

### Port Already in Use

**Error:** `Address already in use`

**Solution:**

**API (port 8000):**
```bash
# Find process
lsof -i :8000
# Kill it
kill -9 <PID>
```

**Portal (port 5173):**
```bash
# Find process
lsof -i :5173
# Kill it
kill -9 <PID>
```

---

### Script Permission Denied

**Error:** `Permission denied`

**Solution:**
```bash
chmod +x scripts/start-full-stack.sh
chmod +x scripts/start-portals.sh
chmod +x scripts/start_api.sh
```

---

### Node Modules Not Found

**Error:** `Cannot find module 'react'`

**Solution:**
```bash
cd src/ui/customer
rm -rf node_modules package-lock.json
npm install
```

---

### API Server Not Starting

**Check:**
1. Is Python 3.13+ installed? `python3 --version`
2. Is uv installed? `uv --version`
3. Is database file accessible? `ls test_insurance.db`
4. Check logs: `tail -f logs/api-server.log`

---

### Portal Not Loading

**Check:**
1. Is Node.js v18+ installed? `node --version`
2. Are dependencies installed? `ls src/ui/customer/node_modules`
3. Is API server running? `curl http://localhost:8000/health`
4. Check browser console for errors (F12)

---

## Development Workflow

### Typical Development Session

```bash
# Terminal 1: Start full stack
./scripts/start-full-stack.sh

# Terminal 2: Make code changes
# Files auto-reload on save

# Terminal 1: Press Ctrl+C to stop when done
```

### Backend-Only Development

```bash
# Terminal 1: Start API
./scripts/start-api-server.sh

# Make changes to src/api/
# Server auto-reloads
```

### Frontend-Only Development

```bash
# Terminal 1: Start API (if not running)
./scripts/start-api-server.sh

# Terminal 2: Start Portal
./scripts/start-customer-portal.sh

# Make changes to src/ui/customer/src/
# Portal auto-reloads via HMR (Hot Module Replacement)
```

---

## Adding New Scripts

When adding new scripts to this directory:

1. **Follow naming convention:** `start-<service>.sh` or `<action>_<service>.sh`
2. **Make executable:** `chmod +x scripts/your-script.sh`
3. **Add documentation** to this README
4. **Include error handling** and user-friendly messages
5. **Use colors** for better readability

---

## Testing Scripts

### Test API Server

```bash
./scripts/start_api.sh
# In another terminal:
curl http://localhost:8000/health
# Should return: {"status":"healthy",...}
```

### Test UI Portals

```bash
./scripts/start-portals.sh
# Open browser: http://localhost:5173
# Should see customer portal login page
```

### Test Full Stack

```bash
./scripts/start-full-stack.sh
# Wait for both servers to start
# Open browser: http://localhost:5173
# Login and test functionality
```

---

## Script Maintenance

**Last Updated:** 2026-05-04  
**Maintained By:** Development Team

**Change Log:**
- 2026-05-04: Added customer portal launcher scripts
- 2026-05-04: Added full stack launcher
- 2026-05-04: Created scripts README

---

For more information, see:
- **API Documentation:** `specifications/API-SPECIFICATIONS.md`
- **Portal Quickstart:** `UI-PORTAL-QUICKSTART.md`
- **Project README:** `README.md`
