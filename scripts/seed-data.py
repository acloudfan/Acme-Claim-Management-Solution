#!/usr/bin/env python
"""
Database seeding script for Insurance Claims API.
Creates sample customers, policies, vehicles, and claims for testing.

Usage:
    python scripts/seed-data.py              # Seed database
    python scripts/seed-data.py --clean      # Delete database and uploads folder
"""
import sys
import argparse
from pathlib import Path
import shutil
import os

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
DB_FILE = "test_insurance.db"
UPLOADS_FOLDER = "uploads"
NEEDS_RESEED_MARKER = ".needs_reseed"

def clean_database_and_uploads():
    """
    Delete database file and uploads folder.
    Creates a marker file to warn API server to display reseed message.
    """
    print("=" * 60)
    print("DATABASE CLEANUP - Insurance Claims API")
    print("=" * 60)
    print()

    deleted_items = []

    # Delete database file
    if os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
            deleted_items.append(f"✅ Deleted database: {DB_FILE}")
        except Exception as e:
            print(f"❌ Failed to delete database: {e}")
    else:
        deleted_items.append(f"ℹ️  Database not found: {DB_FILE}")

    # Delete uploads folder
    if os.path.exists(UPLOADS_FOLDER):
        try:
            shutil.rmtree(UPLOADS_FOLDER)
            deleted_items.append(f"✅ Deleted uploads folder: {UPLOADS_FOLDER}")
        except Exception as e:
            print(f"❌ Failed to delete uploads folder: {e}")
    else:
        deleted_items.append(f"ℹ️  Uploads folder not found: {UPLOADS_FOLDER}")

    # Create marker file for API server
    try:
        with open(NEEDS_RESEED_MARKER, 'w') as f:
            f.write("Database cleaned. Please run scripts/seed-data.py to reseed.\n")
        deleted_items.append(f"✅ Created reseed marker: {NEEDS_RESEED_MARKER}")
    except Exception as e:
        print(f"❌ Failed to create marker file: {e}")

    # Print summary
    print("\n".join(deleted_items))
    print()
    print("=" * 60)
    print("✅ CLEANUP COMPLETE!")
    print("=" * 60)
    print()
    print("⚠️  IMPORTANT: Run the following to reseed the database:")
    print("    python scripts/seed-data.py")
    print()

def create_sample_data():
    """
    Create sample data for testing
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
            print("🔄 Deleting existing data...")

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
                make="Toyota",
                model="Corolla",
                year=2015,
                color="Red"
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
                vin="1FTFW1ET5DFC12345",
                customer_id=101,
                make="BMW",
                model="1 Series (E87)",
                year=2006,
                color="Silver"
            ),
            Vehicle(
                vin="5YJSA1E26HF123456",
                customer_id=102,
                make="Chevrolet",
                model="Silverado",
                year=2012,
                color="Red"
            ),
            Vehicle(
                vin="WBAPL33569A123456",
                customer_id=103,
                make="Honda",
                model="Accord",
                year=2022,
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
            PolicyVehicle(policy_number="POL-2026-002", vin="1FTFW1ET5DFC12345"),
            PolicyVehicle(policy_number="POL-2026-003", vin="5YJSA1E26HF123456"),
            PolicyVehicle(policy_number="POL-2026-004", vin="WBAPL33569A123456"),
            PolicyVehicle(policy_number="POL-2026-005", vin="1G1YY26E955123456"),
        ]

        for pv in policy_vehicles:
            db.add(pv)

        db.commit()
        print(f"✅ Created {len(policy_vehicles)} policy-vehicle links")

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
        print()
        print("Sample Data:")
        print(f"  - Customer IDs:      100-104")
        print(f"  - Adjustor IDs:      ADJ-001 to ADJ-003")
        print(f"  - Policy Numbers:    POL-2026-001 to POL-2026-005")
        print(f"  - Vehicles:          6 vehicles across customers")
        print(f"  - Customer 100:      2 vehicles (Toyota Corolla 2015, Honda Civic 2021)")
        print()
        print("Test the API:")
        print(f"  - GET  /customers/100")
        print(f"  - GET  /customers/101/policies")
        print(f"  - GET  /adjustors/ADJ-001/statistics")
        print()

        # Remove reseed marker if it exists
        if os.path.exists(NEEDS_RESEED_MARKER):
            try:
                os.remove(NEEDS_RESEED_MARKER)
                print(f"✅ Removed reseed marker file")
            except Exception as e:
                print(f"⚠️  Could not remove marker file: {e}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed database with sample data")
    parser.add_argument("--clean", action="store_true", help="Delete database and uploads folder")
    args = parser.parse_args()

    if args.clean:
        clean_database_and_uploads()
    else:
        create_sample_data()
