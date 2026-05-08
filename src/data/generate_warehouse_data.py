#!/usr/bin/env python3
"""
Generate Synthetic Claims Warehouse Data
Purpose: Create 200 realistic claims across 3 months showing progressive AI adoption
Database: claims-warehouse.db
"""

import sqlite3
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuration
TOTAL_CLAIMS = 200
MONTH_1_CLAIMS = 50   # Jan 2026: 80% traditional, 20% AI
MONTH_2_CLAIMS = 70   # Feb 2026: 50% traditional, 50% AI
MONTH_3_CLAIMS = 80   # Mar 2026: 100% AI

# KPI Targets (based on design spec)
TRADITIONAL_CYCLE_TIME_AVG = 12.0
TRADITIONAL_CYCLE_TIME_STD = 2.0
AI_AUTO_CYCLE_TIME_AVG = 3.5
AI_AUTO_CYCLE_TIME_STD = 0.8
AI_HUMAN_CYCLE_TIME_AVG = 6.5
AI_HUMAN_CYCLE_TIME_STD = 1.2

TRADITIONAL_OPERATIONAL_COST = 450.0
AI_COST_SAVINGS_AUTO = 0.9  # 10% savings on operational cost
AI_COST_SAVINGS_APPEALED = 0.8  # 20% savings on operational cost

AUTO_ADJUDICATION_TARGET = 0.68  # 68% of AI claims auto-approved
FRAUD_DETECTION_ACCURACY = 0.85
FRAUD_RATE = 0.05  # 5% of claims are fraudulent
ACCURACY_TOLERANCE = 0.10  # ±10%

# Sample data for realism
VEHICLE_MAKES = ['Toyota', 'Honda', 'Ford', 'Chevrolet', 'BMW', 'Mercedes', 'Nissan', 'Hyundai']
VEHICLE_MODELS = {
    'Toyota': ['Camry', 'Corolla', 'RAV4', 'Highlander'],
    'Honda': ['Civic', 'Accord', 'CR-V', 'Pilot'],
    'Ford': ['F-150', 'Escape', 'Explorer', 'Mustang'],
    'Chevrolet': ['Silverado', 'Malibu', 'Equinox', 'Traverse'],
    'BMW': ['3 Series', '5 Series', 'X3', 'X5'],
    'Mercedes': ['C-Class', 'E-Class', 'GLC', 'GLE'],
    'Nissan': ['Altima', 'Rogue', 'Sentra', 'Pathfinder'],
    'Hyundai': ['Elantra', 'Sonata', 'Tucson', 'Santa Fe']
}

HUMAN_REVIEW_REASONS = [
    'customer_appeal',
    'low_confidence',
    'high_value',
    'fraud_detected',
    'complex_damage'
]

FRAUD_TYPES = [
    'color_mismatch',
    'make_model_mismatch',
    'ai_generated_image',
    'duplicate_claim',
    'staged_accident'
]


def generate_vehicle():
    """Generate random vehicle details"""
    make = random.choice(VEHICLE_MAKES)
    model = random.choice(VEHICLE_MODELS[make])
    year = random.randint(2010, 2023)
    vin = f"1ABC{random.randint(100000, 999999):06d}XYZ"
    return make, model, year, vin


