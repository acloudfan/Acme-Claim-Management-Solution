"""
Validation script to check API implementation structure and imports.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def validate_imports():
    """Validate that key modules can be imported"""
    errors = []

    try:
        print("Validating imports...")

        # Core modules
        from src.api import config, constants, database, exceptions
        print("✓ Core modules imported successfully")

        # Models
        from src.api.models import (
            Customer, Vehicle, Policy, Claim, Damage, ClaimEvent
        )
        print("✓ Database models imported successfully")

        # Services
        from src.api.services import (
            base_service, state_machine, event_logger,
            claim_service, image_service, cost_service, estimate_service
        )
        print("✓ Services imported successfully")

        # Routers
        from src.api.routers import customers, claims, cost
        print("✓ Routers imported successfully")

        # AI
        from src.api.ai import damage_detector
        print("✓ AI modules imported successfully")

        # Schemas
        from src.api.schemas import (
            common, customer, claim, damage, claim_event
        )
        print("✓ Schemas imported successfully")

        # Utils
        from src.api.utils import logging_config, rules_loader
        print("✓ Utilities imported successfully")

        print("\n✅ All imports validated successfully!")
        return True

    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        errors.append(str(e))
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        errors.append(str(e))
        return False

def check_file_structure():
    """Check that required files exist"""
    print("\nChecking file structure...")

    required_files = [
        "src/api/main.py",
        "src/api/config.py",
        "src/api/constants.py",
        "src/api/database.py",
        "src/api/exceptions.py",
        "api-config.example.yaml",
        "pyproject.toml"
    ]

    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} NOT FOUND")
            all_exist = False

    return all_exist

def check_directory_structure():
    """Check that required directories exist"""
    print("\nChecking directory structure...")

    required_dirs = [
        "src/api/models",
        "src/api/schemas",
        "src/api/routers",
        "src/api/services",
        "src/api/ai",
        "src/api/utils",
        "src/api/tests"
    ]

    all_exist = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            count = len(list(path.glob("*.py")))
            print(f"✓ {dir_path} ({count} Python files)")
        else:
            print(f"✗ {dir_path} NOT FOUND")
            all_exist = False

    return all_exist

def main():
    """Run all validations"""
    print("=" * 60)
    print("Insurance Claims API - Validation Script")
    print("=" * 60)

    results = []

    # Check structure
    results.append(("Directory Structure", check_directory_structure()))
    results.append(("File Structure", check_file_structure()))

    # Validate imports (skip if structure checks fail)
    if all(r[1] for r in results):
        results.append(("Module Imports", validate_imports()))
    else:
        print("\n⚠️  Skipping import validation due to structural issues")

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:.<50} {status}")

    all_passed = all(r[1] for r in results)

    if all_passed:
        print("\n🎉 All validations passed! API is ready to run.")
        print("\nNext steps:")
        print("1. Ensure uv is installed: curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("2. Run setup: ./setup_uv.sh")
        print("3. Start API: ./start_api.sh")
        print("   OR manually: uv run uvicorn src.api.main:app --reload")
        return 0
    else:
        print("\n⚠️  Some validations failed. Please review errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
