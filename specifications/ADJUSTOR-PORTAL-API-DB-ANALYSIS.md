# Adjustor Portal API & Database Analysis
## Gap Analysis and Implementation Requirements

**Date:** 2026-05-05  
**Analyst:** Claude Code  
**Status:** Complete  
**Purpose:** Verify all required APIs exist and database schema supports adjustor portal functionality

---

## Executive Summary

**Overall Status:** ✅ **Database schema is 95% ready. Need to create 5 new API endpoints and 1 new database table.**

### Quick Statistics

- **Existing APIs Reusable:** 3 of 8 (37.5%)
- **New APIs Required:** 5 endpoints
- **Database Tables to Create:** 1 (adjustors)
- **Database Fields to Add:** 3 fields to damages table (2 critical, 1 optional)
- **Schema Mismatches Found:** 1 (damages table missing fields from ERD)
- **State Machine Coverage:** 100% (all transitions already defined)
- **Constants/Enums Coverage:** 100% (all required enums exist)

---

## 1. API Requirements Analysis

### 1.1 Required APIs for Adjustor Portal

| API Endpoint | Method | Status | Location | Priority |
|--------------|--------|--------|----------|----------|
| `/adjustors/{adjustor_id}/claims/pending` | GET | ❌ **MISSING** | Need new router | P0 |
| `/adjustors/{adjustor_id}/statistics` | GET | ❌ **MISSING** | Need new router | P0 |
| `/claims/{claim_id}/review/complete` | POST | ❌ **MISSING** | Extend claims.py | P0 |
| `/claims/{claim_id}/damages` | POST | ❌ **MISSING** | Extend claims.py | P0 |
| `/claims/{claim_id}/damages/{damage_id}` | PATCH | ❌ **MISSING** | Extend claims.py | P0 |
| `/customers/{customer_id}/claims/{claim_id}` | GET | ✅ **EXISTS** | customers.py | - |
| `/customers/{customer_id}/claims/{claim_id}/events` | GET | ✅ **EXISTS** | customers.py | - |
| `/customers/{customer_id}/claims/{claim_id}/images` | GET | ✅ **EXISTS** | customers.py | - |

**Summary:** 
- ✅ 3 existing APIs can be reused (claim detail, events, images)
- ❌ 5 new APIs need to be created

---

### 1.2 Detailed API Specifications

#### 1.2.1 GET /adjustors/{adjustor_id}/claims/pending

**Purpose:** Get list of claims in `human_review_pending` status

**Query Parameters:**
- `search` (string, optional) — Search by claim ID, customer name, or VIN
- `sort` (string, optional) — 'oldest' | 'highest_amount' | 'customer_name'
- `filter` (string, optional) — 'appeals' | 'low_confidence' | 'no_damage'
- `page` (int, default: 1) — Pagination page number
- `limit` (int, default: 20) — Results per page

**Response Schema:**
```json
{
  "total": 12,
  "page": 1,
  "limit": 20,
  "claims": [
    {
      "claim_id": 1001,
      "customer_id": 101,
      "customer_name": "Jane Smith",
      "vin": "1FTFW1ET5DFC12345",
      "vehicle": "2022 Honda Accord Silver",
      "policy_number": "POL-2026-001",
      "fnol_date": "2026-05-01",
      "ai_estimate_total": 1234.00,
      "reason_for_review": "customer_appeal",
      "time_in_queue": "2h",
      "current_status": "human_review_pending"
    }
  ]
}
```

**Database Query:**
```sql
SELECT c.*, cust.fname, cust.lname, v.year, v.make, v.model, v.color
FROM claims c
JOIN customers cust ON c.customer_id = cust.customer_id
JOIN vehicles v ON c.vin = v.vin
WHERE c.current_status = 'human_review_pending'
ORDER BY c.fnol_date ASC
LIMIT 20 OFFSET 0;
```

**Implementation Location:** New router `src/api/routers/adjustors.py`

---

#### 1.2.2 GET /adjustors/{adjustor_id}/statistics

**Purpose:** Get adjustor workload statistics

**Response Schema:**
```json
{
  "pending_reviews": 12,
  "completed_today": 5,
  "completed_this_week": 23,
  "average_review_time_minutes": 8,
  "total_reviews_all_time": 456
}
```

