# Portal Setup Guide

This guide explains how to properly set up all UI portals (Customer, Adjustor, Admin, Executive) for the ACME Insurance Claims Management System.

---

## Quick Setup (Recommended)

```bash
# 1. Kill any existing portal processes
pkill -f vite

# 2. Install all portal dependencies with automatic fixes
./scripts/install-ui-dependencies.sh --clean

# 3. Start all portals
./scripts/start-portals.sh
```

That's it! The install script automatically detects and fixes version compatibility issues.

---

## What the Install Script Fixes Automatically

The `install-ui-dependencies.sh` script detects and fixes these common issues:

### 1. **Vite Version Issues**
- **Problem**: Vite 6.x, 7.x, 8.x have npm packaging bugs
- **Fix**: Downgrades to Vite 5.4.21 (stable)

### 2. **React Plugin Compatibility**
- **Problem**: @vitejs/plugin-react@6.x requires Vite 8.x
- **Fix**: Downgrades to @vitejs/plugin-react@5.2.0

### 3. **Tailwind CSS v4 → v3 Conversion**
- **Problem**: Tailwind v4 is incompatible with Vite 5.x
- **Fix**: Complete conversion to Tailwind v3:
  - Downgrades `tailwindcss` package from 4.x → 3.4.19
  - Removes `@tailwindcss/postcss` package
  - Updates `postcss.config.js` to use `tailwindcss` plugin
  - Updates `tailwind.config.js` to proper v3 structure
  - Converts CSS files from v4 syntax (`@import "tailwindcss"`, `@theme`) to v3 syntax (`@tailwind` directives)

---

## Port Assignments

Each portal runs on a specific port:

| Portal | Port | URL |
|--------|------|-----|
| Customer Portal | 5173 | http://localhost:5173 |
| Adjustor Portal | 5174 | http://localhost:5174 |
| Admin Portal | 5170 | http://localhost:5170 |
| Executive Portal | 5176 | http://localhost:5176 |

These ports are configured in each portal's `vite.config.js` file.

---

## Troubleshooting

### Issue: Wrong portal shows up on a port

**Cause**: Multiple vite processes are running and one grabbed the wrong port.

**Solution**:
```bash
# Kill all vite processes
pkill -f vite

# Start fresh
./scripts/start-portals.sh
```

### Issue: Portal shows blank screen

**Causes**:
1. Dependencies not installed correctly
2. Tailwind v4 → v3 conversion incomplete
3. Port conflict with another process

**Solution**:
```bash
# Clean reinstall with automatic fixes
./scripts/install-ui-dependencies.sh --clean

# Then start portals
./scripts/start-portals.sh
```

### Issue: PostCSS errors about @tailwindcss/postcss

**Cause**: Your files still have Tailwind v4 configuration.

**Solution**: The install script automatically fixes this now. Just run:
```bash
./scripts/install-ui-dependencies.sh --clean
```

It will update:
- `package.json` dependencies
- `postcss.config.js` plugin configuration  
- `tailwind.config.js` structure
- `src/index.css` syntax (v4 → v3)

### Issue: CSS error about "use strict" or "Unknown word"

**Cause**: CSS file uses Tailwind v4 `@import "tailwindcss"` syntax which tries to import a JavaScript file.

**Solution**: Already fixed by the install script's CSS conversion. If you see this:
1. Check `src/index.css` - should have `@tailwind` directives, not `@import`
2. Re-run: `./scripts/install-ui-dependencies.sh --clean`

---

## Understanding the Tailwind v3 vs v4 Differences

### Tailwind CSS v4 (Incompatible with Vite 5.x)

**package.json:**
```json
{
  "devDependencies": {
    "@tailwindcss/postcss": "^4.2.4",
    "tailwindcss": "^4.2.4"
  }
}
```

**postcss.config.js:**
```js
export default {
  plugins: {
    '@tailwindcss/postcss': {},
    autoprefixer: {},
  },
}
```

**tailwind.config.js:**
```js
// Empty - uses CSS-based configuration
export default {}
```

**src/index.css:**
```css
@import "tailwindcss";

@theme {
  --color-primary-500: #2563eb;
}
```

### Tailwind CSS v3 (Compatible with Vite 5.x) ✓

**package.json:**
```json
{
  "devDependencies": {
    "tailwindcss": "^3.4.19"
  }
}
```

**postcss.config.js:**
```js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

**tailwind.config.js:**
```js
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**src/index.css:**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

---

## Manual Conversion (if needed)

If you need to manually convert a portal from Tailwind v4 to v3:

### Step 1: Update package.json
```json
{
  "devDependencies": {
    "vite": "^5.4.21",
    "@vitejs/plugin-react": "^5.2.0",
    "tailwindcss": "^3.4.19"
    // Remove: "@tailwindcss/postcss"
  }
}
```

### Step 2: Update postcss.config.js
```js
export default {
  plugins: {
    tailwindcss: {},  // Changed from '@tailwindcss/postcss'
    autoprefixer: {},
  },
}
```

### Step 3: Update tailwind.config.js
```js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

### Step 4: Update src/index.css

**Remove:**
```css
@import "tailwindcss";

@theme {
  /* theme config */
}
```

**Add:**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Step 5: Reinstall
```bash
rm -rf node_modules package-lock.json
npm install
```

---

## Why These Versions?

- **Vite 5.4.21**: Latest stable v5 release. V6+ have packaging issues.
- **@vitejs/plugin-react 5.2.0**: Compatible with both Vite 5.x and React 19.
- **Tailwind CSS 3.4.19**: Stable v3 release. V4 requires Vite 8.x (which is unstable).

These versions are proven to work together reliably across different environments.

---

## CI/CD Integration

For automated deployments, add this to your CI pipeline:

```yaml
- name: Install UI Dependencies
  run: |
    chmod +x scripts/install-ui-dependencies.sh
    ./scripts/install-ui-dependencies.sh --clean

- name: Build Portals
  run: |
    cd src/ui/customer && npm run build
    cd ../adjustor && npm run build
    cd ../admin && npm run build
    cd ../executive && npm run build
```

The install script ensures consistent builds regardless of what's committed to the repo.

---

## Getting Help

If you encounter issues not covered here:

1. Check the logs: `/tmp/{portal-name}-portal.log`
2. Verify ports are free: `lsof -i :5173 -i :5174 -i :5170 -i :5176`
3. Check Node version: `node --version` (need v18+)
4. See `SETUP-TROUBLESHOOTING.md` for detailed error solutions

---

**Last Updated**: 2026-05-08
