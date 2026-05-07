"""
Pydantic schemas for claim review operations.
"""
from pydantic import BaseModel, Field
from typing import Literal, Optional, List


from typing import Union

class DamageUpdate(BaseModel):
    """Schema for damage updates during review"""
    damage_id: Union[int, str]  # Allow string IDs for manual damages not yet saved
    labor_hours: Optional[float] = None
    parts_cost: Optional[float] = None
    adjustor_note: Optional[str] = None
    # Fields for manual damages (when damage_id is a string starting with "manual_")
    damage_part: Optional[str] = None
    damage_type: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    image_id: Optional[str] = None


class ReviewCompleteRequest(BaseModel):
    """Request schema for completing a claim review"""
    action: Literal["denied_appeal", "revised_estimate", "route_to_traditional"]
    customer_note: str = Field(..., min_length=10, max_length=1000)
    internal_note: str = Field(..., min_length=10, max_length=2000)
    revised_estimate_total: Optional[float] = None
    adjustor_id: Optional[str] = None
    damages: Optional[List[DamageUpdate]] = None
    labor_rate_state: Optional[str] = None
    state_avg_labor_cost: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "action": "denied_appeal",
                "customer_note": "After careful review, the AI estimate is accurate...",
                "internal_note": "Reviewed all images. AI detection accurate...",
                "revised_estimate_total": None,
                "adjustor_id": "ADJ-001",
                "damages": [],
                "labor_rate_state": "CA",
                "state_avg_labor_cost": 156.00
            }
        }


class ReviewCompleteResponse(BaseModel):
    """Response schema after completing a review"""
    claim_id: int
    current_status: str
    next_status: str
    revised_estimate_total: Optional[float]
    event_id: int

    class Config:
        from_attributes = True