**Database Queries:**
```sql
-- Pending reviews
SELECT COUNT(*) FROM claims WHERE current_status = 'human_review_pending';

-- Completed today
SELECT COUNT(*) FROM claims_events 
WHERE action IN ('denied_appeal', 'revised_estimate') 
  AND event_date = CURRENT_DATE
  AND action_by = 'adjustor';

-- Average review time (from human_review_pending to human_review_completed)
SELECT AVG(time_diff_minutes) FROM (
  SELECT 
    EXTRACT(EPOCH FROM (e2.event_date + e2.event_time - e1.event_date - e1.event_time)) / 60 AS time_diff_minutes
  FROM claims_events e1
  JOIN claims_events e2 ON e1.claim_id = e2.claim_id
  WHERE e1.status = 'human_review_pending' 
    AND e2.status = 'human_review_completed'
) AS subquery;
```

**Implementation Location:** New router `src/api/routers/adjustors.py`

---

#### 1.2.3 POST /claims/{claim_id}/review/complete

**Purpose:** Complete adjustor review and return claim to customer

**Request Schema:**
```json
{
  "action": "denied_appeal" | "revised_estimate",
  "customer_note": "string (required, 10-1000 chars)",
  "internal_note": "string (required, 10-2000 chars)",
  "revised_estimate_total": 2584.00  // required if action='revised_estimate'
}
```

**Response Schema:**
```json
{
  "claim_id": 1001,
  "current_status": "human_review_completed",
  "next_status": "customer_decision_pending",
  "revised_estimate_total": 2584.00,
  "event_id": 12345
}
```

**Business Logic:**
1. Validate claim is in `human_review_pending` state
2. If action = `denied_appeal`:
   - Record event with `ClaimAction.DENIED_APPEAL`
   - Status: `human_review_pending` → `human_review_completed` → `customer_decision_pending`
   - Keep original AI estimate
3. If action = `revised_estimate`:
   - Record event with `ClaimAction.REVISED_ESTIMATE`
   - Update `claim.active_estimate_id` to latest human estimate
   - Update `claim.claim_amount` to revised total
4. Store notes in `event.comments` as: `"Customer: {note} | Internal: {note}"`
5. Create event record in claims_events table

**Implementation Location:** Extend `src/api/routers/claims.py`

---

#### 1.2.4 POST /claims/{claim_id}/damages

**Purpose:** Add manual damage (human-detected, missed by AI)

**Request Schema:**
```json
{
  "estimate_type": "human",
  "damage_part": "scratch-front-door",
  "description": "string (required)",
  "severity": "light" | "moderate" | "severe",
  "image_id": "IMG_003.jpg" (optional),
  "labor_hours": 1.5,
  "labor_rate": 156.00,
  "parts_cost": 200.00,
  "adjustor_note": "string (required)"
}
```

**Response Schema:**
```json
{
  "damage_id": 4,
  "claim_id": 1001,
  "estimate_id": "1001_human_20260505_143022",
  "estimate_type": "human",
  "damage_part": "scratch-front-door",
  "severity": 0.3,
  "labor_hours": 1.5,
  "avg_labor_cost": 156.00,
  "estimated_parts_cost": 200.00,
  "estimated_total_cost": 434.00,
  "generated_on_date": "2026-05-05",
  "generated_on_time": "14:30:22"
}
```

**Business Logic:**
1. Validate claim is in `human_review_pending` state
2. Generate `estimate_id` = `{claim_id}_human_{timestamp}`
3. Create Damage record with `estimate_type='human'`
4. Calculate total: (labor_hours × labor_rate) + parts_cost
5. Set `generated_on_date` and `generated_on_time` to current timestamp
6. Store adjustor_note in `adjustor_note` field
7. Update `claim.active_estimate_id` if this is first human damage
8. Recalculate `claim.claim_amount` by summing all damage totals

**Implementation Location:** Extend `src/api/routers/claims.py`

---

#### 1.2.5 PATCH /claims/{claim_id}/damages/{damage_id}

**Purpose:** Adjust costs for existing damage

**Request Schema:**
```json
{
  "labor_hours": 3.0 (optional),
  "labor_rate": 156.00 (optional),
  "parts_cost": 650.00 (optional),
  "adjustor_note": "string (required if any cost changes)"
}
```

**Response Schema:**
```json
{
  "damage_id": 1,
  "claim_id": 1001,
  "labor_hours": 3.0,
  "avg_labor_cost": 156.00,
  "estimated_parts_cost": 650.00,
  "estimated_total_cost": 1118.00,
  "updated_at": "2026-05-05T14:35:00Z"
}
```

