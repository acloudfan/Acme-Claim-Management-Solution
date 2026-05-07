"""
Claim-related Pydantic schemas.
"""
from pydantic import BaseModel, Field, field_validator
from datetime import date, time
from typing import Optional, List
from decimal import Decimal

class ClaimCreate(BaseModel):
    """Request schema for creating claim (FNOL)"""
    vin: str = Field(..., min_length=17, max_length=17)
    policy_number: str = Field(..., max_length=50)
    fnol_date: date
    fnol_time: time
    date_of_damage: date
    is_drivable: bool
    incident_description: Optional[str] = Field(None, max_length=2000, description="Customer's description of what happened")

    @field_validator("fnol_date")
    @classmethod
    def validate_fnol_date(cls, v):
        """Ensure FNOL date is not in the future"""
        if v > date.today():
            raise ValueError("FNOL date cannot be in the future")
        return v

    @field_validator("date_of_damage")
    @classmethod
    def validate_date_of_damage(cls, v, info):
        """Ensure damage date is not in the future"""
        if v > date.today():
            raise ValueError("Date of damage cannot be in the future")
        # Validate against FNOL date if available
        if info.data.get("fnol_date") and v > info.data["fnol_date"]:
            raise ValueError("Date of damage cannot be after FNOL date")
        return v

class ClaimUpdate(BaseModel):
    """Schema for updating claim"""
    is_drivable: Optional[bool] = None
    active_estimate_id: Optional[str] = None
    claim_amount: Optional[float] = None
    state_avg_labor_cost: Optional[Decimal] = None  # NEW: Allow adjustor override
    incident_description: Optional[str] = Field(None, max_length=2000)


class BoundingBox(BaseModel):
    """Bounding box coordinates for damage detection"""
    x: int
    y: int
    width: int
    height: int


class DamageDetail(BaseModel):
    """Individual damage detail from damages table with YOLO detection fields and dual-column estimates"""
    damage_id: int
    estimate_id: str
    image_id: str
    estimate_type: str  # 'ai' or 'human'

    # YOLO Detection Fields
    damage_class: Optional[int] = None
    damage_confidence: Optional[float] = None
    damage_part: str
    bounding_box: Optional[BoundingBox] = None

    # Assessment Fields
    internal_damage_probability: Optional[float] = None
    severity: Decimal
    recommended_action: Optional[str] = None
    reasoning: Optional[str] = None
    car_side: Optional[str] = None
    assessment_confidence: Optional[float] = None

    # Effective Cost Breakdown (adjustor if available, else AI)
    estimated_total_cost: Decimal
    labor_hours: Decimal
    estimated_parts_cost: Decimal
    estimate_source: str  # "ai" or "adjustor"

    # AI Estimate (baseline - always included)
    ai_labor_hours: Decimal
    ai_parts_cost: Decimal
    ai_total_cost: Decimal

    # Adjustor Estimate (nullable - set during review)
    adjustor_labor_hours: Optional[Decimal] = None
    adjustor_parts_cost: Optional[Decimal] = None
    adjustor_total_cost: Optional[Decimal] = None
    reviewed_by_adjustor: bool = False
    adjustor_note: Optional[str] = None
    reviewed_at: Optional[str] = None  # ISO format datetime string

    # Annotated Image
    annotated_image_id: Optional[str] = None

    # DEPRECATED
    avg_labor_cost: Optional[Decimal] = None

    class Config:
        from_attributes = True


class DamageAssessment(BaseModel):
    """Damage assessment summary with all damages"""
    total_estimated_cost: Decimal
    damage_count: int
    damages: List[DamageDetail]


class ClaimResponse(BaseModel):
    """Response schema for claim"""
    claim_id: int
    customer_id: int
    vin: str
    policy_number: str
    fnol_date: date
    fnol_time: time
    date_of_damage: date
    is_drivable: bool
    incident_description: Optional[str] = None
    current_status: str
    claim_closed: bool
    claim_closed_date: Optional[date]
    ai_estimate_accepted: bool
    routed_to_traditional: bool
    reason_routing_to_traditional: Optional[str]
    active_estimate_id: Optional[str]
    claim_amount: Optional[float]
    actual_claim_amount: Optional[float]

    # Labor Rate Fields
    state_avg_labor_cost: Optional[Decimal] = None  # $/hour
    labor_rate_state: Optional[str] = None  # e.g., "CA", "TX"
    labor_rate_source: Optional[str] = None  # "customer_state" | "adjustor_override"

    # Appeal Tracking Fields (NEW)
    appeal_count: int = 0  # Number of appeals (0, 1, or 2)
    first_appeal_reason: Optional[str] = None  # Customer's reason for first appeal
    first_appeal_date: Optional[date] = None  # Date of first appeal
    second_appeal_reason: Optional[str] = None  # Customer's reason for second appeal
    second_appeal_date: Optional[date] = None  # Date of second appeal

    # Agent-Enhanced Fields (AI Analysis Results)
    overall_fraud_risk_score: Optional[Decimal] = None  # Fraud risk score (0.0-1.0)
    overall_risk_score: Optional[Decimal] = None  # Actuarial risk score (0.0-1.0)
    agent_flags: Optional[str] = None  # JSON string of agent flags/warnings

    damage_assessment: Optional[DamageAssessment] = None

    class Config:
        from_attributes = True

class ClaimImageResponse(BaseModel):
    """Response schema for claim image"""
    image_id: str
    claim_id: int
    uploaded_at: str
    uploaded_by: str

    class Config:
        from_attributes = True
