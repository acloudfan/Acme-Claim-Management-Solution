#!/usr/bin/env python3
"""
Test script for Executive Portal API endpoints
"""

import requests
import json
from datetime import date

BASE_URL = "http://localhost:8000/api/v1"

def test_get_kpis():
    """Test GET /executive/kpis"""
    print("\n" + "="*60)
    print("TEST: GET /executive/kpis")
    print("="*60)

    response = requests.get(f"{BASE_URL}/executive/kpis", params={
        "time_period": "last_quarter",
        "compare_to_previous": True
    })

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("\nKPIs:")
        for kpi_name, kpi_data in data["kpis"].items():
            print(f"  {kpi_name}:")
            print(f"    Current: {kpi_data['current_value']} {kpi_data['unit']}")
            print(f"    Trend: {kpi_data['trend']} ({kpi_data['change_percent']:+.1f}%)")
            print(f"    Status: {kpi_data['status']}")

        print("\nSummary:")
        summary = data["summary"]
        print(f"  Total Claims: {summary['total_claims']}")
        print(f"  AI-Enabled: {summary['ai_enabled_claims']} ({summary['ai_adoption_rate']}%)")
        print(f"  Total Savings: ${summary['total_savings']:.2f}")
        print(f"  Accuracy: {summary['accuracy_within_tolerance']}%")
    else:
        print(f"Error: {response.text}")


def test_get_trends():
    """Test GET /executive/trends/{kpi_name}"""
    print("\n" + "="*60)
    print("TEST: GET /executive/trends/cycle_time")
    print("="*60)

    response = requests.get(
        f"{BASE_URL}/executive/trends/cycle_time",
        params={
            "granularity": "monthly",
            "start_date": "2026-01-01",
            "end_date": "2026-03-31"
        }
    )

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"\nKPI: {data['kpi_name']}")
        print(f"Granularity: {data['granularity']}")
        print(f"\nData Points:")
        for point in data["data_points"]:
            print(f"  {point['period_label']}: {point['value']} days")
            print(f"    Claims: {point['claim_count']} (AI: {point['ai_enabled_count']}, Trad: {point['traditional_count']})")
    else:
        print(f"Error: {response.text}")


def test_execute_query():
    """Test POST /executive/query"""
    print("\n" + "="*60)
    print("TEST: POST /executive/query (processing_path)")
    print("="*60)

    response = requests.post(
        f"{BASE_URL}/executive/query",
        json={
            "query_type": "preset",
            "preset_id": "processing_path",
            "time_range": {
                "start_date": "2026-01-01",
                "end_date": "2026-03-31"
            }
        }
    )

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"\nQuery: {data['query_text']}")
        print(f"Result Type: {data['result_type']}")
        print(f"\nData:")
        for item in data["data"]:
            print(f"  {item['category']}: {item['count']} claims ({item['percent']}%)")
    else:
        print(f"Error: {response.text}")


def test_drilldown():
    """Test GET /executive/drilldown/{claim_id}"""
    print("\n" + "="*60)
    print("TEST: GET /executive/drilldown/1000")
    print("="*60)

    response = requests.get(f"{BASE_URL}/executive/drilldown/1000")

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"\nClaim ID: {data['claim_id']}")
        print(f"Customer: {data['customer_name']}")
        print(f"Vehicle: {data['vehicle']}")
        print(f"Cycle Time: {data['cycle_time_days']} days")
        print(f"Processing: {data['processing_path']}")
        print(f"\nCosts:")
        print(f"  Estimated: ${data['cost_estimated']:.2f}")
        print(f"  Actual: ${data['cost_actual']:.2f}")
        print(f"  Accuracy: {data['cost_accuracy_percent']:.1f}%")
        print(f"  Within Tolerance: {data['within_tolerance']}")
    else:
        print(f"Error: {response.text}")


def main():
    """Run all tests"""
    print("="*60)
    print("EXECUTIVE PORTAL API TESTS")
    print("="*60)
    print("\nMake sure the API server is running on http://localhost:8000")
    print("If not, start it with: python -m src.api.main")

    try:
        # Test health endpoint first
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health")
        if response.status_code != 200:
            print("\n❌ API server not running!")
            return

        print("\n✓ API server is running")

        # Run tests
        test_get_kpis()
        test_get_trends()
        test_execute_query()
        test_drilldown()

        print("\n" + "="*60)
        print("✓ All tests completed!")
        print("="*60)

    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to API server!")
        print("Start the server with: python -m src.api.main")


if __name__ == "__main__":
    main()
