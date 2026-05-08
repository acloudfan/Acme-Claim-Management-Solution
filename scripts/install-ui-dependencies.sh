#!/bin/bash
#
# UI Dependencies Installation Script
# Installs npm dependencies for all UI portals
# Cross-platform: Works on Linux, macOS, and WSL
#
# IMPORTANT: This script MUST remain platform-independent
# - Do NOT use GNU-specific flags (grep -P, sed -r, etc.)
# - Use portable POSIX commands that work on both Linux and macOS
# - Test on both Linux and macOS before committing changes
# - See CROSS-PLATFORM-FIXES.md for guidelines
# 



set -e  # Exit on error
set -o pipefail  # Exit on pipe failures

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  UI Dependencies Installer${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}ERROR: npm is not installed${NC}"
    echo -e "${YELLOW}Please install Node.js and npm first:${NC}"
    echo "  https://nodejs.org/"
    exit 1
fi

echo -e "${GREEN}✓${NC} npm found: $(npm --version)"
echo -e "${GREEN}✓${NC} node found: $(node --version)"
echo ""

# Array of portals to install
PORTALS=(
    "customer:src/ui/customer"
    "adjustor:src/ui/adjustor"
    "admin:src/ui/admin"
    "executive:src/ui/executive"
)

FAILED_PORTALS=()
SUCCESS_COUNT=0