def generate_claim(claim_id, month, ai_adoption_rate, base_customer_id=100):
    """Generate a single claim record with realistic distributions"""

    # Determine if AI-enabled based on adoption rate
    ai_enabled = random.random() < ai_adoption_rate

    # Determine AI adoption phase
    if month == 1:
        ai_adoption_phase = 'pre_ai'
    elif month == 2:
        ai_adoption_phase = 'partial_ai'
    else:
        ai_adoption_phase = 'full_ai'

    # Processing path and cycle time
    if ai_enabled:
        auto_adjudicated = random.random() < AUTO_ADJUDICATION_TARGET
        processing_path = 'ai_auto_approved' if auto_adjudicated else 'ai_human_reviewed'

        if auto_adjudicated:
            cycle_time = max(1.0, random.gauss(AI_AUTO_CYCLE_TIME_AVG, AI_AUTO_CYCLE_TIME_STD))
            human_review_required = False
            human_review_reason = None
            cost_savings_factor = AI_COST_SAVINGS_AUTO
        else:
            cycle_time = max(2.0, random.gauss(AI_HUMAN_CYCLE_TIME_AVG, AI_HUMAN_CYCLE_TIME_STD))
            human_review_required = True
            human_review_reason = random.choice(HUMAN_REVIEW_REASONS)
            cost_savings_factor = AI_COST_SAVINGS_APPEALED
    else:
        processing_path = 'traditional'
        cycle_time = max(5.0, random.gauss(TRADITIONAL_CYCLE_TIME_AVG, TRADITIONAL_CYCLE_TIME_STD))
        auto_adjudicated = False
        human_review_required = True
        human_review_reason = 'traditional_processing'
        cost_savings_factor = 1.0

    cycle_time = round(cycle_time, 1)
    cycle_time_hours = round(cycle_time * 24, 1)

    # Date calculations
    fnol_date = datetime(2026, month, random.randint(1, 28))
    claim_closed_date = fnol_date + timedelta(days=int(cycle_time))

    # Week and day of week
    week = fnol_date.isocalendar()[1]
    day_of_week = fnol_date.weekday() + 1  # 1=Monday, 7=Sunday

    # Cost estimation
    base_repair_cost = random.uniform(1500, 5000)

    # For AI, estimate should be close to actual (with some variance)
    if ai_enabled:
        # AI estimates are generally more accurate
        variance = random.uniform(-0.08, 0.12)  # -8% to +12% (tighter for AI)
        cost_actual = base_repair_cost
        cost_estimated = cost_actual * (1 + variance)
    else:
        # Traditional has wider variance
        variance = random.uniform(-0.15, 0.20)
        cost_actual = base_repair_cost
        cost_estimated = cost_actual * (1 + variance)

    # Operational cost is what the insurance company pays to process the claim
    # AI reduces this operational cost
    cost_operational = TRADITIONAL_OPERATIONAL_COST * cost_savings_factor

    # Total cost = repair cost + operational cost
    cost_total = cost_actual + cost_operational

    # Amount paid to customer (repair cost only)
    claim_amount = cost_actual

    # Accuracy metrics
    if cost_actual > 0:
        cost_accuracy_percent = abs(cost_estimated - cost_actual) / cost_actual * 100
    else:
        cost_accuracy_percent = 0

    within_tolerance = cost_accuracy_percent <= (ACCURACY_TOLERANCE * 100)

    # Fraud detection (only for AI-enabled)
    if ai_enabled:
        # Simulate fraud detection
        is_actually_fraudulent = random.random() < FRAUD_RATE
        if is_actually_fraudulent:
            # AI detects fraud with FRAUD_DETECTION_ACCURACY accuracy
            fraud_detected = random.random() < FRAUD_DETECTION_ACCURACY
            fraud_risk_score = random.uniform(0.7, 1.0) if fraud_detected else random.uniform(0.3, 0.6)
            fraud_type = random.choice(FRAUD_TYPES) if fraud_detected else None
        else:
            # False positive rate is low
            fraud_detected = random.random() < 0.03  # 3% false positive
            fraud_risk_score = random.uniform(0.1, 0.4)
            fraud_type = random.choice(FRAUD_TYPES) if fraud_detected else None
    else:
        fraud_detected = False
        fraud_risk_score = None
        fraud_type = None

    # Vehicle and customer details
    vehicle_make, vehicle_model, vehicle_year, vehicle_vin = generate_vehicle()
    customer_id = base_customer_id + (claim_id % 50)  # Cycle through ~50 customers
    policy_number = f"PA-{random.randint(100000, 999999):06d}-01"

    # Damage and image counts
    damage_count = random.randint(1, 4)
    image_count = random.randint(damage_count, damage_count * 3)

    # Flags
    is_closed = True
    routed_to_traditional = not ai_enabled or (human_review_required and random.random() < 0.1)

    return {
        'claim_id': claim_id,
        'fnol_date': fnol_date.date().isoformat(),
        'fnol_datetime': fnol_date.isoformat(),
        'claim_closed_date': claim_closed_date.date().isoformat(),
        'claim_closed_datetime': claim_closed_date.isoformat(),
        'month': month,
        'week': week,
        'day_of_week': day_of_week,
        'quarter': 'Q1',
        'year': 2026,
        'customer_id': customer_id,
        'policy_number': policy_number,
        'vehicle_vin': vehicle_vin,
        'vehicle_make': vehicle_make,
        'vehicle_model': vehicle_model,
        'vehicle_year': vehicle_year,
        'processing_path': processing_path,
        'ai_enabled': 1 if ai_enabled else 0,
        'ai_adoption_phase': ai_adoption_phase,
        'cycle_time_days': cycle_time,
        'cycle_time_hours': cycle_time_hours,
        'auto_adjudicated': 1 if auto_adjudicated else 0,
        'human_review_required': 1 if human_review_required else 0,
        'human_review_reason': human_review_reason,
        'cost_estimated': round(cost_estimated, 2),
        'cost_actual': round(cost_actual, 2),
        'cost_operational': round(cost_operational, 2),
        'cost_savings_factor': cost_savings_factor,
        'cost_total': round(cost_total, 2),
        'fraud_detected': 1 if fraud_detected else 0,
        'fraud_risk_score': round(fraud_risk_score, 3) if fraud_risk_score else None,
        'fraud_type': fraud_type,
        'cost_accuracy_percent': round(cost_accuracy_percent, 2),
        'within_tolerance': 1 if within_tolerance else 0,
        'claim_amount': round(claim_amount, 2),
        'damage_count': damage_count,
        'image_count': image_count,
        'is_closed': 1 if is_closed else 0,
        'routed_to_traditional': 1 if routed_to_traditional else 0
    }