**Business Logic:**
1. Validate claim is in `human_review_pending` state
2. Validate damage exists and belongs to claim
3. Update only provided cost fields
4. Recalculate `estimated_total_cost`: (labor_hours × labor_rate) + parts_cost
5. Append adjustor_note (don't overwrite, append with timestamp)
6. Recalculate `claim.claim_amount` by summing all damage totals

**Implementation Location:** Extend `src/api/routers/claims.py`

---

## 2. Database Schema Analysis

### 2.1 Existing Tables (Sufficient)

#### ✅ claims table
**Status:** Fully supports adjustor workflow

| Field | Type | Purpose | Status |
|-------|------|---------|--------|
| `claim_id` | int PK | Unique claim identifier | ✅ EXISTS |
| `customer_id` | int FK | References customers | ✅ EXISTS |
| `vin` | string FK | References vehicles | ✅ EXISTS |
| `policy_number` | string FK | References policies | ✅ EXISTS |
| `fnol_date`, `fnol_time` | date, time | First Notice of Loss timestamp | ✅ EXISTS |
| `date_of_damage` | date | When damage occurred | ✅ EXISTS |
| `is_drivable` | boolean | Vehicle drivability | ✅ EXISTS |
| `current_status` | string | Claim state (supports `human_review_pending`) | ✅ EXISTS |
| `claim_closed`, `claim_closed_date` | boolean, date | Closure tracking | ✅ EXISTS |
| `ai_estimate_accepted` | boolean | Customer acceptance flag | ✅ EXISTS |
| `routed_to_traditional` | boolean | Traditional routing flag | ✅ EXISTS |
| `reason_routing_to_traditional` | string | Reason for traditional | ✅ EXISTS |
| `active_estimate_id` | string | Current estimate (can store human estimate) | ✅ EXISTS |
| `claim_amount` | decimal | Approved amount (can update with revised) | ✅ EXISTS |
| `actual_claim_amount` | decimal | Actual repair cost | ✅ EXISTS |

**Optional Enhancements (P2):**
- `assigned_adjustor_id` (string FK to adjustors) — For claim assignment feature
- `review_completed_date`, `review_completed_time` (date, time) — Track review completion

---

#### ✅ damages table
**Status:** Mostly sufficient, **3 fields need to be added**

| Field | Type | Purpose | Status |
|-------|------|---------|--------|
| `damage_id` | int PK | Unique damage identifier | ✅ EXISTS |
| `claim_id` | int FK | References claims | ✅ EXISTS |
| `estimate_id` | string | Estimate identifier (supports `{claim_id}_human_{ts}`) | ✅ EXISTS |
| `estimate_type` | string | 'ai' or 'human' | ✅ EXISTS |
| `image_id` | string FK | References image (nullable for manual) | ✅ EXISTS |
| `damage_part` | string | Part name | ✅ EXISTS |
| `severity` | decimal | Severity score (0.0-1.0) | ✅ EXISTS |
| `estimated_total_cost` | decimal | Total repair cost | ✅ EXISTS |
| `labor_hours` | decimal | Labor hours estimate | ✅ EXISTS |
| `avg_labor_cost` | decimal | Labor rate ($/hour) | ✅ EXISTS |
| `estimated_parts_cost` | decimal | Parts cost | ✅ EXISTS |
| `damage_class`, `damage_confidence` | int, decimal | YOLO fields (nullable, OK for human) | ✅ EXISTS |
| `bounding_box_*` | int | Bounding box coords (nullable, OK for human) | ✅ EXISTS |
| `reasoning` | text | AI reasoning (can temporarily store adjustor notes) | ✅ EXISTS |
| **`generated_on_date`** | date | **MISSING** — When damage was created | ❌ **ADD** |
| **`generated_on_time`** | time | **MISSING** — When damage was created | ❌ **ADD** |
| **`adjustor_note`** | text | **MISSING** — Adjustor reasoning for changes | ⚠️ **ADD (P1)** |

**CRITICAL ISSUE:** The ERD diagram (`claim-database-erd.mmd`) includes `generated_on_date` and `generated_on_time` fields, but the SQLAlchemy model (`src/api/models/damage.py`) is missing them. This is a schema mismatch that must be fixed!

---

#### ✅ claims_events table
**Status:** Fully supports adjustor actions

| Field | Type | Purpose | Status |
|-------|------|---------|--------|
| `claim_id` | int FK | References claim | ✅ EXISTS |
| `event_id` | int | Event sequence number | ✅ EXISTS |
| `event_date`, `event_time` | date, time | When event occurred | ✅ EXISTS |
| `status` | string | Claim status at event time | ✅ EXISTS |
| `action` | string | Action taken (supports `denied_appeal`, `revised_estimate`) | ✅ EXISTS |
| `action_by` | string | Actor type (supports 'adjustor') | ✅ EXISTS |
| `action_by_identity` | string | Actor ID (can store "ADJ-001") | ✅ EXISTS |
| `comments` | text | Free text (can store structured notes) | ✅ EXISTS |

**Implementation Note:** Store customer and internal notes as:
```
"Customer: <customer_note> | Internal: <internal_note>"
```

---

#### ✅ Other Tables (Fully Sufficient)

- ✅ **customers** — All fields present (customer_id, fname, lname, email, phone, address)
- ✅ **vehicles** — All fields present (vin, customer_id, year, make, model, color)
- ✅ **policies** — All fields present (policy_number, customer_id, dates, limits, premium)
- ✅ **claim_images** — All fields present (image_id, claim_id, uploaded_at, uploaded_by)

---

### 2.2 Missing Tables

#### ❌ adjustors table
**Status:** **MUST CREATE** (P0)

**Required Schema:**
```sql
CREATE TABLE adjustors (
    adjustor_id VARCHAR(20) PRIMARY KEY,  -- e.g., "ADJ-001"
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(100),  -- e.g., "Senior Adjustor"
    status VARCHAR(20) NOT NULL DEFAULT 'active'  -- 'active' or 'inactive'
);
```

**SQLAlchemy Model:**
```python
class Adjustor(Base):
    __tablename__ = "adjustors"
    
    adjustor_id = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(String(100), nullable=True)
    status = Column(String(20), nullable=False, default='active')
    
    # Optional relationship (P2)
    # assigned_claims = relationship("Claim", back_populates="adjustor")
```

**Seed Data:**
```python
adjustors = [
    Adjustor(adjustor_id="ADJ-001", name="Sarah Chen", email="sarah.chen@acme-insurance.com", role="Senior Adjustor", status="active"),
    Adjustor(adjustor_id="ADJ-002", name="Michael Torres", email="michael.torres@acme-insurance.com", role="Collision Specialist", status="active"),
    Adjustor(adjustor_id="ADJ-003", name="Emily Watson", email="emily.watson@acme-insurance.com", role="Claims Supervisor", status="active"),
]
```

---

## 3. Constants & Enums Analysis

### 3.1 Existing Constants (Fully Sufficient)

#### ✅ ClaimState Enum (`src/api/constants.py`)
```python
class ClaimState(str, Enum):
    DRAFT = "draft"
    FNOL = "FNOL"
    IMAGE_UPLOADED = "image_uploaded"
    LOSS_ESTIMATED_AI = "loss_estimated_ai"
    CUSTOMER_DECISION_PENDING = "customer_decision_pending"
    LOSS_APPROVED = "loss_approved"
    LOSS_APPEALED = "loss_appealed"
    HUMAN_REVIEW_PENDING = "human_review_pending"  # ✅ Required
    HUMAN_REVIEW_COMPLETED = "human_review_completed"  # ✅ Required
    SENT_FOR_PAYMENT = "sent_for_payment"
    CLAIM_PAID = "claim_paid"
    ROUTED_TO_TRADITIONAL = "routed_to_traditional"
    TRADITIONAL_PROCESSING_ACTIVE = "traditional_processing_active"
    CLAIM_CLOSED = "claim_closed"
```

**Status:** ✅ All required states exist

---

#### ✅ ClaimAction Enum (`src/api/constants.py`)
```python
class ClaimAction(str, Enum):
    # Customer actions
    CREATE_CLAIM = "create_claim"
    SUBMIT_CLAIM = "submit_claim"
    UPLOAD_DAMAGE_PHOTOS = "upload_damage_photos"
    IMAGE_DELETED = "image_deleted"
    CLAIM_DELETED = "claim_deleted"
    ACCEPT_ESTIMATE = "accept_estimate"
    APPEAL_ESTIMATE = "appeal_estimate"

    # AI agent actions
    GENERATE_ESTIMATE = "generate_estimate"
    PRESENT_ESTIMATE_TO_CUSTOMER = "present_estimate_to_customer"
    ASSESS_FRAUD_RISK = "assess_fraud_risk"
    CALCULATE_CONFIDENCE_SCORE = "calculate_confidence_score"
    FLAG_FOR_HUMAN_REVIEW = "flag_for_human_review"

    # Adjustor actions
    DENIED_APPEAL = "denied_appeal"  # ✅ Required
    APPROVED_APPEAL = "approved_appeal"
    REVISED_ESTIMATE = "revised_estimate"  # ✅ Required
    ROUTE_TO_TRADITIONAL = "route_to_traditional"

    # Admin actions
    INITIATE_PAYMENT = "initiate_payment"
    PAYMENT_SENT = "payment_sent"
    CLOSE_CLAIM = "close_claim"
```

**Status:** ✅ All required actions exist

---

#### ✅ ActorType Enum (`src/api/constants.py`)
```python
class ActorType(str, Enum):
    CUSTOMER = "customer"
    AI_AGENT = "AI agent"
    ADJUSTOR = "adjustor"  # ✅ Required
    ADMIN = "admin"
```

**Status:** ✅ ADJUSTOR actor type exists

---

#### ✅ EstimateType Enum (`src/api/constants.py`)
```python
class EstimateType(str, Enum):
    AI = "ai"  # ✅ Required
    HUMAN = "human"  # ✅ Required
```

**Status:** ✅ Both estimate types exist

---

### 3.2 State Machine Validation

**Required State Transitions:**

| From State | Action | To State | Defined in VALID_TRANSITIONS? |
|------------|--------|----------|-------------------------------|
| `human_review_pending` | `DENIED_APPEAL` | `human_review_completed` | ✅ YES |
| `human_review_pending` | `REVISED_ESTIMATE` | `human_review_completed` | ✅ YES |
| `human_review_completed` | (auto) | `customer_decision_pending` | ✅ YES |

**Validation from `constants.py`:**
```python
VALID_TRANSITIONS = {
    ClaimState.HUMAN_REVIEW_PENDING: [ClaimState.HUMAN_REVIEW_COMPLETED],
    ClaimState.HUMAN_REVIEW_COMPLETED: [
        ClaimState.CUSTOMER_DECISION_PENDING,
        ClaimState.ROUTED_TO_TRADITIONAL
    ],
    # ...
}
```

**Status:** ✅ All required transitions are defined correctly!

---

## 4. Services & Infrastructure Analysis

### 4.1 Existing Services (Reusable)

| Service | Location | Reusable For | Status |
|---------|----------|--------------|--------|
| `ClaimService` | `src/api/services/claim_service.py` | Base claim operations, can extend with `complete_review()` | ✅ EXTEND |
| `EventService` | `src/api/services/event_service.py` | Query claim events, get statistics | ✅ REUSE |
| `EventLogger` | `src/api/services/event_logger.py` | `@log_event()` decorator for adjustor actions | ✅ REUSE |
| `StateMachine` | `src/api/services/state_machine.py` | Validate state transitions | ✅ REUSE |
| `ImageService` | `src/api/services/image_service.py` | Image upload/retrieval | ✅ REUSE |
| `CustomerService` | `src/api/services/customer_service.py` | Get customer details | ✅ REUSE |
| `PolicyService` | `src/api/services/policy_service.py` | Get policy details | ✅ REUSE |

---

### 4.2 Missing Services (Must Create)

| Service | Purpose | Priority |
|---------|---------|----------|
| `AdjustorService` | Query pending claims, calculate statistics, assign claims (P2) | P0 |
| `DamageService` | Create manual damages, update damage costs | P0 |

**AdjustorService Methods:**
- `get_pending_claims(adjustor_id, filters)` → List of claims in `human_review_pending`
- `get_statistics(adjustor_id)` → Workload statistics
- `assign_claim_to_adjustor(claim_id, adjustor_id)` (P2) → For claim assignment

**DamageService Methods:**
- `create_manual_damage(claim_id, damage_data)` → Create human-added damage
- `update_damage_costs(damage_id, cost_data)` → Update existing damage costs
- `recalculate_claim_total(claim_id)` → Sum all damage costs and update claim amount

---

## 5. Implementation Checklist

### 5.1 Database Changes (Priority Order)

**P0 (Critical):**
- [ ] Create `adjustors` table with SQLAlchemy model
- [ ] Add `generated_on_date` (Date) to damages table
- [ ] Add `generated_on_time` (Time) to damages table
- [ ] Create Alembic migration for above changes
- [ ] Update seed_data.py to create 3 adjustors
- [ ] Update seed_data.py to set generated_on_date/time for all damages

**P1 (High Priority):**
- [ ] Add `adjustor_note` (Text, nullable) to damages table
- [ ] Create Alembic migration

**P2 (Future Enhancement):**
- [ ] Add `assigned_adjustor_id` (String FK, nullable) to claims table
- [ ] Add `review_completed_date` (Date, nullable) to claims table
- [ ] Add `review_completed_time` (Time, nullable) to claims table
- [ ] Add `adjustor_id` (String FK, nullable) to damages table
- [ ] Create Alembic migrations

---

### 5.2 Backend API Changes (Priority Order)

**P0 (Critical):**
- [ ] Create `src/api/routers/adjustors.py` with 2 endpoints
- [ ] Extend `src/api/routers/claims.py` with 3 endpoints
- [ ] Create `src/api/services/adjustor_service.py`
- [ ] Create `src/api/services/damage_service.py`
- [ ] Create `src/api/schemas/adjustor.py` (AdjustorResponse, PendingClaimSummary, AdjustorStatistics)
- [ ] Create `src/api/schemas/review.py` (ReviewCompleteRequest, ReviewCompleteResponse)
- [ ] Extend `src/api/schemas/damage.py` (DamageCreateRequest, DamageUpdateRequest)
- [ ] Register adjustors router in `src/api/main.py`
- [ ] Add method `ClaimService.complete_review()` to handle review completion
- [ ] Add error handling for invalid state transitions

**P1 (High Priority):**
- [ ] Add comprehensive logging for all adjustor actions
- [ ] Add validation for cost ranges (labor_hours: 0.1-100, labor_rate: $50-$500, etc.)
- [ ] Add business rule enforcement (e.g., warn if cost change > 100%)

**P2 (Future Enhancement):**
- [ ] Add claim assignment logic in AdjustorService
- [ ] Add adjustor authentication/authorization middleware
- [ ] Add rate limiting for API endpoints

---

### 5.3 Documentation Updates

**P1:**
- [ ] Update ERD diagram (`claim-database-erd.mmd`) to include adjustors table
- [ ] Update API documentation with new endpoints
- [ ] Update state machine diagram if needed

---

## 6. Risk Assessment

### 6.1 High Risk Items

| Risk | Impact | Mitigation |
|------|--------|------------|
| Schema mismatch (damages table missing fields from ERD) | **HIGH** | Fix immediately in Task 1.3 |
| State transition logic complexity | **MEDIUM** | Existing StateMachine service handles this, just need to call correctly |
| Cost recalculation errors | **MEDIUM** | Write unit tests for DamageService calculations |
| Note storage format inconsistency | **LOW** | Use structured format: "Customer: ... \| Internal: ..." |

### 6.2 Low Risk Items

| Item | Reason |
|------|--------|
| State machine transitions | Already defined and validated |
| Constants/enums | All exist, no changes needed |
| Existing API reuse | Customer endpoints already proven and tested |
| Database schema capacity | Existing fields support all required data |

---

## 7. Timeline Estimate

Based on the gap analysis:

| Phase | Tasks | Estimated Hours |
|-------|-------|-----------------|
| Database schema changes | Create adjustors table, add 3 fields to damages | 3h |
| Pydantic schemas | Create 3 new schema files | 2h |
| Services layer | Create AdjustorService, DamageService, extend ClaimService | 6h |
| API routers | Create adjustors router, extend claims router (5 endpoints) | 8h |
| Seed data | Add adjustors, test claims | 2h |
| Testing | Test all endpoints, state transitions | 3h |
| **Total Backend** | | **24h** |

**Frontend:** Already estimated at 58 hours in TODOs document

**Grand Total:** ~82 hours (10 days at 8h/day)

---

## 8. Conclusion

**Readiness Assessment:** ✅ **95% Ready**

**Strengths:**
- State machine fully defined with correct transitions
- All required constants/enums exist
- Database schema is mostly complete
- Existing services (ClaimService, EventService, StateMachine) are reusable
- 3 of 8 required APIs already exist

**Gaps to Address:**
1. Create adjustors table (trivial, ~1 hour)
2. Fix damages table schema mismatch (critical, ~1 hour)
3. Create 5 new API endpoints (~8 hours)
4. Create 2 new services (~6 hours)
5. Create Pydantic schemas (~2 hours)

**Recommendation:** Proceed with implementation. The infrastructure is solid, and the gaps are well-defined and straightforward to implement.

---

**End of Analysis**
