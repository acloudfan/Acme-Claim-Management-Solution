"""
Cost estimation API router.
Provides endpoint for calculating repair cost estimates.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.api.database import get_db
from src.api.services.cost_service import CostService
from pydantic import BaseModel, Field
from typing import Dict

router = APIRouter()

# Pydantic schemas
class DamageReportSchema(BaseModel):
    """Damage report from detection system"""
    id: int = Field(default=1)
    class_: int = Field(..., alias="class")
    confidence: float = Field(..., ge=0.0, le=1.0)
    part: str

class AssessmentSchema(BaseModel):
    """Damage assessment details"""
    internal_damage_probability: float = Field(..., ge=0.0, le=1.0)
    severity: float = Field(..., ge=0.0, le=1.0)
    recommended_action: str
    reasoning: str
    car_side: str
    confidence: float = Field(..., ge=0.0, le=1.0)

class CostEstimateRequest(BaseModel):
    """Request for cost estimation"""
    damage_report: DamageReportSchema
    assessment: AssessmentSchema
    state: str = Field("CA", max_length=2)

@router.post(
    "/estimate",
    response_model=Dict,
    summary="Calculate repair cost estimate"
)
def calculate_cost_estimate(
    request: CostEstimateRequest,
    db: Session = Depends(get_db)
):
    """
    Calculate repair cost estimate for damage report.

    Uses state-specific labor rates and damage part estimates to calculate
    total repair cost including labor and parts.

    - **damage_report**: Damage detection results (part, class, confidence)
    - **assessment**: Damage assessment details (severity, internal damage probability)
    - **state**: State code for labor rate (default: CA)

    Returns cost breakdown with:
    - Labor hours and cost
    - Parts cost
    - Total estimated cost
    - Confidence level
    """
    service = CostService(db)

    cost_info = service.calculate_cost(
        damage_report=request.damage_report.model_dump(by_alias=True),
        assessment=request.assessment.model_dump(),
        state=request.state
    )

    return {"data": cost_info}
