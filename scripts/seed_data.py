#!/usr/bin/env python
"""
Database seeding script for Insurance Claims API.
Creates sample customers, policies, vehicles, and claims for testing.

Usage:
    python scripts/seed_data.py              # Interactive mode
    python scripts/seed_data.py --force      # Force reseed without prompt
"""
import sys
import argparse
from pathlib import Path

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, time, datetime
from src.api.models.customer import Customer, CustomerPolicy
from src.api.models.policy import Policy, PolicyVehicle
from src.api.models.vehicle import Vehicle
from src.api.models.claim import Claim, ClaimImage
from src.api.models.claim_event import ClaimEvent
from src.api.models.adjustor import Adjustor
from src.api.database import Base
from src.api.constants import ClaimState, ClaimAction, ActorType

# Database URL (SQLite for development)
DATABASE_URL = "sqlite:///./test_insurance.db"

def create_sample_data(force=False):
    """
    Create sample data for testing

    Args:
        force: If True, skip confirmation prompt and force reseed
    """

    # Create engine and session
    engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(bind=engine)

    # Create all tables from models
    print("🔧 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    print()

    db = SessionLocal()

    try:
        print("=" * 60)
        print("DATABASE SEEDING - Insurance Claims API")
        print("=" * 60)
        print()

        # Check if data already exists
        existing_customers = db.query(Customer).count()
        if existing_customers > 0:
            print(f"⚠️  Database already contains {existing_customers} customers")
            if not force:
                response = input("Delete existing data and reseed? (yes/no): ")
                if response.lower() != 'yes':
                    print("❌ Seeding cancelled")
                    return
            else:
                print("🔄 Force mode enabled - deleting existing data...")

            # Delete all data
            print("\n🗑️  Deleting existing data...")
            db.query(ClaimEvent).delete()
            db.query(ClaimImage).delete()
            db.query(Claim).delete()
            db.query(PolicyVehicle).delete()
            db.query(CustomerPolicy).delete()
            db.query(Vehicle).delete()
            db.query(Policy).delete()
            db.query(Customer).delete()
            db.query(Adjustor).delete()
            db.commit()
            print("✅ Existing data deleted")
            print()

        # Create Customers
        print("👥 Creating customers...")
        customers = [
            Customer(
                customer_id=100,
                fname="John",
                lname="Doe",
                email="john.doe@example.com",
                phone="+15551234567",
                address="123 Main St, Los Angeles, CA 90001"
            ),
            Customer(
                customer_id=101,
                fname="Jane",
                lname="Smith",
                email="jane.smith@example.com",
                phone="+15559876543",
                address="456 Oak Ave, San Francisco, CA 94102"
            ),
            Customer(
                customer_id=102,
                fname="Bob",
                lname="Johnson",
                email="bob.johnson@example.com",
                phone="+15555551234",
                address="789 Pine Rd, San Diego, CA 92101"
            ),
            Customer(
                customer_id=103,
                fname="Alice",
                lname="Williams",
                email="alice.williams@example.com",
                phone="+15555559876",
                address="321 Elm St, Sacramento, CA 95814"
            ),
            Customer(
                customer_id=104,
                fname="Charlie",
                lname="Brown",
                email="charlie.brown@example.com",
                phone="+15555554321",
                address="654 Maple Dr, Oakland, CA 94601"
            ),
        ]

        for customer in customers:
            db.add(customer)

        db.commit()
        print(f"✅ Created {len(customers)} customers")

        # Create Adjustors
        print("👨‍💼 Creating adjustors...")
        adjustors = [
            Adjustor(
                adjustor_id="ADJ-001",
                name="Sarah Chen",
                email="sarah.chen@acme-insurance.com",
                role="Senior Adjustor",
                status="active"
            ),
            Adjustor(
                adjustor_id="ADJ-002",
                name="Michael Torres",
                email="michael.torres@acme-insurance.com",
                role="Collision Specialist",
                status="active"
            ),
            Adjustor(
                adjustor_id="ADJ-003",
                name="Emily Watson",
                email="emily.watson@acme-insurance.com",
                role="Claims Supervisor",
                status="active"
            ),
        ]

        for adjustor in adjustors:
            db.add(adjustor)

        db.commit()
        print(f"✅ Created {len(adjustors)} adjustors")

        # Create Policies
        print("📋 Creating policies...")
        policies = [
            Policy(
                policy_number="POL-2026-001",
                customer_id=100,
                start_date=date(2026, 1, 1),
                end_date=date(2027, 1, 1),
                policyholder_name="John Doe",
                insured_name="John Doe",
                bodily_injury_limit=100000.00,
                property_damage_limit=50000.00,
                premium=1200.00,
                deductible=500.00
            ),
            Policy(
                policy_number="POL-2026-002",
                customer_id=101,
                start_date=date(2026, 2, 1),
                end_date=date(2027, 2, 1),
                policyholder_name="Jane Smith",
                insured_name="Jane Smith",
                bodily_injury_limit=50000.00,
                property_damage_limit=25000.00,
                premium=800.00,
                deductible=1000.00
            ),
            Policy(
                policy_number="POL-2026-003",
                customer_id=102,
                start_date=date(2026, 1, 15),
                end_date=date(2027, 1, 15),
                policyholder_name="Bob Johnson",
                insured_name="Bob Johnson",
                bodily_injury_limit=250000.00,
                property_damage_limit=100000.00,
                premium=1500.00,
                deductible=250.00
            ),
            Policy(
                policy_number="POL-2026-004",
                customer_id=103,
                start_date=date(2026, 3, 1),
                end_date=date(2027, 3, 1),
                policyholder_name="Alice Williams",
                insured_name="Alice Williams",
                bodily_injury_limit=100000.00,
                property_damage_limit=50000.00,
                premium=1000.00,
                deductible=500.00
            ),
            Policy(
                policy_number="POL-2026-005",
                customer_id=104,
                start_date=date(2026, 4, 1),
                end_date=date(2027, 4, 1),
                policyholder_name="Charlie Brown",
                insured_name="Charlie Brown",
                bodily_injury_limit=150000.00,
                property_damage_limit=75000.00,
                premium=1300.00,
                deductible=500.00
            ),
        ]

        for policy in policies:
            db.add(policy)

        db.commit()
        print(f"✅ Created {len(policies)} policies")

        # Create Vehicles
        print("🚗 Creating vehicles...")
        vehicles = [
            Vehicle(
                vin="1HGBH41JXMN109186",
                customer_id=100,
                make="Honda",
                model="Accord",
                year=2022,
                color="Silver"
            ),
            Vehicle(
                vin="2HGFC2F50MH123456",
                customer_id=100,
                make="Honda",
                model="Civic",
                year=2021,
                color="White"
            ),
            Vehicle(
                vin="3FADP4EJ9FM123456",
                customer_id=100,
                make="Ford",
                model="Mustang",
                year=2023,
                color="Red"
            ),
            Vehicle(
                vin="1FTFW1ET5DFC12345",
                customer_id=101,
                make="Ford",
                model="F-150",
                year=2023,
                color="Blue"
            ),
            Vehicle(
                vin="5YJSA1E26HF123456",
                customer_id=102,
                make="Tesla",
                model="Model S",
                year=2021,
                color="Red"
            ),
            Vehicle(
                vin="WBAPL33569A123456",
                customer_id=103,
                make="BMW",
                model="3 Series",
                year=2020,
                color="Black"
            ),
            Vehicle(
                vin="1G1YY26E955123456",
                customer_id=104,
                make="Chevrolet",
                model="Corvette",
                year=2024,
                color="Yellow"
            ),
        ]

        for vehicle in vehicles:
            db.add(vehicle)

        db.commit()
        print(f"✅ Created {len(vehicles)} vehicles")

        # Link Customers to Policies
        print("🔗 Linking customers to policies...")
        customer_policies = [
            CustomerPolicy(customer_id=100, policy_number="POL-2026-001"),
            CustomerPolicy(customer_id=101, policy_number="POL-2026-002"),
            CustomerPolicy(customer_id=102, policy_number="POL-2026-003"),
            CustomerPolicy(customer_id=103, policy_number="POL-2026-004"),
            CustomerPolicy(customer_id=104, policy_number="POL-2026-005"),
        ]

        for cp in customer_policies:
            db.add(cp)

        db.commit()
        print(f"✅ Created {len(customer_policies)} customer-policy links")

        # Link Policies to Vehicles
        print("🔗 Linking policies to vehicles...")
        policy_vehicles = [
            PolicyVehicle(policy_number="POL-2026-001", vin="1HGBH41JXMN109186"),
            PolicyVehicle(policy_number="POL-2026-001", vin="2HGFC2F50MH123456"),
            PolicyVehicle(policy_number="POL-2026-001", vin="3FADP4EJ9FM123456"),
            PolicyVehicle(policy_number="POL-2026-002", vin="1FTFW1ET5DFC12345"),
            PolicyVehicle(policy_number="POL-2026-003", vin="5YJSA1E26HF123456"),
            PolicyVehicle(policy_number="POL-2026-004", vin="WBAPL33569A123456"),
            PolicyVehicle(policy_number="POL-2026-005", vin="1G1YY26E955123456"),
        ]

        for pv in policy_vehicles:
            db.add(pv)

        db.commit()
        print(f"✅ Created {len(policy_vehicles)} policy-vehicle links")

        # Create Sample Claims (excluding customer_id=100)
        print("📝 Creating sample claims...")
        claims = [
            Claim(
                claim_id=1001,
                customer_id=101,
                vin="1FTFW1ET5DFC12345",
                policy_number="POL-2026-002",
                fnol_date=date(2026, 5, 2),
                fnol_time=time(14, 15, 0),
                date_of_damage=date(2026, 5, 1),
                is_drivable=True,
                current_status=ClaimState.FNOL.value,
                claim_closed=False
            ),
            Claim(
                claim_id=1002,
                customer_id=102,
                vin="5YJSA1E26HF123456",
                policy_number="POL-2026-003",
                fnol_date=date(2026, 5, 3),
                fnol_time=time(9, 0, 0),
                date_of_damage=date(2026, 5, 2),
                is_drivable=False,
                current_status=ClaimState.FNOL.value,
                claim_closed=False
            ),
            # Claims for human review testing
            Claim(
                claim_id=2001,
                customer_id=103,
                vin="WBAPL33569A123456",  # Customer 103's BMW 3 Series
                policy_number="POL-2026-004",
                fnol_date=date(2026, 5, 4),
                fnol_time=time(10, 0, 0),
                date_of_damage=date(2026, 5, 3),
                is_drivable=True,
                current_status=ClaimState.HUMAN_REVIEW_PENDING.value,
                claim_amount=2850.00,
                claim_closed=False
            ),
            Claim(
                claim_id=2002,
                customer_id=104,
                vin="1G1YY26E955123456",  # Customer 104's Chevy Corvette
                policy_number="POL-2026-005",
                fnol_date=date(2026, 5, 3),
                fnol_time=time(15, 30, 0),
                date_of_damage=date(2026, 5, 2),
                is_drivable=True,
                current_status=ClaimState.HUMAN_REVIEW_PENDING.value,
                claim_amount=1250.00,
                claim_closed=False
            ),
        ]

        for claim in claims:
            db.add(claim)

        db.commit()
        print(f"✅ Created {len(claims)} claims")

        # Create Claim Events (excluding customer_id=100)
        print("📅 Creating claim events...")
        events = [
            # Claim 1001 - Submitted to FNOL
            ClaimEvent(
                claim_id=1001,
                event_date=date(2026, 5, 2),
                event_time=time(14, 15, 0),
                status=ClaimState.DRAFT.value,
                action=ClaimAction.CREATE_CLAIM.value,
                action_by=ActorType.CUSTOMER.value,
                action_by_identity="customer_101",
                comments="Claim created in draft state"
            ),
            ClaimEvent(
                claim_id=1001,
                event_date=date(2026, 5, 2),
                event_time=time(14, 20, 0),
                status=ClaimState.FNOL.value,
                action=ClaimAction.SUBMIT_CLAIM.value,
                action_by=ActorType.CUSTOMER.value,
                action_by_identity="customer_101",
                comments="Claim submitted for processing"
            ),
            # Claim 1002 - Submitted to FNOL
            ClaimEvent(
                claim_id=1002,
                event_date=date(2026, 5, 3),
                event_time=time(9, 0, 0),
                status=ClaimState.DRAFT.value,
                action=ClaimAction.CREATE_CLAIM.value,
                action_by=ActorType.CUSTOMER.value,
                action_by_identity="customer_102",
                comments="Claim created in draft state"
            ),
            ClaimEvent(
                claim_id=1002,
                event_date=date(2026, 5, 3),
                event_time=time(9, 5, 0),
                status=ClaimState.FNOL.value,
                action=ClaimAction.SUBMIT_CLAIM.value,
                action_by=ActorType.CUSTOMER.value,
                action_by_identity="customer_102",
                comments="Claim submitted for processing"
            ),
            # Claim 2001 - Customer appealed, in human review
            ClaimEvent(
                claim_id=2001,
                event_date=date(2026, 5, 4),
                event_time=time(10, 0, 0),
                status=ClaimState.DRAFT.value,
                action=ClaimAction.CREATE_CLAIM.value,
                action_by=ActorType.CUSTOMER.value,
                action_by_identity="customer_103",
                comments="Claim created"
            ),
            ClaimEvent(
                claim_id=2001,
                event_date=date(2026, 5, 4),
                event_time=time(10, 5, 0),
                status=ClaimState.LOSS_ESTIMATED_AI.value,
                action=ClaimAction.GENERATE_ESTIMATE.value,
                action_by=ActorType.AI_AGENT.value,
                action_by_identity="ai_agent",
                comments="AI generated estimate: $2,850"
            ),
            ClaimEvent(
                claim_id=2001,
                event_date=date(2026, 5, 4),
                event_time=time(10, 30, 0),
                status=ClaimState.LOSS_APPEALED.value,
                action=ClaimAction.APPEAL_ESTIMATE.value,
                action_by=ActorType.CUSTOMER.value,
                action_by_identity="customer_103",
                comments="Customer appealed AI estimate - believes damage is less severe"
            ),
            ClaimEvent(
                claim_id=2001,
                event_date=date(2026, 5, 4),
                event_time=time(10, 31, 0),
                status=ClaimState.HUMAN_REVIEW_PENDING.value,
                action=ClaimAction.FLAG_FOR_HUMAN_REVIEW.value,
                action_by=ActorType.AI_AGENT.value,
                action_by_identity="system",
                comments="Routed to human review due to customer appeal"
            ),
            # Claim 2002 - Low confidence, in human review
            ClaimEvent(
                claim_id=2002,
                event_date=date(2026, 5, 3),
                event_time=time(15, 30, 0),
                status=ClaimState.DRAFT.value,
                action=ClaimAction.CREATE_CLAIM.value,
                action_by=ActorType.CUSTOMER.value,
                action_by_identity="customer_104",
                comments="Claim created"
            ),
            ClaimEvent(
                claim_id=2002,
                event_date=date(2026, 5, 3),
                event_time=time(15, 35, 0),
                status=ClaimState.LOSS_ESTIMATED_AI.value,
                action=ClaimAction.GENERATE_ESTIMATE.value,
                action_by=ActorType.AI_AGENT.value,
                action_by_identity="ai_agent",
                comments="AI generated estimate: $1,250 (low confidence: 0.42)"
            ),
            ClaimEvent(
                claim_id=2002,
                event_date=date(2026, 5, 3),
                event_time=time(15, 36, 0),
                status=ClaimState.HUMAN_REVIEW_PENDING.value,
                action=ClaimAction.FLAG_FOR_HUMAN_REVIEW.value,
                action_by=ActorType.AI_AGENT.value,
                action_by_identity="system",
                comments="Routed to human review due to low AI confidence (0.42 < 0.55 threshold)"
            ),
        ]

        for event in events:
            db.add(event)

        db.commit()
        print(f"✅ Created {len(events)} claim events")

        # Summary
        print()
        print("=" * 60)
        print("✅ DATABASE SEEDING COMPLETE!")
        print("=" * 60)
        print()
        print("Summary:")
        print(f"  👥 Customers:        {len(customers)}")
        print(f"  👨‍💼 Adjustors:        {len(adjustors)}")
        print(f"  📋 Policies:         {len(policies)}")
        print(f"  🚗 Vehicles:         {len(vehicles)}")
        print(f"  📝 Claims:           {len(claims)}")
        print(f"  📅 Events:           {len(events)}")
        print()
        print("Sample Data:")
        print(f"  - Customer IDs:      100-104")
        print(f"  - Adjustor IDs:      ADJ-001 to ADJ-003")
        print(f"  - Policy Numbers:    POL-2026-001 to POL-2026-005")
        print(f"  - Claim IDs:         1001-1002 (FNOL), 2001-2002 (Human Review)")
        print(f"  - Customer 100:      3 vehicles, no claims")
        print()
        print("Test the API:")
        print(f"  - GET  /customers/100")
        print(f"  - GET  /customers/100/claims")
        print(f"  - GET  /customers/101/claims/1001/events")
        print(f"  - GET  /adjustors/ADJ-001/claims/pending")
        print(f"  - GET  /adjustors/ADJ-001/statistics")
        print(f"  - POST /claims/2001/review/complete")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed database with sample data")
    parser.add_argument("--force", action="store_true", help="Force reseed without confirmation")
    args = parser.parse_args()

    create_sample_data(force=args.force)
