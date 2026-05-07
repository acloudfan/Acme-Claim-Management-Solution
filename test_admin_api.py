#!/usr/bin/env python3
"""
Test script for Admin Portal API endpoints.
Tests all 4 endpoints with various scenarios.
"""
import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1/admin"
HEADERS = {"X-Admin-ID": "test_admin_001"}

def test_get_config():
    """Test GET /admin/config"""
    print("\n" + "="*60)
    print("TEST 1: GET /admin/config")
    print("="*60)

    response = requests.get(f"{BASE_URL}/config", headers=HEADERS)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✓ Configuration loaded successfully")
        print(f"  File Path: {data['file_path']}")
        print(f"  Last Modified: {data['last_modified']}")
        print(f"  Config Keys: {list(data['config'].keys())}")

        # Check if database URL is masked
        if 'database' in data['config'] and 'url' in data['config']['database']:
            db_url = data['config']['database']['url']
            if '****' in db_url:
                print(f"  ✓ Database URL masked: {db_url}")
            else:
                print(f"  ⚠ Database URL not masked: {db_url}")

        return data['config']
    else:
        print(f"✗ Failed: {response.text}")
        return None


def test_save_config(original_config):
    """Test POST /admin/config with valid config"""
    print("\n" + "="*60)
    print("TEST 2: POST /admin/config (valid config)")
    print("="*60)

    # Modify a threshold slightly
    test_config = original_config.copy()
    if 'ai' in test_config and 'confidence' in test_config['ai']:
        old_value = test_config['ai']['confidence']['high_threshold']
        # Change value slightly
        test_config['ai']['confidence']['high_threshold'] = 0.60
        print(f"  Changing high_threshold from {old_value} to 0.60")

    response = requests.post(
        f"{BASE_URL}/config",
        headers=HEADERS,
        json={"config": test_config}
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✓ Configuration saved successfully")
        print(f"  Backup File: {data['backup_file']}")
        print(f"  Config Path: {data['config_path']}")
        print(f"  Restart Required: {data['restart_required']}")
        return data['backup_file']
    else:
        print(f"✗ Failed: {response.text}")
        return None


def test_save_invalid_config():
    """Test POST /admin/config with invalid config"""
    print("\n" + "="*60)
    print("TEST 3: POST /admin/config (invalid config)")
    print("="*60)

    invalid_config = {
        "ai": {
            "confidence": {
                "high_threshold": 1.5,  # Invalid: > 1.0
                "low_threshold": 0.35
            }
        },
        "database": {
            "pool_size": 150  # Invalid: > 100
        }
    }

    response = requests.post(
        f"{BASE_URL}/config",
        headers=HEADERS,
        json={"config": invalid_config}
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 400:
        data = response.json()
        print(f"✓ Validation correctly failed")
        print(f"  Success: {data['success']}")
        print(f"  Message: {data['message']}")
        print(f"  Errors:")
        for field, error in data['errors'].items():
            print(f"    - {field}: {error}")
        return True
    else:
        print(f"✗ Expected 400 status, got {response.status_code}")
        print(f"  Response: {response.text}")
        return False


def test_list_backups():
    """Test GET /admin/config/backups"""
    print("\n" + "="*60)
    print("TEST 4: GET /admin/config/backups")
    print("="*60)

    response = requests.get(f"{BASE_URL}/config/backups", headers=HEADERS)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✓ Backup list retrieved successfully")
        print(f"  Total Count: {data['total_count']}")
        print(f"  Total Size: {data['total_size_bytes']} bytes")

        if data['backups']:
            print(f"  Recent Backups:")
            for backup in data['backups'][:3]:  # Show first 3
                print(f"    - {backup['filename']}")
                print(f"      Timestamp: {backup['timestamp']}")
                print(f"      Size: {backup['size_formatted']}")

        return data['backups'][0]['filename'] if data['backups'] else None
    else:
        print(f"✗ Failed: {response.text}")
        return None


def test_restore_config(backup_filename):
    """Test POST /admin/config/restore"""
    print("\n" + "="*60)
    print("TEST 5: POST /admin/config/restore")
    print("="*60)

    if not backup_filename:
        print("⚠ No backup file available to test restore")
        return False

    print(f"  Restoring from: {backup_filename}")

    response = requests.post(
        f"{BASE_URL}/config/restore",
        headers=HEADERS,
        json={"backup_filename": backup_filename}
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✓ Configuration restored successfully")
        print(f"  Message: {data['message']}")
        print(f"  Backup of Current: {data['backup_of_current']}")
        print(f"  Restart Required: {data['restart_required']}")
        return True
    else:
        print(f"✗ Failed: {response.text}")
        return False


def test_restore_invalid_filename():
    """Test POST /admin/config/restore with invalid filename"""
    print("\n" + "="*60)
    print("TEST 6: POST /admin/config/restore (invalid filename)")
    print("="*60)

    # Test path traversal attempt
    response = requests.post(
        f"{BASE_URL}/config/restore",
        headers=HEADERS,
        json={"backup_filename": "../../../etc/passwd"}
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 422:  # Pydantic validation error
        print(f"✓ Invalid filename correctly rejected (Pydantic validation)")
        return True
    elif response.status_code == 400:
        print(f"✓ Invalid filename correctly rejected")
        print(f"  Response: {response.json()}")
        return True
    else:
        print(f"✗ Expected 400/422 status, got {response.status_code}")
        print(f"  Response: {response.text}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("ADMIN PORTAL API ENDPOINT TESTS")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Admin ID: {HEADERS['X-Admin-ID']}")

    # Check if API is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code != 200:
            print("\n✗ API is not responding at http://localhost:8000")
            print("  Please start the API server first:")
            print("    make dev")
            return
    except requests.exceptions.RequestException:
        print("\n✗ API is not running at http://localhost:8000")
        print("  Please start the API server first:")
        print("    make dev")
        return

    print("✓ API is running")

    # Run tests
    results = []

    # Test 1: Get config
    original_config = test_get_config()
    results.append(("GET /admin/config", original_config is not None))

    if not original_config:
        print("\n✗ Cannot continue tests without original config")
        return

    # Test 2: Save valid config
    backup_file = test_save_config(original_config)
    results.append(("POST /admin/config (valid)", backup_file is not None))

    # Test 3: Save invalid config
    validation_worked = test_save_invalid_config()
    results.append(("POST /admin/config (invalid)", validation_worked))

    # Test 4: List backups
    latest_backup = test_list_backups()
    results.append(("GET /admin/config/backups", latest_backup is not None))

    # Test 5: Restore config
    if latest_backup:
        restore_worked = test_restore_config(latest_backup)
        results.append(("POST /admin/config/restore (valid)", restore_worked))

    # Test 6: Restore with invalid filename
    invalid_restore = test_restore_invalid_filename()
    results.append(("POST /admin/config/restore (invalid)", invalid_restore))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()
