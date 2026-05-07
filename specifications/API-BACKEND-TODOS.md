# API Backend TODOs - Adjustor Portal Support
## Backend Implementation Tasks for Human Review Workflow

**Version:** 1.0  
**Date:** 2026-05-05  
**Status:** Implementation Checklist  
**Priority:** P0 (MVP), P1 (Core), P2 (Enhancement)  
**Related:** See `API-BACKEND-DESIGN.md` for architecture details

---

## Overview

These tasks extend the existing API backend to support the Adjustor Portal functionality:
- Human review of claims in `human_review_pending` status
- Manual damage entry by adjustors
- Damage cost adjustments
- Review completion with customer/internal notes

**Estimated Time:** 24 hours for P0 tasks

---

## Table of Contents

1. [Database Schema Extensions](#database-schema-extensions)
2. [API Schemas (Pydantic)](#api-schemas-pydantic)
3. [Services Layer](#services-layer)
4. [API Routers](#api-routers)
5. [Seed Data Updates](#seed-data-updates)
6. [Testing](#testing)

---

## Database Schema Extensions

### Task 1.1: Create Adjustor Model (P0) [1 hour]

**Location:** `src/api/models/adjustor.py` (NEW FILE)

- [ ] Create new file `src/api/models/adjustor.py`
- [ ] Define Adjustor model with fields:
  - `adjustor_id` (String(20), PK) — e.g., "ADJ-001"
  - `name` (String(100), not null)
  - `email` (String(255), unique, not null)
  - `role` (String(100), nullable) — e.g., "Senior Adjustor"
  - `status` (String(20), not null, default='active') — 'active' or 'inactive'
- [ ] Add relationships (optional, P2):
  - `assigned_claims` (backref to Claim model)
- [ ] Import in `src/api/models/__init__.py`
- [ ] Create Alembic migration: `alembic revision --autogenerate -m "Add adjustor model"`
- [ ] Run migration: `alembic upgrade head`

**Acceptance Criteria:**
- Model defined with proper SQLAlchemy types
- Table created in database
- Can insert/query adjustor records
- Migration runs without errors

**Example Model:**
```python
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from src.api.database import Base

class Adjustor(Base):
    __tablename__ = "adjustors"
    
    adjustor_id = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(String(100), nullable=True)
    status = Column(String(20), nullable=False, default='active')
    
    # Optional (P2)
    # assigned_claims = relationship("Claim", back_populates="adjustor")
    
    def __repr__(self):
        return f"<Adjustor(adjustor_id={self.adjustor_id}, name={self.name})>"
```

---

### Task 1.2: Extend Damage Model (P0) [1 hour]

**Location:** `src/api/models/damage.py` (EXISTING FILE)

**CRITICAL FIX:** The ERD diagram shows `generated_on_date` and `generated_on_time` fields but the model is missing them!

- [ ] Open `src/api/models/damage.py`
- [ ] Add **REQUIRED** fields (missing from model but in ERD):
  ```python
  from sqlalchemy import Date, Time
  
  generated_on_date = Column(Date, nullable=True)
  generated_on_time = Column(Time, nullable=True)
  ```
- [ ] Add **OPTIONAL** field for adjustor functionality:
  ```python
  adjustor_note = Column(Text, nullable=True)  # P1
  # adjustor_id = Column(String(20), ForeignKey("adjustors.adjustor_id"), nullable=True)  # P2
  ```
- [ ] Create Alembic migration: `alembic revision --autogenerate -m "Add generated timestamps and adjustor note to damage"`
- [ ] Run migration: `alembic upgrade head`
- [ ] Update `seed_data.py` to set `generated_on_date` and `generated_on_time` for all damage records

**Acceptance Criteria:**
- Model matches ERD diagram
- Migration runs successfully
- Seed data populates timestamps
- Can store adjustor notes

---

### Task 1.3: Add Adjustor Fields to Claim Model (P2) [30 minutes]

**Location:** `src/api/models/claim.py` (EXISTING FILE)

**Optional enhancement for claim assignment feature (not required for MVP)**

- [ ] Open `src/api/models/claim.py`
- [ ] Add fields:
  ```python
  assigned_adjustor_id = Column(String(20), ForeignKey("adjustors.adjustor_id"), nullable=True)
  review_completed_date = Column(Date, nullable=True)
  review_completed_time = Column(Time, nullable=True)
  ```
- [ ] Add relationship:
  ```python
  adjustor = relationship("Adjustor", back_populates="assigned_claims")
  ```
- [ ] Create Alembic migration
- [ ] Run migration

**Acceptance Criteria:**
- Claims can be assigned to adjustors
- Foreign key relationship works
- Migration runs without errors

---

## API Schemas (Pydantic)

### Task 2.1: Create Adjustor Schemas (P0) [30 minutes]

**Location:** `src/api/schemas/adjustor.py` (NEW FILE)

- [ ] Create `src/api/schemas/adjustor.py`
- [ ] Define schemas:

```python
from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class AdjustorResponse(BaseModel):
    adjustor_id: str
    name: str
    email: EmailStr
    role: Optional[str]
    status: str
    
    class Config:
        from_attributes = True

class PendingClaimSummary(BaseModel):
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

class AdjustorStatistics(BaseModel):
    pending_reviews: int
    completed_today: int
    completed_this_week: int
    average_review_time_minutes: float
    total_reviews_all_time: int
```

**Acceptance Criteria:**
- Schemas compile without errors
- Field types match database models
- Validation works correctly

---

### Task 2.2: Create Review Schemas (P0) [30 minutes]

**Location:** `src/api/schemas/review.py` (NEW FILE)

- [ ] Create `src/api/schemas/review.py`
- [ ] Define schemas:

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional

class ReviewCompleteRequest(BaseModel):
    action: Literal["denied_appeal", "revised_estimate"]
    customer_note: str = Field(..., min_length=10, max_length=1000)
    internal_note: str = Field(..., min_length=10, max_length=2000)
    revised_estimate_total: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "action": "denied_appeal",
                "customer_note": "After careful review, the AI estimate is accurate...",
                "internal_note": "Reviewed all images. AI detection accurate...",
                "revised_estimate_total": None
            }
        }

class ReviewCompleteResponse(BaseModel):
    claim_id: int
    current_status: str
    next_status: str
    revised_estimate_total: Optional[float]
    event_id: int
```

**Acceptance Criteria:**
- Validation enforces note lengths
- Action restricted to valid values
- Example JSON included

---

### Task 2.3: Extend Damage Schemas (P1) [30 minutes]

**Location:** `src/api/schemas/damage.py` (EXISTING FILE)

- [ ] Open `src/api/schemas/damage.py` (create if missing)
- [ ] Add schemas for manual damage entry and cost updates:

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional

class DamageCreateRequest(BaseModel):
    estimate_type: Literal["human"] = "human"
    damage_part: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    severity: Literal["light", "moderate", "severe"]
    image_id: Optional[str] = None
    labor_hours: float = Field(..., gt=0, le=100)
    labor_rate: float = Field(..., ge=50, le=500)
    parts_cost: float = Field(..., ge=0, le=50000)
    adjustor_note: str = Field(..., min_length=10, max_length=1000)

class DamageUpdateRequest(BaseModel):
    labor_hours: Optional[float] = Field(None, gt=0, le=100)
    labor_rate: Optional[float] = Field(None, ge=50, le=500)
    parts_cost: Optional[float] = Field(None, ge=0, le=50000)
    adjustor_note: str = Field(..., min_length=10, max_length=1000)
```

**Acceptance Criteria:**
- Validation ranges enforce business rules
- Optional fields work correctly
- Error messages are clear

---

## Services Layer

### Task 3.1: Create AdjustorService (P0) [2 hours]

**Location:** `src/api/services/adjustor_service.py` (NEW FILE)

- [ ] Create `src/api/services/adjustor_service.py`
- [ ] Extend BaseService class
- [ ] Implement methods:
  - `get_pending_claims(adjustor_id, filters)` → Query claims with `human_review_pending` status
  - `get_statistics(adjustor_id)` → Calculate workload statistics
  - `assign_claim_to_adjustor(claim_id, adjustor_id)` (P2, optional)

**Key Method Implementation:**
```python
from src.api.services.base_service import BaseService
from src.api.models.claim import Claim
from src.api.models.customer import Customer
from src.api.models.vehicle import Vehicle
from src.api.constants import ClaimState
from sqlalchemy import func

class AdjustorService(BaseService):
    def get_pending_claims(self, adjustor_id: str, filters: dict):
        query = self.db.query(
            Claim, Customer, Vehicle
        ).join(
            Customer, Claim.customer_id == Customer.customer_id
        ).join(
            Vehicle, Claim.vin == Vehicle.vin
        ).filter(
            Claim.current_status == ClaimState.HUMAN_REVIEW_PENDING.value
        )
        
        # Apply search filter
        if filters.get('search'):
            search = f"%{filters['search']}%"
            query = query.filter(
                (Claim.claim_id.like(search)) |
                (Customer.fname.like(search)) |
                (Customer.lname.like(search)) |
                (Claim.vin.like(search))
            )
        
        # Apply sort
        if filters.get('sort') == 'oldest':
            query = query.order_by(Claim.fnol_date.asc())
        elif filters.get('sort') == 'highest_amount':
            query = query.order_by(Claim.claim_amount.desc())
        elif filters.get('sort') == 'customer_name':
            query = query.order_by(Customer.lname.asc())
        
        # Pagination
        page = filters.get('page', 1)
        limit = filters.get('limit', 20)
        query = query.offset((page - 1) * limit).limit(limit)
        
        return query.all()
    
    def get_statistics(self, adjustor_id: str):
        # Pending reviews
        pending = self.db.query(Claim).filter(
            Claim.current_status == ClaimState.HUMAN_REVIEW_PENDING.value
        ).count()
        
        # Completed today (events with adjustor actions)
        from datetime import date
        from src.api.models.claim_event import ClaimEvent
        from src.api.constants import ClaimAction, ActorType
        
        completed_today = self.db.query(ClaimEvent).filter(
            ClaimEvent.action.in_([
                ClaimAction.DENIED_APPEAL.value,
                ClaimAction.REVISED_ESTIMATE.value
            ]),
            ClaimEvent.action_by == ActorType.ADJUSTOR.value,
            ClaimEvent.event_date == date.today()
        ).count()
        
        return {
            "pending_reviews": pending,
            "completed_today": completed_today,
            "completed_this_week": 0,  # TODO: implement
            "average_review_time_minutes": 8,  # TODO: implement
            "total_reviews_all_time": 0  # TODO: implement
        }
```

**Acceptance Criteria:**
- Service returns correct data
- Filters and sorting work
- Pagination implemented
- Statistics calculated accurately

---

### Task 3.2: Extend ClaimService for Review Operations (P0) [2 hours]

**Location:** `src/api/services/claim_service.py` (EXISTING FILE)

- [ ] Open `src/api/services/claim_service.py`
- [ ] Add method `complete_review(claim_id, review_data)`:

```python
from src.api.models.claim_event import ClaimEvent
from src.api.constants import ClaimState, ClaimAction, ActorType
from datetime import date, datetime

def complete_review(self, claim_id: int, review_data: dict):
    # Get claim
    claim = self.get_claim(claim_id)
    
    # Validate state
    if claim.current_status != ClaimState.HUMAN_REVIEW_PENDING.value:
        raise ValueError(f"Claim must be in human_review_pending state, currently: {claim.current_status}")
    
    # Determine action
    action = review_data['action']
    customer_note = review_data['customer_note']
    internal_note = review_data['internal_note']
    
    # Update claim status
    claim.current_status = ClaimState.CUSTOMER_DECISION_PENDING.value
    
    # If revised estimate, update claim amount
    if action == 'revised_estimate' and review_data.get('revised_estimate_total'):
        claim.claim_amount = review_data['revised_estimate_total']
    
    # Create event
    event = ClaimEvent(
        claim_id=claim_id,
        event_date=date.today(),
        event_time=datetime.now().time(),
        status=ClaimState.CUSTOMER_DECISION_PENDING.value,
        action=action,
        action_by=ActorType.ADJUSTOR.value,
        action_by_identity=review_data.get('adjustor_id', 'UNKNOWN'),
        comments=f"Customer: {customer_note} | Internal: {internal_note}"
    )
    
    self.db.add(event)
    self.db.commit()
    
    return {
        "claim_id": claim_id,
        "current_status": claim.current_status,
        "next_status": ClaimState.CUSTOMER_DECISION_PENDING.value,
        "revised_estimate_total": claim.claim_amount,
        "event_id": event.event_id
    }
```

**Acceptance Criteria:**
- State transitions validated
- Events logged correctly
- Notes stored in structured format
- Claim amount updated if revised

---

### Task 3.3: Create DamageService (P1) [2 hours]

**Location:** `src/api/services/damage_service.py` (NEW FILE)

- [ ] Create `src/api/services/damage_service.py`
- [ ] Implement methods:
  - `create_manual_damage(claim_id, damage_data)` → Create human-added damage
  - `update_damage_costs(damage_id, update_data)` → Update existing damage costs
  - `recalculate_claim_total(claim_id)` → Sum all damage costs

**Key Methods:**
```python
from src.api.services.base_service import BaseService
from src.api.models.damage import Damage
from src.api.models.claim import Claim
from datetime import date, datetime

class DamageService(BaseService):
    def create_manual_damage(self, claim_id: int, damage_data: dict):
        # Generate estimate_id
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        estimate_id = f"{claim_id}_human_{timestamp}"
        
        # Calculate total cost
        total_cost = (damage_data['labor_hours'] * damage_data['labor_rate']) + damage_data['parts_cost']
        
        # Create damage record
        damage = Damage(
            claim_id=claim_id,
            estimate_id=estimate_id,
            estimate_type='human',
            image_id=damage_data.get('image_id'),
            damage_part=damage_data['damage_part'],
            severity=self._severity_to_decimal(damage_data['severity']),
            estimated_total_cost=total_cost,
            labor_hours=damage_data['labor_hours'],
            avg_labor_cost=damage_data['labor_rate'],
            estimated_parts_cost=damage_data['parts_cost'],
            adjustor_note=damage_data['adjustor_note'],
            generated_on_date=date.today(),
            generated_on_time=datetime.now().time()
        )
        
        self.db.add(damage)
        self.db.commit()
        self.db.refresh(damage)
        
        # Recalculate claim total
        self.recalculate_claim_total(claim_id)
        
        return damage
    
    def update_damage_costs(self, damage_id: int, update_data: dict):
        damage = self.db.query(Damage).filter(Damage.damage_id == damage_id).first()
        
        if not damage:
            raise ValueError(f"Damage {damage_id} not found")
        
        # Update provided fields
        if 'labor_hours' in update_data:
            damage.labor_hours = update_data['labor_hours']
        if 'labor_rate' in update_data:
            damage.avg_labor_cost = update_data['labor_rate']
        if 'parts_cost' in update_data:
            damage.estimated_parts_cost = update_data['parts_cost']
        
        # Recalculate total
        damage.estimated_total_cost = (damage.labor_hours * damage.avg_labor_cost) + damage.estimated_parts_cost
        
        # Append note
        if update_data.get('adjustor_note'):
            existing_note = damage.adjustor_note or ""
            damage.adjustor_note = f"{existing_note}\n[{datetime.now()}] {update_data['adjustor_note']}"
        
        self.db.commit()
        
        # Recalculate claim total
        self.recalculate_claim_total(damage.claim_id)
        
        return damage
    
    def recalculate_claim_total(self, claim_id: int):
        total = self.db.query(func.sum(Damage.estimated_total_cost)).filter(
            Damage.claim_id == claim_id
        ).scalar() or 0
        
        claim = self.db.query(Claim).filter(Claim.claim_id == claim_id).first()
        claim.claim_amount = total
        self.db.commit()
    
    def _severity_to_decimal(self, severity: str) -> float:
        mapping = {"light": 0.3, "moderate": 0.6, "severe": 0.9}
        return mapping.get(severity, 0.5)
```

**Acceptance Criteria:**
- Manual damages created with correct fields
- Cost calculations accurate
- Claim totals recalculated correctly
- Notes stored properly

---

## API Routers

### Task 4.1: Create Adjustor Router (P0) [2 hours]

**Location:** `src/api/routers/adjustors.py` (NEW FILE)

- [ ] Create `src/api/routers/adjustors.py`
- [ ] Register in `src/api/main.py` with prefix `/api/v1/adjustors`
- [ ] Implement endpoints:

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.api.database import get_db
from src.api.services.adjustor_service import AdjustorService
from src.api.schemas.adjustor import PendingClaimSummary, AdjustorStatistics
from typing import List, Optional

router = APIRouter()

@router.get("/{adjustor_id}/claims/pending")
def get_pending_claims(
    adjustor_id: str,
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query("oldest"),
    filter: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    service = AdjustorService(db)
    claims = service.get_pending_claims(adjustor_id, {
        'search': search,
        'sort': sort,
        'filter': filter,
        'page': page,
        'limit': limit
    })
    
    # Format response (map to PendingClaimSummary)
    return {"total": len(claims), "page": page, "limit": limit, "claims": claims}

@router.get("/{adjustor_id}/statistics", response_model=AdjustorStatistics)
def get_statistics(
    adjustor_id: str,
    db: Session = Depends(get_db)
):
    service = AdjustorService(db)
    return service.get_statistics(adjustor_id)
```

**Register in main.py:**
```python
from src.api.routers import adjustors
app.include_router(adjustors.router, prefix="/api/v1/adjustors", tags=["adjustors"])
```

**Acceptance Criteria:**
- Endpoints accessible via HTTP
- Query parameters work correctly
- Response format matches schemas

---

### Task 4.2: Extend Claims Router (P0) [2 hours]

**Location:** `src/api/routers/claims.py` (EXISTING FILE)

- [ ] Open `src/api/routers/claims.py`
- [ ] Add endpoints:

```python
from src.api.schemas.review import ReviewCompleteRequest, ReviewCompleteResponse
from src.api.schemas.damage import DamageCreateRequest, DamageUpdateRequest, DamageResponse
from src.api.services.damage_service import DamageService

@router.post("/{claim_id}/review/complete", response_model=ReviewCompleteResponse)
def complete_review(
    claim_id: int,
    request: ReviewCompleteRequest,
    db: Session = Depends(get_db)
):
    service = ClaimService(db)
    result = service.complete_review(claim_id, request.dict())
    return result

@router.post("/{claim_id}/damages", response_model=DamageResponse)
def create_manual_damage(
    claim_id: int,
    request: DamageCreateRequest,
    db: Session = Depends(get_db)
):
    service = DamageService(db)
    damage = service.create_manual_damage(claim_id, request.dict())
    return damage

@router.patch("/{claim_id}/damages/{damage_id}", response_model=DamageResponse)
def update_damage_costs(
    claim_id: int,
    damage_id: int,
    request: DamageUpdateRequest,
    db: Session = Depends(get_db)
):
    service = DamageService(db)
    damage = service.update_damage_costs(damage_id, request.dict())
    return damage
```

**Acceptance Criteria:**
- All endpoints callable
- Request validation works
- State transitions validated
- Errors handled properly

---

### Task 4.3: Update ERD Diagram (P1) [30 minutes]

**Location:** `specifications/diagrams/claim-database-erd.mmd` (EXISTING FILE)

- [ ] Open `claim-database-erd.mmd`
- [ ] Add adjustors entity:
```mermaid
adjustors {
    string adjustor_id PK "Adjustor identifier (ADJ-001)"
    string name "Adjustor full name"
    string email "Email address"
    string role "Senior Adjustor, Specialist, etc"
    string status "active or inactive"
}
```
- [ ] Add relationship: `adjustors ||--o{ claims : "reviews (optional)"`
- [ ] Verify damages entity shows `generated_on_date`, `generated_on_time`, `adjustor_note`

**Acceptance Criteria:**
- Diagram renders correctly
- All new entities and fields documented
- Relationships accurate

---

## Seed Data Updates

### Task 5.1: Add Adjustors to Seed Data (P0) [30 minutes]

**Location:** `scripts/seed_data.py` (EXISTING FILE)

- [ ] Open `scripts/seed_data.py`
- [ ] Import Adjustor model
- [ ] Add adjustor creation code:

```python
from src.api.models.adjustor import Adjustor

# Create Adjustors
print("👥 Creating adjustors...")
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
```

**Acceptance Criteria:**
- Seed script runs without errors
- Adjustors created in database
- Email domain is @acme-insurance.com

---

### Task 5.2: Create Test Claims in Human Review State (P0) [1 hour]

**Location:** `scripts/seed_data.py` (EXISTING FILE)

- [ ] Add 2-3 claims with `current_status = "human_review_pending"`
- [ ] Add corresponding events showing why claims are in human review:
  - Customer appealed AI estimate
  - Low AI confidence
  - No damages detected

```python
# Create claims in human_review_pending status
print("📝 Creating claims for human review...")
review_claims = [
    Claim(
        claim_id=2001,
        customer_id=101,
        vin="1FTFW1ET5DFC12345",
        policy_number="POL-2026-002",
        fnol_date=date(2026, 5, 4),
        fnol_time=time(10, 0, 0),
        date_of_damage=date(2026, 5, 3),
        is_drivable=True,
        current_status=ClaimState.HUMAN_REVIEW_PENDING.value,
        claim_closed=False
    ),
]

for claim in review_claims:
    db.add(claim)

db.commit()

# Add events showing customer appealed
events = [
    ClaimEvent(
        claim_id=2001,
        event_date=date(2026, 5, 4),
        event_time=time(10, 30, 0),
        status=ClaimState.LOSS_APPEALED.value,
        action=ClaimAction.APPEAL_ESTIMATE.value,
        action_by=ActorType.CUSTOMER.value,
        action_by_identity="customer_101",
        comments="Customer appealed AI estimate"
    ),
    ClaimEvent(
        claim_id=2001,
        event_date=date(2026, 5, 4),
        event_time=time(10, 31, 0),
        status=ClaimState.HUMAN_REVIEW_PENDING.value,
        action=ClaimAction.FLAG_FOR_HUMAN_REVIEW.value,
        action_by=ActorType.AI_AGENT.value,
        action_by_identity="ai_agent",
        comments="Routed to human review due to customer appeal"
    ),
]

for event in events:
    db.add(event)

db.commit()
```

**Acceptance Criteria:**
- Claims visible in pending queue API
- Events show clear reason for review
- Different test scenarios created

---

## Testing

### Task 6.1: Test API Endpoints (P0) [2 hours]

- [ ] Test GET /adjustors/{id}/claims/pending with various filters
- [ ] Test GET /adjustors/{id}/statistics
- [ ] Test POST /claims/{id}/review/complete with denied_appeal
- [ ] Test POST /claims/{id}/review/complete with revised_estimate
- [ ] Test POST /claims/{id}/damages (create manual damage)
- [ ] Test PATCH /claims/{id}/damages/{damage_id} (update costs)
- [ ] Verify state transitions work correctly
- [ ] Verify claim totals recalculate
- [ ] Verify events logged properly

**Test with curl:**
```bash
# Get pending claims
curl http://localhost:8000/api/v1/adjustors/ADJ-001/claims/pending

# Get statistics
curl http://localhost:8000/api/v1/adjustors/ADJ-001/statistics

# Complete review
curl -X POST http://localhost:8000/api/v1/claims/2001/review/complete \
  -H "Content-Type: application/json" \
  -d '{
    "action": "denied_appeal",
    "customer_note": "After review, the estimate is accurate.",
    "internal_note": "AI detection verified. No changes needed."
  }'
```

**Acceptance Criteria:**
- All endpoints return expected responses
- No 500 errors
- Validation works correctly
- Database updated properly

---

## Additional API Requirements for Customer Portal Integration

### Task 7.1: List All Adjustors with Workload (P0) [1 hour]

**NEW REQUIREMENT:** Customer Portal needs to auto-assign claims to adjustors with shortest queue when claim status becomes `human_review_pending`.

**Location:** `src/api/routers/adjustors.py` (EXTEND EXISTING FILE)

- [ ] Add new endpoint: `GET /api/v1/adjustors`
- [ ] Returns list of all adjustors with their current workload

**Implementation:**

```python
@router.get("", response_model=List[AdjustorWithWorkload])
def list_adjustors(
    status_filter: Optional[str] = Query(None, description="Filter by status: active, inactive"),
    db: Session = Depends(get_db)
):
    """
    Get all adjustors with their current workload statistics.
    
    Used by Customer Portal to auto-assign claims to adjustor with shortest queue.
    """
    from src.api.models.adjustor import Adjustor
    
    query = db.query(Adjustor)
    
    # Apply status filter
    if status_filter:
        query = query.filter(Adjustor.status == status_filter)
    
    adjustors = query.all()
    
    # Enhance each adjustor with workload stats
    service = AdjustorService(db)
    result = []
    
    for adjustor in adjustors:
        stats = service.get_statistics(adjustor.adjustor_id)
        result.append({
            "adjustor_id": adjustor.adjustor_id,
            "name": adjustor.name,
            "email": adjustor.email,
            "role": adjustor.role,
            "status": adjustor.status,
            "pending_reviews": stats["pending_reviews"],
            "completed_today": stats["completed_today"],
            "completed_this_week": stats["completed_this_week"]
        })
    
    return result
```

**New Schema Required:**

```python
# src/api/schemas/adjustor.py
class AdjustorWithWorkload(BaseModel):
    """Adjustor information with workload statistics"""
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
```

**Acceptance Criteria:**
- Returns all adjustors (or filtered by status)
- Includes current pending_reviews count for each adjustor
- Response time < 500ms
- Used by Customer Portal for load balancing

---

### Task 7.2: Assign Claim to Adjustor (P1) [2 hours]

**Location:** `src/api/routers/adjustors.py` (EXTEND EXISTING FILE)

- [ ] Add new endpoint: `POST /api/v1/adjustors/{adjustor_id}/claims/{claim_id}/assign`
- [ ] Assigns specific claim to specific adjustor

**Implementation:**

```python
from src.api.schemas.common import SuccessResponse

@router.post("/{adjustor_id}/claims/{claim_id}/assign", response_model=SuccessResponse)
def assign_claim(
    adjustor_id: str,
    claim_id: int,
    db: Session = Depends(get_db)
):
    """
    Assign a claim to a specific adjustor.
    
    Used by Customer Portal auto-assignment logic when claim enters human review.
    """
    from src.api.models.claim import Claim
    from src.api.models.adjustor import Adjustor
    from src.api.models.claim_event import ClaimEvent
    from src.api.constants import ClaimAction, ActorType
    from datetime import date, datetime
    
    # Verify adjustor exists and is active
    adjustor = db.query(Adjustor).filter(
        Adjustor.adjustor_id == adjustor_id,
        Adjustor.status == 'active'
    ).first()
    
    if not adjustor:
        raise HTTPException(
            status_code=404,
            detail=f"Active adjustor {adjustor_id} not found"
        )
    
    # Verify claim exists and is in human_review_pending status
    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    
    if not claim:
        raise HTTPException(
            status_code=404,
            detail=f"Claim {claim_id} not found"
        )
    
    if claim.current_status != ClaimState.HUMAN_REVIEW_PENDING.value:
        raise HTTPException(
            status_code=400,
            detail=f"Claim must be in human_review_pending status, currently: {claim.current_status}"
        )
    
    # TODO (P2): Add assigned_adjustor_id field to Claim model
    # For now, log assignment in claim event
    
    # Create assignment event
    event = ClaimEvent(
        claim_id=claim_id,
        event_date=date.today(),
        event_time=datetime.now().time(),
        status=claim.current_status,
        action="assign_to_adjustor",  # Add to ClaimAction enum if needed
        action_by=ActorType.AI_AGENT.value,
        action_by_identity="auto_assignment_system",
        comments=f"Claim assigned to adjustor {adjustor.name} ({adjustor_id})"
    )
    
    db.add(event)
    db.commit()
    
    return {
        "success": True,
        "message": f"Claim {claim_id} assigned to {adjustor.name}",
        "data": {
            "claim_id": claim_id,
            "adjustor_id": adjustor_id,
            "adjustor_name": adjustor.name,
            "assigned_at": datetime.now().isoformat()
        }
    }
```

**Acceptance Criteria:**
- Only allows assignment if claim is in `human_review_pending` status
- Only allows assignment to active adjustors
- Logs assignment event in `claims_events` table
- Returns confirmation with adjustor name
- Handles errors gracefully (404 for not found, 400 for invalid state)

**Future Enhancement (P2):**
- Add `assigned_adjustor_id` field to Claim model
- Update field during assignment
- Add index on `assigned_adjustor_id` for faster queries

---

### Task 7.3: Update Constants for Assignment Action (P2) [15 minutes]

**Location:** `src/api/constants.py` (EXTEND EXISTING FILE)

- [ ] Add new action to `ClaimAction` enum

```python
class ClaimAction(str, Enum):
    # ... existing actions ...
    
    # System actions
    ASSIGN_TO_ADJUSTOR = "assign_to_adjustor"  # NEW
```

**Acceptance Criteria:**
- Action available for event logging
- Consistent with existing action naming

---

### Task 7.4: Update API Documentation (P1) [30 minutes]

**Location:** `specifications/API-SPECIFICATIONS.md` (UPDATE EXISTING FILE)

- [ ] Document `GET /api/v1/adjustors` endpoint
- [ ] Document `POST /api/v1/adjustors/{id}/claims/{id}/assign` endpoint
- [ ] Add request/response examples
- [ ] Update API endpoint summary table

---

## Integration Flow Summary

**Customer Portal → API Backend:**

1. Customer uploads images → AI detects low confidence OR customer appeals estimate
2. Claim status becomes `human_review_pending`
3. Customer Portal calls `GET /api/v1/adjustors?status_filter=active`
4. Customer Portal selects adjustor with minimum `pending_reviews`
5. Customer Portal calls `POST /api/v1/adjustors/{id}/claims/{claim_id}/assign`
6. Assignment logged in `claims_events` table
7. Adjustor sees claim in their review queue

**Benefits:**
- Automatic load balancing across adjustors
- No manual assignment needed
- Faster claim processing
- Audit trail of assignments

---

## Summary

**Total Estimated Time:** 27.75 hours

| Phase | Tasks | Hours |
|-------|-------|-------|
| Database Schema | 3 tasks | 2.5h |
| API Schemas | 3 tasks | 1.5h |
| Services Layer | 3 tasks | 6h |
| API Routers | 3 tasks | 4.5h |
| Seed Data | 2 tasks | 1.5h |
| Testing | 1 task | 2h |
| Documentation | ERD update | 0.5h |
| **Customer Portal Integration** | **4 tasks** | **3.75h** |
| - List adjustors API | Task 7.1 | 1h |
| - Assign claim API | Task 7.2 | 2h |
| - Update constants | Task 7.3 | 0.25h |
| - API documentation | Task 7.4 | 0.5h |
| **Total** | | **27.75h** |

**Dependencies:**
- Database changes must be completed before services
- Services must be completed before routers
- Seed data should be updated last

**Integration with Frontend:**
- Frontend will consume these APIs
- See `UI-ADJUSTOR-PORTAL-TODOS.md` for frontend tasks
- Frontend development can start after Task 4.2 is complete

---

**End of API Backend TODOs**
