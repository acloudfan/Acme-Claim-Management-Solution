"""
Pydantic schemas for adjustor-related API requests and responses.
"""
from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional


class AdjustorResponse(BaseModel):
    """Response schema for adjustor information"""
    adjustor_id: str
    name: str
    email: EmailStr
    role: Optional[str]
    status: str

    class Config:
        from_attributes = True


class PendingClaimSummary(BaseModel):
    """Summary information for claims pending human review"""
    claim_id: int
    customer_id: int
    customer_name: str
    vin: str
    vehicle: str  # "2022 Honda Accord Silver"
    policy_number: str
    fnol_date: date
    ai_estimate_total: float
    reason_for_review: str  # "customer_appeal", "low_confidence", "no_damage"
    time_in_queue: str  # "2h", "1d", etc.
    current_status: str

    class Config:
        from_attributes = True


class AdjustorStatistics(BaseModel):
    """Statistics for adjustor workload and performance"""
    pending_reviews: int
    completed_today: int
    completed_this_week: int
    average_review_time_minutes: float
    total_reviews_all_time: int

    class Config:
        from_attributes = True


class AdjustorWithWorkload(BaseModel):
    """Adjustor information with current workload statistics"""
    adjustor_id: str
    name: str
    email: EmailStr
    role: Optional[str]
    status: str
    pending_reviews: int
    completed_today: int
    completed_this_week: int

    class Config:
        from_attributes = True
