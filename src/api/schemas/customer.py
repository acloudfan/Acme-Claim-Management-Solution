"""
Customer-related Pydantic schemas.
"""
from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import date
from typing import Optional, List

class CustomerCreate(BaseModel):
    """Request schema for creating customer"""
    fname: str = Field(..., min_length=1, max_length=50, description="First name")
    lname: str = Field(..., min_length=1, max_length=50, description="Last name")
    email: EmailStr = Field(..., description="Email address (must be valid format)")
    phone: str = Field(..., pattern=r'^\+?1?\d{9,15}$', description="Phone number")

    # Optional fields matching existing database schema
    address: Optional[str] = Field(None, max_length=255, description="Street address")
    state: Optional[str] = Field(None, pattern=r'^[A-Z]{2}$', description="2-letter state code")

class CustomerUpdate(BaseModel):
    """Request schema for full customer update (all fields required)"""
    fname: str = Field(..., min_length=1, max_length=50)
    lname: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone: str = Field(..., pattern=r'^\+?1?\d{9,15}$')
    address: Optional[str] = Field(None, max_length=255)
    state: Optional[str] = Field(None, pattern=r'^[A-Z]{2}$')

class CustomerPatch(BaseModel):
    """Request schema for partial customer update (all fields optional)"""
    fname: Optional[str] = Field(None, min_length=1, max_length=50)
    lname: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    address: Optional[str] = Field(None, max_length=255)
    state: Optional[str] = Field(None, pattern=r'^[A-Z]{2}$')

class CustomerResponse(BaseModel):
    """Response schema for customer"""
    customer_id: int
    fname: str
    lname: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    state: Optional[str]  # NEW: 2-letter state code

    # Optional: included if include_policies=true
    # policies: Optional[List["PolicyResponse"]] = None

    class Config:
        from_attributes = True
