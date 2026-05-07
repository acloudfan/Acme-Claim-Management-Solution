"""
Damage and estimate-related Pydantic schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class BoundingBox(BaseModel):
    """Bounding box coordinates"""
    x: int
    y: int
    width: int
    height: int

class DamageResponse(BaseModel):
    """Response schema for damage assessment with dual-column support"""
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
    severity: float
    recommended_action: Optional[str] = None
    reasoning: Optional[str] = None
    car_side: Optional[str] = None
    assessment_confidence: Optional[float] = None

    # Effective Cost Breakdown (adjustor if available, else AI)
    labor_hours: float
    estimated_parts_cost: float
    estimated_total_cost: float
    estimate_source: Literal["ai", "adjustor"]  # Which estimate is active

    # AI Estimate (baseline - always included)
    ai_labor_hours: float
    ai_parts_cost: float
    ai_total_cost: float

    # Adjustor Estimate (nullable - set during review)
    adjustor_labor_hours: Optional[float] = None
    adjustor_parts_cost: Optional[float] = None
    adjustor_total_cost: Optional[float] = None
    reviewed_by_adjustor: bool = False
    adjustor_note: Optional[str] = None
    reviewed_at: Optional[str] = None  # ISO format datetime string

    # Annotated Image
    annotated_image_id: Optional[str] = None

    # DEPRECATED
    avg_labor_cost: Optional[float] = None

    class Config:
        from_attributes = True

class EstimateRequest(BaseModel):
    """Request schema for generating estimate"""
    claim_id: int
    image_ids: list[str] = Field(..., min_length=1)
    state: str = Field("CA", max_length=2)

class EstimateResponse(BaseModel):
    """Response schema for estimate"""
    estimate_id: str
    claim_id: int
    total_cost: float
    damages_count: int
    damages: list[DamageResponse]

class CostBreakdown(BaseModel):
    """Cost breakdown details"""
    labor_cost: float
    parts_cost: float
    total: float

class CostEstimateResponse(BaseModel):
    """Response schema for cost calculation"""
    damage_part: str
    severity: float
    labor_hours: float
    avg_labor_cost: float
    estimated_parts_cost: float
    estimated_total_cost: float
    breakdown: CostBreakdown
    confidence: float
    notes: str


class DamageCreateRequest(BaseModel):
    """Request schema for creating manual damage entry"""
    estimate_type: Literal["human"] = "human"
    damage_part: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    severity: Literal["light", "moderate", "severe"]
    image_id: Optional[str] = None
    labor_hours: float = Field(..., gt=0, le=100)
    labor_rate: float = Field(..., ge=50, le=500)
    parts_cost: float = Field(..., ge=0, le=50000)
    adjustor_note: str = Field(..., min_length=10, max_length=1000)

    class Config:
        json_schema_extra = {
            "example": {
                "estimate_type": "human",
                "damage_part": "Front Bumper",
                "description": "Significant impact damage requiring replacement",
                "severity": "severe",
                "image_id": "IMG_001",
                "labor_hours": 3.5,
                "labor_rate": 125.0,
                "parts_cost": 850.0,
                "adjustor_note": "Inspection reveals internal bracket damage not visible in images"
            }
        }


class DamageUpdateRequest(BaseModel):
    """Request schema for updating damage costs"""
    labor_hours: Optional[float] = Field(None, gt=0, le=100)
    labor_rate: Optional[float] = Field(None, ge=50, le=500)
    parts_cost: Optional[float] = Field(None, ge=0, le=50000)
    adjustor_note: str = Field(..., min_length=10, max_length=1000)

    class Config:
        json_schema_extra = {
            "example": {
                "labor_hours": 4.0,
                "labor_rate": 125.0,
                "parts_cost": 950.0,
                "adjustor_note": "Revised estimate after consulting parts supplier"
            }
        }
