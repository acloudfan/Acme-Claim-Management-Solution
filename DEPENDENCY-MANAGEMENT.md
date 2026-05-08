# Dependency Management Guide

This guide explains how to lock down and manage dependencies for both NPM (frontend) and Python (backend) to ensure reproducible builds across all environments.

---

## Why Lock Dependencies?

**Without locking:**
- `"react": "^19.2.5"` means npm can install 19.2.5, 19.2.6, 19.3.0, etc.
- Different developers get different versions
- CI/CD might install different versions than local
- "Works on my machine" problems

**With locking:**
- Everyone gets **exactly** the same versions
- Builds are reproducible
- No surprise version updates

---

## NPM Dependency Locking (Frontend Portals)

### Current State

The project uses:
- **package.json** - Defines dependency ranges (e.g., `^19.2.5`)
- **package-lock.json** - Records exact versions installed

### Problem

Semver ranges (`^`, `~`) allow version flexibility:
- `^19.2.5` → allows 19.2.6, 19.3.0, 19.9.9 (not 20.0.0)
- `~19.2.5` → allows 19.2.6, 19.2.9 (not 19.3.0)

### Solution: Exact Versions + Lock Files

#### Method 1: Automatic Locking (Recommended)

```bash
# Lock all dependencies to exact versions
./scripts/lock-dependencies.sh
```

This script:
1. Removes `^` and `~` from all package.json files
2. Regenerates package-lock.json files
3. Uses exact versions (e.g., `"react": "19.2.5"`)

#### Method 2: Manual Locking

**Step 1: Install with exact versions**
```bash
cd src/ui/customer
npm install --save-exact react@19.2.5
npm install --save-exact --save-dev vite@5.4.21
```

**Step 2: Configure npm to always use exact versions**
```bash
npm config set save-exact true
```

**Step 3: Commit lock files**
```bash
git add package.json package-lock.json
git commit -m "Lock npm dependencies to exact versions"
```

### Verification

Check that package.json has no `^` or `~`:
```bash
grep -E "\\^|~" src/ui/*/package.json
# Should return nothing
```

### Updating Locked Dependencies

When you need to update:

```bash
# Update specific package
cd src/ui/customer
npm install --save-exact react@19.3.0

# Or update all (carefully!)
rm -rf node_modules package-lock.json
npm install
./scripts/lock-dependencies.sh  # Lock new versions
```

---

## Python Dependency Locking (Backend)

### Current State

The project uses:
- **pyproject.toml** - Defines dependencies with ranges
- **uv** - Modern Python package manager (replaces pip)

### Problem

Without a lock file:
```toml
dependencies = [
    "fastapi>=0.104.0",  # Could install 0.104.0 or 0.115.0
]
```

### Solution: uv.lock File

UV automatically creates and uses `uv.lock` file for exact versions.

#### Generate Lock File

```bash
# Generate uv.lock
uv lock

# Or use the locking script
./scripts/lock-dependencies.sh
```

#### What Gets Locked

The `uv.lock` file contains:
- Exact version of every package
- Checksums for integrity verification
- Dependency tree resolution
- Platform-specific details

#### Install from Lock File

```bash
# Install exact versions from uv.lock
uv sync

# Or specific extras
uv sync --extra dev
```

### Benefits of uv over pip

| Feature | pip + requirements.txt | uv + uv.lock |
|---------|------------------------|--------------|
| Lock file | ❌ (or manual pip freeze) | ✅ Automatic |
| Fast installs | Slow | ⚡ Very fast |
| Dependency resolution | Basic | Advanced |
| Reproducible | ❌ (without freeze) | ✅ Always |

### Updating Python Dependencies

```bash
# Update specific package
uv add fastapi@0.115.0

# Update all packages
uv lock --upgrade

# Update and sync
uv lock --upgrade && uv sync
```

---

## Lock File Best Practices

### ✅ DO

1. **Commit all lock files to git**
   ```bash
   git add package-lock.json uv.lock
   ```

2. **Use lock files in CI/CD**
   ```yaml
   # .github/workflows/ci.yml
   - name: Install Python deps
     run: uv sync
   
   - name: Install npm deps
     run: npm ci  # Uses package-lock.json, faster than install
   ```

3. **Regenerate locks when changing dependencies**
   ```bash
   # After editing package.json or pyproject.toml
   ./scripts/lock-dependencies.sh
   ```

4. **Review lock file changes in PRs**
   - Look for unexpected version changes
   - Check if major versions changed

