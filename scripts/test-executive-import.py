#!/usr/bin/env python3
"""
Test if executive router can be imported successfully
Run this to diagnose why executive routes aren't registering

Usage: uv run python scripts/test-executive-import.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("Testing executive router import...")
print("=" * 60)

try:
    print("\n1. Importing executive router module...")
    from src.api.routers import executive
    print("   ✓ Import successful")

    print("\n2. Checking router object...")
    print(f"   Router prefix: {executive.router.prefix}")
    print(f"   Router tags: {executive.router.tags}")

    print("\n3. Checking registered routes...")
    routes = executive.router.routes
    print(f"   Found {len(routes)} routes:")
    for route in routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            print(f"     - {list(route.methods)[0]:6} {route.path}")

    print("\n4. Checking warehouse database...")
    if executive.WAREHOUSE_DB.exists():
        print(f"   ✓ Warehouse DB found: {executive.WAREHOUSE_DB}")

        # Test connection
        try:
            conn = executive.get_warehouse_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM claims_warehouse")
            count = cursor.fetchone()[0]
            print(f"   ✓ Database contains {count} claims")
            conn.close()
        except Exception as e:
            print(f"   ✗ Database error: {e}")
    else:
        print(f"   ✗ Warehouse DB not found: {executive.WAREHOUSE_DB}")
        print(f"      Looking in: {executive.WAREHOUSE_DB.absolute()}")

    print("\n" + "=" * 60)
    print("✓ Executive router is properly configured")
    print("\nExpected API endpoints:")
    print("  GET  /api/v1/executive/kpis")
    print("  GET  /api/v1/executive/trends/{kpi_name}")
    print("  POST /api/v1/executive/query")
    print("  GET  /api/v1/executive/drilldown/{claim_id}")
    print("  GET  /api/v1/executive/export/{format}")

except ImportError as e:
    print(f"\n✗ Import error: {e}")
    print("\nThis likely means:")
    print("  - Missing Python dependencies")
    print("  - Schema definitions missing")
    print("  - Database connection issues")
    sys.exit(1)

except Exception as e:
    print(f"\n✗ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
