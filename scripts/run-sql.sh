#!/bin/bash
# ==============================================================================
# SQL Query Utility Script
# ==============================================================================
# Executes SQL queries against the insurance database and displays results
# in a formatted table.
#
# Usage:
#   ./scripts/run-sql.sh "SELECT * FROM claims WHERE claim_id = 2004"
#   ./scripts/run-sql.sh "SELECT COUNT(*) FROM fraud_signals"
#
# The script automatically detects the database type from api-config.yaml
# and uses the appropriate client (sqlite3 or dbisql for SQLAnywhere)
# ==============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/api-config.yaml"

# Check if SQL query provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: No SQL query provided${NC}"
    echo ""
    echo "Usage: $0 \"SQL_QUERY\""
    echo ""
    echo "Examples:"
    echo "  $0 \"SELECT * FROM claims WHERE claim_id = 2004\""
    echo "  $0 \"SELECT signal_type, severity FROM fraud_signals WHERE claim_id = 2004\""
    echo "  $0 \"SELECT COUNT(*) as total FROM agent_usage_logs\""
    exit 1
fi

SQL_QUERY="$1"

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}Error: Configuration file not found: $CONFIG_FILE${NC}"
    exit 1
fi

# Extract database URL from YAML config
DB_URL=$(grep "url:" "$CONFIG_FILE" | grep -v "base_url" | head -1 | sed 's/.*url: *"\([^"]*\)".*/\1/')

if [ -z "$DB_URL" ]; then
    echo -e "${RED}Error: Could not extract database URL from $CONFIG_FILE${NC}"
    exit 1
fi

echo -e "${BLUE}Database:${NC} $DB_URL"
echo -e "${BLUE}Query:${NC} $SQL_QUERY"
echo ""

# Detect database type and execute query
if [[ "$DB_URL" == sqlite://* ]]; then
    # SQLite database
    DB_FILE=$(echo "$DB_URL" | sed 's|sqlite:///\./||' | sed 's|sqlite:///||')
    DB_PATH="$PROJECT_ROOT/$DB_FILE"

    if [ ! -f "$DB_PATH" ]; then
        echo -e "${RED}Error: Database file not found: $DB_PATH${NC}"
        exit 1
    fi

    echo -e "${GREEN}Executing query against SQLite database...${NC}"
    echo ""

    # Execute query with nice formatting
    sqlite3 -header -column "$DB_PATH" "$SQL_QUERY"

    echo ""
    echo -e "${GREEN}✓ Query completed successfully${NC}"

elif [[ "$DB_URL" == sqlanywhere://* ]]; then
    # SQLAnywhere database
    echo -e "${YELLOW}SQLAnywhere database detected${NC}"

    # Check if dbisql is available
    if ! command -v dbisql &> /dev/null; then
        echo -e "${RED}Error: dbisql command not found${NC}"
        echo "Please install SQLAnywhere client tools"
        exit 1
    fi

    # Parse connection string
    # Format: sqlanywhere://user:password@host:port/database
    USER_PASS=$(echo "$DB_URL" | sed 's|sqlanywhere://\([^@]*\)@.*|\1|')
    HOST_PORT_DB=$(echo "$DB_URL" | sed 's|sqlanywhere://[^@]*@\(.*\)|\1|')

    USER=$(echo "$USER_PASS" | cut -d: -f1)
    PASS=$(echo "$USER_PASS" | cut -d: -f2)
    HOST=$(echo "$HOST_PORT_DB" | cut -d: -f1 | cut -d/ -f1)
    PORT=$(echo "$HOST_PORT_DB" | cut -d: -f2 | cut -d/ -f1)
    DATABASE=$(echo "$HOST_PORT_DB" | cut -d/ -f2)

    echo -e "${GREEN}Executing query against SQLAnywhere database...${NC}"
    echo ""

    # Execute query using dbisql
    dbisql -c "UID=$USER;PWD=$PASS;HOST=$HOST:$PORT;DBN=$DATABASE" "$SQL_QUERY"

    echo ""
    echo -e "${GREEN}✓ Query completed successfully${NC}"

else
    echo -e "${RED}Error: Unsupported database type: $DB_URL${NC}"
    echo "Supported types: sqlite://, sqlanywhere://"
    exit 1
fi
