#!/usr/bin/env python3
"""
Seed Claims Warehouse Database with Synthetic Data

Generates 4,500 synthetic claims (750 per month for 6 months)
following the rules defined in simulation/synthetic-data-rules.md

Usage:
    python scripts/seed-claims-warehouse.py
    python scripts/seed-claims-warehouse.py --reset  # Clear and regenerate
"""

import sqlite3
import random
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker

fake = Faker()
random.seed(42)  # For reproducibility

# Constants from synthetic-data-rules.md
MONTHS = [
    {'date': '2025-10', 'month': 10, 'year': 2025, 'threshold': 5500, 'fraud_detection_rate': 0.40, 'auto_approval_rate': 0.70},
    {'date': '2025-11', 'month': 11, 'year': 2025, 'threshold': 6000, 'fraud_detection_rate': 0.50, 'auto_approval_rate': 0.80},
    {'date': '2025-12', 'month': 12, 'year': 2025, 'threshold': 6500, 'fraud_detection_rate': 0.60, 'auto_approval_rate': 0.88},
    {'date': '2026-01', 'month': 1, 'year': 2026, 'threshold': 7000, 'fraud_detection_rate': 0.70, 'auto_approval_rate': 0.94},
    {'date': '2026-02', 'month': 2, 'year': 2026, 'threshold': 7500, 'fraud_detection_rate': 0.80, 'auto_approval_rate': 0.97},
    {'date': '2026-03', 'month': 3, 'year': 2026, 'threshold': 8000, 'fraud_detection_rate': 0.85, 'auto_approval_rate': 0.99},
]

CLAIMS_PER_MONTH = 750
AVERAGE_CLAIM_AMOUNT = 6000
FRAUD_RATE_OF_AUTO_ADJ = 0.15  # 15% of auto-adjudicated claims are fraudulent
INDUSTRY_CYCLE_TIME_AVG = 19.3

# AI Eligibility Constraints
AI_ELIGIBLE_RATE = 0.35  # Only 35% of claims are body damage (AI-eligible)
CUSTOMER_AI_CONSENT_RATE = 0.80  # 80% of eligible customers opt-in to AI

# Operational cost configurations (cost to PROCESS the claim, not claim loss amount)
COST_TRADITIONAL = 325.00  # Traditional/standard processing baseline
COST_AI_AUTO_APPROVED = 32.50  # 90% cheaper (10% of traditional)
COST_AI_HUMAN_REVIEW = 48.75  # 85% cheaper (15% of traditional)

# Cost savings factors (what percentage of traditional cost is spent)
SAVINGS_FACTOR_AUTO = 0.10  # AI auto-approved costs 10% of traditional
SAVINGS_FACTOR_REVIEWED = 0.15  # AI + human review costs 15% of traditional
SAVINGS_FACTOR_TRADITIONAL = 1.0  # Traditional costs 100% (baseline)

ACCURACY_TOLERANCE = 0.10  # ±10%


def get_ai_adoption_phase(month_year):
    """Determine AI adoption phase based on month"""
    if month_year in ['2025-10', '2025-11']:
        return 'early_adoption'
    elif month_year in ['2025-12', '2026-01']:
        return 'mid_adoption'
    else:
        return 'mature_adoption'