# Install dependencies for each portal
for portal_info in "${PORTALS[@]}"; do
    IFS=':' read -r portal_name portal_path <<< "$portal_info"
    PORTAL_DIR="$PROJECT_ROOT/$portal_path"

    echo -e "${BLUE}Installing ${portal_name} portal dependencies...${NC}"

    if [ ! -d "$PORTAL_DIR" ]; then
        echo -e "${RED}ERROR: Portal directory not found: $PORTAL_DIR${NC}"
        FAILED_PORTALS+=("$portal_name (directory not found)")
        continue
    fi

    # Change to portal directory
    if ! cd "$PORTAL_DIR"; then
        echo -e "${RED}ERROR: Cannot change to directory: $PORTAL_DIR${NC}"
        FAILED_PORTALS+=("$portal_name (cannot access directory)")
        continue
    fi

    # Check if package.json exists
    if [ ! -f "package.json" ]; then
        echo -e "${RED}ERROR: package.json not found in $PORTAL_DIR${NC}"
        FAILED_PORTALS+=("$portal_name (no package.json)")
        cd "$PROJECT_ROOT"
        continue
    fi

    # Fix version compatibility issues in package.json
    echo -e "${YELLOW}  Checking for version compatibility issues...${NC}"

    # Check for Vite version (portable approach, works on Linux and macOS)
    # Extract version from either "vite": "^X.Y.Z" or "dev": "vite" patterns
    VITE_LINE=$(grep '"vite":' package.json | grep -v '"dev"')

    if [ ! -z "$VITE_LINE" ]; then
        # Extract version: "vite": "^5.4.21" -> 5.4.21 -> 5.4
        VITE_VERSION=$(echo "$VITE_LINE" | awk -F'"' '{for(i=1;i<=NF;i++) if($i ~ /^[\^~]?[0-9]/) print $i}' | sed 's/[^0-9.]//g' | cut -d. -f1-2)
        VITE_MAJOR=$(echo "$VITE_VERSION" | cut -d. -f1)
    else
        VITE_VERSION=""
        VITE_MAJOR=""
    fi

    # Ensure VITE_MAJOR is a valid number (default to 5 if empty)
    if [ -z "$VITE_MAJOR" ] || ! [[ "$VITE_MAJOR" =~ ^[0-9]+$ ]]; then
        echo -e "${YELLOW}  → Could not detect Vite version, assuming 5.x${NC}"
        VITE_MAJOR=5
    fi

    if [ ! -z "$VITE_VERSION" ]; then

        # Fix incompatible @vitejs/plugin-react version
        if [ "$VITE_MAJOR" -lt 8 ]; then
            # Vite < 8.x requires @vitejs/plugin-react < 6.x
            if grep -q '"@vitejs/plugin-react": "\^[6-9]' package.json; then
                echo -e "${YELLOW}  → Fixing @vitejs/plugin-react version (incompatible with Vite $VITE_VERSION)${NC}"
                sed -i.bak 's/"@vitejs\/plugin-react": "\^[6-9][^"]*"/"@vitejs\/plugin-react": "^5.2.0"/g' package.json && rm -f package.json.bak
            fi
        fi

        # Fix incompatible Tailwind CSS v4 with Vite 5.x
        if [ "$VITE_MAJOR" -eq 5 ]; then
            if grep -q '"tailwindcss": "\^[4-9]' package.json; then
                echo -e "${YELLOW}  → Fixing Tailwind CSS version (v4+ incompatible with Vite 5.x)${NC}"
                sed -i.bak 's/"tailwindcss": "\^[4-9][^"]*"/"tailwindcss": "^3.4.19"/g' package.json && rm -f package.json.bak
            fi

            # Remove @tailwindcss/postcss if present (only needed for Tailwind v4)
            if grep -q '"@tailwindcss/postcss"' package.json; then
                echo -e "${YELLOW}  → Removing @tailwindcss/postcss (not needed with Tailwind v3)${NC}"
                sed -i.bak '/"@tailwindcss\/postcss":/d' package.json && rm -f package.json.bak
            fi

            # Fix postcss.config.js if it uses Tailwind v4 syntax
            if [ -f "postcss.config.js" ] && grep -q "@tailwindcss/postcss" postcss.config.js; then
                echo -e "${YELLOW}  → Fixing postcss.config.js (updating to Tailwind v3 syntax)${NC}"
                sed -i.bak "s/'@tailwindcss\/postcss'/'tailwindcss'/g" postcss.config.js && rm -f postcss.config.js.bak
                sed -i.bak 's/"@tailwindcss\/postcss"/"tailwindcss"/g' postcss.config.js && rm -f postcss.config.js.bak
            fi

            # Fix tailwind.config.js if it's using Tailwind v4 empty config
            if [ -f "tailwind.config.js" ] && grep -q "Tailwind CSS v4" tailwind.config.js; then
                echo -e "${YELLOW}  → Fixing tailwind.config.js (updating to Tailwind v3 config)${NC}"
                cat > tailwind.config.js << 'TAILWIND_EOF'
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
TAILWIND_EOF
            fi

            # Fix CSS files that use Tailwind v4 syntax
            for css_file in src/index.css src/main.css index.css; do
                if [ -f "$css_file" ] && grep -q '@import "tailwindcss"' "$css_file"; then
                    echo -e "${YELLOW}  → Fixing $css_file (converting v4 CSS syntax to v3)${NC}"

                    # Create a backup
                    cp "$css_file" "${css_file}.v4.bak"

                    # Remove v4 import and @theme block, add v3 directives
                    sed -i.bak '/^@import "tailwindcss";$/d' "$css_file" && rm -f "${css_file}.bak"

                    # Remove @theme block (everything between @theme { and the closing })
                    sed -i.bak '/@theme {/,/^}/d' "$css_file" && rm -f "${css_file}.bak"

                    # Add v3 directives at the top
                    tmpfile=$(mktemp)
                    {
                        echo "@tailwind base;"
                        echo "@tailwind components;"
                        echo "@tailwind utilities;"
                        echo ""
                        cat "$css_file"
                    } > "$tmpfile"
                    mv "$tmpfile" "$css_file"

                    echo -e "${YELLOW}     (v4 backup saved as ${css_file}.v4.bak)${NC}"
                fi
            done
        fi

        # Fix Vite version if it's 6.x, 7.x, or 8.x (unstable packaging)
        if [ "$VITE_MAJOR" -gt 5 ]; then
            echo -e "${YELLOW}  → Downgrading Vite from $VITE_VERSION to 5.4.21 (stable version)${NC}"
            sed -i.bak 's/"vite": "\^[6-9][^"]*"/"vite": "^5.4.21"/g' package.json && rm -f package.json.bak
        fi
    fi

    # Remove existing node_modules if --clean flag is provided
    if [ "$1" = "--clean" ]; then
        if [ -d "node_modules" ]; then
            echo -e "${YELLOW}  Removing existing node_modules...${NC}"
            rm -rf node_modules
        fi
        if [ -f "package-lock.json" ]; then
            echo -e "${YELLOW}  Removing package-lock.json...${NC}"
            rm -f package-lock.json
        fi
    fi

    # Install dependencies
    if npm install; then
        # Verify critical dependency (vite) was installed correctly
        if [ ! -d "node_modules/vite/dist" ]; then
            echo -e "${RED}✗${NC} ${portal_name} portal installation incomplete (vite dist missing)"
            echo -e "${YELLOW}  Retrying with clean install...${NC}"
            rm -rf node_modules package-lock.json
            if npm install; then
                if [ -d "node_modules/vite/dist" ]; then
                    echo -e "${GREEN}✓${NC} ${portal_name} portal dependencies installed (after retry)"
                    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
                else
                    echo -e "${RED}✗${NC} ${portal_name} portal still incomplete after retry"
                    FAILED_PORTALS+=("$portal_name (vite corrupted)")
                fi
            else
                echo -e "${RED}✗${NC} Failed to install ${portal_name} portal dependencies (retry failed)"
                FAILED_PORTALS+=("$portal_name")
            fi
        else
            echo -e "${GREEN}✓${NC} ${portal_name} portal dependencies installed"
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        fi
    else
        echo -e "${RED}✗${NC} Failed to install ${portal_name} portal dependencies"
        FAILED_PORTALS+=("$portal_name")
    fi

    # Return to project root for next iteration
    cd "$PROJECT_ROOT"

    echo ""
done

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Installation Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Successful:${NC} $SUCCESS_COUNT/${#PORTALS[@]} portals"

if [ ${#FAILED_PORTALS[@]} -gt 0 ]; then
    echo -e "${RED}Failed:${NC}"
    for failed in "${FAILED_PORTALS[@]}"; do
        echo -e "  ${RED}✗${NC} $failed"
    done
    echo ""
    echo -e "${YELLOW}TIP: Try running with --clean flag to remove existing node_modules:${NC}"
    echo -e "  ./scripts/install-ui-dependencies.sh --clean"
    exit 1
else
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  All dependencies installed!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "Next steps:"
    echo -e "  1. Start API server:    ${BLUE}./scripts/start-api-server.sh${NC}"
    echo -e "  2. Start UI portals:    ${BLUE}./scripts/start-portals.sh${NC}"
    echo ""
fi
