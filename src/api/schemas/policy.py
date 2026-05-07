"""
Pydantic schemas for policy operations.
"""
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List
from decimal import Decimal


class VehicleInfo(BaseModel):
    """Vehicle information in policy response"""
    vin: str
    year: int
    make: str
    model: str
    color: Optional[str] = None

    class Config:
        from_attributes = True


class PolicyResponse(BaseModel):
    """Response schema for policy"""
    policy_number: str
    customer_id: int
    policy_type: str = Field(default="auto", description="Policy type (auto, home, etc.)")
    policyholder_name: str
    insured_name: str

    # Dates
    start_date: date
    end_date: date

    # Additional Insured (flattened structure)
    additional_insured_1: Optional[str] = None
    additional_insured_2: Optional[str] = None
    additional_insured_3: Optional[str] = None

    # Coverage limits
    bodily_injury_limit: Decimal
    property_damage_limit: Decimal

    # Financial
    premium: Decimal
    deductible: Decimal

    # Associated vehicles
    vehicles: List[VehicleInfo] = []

    class Config:
        from_attributes = True