def generate_claim(claim_id, month_config):
    """Generate a single synthetic claim"""
    month = month_config['month']
    year = month_config['year']
    threshold = month_config['threshold']
    fraud_detection_rate = month_config['fraud_detection_rate']
    auto_approval_rate = month_config['auto_approval_rate']  # Progressive improvement

    # 1. Generate claim amount (normal distribution, mean=$6000, std=$2000)
    claim_amount = max(500, random.gauss(AVERAGE_CLAIM_AMOUNT, 2000))

    # 2. Determine AI eligibility (only body damage claims are eligible)
    # 35% of claims are body damage, 65% are internal damage
    damage_type = 'body' if random.random() < AI_ELIGIBLE_RATE else 'internal'
    ai_eligible = (damage_type == 'body')

    # 3. Determine customer AI consent (only for eligible claims)
    if ai_eligible:
        customer_ai_consent = random.random() < CUSTOMER_AI_CONSENT_RATE
    else:
        customer_ai_consent = None  # Not applicable for non-eligible claims

    # 4. Determine AI enablement (progressive adoption for eligible + consented claims)
    # Oct 2025: 20% AI, Nov 2025: 30%, Dec 2025: 50%, Jan-Mar 2026: 100%
    ai_adoption_rates = {
        '2025-10': 0.20,
        '2025-11': 0.30,
        '2025-12': 0.50,
        '2026-01': 1.00,
        '2026-02': 1.00,
        '2026-03': 1.00
    }
    ai_adoption_rate = ai_adoption_rates.get(month_config['date'], 1.00)

    # AI is enabled only if: eligible AND customer consented AND monthly adoption rate
    if ai_eligible and customer_ai_consent:
        ai_enabled = random.random() < ai_adoption_rate
    else:
        ai_enabled = False

    # 5. Determine if auto-adjudicated (only for AI-enabled claims)
    if ai_enabled:
        auto_adjudicated = claim_amount < threshold

        if auto_adjudicated:
            # Progressive auto-approval rate: improves from 40% (Oct) to 90% (Mar)
            # This simulates improving AI confidence over time
            if random.random() < auto_approval_rate:
                processing_path = 'ai_auto_approved'
                human_review_required = False
                human_review_reason = None
            else:
                processing_path = 'ai_human_reviewed'
                human_review_required = True
                human_review_reason = random.choice(['customer_appeal', 'low_confidence', 'fraud_detected'])
        else:
            # Above threshold - requires human review
            processing_path = 'ai_human_reviewed'
            human_review_required = True
            human_review_reason = 'high_value'
    else:
        # Traditional processing (no AI)
        processing_path = 'traditional'
        auto_adjudicated = False
        human_review_required = True
        human_review_reason = 'traditional_adjuster'

    # 6. Fraud detection (15% of auto-adjudicated claims are fraudulent)
    is_fraudulent = auto_adjudicated and random.random() < FRAUD_RATE_OF_AUTO_ADJ

    if is_fraudulent:
        fraud_detected = random.random() < fraud_detection_rate
        fraud_risk_score = random.uniform(0.7, 1.0) if fraud_detected else random.uniform(0.3, 0.6)
        fraud_type = random.choice(['color_mismatch', 'make_model_mismatch', 'ai_generated_image']) if fraud_detected else None
    else:
        fraud_detected = False
        fraud_risk_score = random.uniform(0.0, 0.3)
        fraud_type = None

    # 7. Calculate cycle time
    if processing_path == 'ai_auto_approved':
        cycle_time_days = max(1, random.gauss(4, 1))  # 3-5 days
    elif processing_path == 'ai_human_reviewed':
        cycle_time_days = max(5, random.gauss(15, 3))  # 10-20 days
    else:
        cycle_time_days = max(10, random.gauss(INDUSTRY_CYCLE_TIME_AVG, 3))  # 15-25 days

    cycle_time_hours = cycle_time_days * 24

    # 8. Calculate costs
    # cost_estimated and cost_actual = claim loss amount (what we pay to customer for repairs)
    cost_estimated = claim_amount
    cost_actual = claim_amount * random.uniform(0.85, 1.15)  # ±15% variance

    # cost_operational = operational cost to PROCESS the claim (not the claim payout)
    if processing_path == 'ai_auto_approved':
        cost_operational = COST_AI_AUTO_APPROVED + random.uniform(-2, 2)  # $32.50 ± $2
        cost_savings_factor = SAVINGS_FACTOR_AUTO  # 0.10 (90% savings)
    elif processing_path == 'ai_human_reviewed':
        cost_operational = COST_AI_HUMAN_REVIEW + random.uniform(-3, 3)  # $48.75 ± $3
        cost_savings_factor = SAVINGS_FACTOR_REVIEWED  # 0.15 (85% savings)
    else:  # traditional
        cost_operational = COST_TRADITIONAL + random.uniform(-25, 25)  # $325 ± $25
        cost_savings_factor = SAVINGS_FACTOR_TRADITIONAL  # 1.0 (no savings)

    # Ensure positive costs
    cost_operational = max(10, cost_operational)

    # cost_total = total claim cost (payout + operational)
    cost_total = cost_actual + cost_operational

    # 7. Calculate accuracy
    cost_accuracy_percent = abs(cost_estimated - cost_actual) / cost_actual * 100
    within_tolerance = cost_accuracy_percent <= (ACCURACY_TOLERANCE * 100)

    # 8. Generate dates
    day = random.randint(1, 28)  # Avoid month-end edge cases
    fnol_date = datetime(year, month, day)
    fnol_datetime = fnol_date + timedelta(hours=random.randint(8, 18))  # Business hours
    claim_closed_datetime = fnol_datetime + timedelta(days=cycle_time_days)
    claim_closed_date = claim_closed_datetime.date()

    # 9. Generate customer/vehicle details
    customer_id = random.randint(1000, 9999)
    policy_number = f"PA-{random.randint(100000, 999999)}-{random.randint(10, 99)}"
    vehicle_vin = fake.vin()
    vehicle_make = random.choice(['Toyota', 'Honda', 'Ford', 'Chevrolet', 'Nissan', 'BMW', 'Mercedes', 'Tesla'])
    vehicle_model = random.choice(['Corolla', 'Civic', 'F-150', 'Silverado', 'Altima', '3 Series', 'C-Class', 'Model 3'])
    vehicle_year = random.randint(2015, 2025)

    # 10. Calculate derived fields
    week = fnol_date.isocalendar()[1]
    day_of_week = fnol_date.isoweekday()
    quarter = f"Q{(month - 1) // 3 + 1}"
    ai_adoption_phase = get_ai_adoption_phase(month_config['date'])
    is_closed = True
    routed_to_traditional = not ai_enabled
    damage_count = random.randint(1, 5)
    image_count = random.randint(3, 10)

    return {
        'claim_id': claim_id,
        'fnol_date': fnol_date.date(),
        'fnol_datetime': fnol_datetime,
        'claim_closed_date': claim_closed_date,
        'claim_closed_datetime': claim_closed_datetime,
        'month': month,
        'week': week,
        'day_of_week': day_of_week,
        'quarter': quarter,
        'year': year,
        'customer_id': customer_id,
        'policy_number': policy_number,
        'vehicle_vin': vehicle_vin,
        'vehicle_make': vehicle_make,
        'vehicle_model': vehicle_model,
        'vehicle_year': vehicle_year,
        'damage_type': damage_type,
        'ai_eligible': ai_eligible,
        'customer_ai_consent': customer_ai_consent,
        'processing_path': processing_path,
        'ai_enabled': ai_enabled,
        'ai_adoption_phase': ai_adoption_phase,
        'cycle_time_days': round(cycle_time_days, 2),
        'cycle_time_hours': round(cycle_time_hours, 2),
        'auto_adjudicated': auto_adjudicated,
        'human_review_required': human_review_required,
        'human_review_reason': human_review_reason,
        'cost_estimated': round(cost_estimated, 2),
        'cost_actual': round(cost_actual, 2),
        'cost_operational': round(cost_operational, 2),
        'cost_savings_factor': cost_savings_factor,
        'cost_total': round(cost_total, 2),
        'is_fraudulent': is_fraudulent,
        'fraud_detected': fraud_detected,
        'fraud_risk_score': round(fraud_risk_score, 3) if fraud_risk_score else None,
        'fraud_type': fraud_type,
        'cost_accuracy_percent': round(cost_accuracy_percent, 2),
        'within_tolerance': within_tolerance,
        'claim_amount': round(claim_amount, 2),
        'damage_count': damage_count,
        'image_count': image_count,
        'is_closed': is_closed,
        'routed_to_traditional': routed_to_traditional,
    }