def generate_all_claims():
    """Generate all 200 claims with progressive AI adoption"""
    claims = []
    claim_id = 1000  # Start from 1000

    print("Generating claims for 3-month timeline...")

    # Month 1: January 2026 (20% AI adoption)
    print(f"Month 1 (Jan 2026): Generating {MONTH_1_CLAIMS} claims (20% AI)...")
    for _ in range(MONTH_1_CLAIMS):
        claims.append(generate_claim(claim_id, 1, 0.20))
        claim_id += 1

    # Month 2: February 2026 (50% AI adoption)
    print(f"Month 2 (Feb 2026): Generating {MONTH_2_CLAIMS} claims (50% AI)...")
    for _ in range(MONTH_2_CLAIMS):
        claims.append(generate_claim(claim_id, 2, 0.50))
        claim_id += 1

    # Month 3: March 2026 (100% AI adoption)
    print(f"Month 3 (Mar 2026): Generating {MONTH_3_CLAIMS} claims (100% AI)...")
    for _ in range(MONTH_3_CLAIMS):
        claims.append(generate_claim(claim_id, 3, 1.00))
        claim_id += 1

    print(f"Total claims generated: {len(claims)}")
    return claims


def insert_into_warehouse(claims, db_path='claims-warehouse.db'):
    """Insert claims into warehouse database"""
    print(f"\nInserting claims into {db_path}...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Clear existing data
    cursor.execute("DELETE FROM claims_warehouse")

    for claim in claims:
        cursor.execute('''
            INSERT INTO claims_warehouse (
                claim_id, fnol_date, fnol_datetime, claim_closed_date, claim_closed_datetime,
                month, week, day_of_week, quarter, year,
                customer_id, policy_number, vehicle_vin, vehicle_make, vehicle_model, vehicle_year,
                processing_path, ai_enabled, ai_adoption_phase,
                cycle_time_days, cycle_time_hours,
                auto_adjudicated, human_review_required, human_review_reason,
                cost_estimated, cost_actual, cost_operational, cost_savings_factor, cost_total,
                fraud_detected, fraud_risk_score, fraud_type,
                cost_accuracy_percent, within_tolerance,
                claim_amount, damage_count, image_count,
                is_closed, routed_to_traditional
            ) VALUES (
                :claim_id, :fnol_date, :fnol_datetime, :claim_closed_date, :claim_closed_datetime,
                :month, :week, :day_of_week, :quarter, :year,
                :customer_id, :policy_number, :vehicle_vin, :vehicle_make, :vehicle_model, :vehicle_year,
                :processing_path, :ai_enabled, :ai_adoption_phase,
                :cycle_time_days, :cycle_time_hours,
                :auto_adjudicated, :human_review_required, :human_review_reason,
                :cost_estimated, :cost_actual, :cost_operational, :cost_savings_factor, :cost_total,
                :fraud_detected, :fraud_risk_score, :fraud_type,
                :cost_accuracy_percent, :within_tolerance,
                :claim_amount, :damage_count, :image_count,
                :is_closed, :routed_to_traditional
            )
        ''', claim)

    conn.commit()

    # Verify insertion
    cursor.execute("SELECT COUNT(*) FROM claims_warehouse")
    count = cursor.fetchone()[0]
    print(f"✓ Inserted {count} claims into warehouse")

    conn.close()


def validate_data(db_path='claims-warehouse.db'):
    """Validate generated data meets design requirements"""
    print("\n" + "="*60)
    print("DATA VALIDATION")
    print("="*60)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Check total claims
    cursor.execute("SELECT COUNT(*) FROM claims_warehouse")
    total = cursor.fetchone()[0]
    print(f"\n✓ Total claims: {total} (Expected: {TOTAL_CLAIMS})")

    # 2. Check distribution by month
    print("\n--- Claims by Month ---")
    cursor.execute("""
        SELECT month, COUNT(*),
               SUM(CASE WHEN ai_enabled = 1 THEN 1 ELSE 0 END) as ai_count,
               ROUND(SUM(CASE WHEN ai_enabled = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as ai_percent
        FROM claims_warehouse
        GROUP BY month
        ORDER BY month
    """)
    for row in cursor.fetchall():
        month, count, ai_count, ai_percent = row
        print(f"  Month {month}: {count} claims, {ai_count} AI ({ai_percent}%)")

    # 3. Check KPIs
    print("\n--- KPI Validation ---")

    # Cycle Time
    cursor.execute("""
        SELECT
            ROUND(AVG(CASE WHEN ai_enabled = 0 THEN cycle_time_days END), 2) as traditional_avg,
            ROUND(AVG(CASE WHEN ai_enabled = 1 THEN cycle_time_days END), 2) as ai_avg,
            ROUND(AVG(cycle_time_days), 2) as overall_avg
        FROM claims_warehouse
    """)
    trad_cycle, ai_cycle, overall_cycle = cursor.fetchone()
    print(f"  Cycle Time: Traditional={trad_cycle}d, AI={ai_cycle}d, Overall={overall_cycle}d")
    print(f"    Target: Traditional=~12d, AI=~4-5d")

    # Auto-Adjudication Rate
    cursor.execute("""
        SELECT
            ROUND(SUM(CASE WHEN auto_adjudicated = 1 THEN 1 ELSE 0 END) * 100.0 /
                  SUM(CASE WHEN ai_enabled = 1 THEN 1 ELSE 0 END), 2) as auto_adj_rate
        FROM claims_warehouse
        WHERE ai_enabled = 1
    """)
    auto_adj = cursor.fetchone()[0]
    print(f"  Auto-Adjudication Rate: {auto_adj}% (Target: ~68%)")

    # Cost per Claim
    cursor.execute("""
        SELECT
            ROUND(AVG(CASE WHEN ai_enabled = 0 THEN cost_total END), 2) as traditional_cost,
            ROUND(AVG(CASE WHEN ai_enabled = 1 THEN cost_total END), 2) as ai_cost,
            ROUND(AVG(cost_total), 2) as overall_cost
        FROM claims_warehouse
    """)
    trad_cost, ai_cost, overall_cost = cursor.fetchone()
    savings_percent = round((trad_cost - ai_cost) / trad_cost * 100, 1) if trad_cost else 0
    print(f"  Cost per Claim: Traditional=${trad_cost}, AI=${ai_cost}, Overall=${overall_cost}")
    print(f"    Savings: {savings_percent}% (Target: ~15-20%)")

    # Fraud Detection
    cursor.execute("""
        SELECT
            ROUND(SUM(CASE WHEN fraud_detected = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as fraud_rate
        FROM claims_warehouse
        WHERE ai_enabled = 1
    """)
    fraud_rate = cursor.fetchone()[0] or 0
    print(f"  Fraud Detection Rate: {fraud_rate}% (Target: ~5-10%)")

    # Accuracy
    cursor.execute("""
        SELECT
            ROUND(SUM(CASE WHEN within_tolerance = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as accuracy
        FROM claims_warehouse
        WHERE ai_enabled = 1
    """)
    accuracy = cursor.fetchone()[0]
    print(f"  Accuracy (within ±10%): {accuracy}% (Target: ~87-90%)")

    # 4. Monthly KPI Summary View
    print("\n--- Monthly KPI Summary (View) ---")
    cursor.execute("SELECT * FROM monthly_kpi_summary")
    rows = cursor.fetchall()
    if rows:
        print(f"  {'Month':<6} {'Claims':<8} {'AI%':<8} {'Cycle':<8} {'AutoAdj%':<10} {'Cost':<10}")
        print(f"  {'-'*6} {'-'*8} {'-'*8} {'-'*8} {'-'*10} {'-'*10}")
        for row in rows:
            month, year, quarter, total, ai_count, ai_rate, cycle, auto_adj, cost, fraud, accuracy = row
            print(f"  {month:<6} {total:<8} {ai_rate or 0:<8.1f} {cycle or 0:<8.1f} {auto_adj or 0:<10.1f} ${cost or 0:<9.2f}")

    # 5. Processing Path Distribution
    print("\n--- Processing Path Distribution ---")
    cursor.execute("SELECT * FROM processing_path_summary")
    for row in cursor.fetchall():
        path, count, percent, cycle, cost = row
        print(f"  {path}: {count} claims ({percent}%), Cycle={cycle}d, Cost=${cost}")

    conn.close()

    print("\n" + "="*60)
    print("✓ Data validation complete!")
    print("="*60)


def main():
    """Main execution"""
    print("="*60)
    print("CLAIMS WAREHOUSE DATA GENERATION")
    print("="*60)

    # Generate claims
    claims = generate_all_claims()

    # Insert into database
    insert_into_warehouse(claims)

    # Validate data
    validate_data()

    print("\n✓ Warehouse data generation complete!")
    print("  Database: claims-warehouse.db")
    print("  Total claims: 200")
    print("  Ready for Executive Portal API integration")


if __name__ == '__main__':
    main()
