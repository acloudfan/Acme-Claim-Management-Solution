"""
Run database migration to add agent tables and columns.
"""
import sys
import os
import sqlite3
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.api.config import get_settings

def run_migration():
    """Execute the agent tables migration"""
    settings = get_settings()

    # Extract database path from SQLite URL
    # Format: sqlite:///./test_insurance.db
    db_url = settings.DATABASE_URL
    if not db_url.startswith('sqlite:///'):
        print(f"Error: Only SQLite databases supported. Got: {db_url}")
        return False

    db_path = db_url.replace('sqlite:///', '')

    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return False

    print(f"Running migration on database: {db_path}")

    # Read migration SQL
    migration_file = Path(__file__).parent / "add_agent_tables.sql"
    with open(migration_file, 'r') as f:
        migration_sql = f.read()

    # Execute migration
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Split by semicolon and execute each statement
        statements = [s.strip() for s in migration_sql.split(';') if s.strip()]

        for i, statement in enumerate(statements):
            try:
                cursor.execute(statement)
                print(f"✓ Executed statement {i+1}/{len(statements)}")
            except sqlite3.OperationalError as e:
                # Skip if column already exists
                if "duplicate column name" in str(e).lower():
                    print(f"⚠ Skipped statement {i+1}: Column already exists")
                else:
                    raise

        conn.commit()
        conn.close()

        print("\n✓ Migration completed successfully!")
        print("\nNew tables created:")
        print("  - agent_usage_logs")
        print("  - fraud_signals")
        print("  - risk_assessments")
        print("\nNew columns added to damages:")
        print("  - enhanced_severity")
        print("  - ai_generated_probability")
        print("  - fraud_risk_score")
        print("  - risk_score")
        print("  - agent_reasoning")
        print("  - secondary_damages_predicted")
        print("\nNew columns added to claims:")
        print("  - overall_fraud_risk_score")
        print("  - overall_risk_score")
        print("  - agent_flags")

        return True

    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