def create_warehouse_schema(conn):
    """Create claims_warehouse table if it doesn't exist"""
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claims_warehouse (
            -- Primary Key
            warehouse_id INTEGER PRIMARY KEY AUTOINCREMENT,

            -- Link to Main Database
            claim_id INTEGER NOT NULL,

            -- Time Dimensions
            fnol_date DATE NOT NULL,
            fnol_datetime TIMESTAMP NOT NULL,
            claim_closed_date DATE,
            claim_closed_datetime TIMESTAMP,
            month INTEGER NOT NULL,
            week INTEGER NOT NULL,
            day_of_week INTEGER NOT NULL,
            quarter TEXT NOT NULL,
            year INTEGER NOT NULL,

            -- Customer/Policy Dimensions
            customer_id INTEGER NOT NULL,
            policy_number TEXT NOT NULL,
            vehicle_vin TEXT NOT NULL,
            vehicle_make TEXT,
            vehicle_model TEXT,
            vehicle_year INTEGER,

            -- Processing Path
            damage_type TEXT NOT NULL,      -- 'body' (35% - AI eligible) or 'internal' (65% - NOT AI eligible)
            ai_eligible BOOLEAN NOT NULL,   -- TRUE if body damage (35%), FALSE if internal damage (65%)
            customer_ai_consent BOOLEAN,    -- TRUE if customer opted into AI (80-85% of eligible)
            processing_path TEXT NOT NULL,
            ai_enabled BOOLEAN NOT NULL,
            ai_adoption_phase TEXT NOT NULL,

            -- KPI 1: Cycle Time
            cycle_time_days REAL NOT NULL,
            cycle_time_hours REAL,

            -- KPI 2: Auto-Adjudication
            auto_adjudicated BOOLEAN NOT NULL,
            human_review_required BOOLEAN NOT NULL,
            human_review_reason TEXT,

            -- KPI 3: Cost per Claim
            cost_estimated REAL NOT NULL,
            cost_actual REAL NOT NULL,
            cost_operational REAL NOT NULL,
            cost_savings_factor REAL,
            cost_total REAL NOT NULL,

            -- KPI 4: Fraud Detection
            is_fraudulent BOOLEAN NOT NULL,     -- Ground truth: is this claim actually fraudulent?
            fraud_detected BOOLEAN NOT NULL,    -- Did our AI detect the fraud?
            fraud_risk_score REAL,
            fraud_type TEXT,

            -- Accuracy Metrics
            cost_accuracy_percent REAL,
            within_tolerance BOOLEAN,

            -- Claim Details
            claim_amount REAL NOT NULL,
            damage_count INTEGER,
            image_count INTEGER,

            -- Derived Flags
            is_closed BOOLEAN NOT NULL,
            routed_to_traditional BOOLEAN NOT NULL,

            -- Metadata
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_warehouse_fnol_date ON claims_warehouse(fnol_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_warehouse_month ON claims_warehouse(month)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_warehouse_damage_type ON claims_warehouse(damage_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_warehouse_ai_eligible ON claims_warehouse(ai_eligible)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_warehouse_processing_path ON claims_warehouse(processing_path)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_warehouse_ai_enabled ON claims_warehouse(ai_enabled)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_warehouse_ai_adoption_phase ON claims_warehouse(ai_adoption_phase)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_warehouse_claim_id ON claims_warehouse(claim_id)')

    conn.commit()


def insert_claims(conn, claims):
    """Insert claims into database"""
    cursor = conn.cursor()

    for claim in claims:
        cursor.execute('''
            INSERT INTO claims_warehouse (
                claim_id, fnol_date, fnol_datetime, claim_closed_date, claim_closed_datetime,
                month, week, day_of_week, quarter, year,
                customer_id, policy_number, vehicle_vin, vehicle_make, vehicle_model, vehicle_year,
                damage_type, ai_eligible, customer_ai_consent,
                processing_path, ai_enabled, ai_adoption_phase,
                cycle_time_days, cycle_time_hours,
                auto_adjudicated, human_review_required, human_review_reason,
                cost_estimated, cost_actual, cost_operational, cost_savings_factor, cost_total,
                is_fraudulent, fraud_detected, fraud_risk_score, fraud_type,
                cost_accuracy_percent, within_tolerance,
                claim_amount, damage_count, image_count,
                is_closed, routed_to_traditional
            ) VALUES (
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?,
                ?, ?, ?,
                ?, ?
            )
        ''', (
            claim['claim_id'], claim['fnol_date'], claim['fnol_datetime'],
            claim['claim_closed_date'], claim['claim_closed_datetime'],
            claim['month'], claim['week'], claim['day_of_week'], claim['quarter'], claim['year'],
            claim['customer_id'], claim['policy_number'], claim['vehicle_vin'],
            claim['vehicle_make'], claim['vehicle_model'], claim['vehicle_year'],
            claim['damage_type'], claim['ai_eligible'], claim['customer_ai_consent'],
            claim['processing_path'], claim['ai_enabled'], claim['ai_adoption_phase'],
            claim['cycle_time_days'], claim['cycle_time_hours'],
            claim['auto_adjudicated'], claim['human_review_required'], claim['human_review_reason'],
            claim['cost_estimated'], claim['cost_actual'], claim['cost_operational'],
            claim['cost_savings_factor'], claim['cost_total'],
            claim['is_fraudulent'], claim['fraud_detected'], claim['fraud_risk_score'], claim['fraud_type'],
            claim['cost_accuracy_percent'], claim['within_tolerance'],
            claim['claim_amount'], claim['damage_count'], claim['image_count'],
            claim['is_closed'], claim['routed_to_traditional']
        ))

    conn.commit()


def print_statistics(conn):
    """Print summary statistics of generated data"""
    cursor = conn.cursor()

    print("\n" + "="*80)
    print("CLAIMS WAREHOUSE - DATA GENERATION SUMMARY")
    print("="*80)

    # Total claims
    cursor.execute("SELECT COUNT(*) FROM claims_warehouse")
    total = cursor.fetchone()[0]
    print(f"\nTotal Claims Generated: {total}")

    # Monthly breakdown
    print("\n" + "-"*80)
    print("MONTHLY BREAKDOWN")
    print("-"*80)
    print(f"{'Month':<15} {'Claims':<10} {'Auto-Adj %':<15} {'Avg Cycle':<15} {'Fraud Det %':<15}")
    print("-"*80)

    cursor.execute('''
        SELECT
            month || '-' || year as period,
            COUNT(*) as total,
            ROUND(AVG(CASE WHEN auto_adjudicated THEN 100.0 ELSE 0.0 END), 1) as auto_adj_pct,
            ROUND(AVG(cycle_time_days), 1) as avg_cycle,
            -- Fraud detection rate = % of fraudulent claims detected (not % of all claims)
            ROUND(SUM(CASE WHEN fraud_detected = 1 THEN 1 ELSE 0 END) * 100.0 /
                  NULLIF(SUM(CASE WHEN is_fraudulent = 1 THEN 1 ELSE 0 END), 0), 1) as fraud_det_pct
        FROM claims_warehouse
        GROUP BY year, month
        ORDER BY year, month
    ''')

    for row in cursor.fetchall():
        print(f"{row[0]:<15} {row[1]:<10} {row[2]:<15} {row[3]:<15} {row[4]:<15}")

    # Processing path distribution
    print("\n" + "-"*80)
    print("PROCESSING PATH DISTRIBUTION")
    print("-"*80)
    cursor.execute('''
        SELECT processing_path, COUNT(*), ROUND(COUNT(*) * 100.0 / ?, 1)
        FROM claims_warehouse
        GROUP BY processing_path
    ''', (total,))

    for row in cursor.fetchall():
        print(f"{row[0]:<30} {row[1]:<10} ({row[2]}%)")

    # KPI Summary
    print("\n" + "-"*80)
    print("KPI SUMMARY")
    print("-"*80)

    cursor.execute('''
        SELECT
            ROUND(AVG(cycle_time_days), 2) as avg_cycle,
            ROUND(AVG(CASE WHEN auto_adjudicated THEN 100.0 ELSE 0.0 END), 1) as auto_adj_rate,
            ROUND(AVG(cost_operational), 2) as avg_operational_cost,
            -- Fraud detection rate = % of fraudulent claims that were detected
            ROUND(SUM(CASE WHEN fraud_detected = 1 THEN 1 ELSE 0 END) * 100.0 /
                  NULLIF(SUM(CASE WHEN is_fraudulent = 1 THEN 1 ELSE 0 END), 0), 1) as fraud_detection_rate,
            ROUND(AVG(CASE WHEN within_tolerance THEN 100.0 ELSE 0.0 END), 1) as accuracy_rate
        FROM claims_warehouse
        WHERE ai_enabled = TRUE
    ''')

    kpi = cursor.fetchone()
    print(f"Average Cycle Time: {kpi[0]} days")
    print(f"Auto-Adjudication Rate: {kpi[1]}%")
    print(f"Average Operational Cost per Claim: ${kpi[2]}")
    print(f"Fraud Detection Rate: {kpi[3]}% (of fraudulent claims)")
    print(f"Accuracy Within Tolerance: {kpi[4]}%")

    print("\n" + "="*80)


def main():
    parser = argparse.ArgumentParser(description='Seed claims warehouse with synthetic data')
    parser.add_argument('--reset', action='store_true', help='Clear existing data before seeding')
    parser.add_argument('--append', action='store_true', help='Append to existing data (use with caution)')
    parser.add_argument('--db', default='claims-warehouse.db', help='Path to database file')
    args = parser.parse_args()

    # Ensure data directory exists
    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Connect to database
    conn = sqlite3.connect(str(db_path))

    # Check if table exists and has data
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='claims_warehouse'")
    table_exists = cursor.fetchone() is not None

    if table_exists:
        cursor.execute("SELECT COUNT(*) FROM claims_warehouse")
        existing_count = cursor.fetchone()[0]

        if existing_count > 0 and not args.reset and not args.append:
            print(f"\n⚠️  WARNING: Database already contains {existing_count} claims!")
            print("Choose one of the following options:")
            print("  --reset   : Delete all existing data and regenerate")
            print("  --append  : Add new data (will create duplicate claim_ids)")
            print("\nExiting without making changes.\n")
            conn.close()
            return

        if existing_count > 0:
            if args.reset:
                print(f"Resetting database (removing {existing_count} existing claims)...")
                cursor.execute("DROP TABLE IF EXISTS claims_warehouse")
                conn.commit()
            elif args.append:
                print(f"Appending to existing {existing_count} claims...")

    # Create schema
    create_warehouse_schema(conn)

    # Generate claims
    print(f"Generating {CLAIMS_PER_MONTH * len(MONTHS)} synthetic claims...")
    claim_id = 1000
    all_claims = []

    for month_config in MONTHS:
        print(f"  Generating {CLAIMS_PER_MONTH} claims for {month_config['date']}...")
        for _ in range(CLAIMS_PER_MONTH):
            claim = generate_claim(claim_id, month_config)
            all_claims.append(claim)
            claim_id += 1

    # Insert into database
    print(f"Inserting {len(all_claims)} claims into database...")
    insert_claims(conn, all_claims)

    # Print statistics
    print_statistics(conn)

    conn.close()
    print(f"\n✓ Successfully seeded {len(all_claims)} claims to {args.db}")


if __name__ == '__main__':
    main()
