#!/bin/bash
#
# Dependency Locking Script
# Locks all npm and Python dependencies to exact versions for reproducible builds
#

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Dependency Locking Tool${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# ============================================================================
# NPM Dependencies
# ============================================================================

echo -e "${BLUE}Locking NPM Dependencies...${NC}"
echo ""

PORTALS=("customer" "adjustor" "admin" "executive")

for portal in "${PORTALS[@]}"; do
    PORTAL_DIR="$PROJECT_ROOT/src/ui/$portal"

    if [ ! -d "$PORTAL_DIR" ]; then
        echo -e "${YELLOW}⚠${NC} Skipping $portal (directory not found)"
        continue
    fi

    cd "$PORTAL_DIR"

    echo -e "${BLUE}Processing $portal portal...${NC}"

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}  Installing dependencies first...${NC}"
        npm install
    fi

    # Convert package.json to exact versions
    echo -e "${YELLOW}  Converting to exact versions...${NC}"

    # Use jq to remove ^ and ~ from versions, or use sed as fallback
    if command -v jq &> /dev/null; then
        # Using jq (more reliable)
        jq '(.dependencies, .devDependencies) |= with_entries(.value |= sub("^[~^]"; ""))' package.json > package.json.tmp
        mv package.json.tmp package.json
    else
        # Using sed (fallback)
        sed -i.bak 's/"\^/"/g' package.json
        sed -i.bak 's/"~/"/g' package.json
        rm -f package.json.bak
    fi

    # Regenerate package-lock.json with exact versions
    echo -e "${YELLOW}  Regenerating package-lock.json...${NC}"
    rm -f package-lock.json
    npm install --package-lock-only

    echo -e "${GREEN}✓${NC} $portal portal locked"
    echo ""
done

cd "$PROJECT_ROOT"

# ============================================================================
# Python Dependencies
# ============================================================================

echo -e "${BLUE}Locking Python Dependencies...${NC}"
echo ""

if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}ERROR: pyproject.toml not found${NC}"
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${RED}ERROR: uv is not installed${NC}"
    echo "Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Generate uv.lock with exact versions
echo -e "${YELLOW}Generating uv.lock file...${NC}"
uv lock

echo -e "${GREEN}✓${NC} Python dependencies locked"
echo ""

# ============================================================================
# Summary
# ============================================================================

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Lock Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}NPM:${NC}"
echo -e "  ✓ All package.json files now use exact versions (no ^ or ~)"
echo -e "  ✓ package-lock.json files regenerated"
echo ""
echo -e "${GREEN}Python:${NC}"
echo -e "  ✓ uv.lock file generated/updated"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "  1. Review changes: ${BLUE}git diff${NC}"
echo -e "  2. Test installations: ${BLUE}./scripts/install-ui-dependencies.sh --clean${NC}"
echo -e "  3. Commit lock files: ${BLUE}git add package*.json uv.lock && git commit -m 'Lock dependencies'${NC}"
echo ""
echo -e "${YELLOW}Note:${NC} Lock files ensure everyone gets identical dependency versions."
echo ""
