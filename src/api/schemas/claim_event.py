"""
Claim event-related Pydantic schemas.
"""
from pydantic import BaseModel
from datetime import date, time
from typing import Optional, List

class ClaimEventResponse(BaseModel):
    """Response schema for claim event"""
    claim_id: int
    event_id: int
    event_date: date
    event_time: time
    status: str
    action: str
    action_by: str
    action_by_identity: str
    comments: Optional[str]

    class Config:
        from_attributes = True

class ClaimEventSummary(BaseModel):
    """Summary response for event listing"""
    total_events: int
    events: List[ClaimEventResponse]

    # Optional: event statistics
    customer_actions: Optional[int] = 0
    ai_actions: Optional[int] = 0
    adjustor_actions: Optional[int] = 0
    admin_actions: Optional[int] = 0