### ❌ DON'T

1. **Don't use `npm install` in CI** - use `npm ci` instead
   - `npm ci` uses lock file strictly
   - `npm install` can modify lock file

2. **Don't delete lock files** - they're not "bloat"
   - They ensure reproducibility
   - They're required for CI/CD

3. **Don't use `pip install` directly** - use `uv sync`
   - pip doesn't use uv.lock
   - uv is faster and more reliable

4. **Don't commit node_modules or .venv** - only lock files
   - Lock files are small (~100KB)
   - node_modules can be hundreds of MB

---

## CI/CD Configuration

### GitHub Actions Example

```yaml
name: CI

on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # Install uv
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
      # Install from lock file
      - name: Install Python dependencies
        run: uv sync
      
      # Run tests
      - name: Run tests
        run: uv run pytest

  frontend:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        portal: [customer, adjustor, admin, executive]
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      # Install from lock file (faster, stricter)
      - name: Install dependencies
        working-directory: src/ui/${{ matrix.portal }}
        run: npm ci
      
      # Build
      - name: Build
        working-directory: src/ui/${{ matrix.portal }}
        run: npm run build
```

---

## Troubleshooting

### "npm ci can only install packages when your package.json and package-lock.json are in sync"

**Cause:** package.json was modified but package-lock.json wasn't regenerated.

**Fix:**
```bash
rm package-lock.json
npm install
git add package.json package-lock.json
```

### "uv.lock is out of date"

**Cause:** pyproject.toml was modified but uv.lock wasn't regenerated.

**Fix:**
```bash
uv lock
git add pyproject.toml uv.lock
```

### Lock file merge conflicts

**Fix:**
```bash
# For npm
npm install  # Regenerate lock file
git add package-lock.json

# For Python
uv lock  # Regenerate lock file
git add uv.lock
```

---

## Dependency Audit & Security

### NPM Security Audit

```bash
# Check for vulnerabilities
npm audit

# Auto-fix (updates to latest safe version)
npm audit fix

# After fixing, re-lock
./scripts/lock-dependencies.sh
```

### Python Security Audit

```bash
# Check for vulnerabilities
uv pip list --outdated

# Or use pip-audit
pip install pip-audit
pip-audit
```

---

## Version Pinning Strategy

### Critical Dependencies (Pin Exactly)

These should use exact versions with no ranges:

```json
{
  "vite": "5.4.21",
  "@vitejs/plugin-react": "5.2.0",
  "tailwindcss": "3.4.19"
}
```

### Stable Dependencies (Allow Patch Updates)

For well-tested, stable packages:

```json
{
  "react": "19.2.5",      // Exact
  "axios": "^1.16.0"      // Allow 1.16.x patches (or use exact)
}
```

### Development Dependencies (More Flexible)

Dev tools can be more flexible:

```json
{
  "eslint": "^10.2.1",
  "prettier": "^3.0.0"
}
```

**Recommendation:** Use exact versions for everything to avoid surprises.

---

## Complete Locking Workflow

```bash
# 1. Lock all dependencies
./scripts/lock-dependencies.sh

# 2. Test installations work
./scripts/install-ui-dependencies.sh --clean
./scripts/start-api-server.sh --clean

# 3. Run tests
npm test --prefix src/ui/customer
uv run pytest

# 4. Commit lock files
git add package.json package-lock.json pyproject.toml uv.lock
git commit -m "Lock dependencies to exact versions"

# 5. Push and verify CI passes
git push
```

---

## Migration from Current State

If you're migrating from flexible versions to locked versions:

```bash
# 1. Ensure everything works first
./scripts/install-ui-dependencies.sh --clean
./scripts/start-api-server.sh --clean
# Test everything!

# 2. Lock dependencies
./scripts/lock-dependencies.sh

# 3. Test again with locked versions
rm -rf src/ui/*/node_modules
./scripts/install-ui-dependencies.sh --clean

# 4. If everything works, commit
git add -A
git commit -m "Lock all dependencies to exact versions for reproducible builds"
```

---

## Summary

| Tool | Lock File | Command to Install | Command to Lock |
|------|-----------|-------------------|-----------------|
| **npm** | package-lock.json | `npm ci` | `./scripts/lock-dependencies.sh` |
| **uv** | uv.lock | `uv sync` | `uv lock` |

**Key Takeaway:** Always commit lock files and use them in CI/CD for reproducible builds!

---

**Last Updated:** 2026-05-08
