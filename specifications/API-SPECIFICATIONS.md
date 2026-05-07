# API Backend Specifications
## AI-Powered Auto Insurance Claims System

**Version:** 1.0 (Prototype)  
**Last Updated:** 2026-05-03  
**Status:** Draft  
**Security:** ⚠️ **NO AUTHENTICATION/AUTHORIZATION - PROTOTYPE ONLY**

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Architecture Overview](#2-architecture-overview)
3. [API Versioning & Base URL](#3-api-versioning--base-url)
4. [Authentication & Authorization](#4-authentication--authorization)
5. [Common Patterns](#5-common-patterns)
6. [Data Models](#6-data-models)
7. [API Endpoints](#7-api-endpoints)
   - [7.1 Customers API](#71-customers-api)
   - [7.2 Claims API (Internal/Admin)](#72-claims-api-internaladmin)
   - [7.3 Adjustors API](#73-adjustors-api)
8. [State Machine Integration](#8-state-machine-integration)
9. [Error Handling](#9-error-handling)
10. [Implementation Guide](#10-implementation-guide)
11. [Environment Configuration](#11-environment-configuration)
12. [References](#12-references)

---

## 1. Introduction

### 1.1 Project Overview

This document specifies the RESTful API backend for an AI-powered auto insurance claims processing system. The system streamlines the claims adjudication process by leveraging computer vision for damage assessment, enabling faster claim resolution while maintaining human oversight for complex cases.

### 1.2 Purpose

This API serves as the backend layer for:
- **Customer Portal**: Submit claims (FNOL), upload damage photos, track claim status
- **Adjustor Portal**: Review AI-generated estimates, provide manual overrides, approve/reject claims
- **Admin Portal**: Manage claim workflows, initiate payments, close claims
- **AI Agents**: Process images, generate damage estimates, assess fraud risk

**⚠️ PROTOTYPE NOTICE**: This is a **demo/prototype system** for showcasing AI-powered claims processing. Version 1.0 does **NOT** implement authentication, authorization, or security features. All endpoints are publicly accessible. This system is **NOT suitable for production use** and should only be deployed in isolated development/demo environments.

### 1.3 Technology Stack

- **Framework**: Python FastAPI 0.104+
- **Database**: SQLAnywhere (local development)
- **ORM**: SQLAlchemy 2.0+
- **Validation**: Pydantic 2.0+
- **Testing**: pytest, httpx
- **Documentation**: Auto-generated via FastAPI/Swagger UI

### 1.4 Key Design Principles

1. **State Machine Driven**: All claim state transitions follow a deterministic state machine
2. **Event Sourcing**: Every action is logged in `claims_events` for audit trail
3. **Idempotency**: Critical operations (payment, state transitions) are idempotent
4. **Fail-Safe**: Invalid state transitions are rejected with clear error messages
5. **RESTful**: Follow REST principles for resource-oriented API design

---

## 2. Architecture Overview

### 2.1 System Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Customer   │────▶│  FastAPI    │────▶│ SQLAnywhere │
│   Portal    │     │   Backend   │     │  Database   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  AI Agent   │
                    │  (Damage    │
                    │  Detection) │
                    └─────────────┘
```

### 2.2 API Design Patterns

- **Resource-based URLs**: `/customers/{id}/claims/{claim_id}`
- **HTTP verbs**: GET (read), POST (create), PUT (update), DELETE (remove)
- **Nested resources**: Related entities nested under parent (e.g., `/claims/{id}/images`)
- **Action endpoints**: State transitions via action endpoints (e.g., `/claims/{id}/accept`)

### 2.3 State Machine Integration

All claim processing follows the state machine defined in:
- **Diagram**: [claims-state-machine.mmd](./diagrams/claims-state-machine.mmd)
- **Documentation**: [claims-state-machine.md](./diagrams/claims-state-machine.md)

Valid states:
```
draft | FNOL | image_uploaded | loss_estimated_ai | customer_decision_pending | 
loss_approved | loss_appealed | human_review_pending | human_review_completed | 
sent_for_payment | claim_paid | routed_to_traditional | 
traditional_processing_active | claim_closed
```

### 2.4 Database Integration

Database schema defined in:
- **ERD Diagram**: [claim-database-erd.mmd](./diagrams/claim-database-erd.mmd)

**Core Tables**:
- `customers`, `policies`, `vehicles`
- `claims`, `claim_images`, `damages`
- `claims_events` (audit trail)

---

## 3. API Versioning & Base URL

### 3.1 Versioning Strategy

- **Version format**: URL-based versioning (`/api/v1/`)
- **Current version**: `v1`
- **Breaking changes**: New major version (v2, v3, etc.)
- **Deprecation**: 6-month notice for version sunset

### 3.2 Base URL

**Development**: `http://localhost:8000/api/v1`  
**Production**: `https://api.insurance-claims.example.com/api/v1`

### 3.3 API Version Lifecycle

| Version | Status | Release Date | Sunset Date | Notes |
|---------|--------|--------------|-------------|-------|
| v1      | Prototype | 2026-05-01 | TBD | **NO SECURITY** - Demo/development only |

**⚠️ v1.0 Security Notice**: Version 1.0 is a **prototype** without authentication or authorization. Do not use in production.

---

## 4. Authentication & Authorization

### 4.1 **⚠️ NO SECURITY IN v1.0 (PROTOTYPE)**

**Version 1.0 Implementation**:
- ❌ **NO authentication required**
- ❌ **NO authorization checks**
- ❌ **NO API keys, JWT tokens, or session management**
- ✅ **All endpoints are publicly accessible**
- ✅ **No security headers required**

**Rationale**: This is a **prototype/demo system** to showcase AI-powered claims functionality. Security implementation is **explicitly out of scope** for v1.0 to accelerate development and simplify demo deployments.

**⚠️ CRITICAL**: This API **MUST NOT** be deployed in production or exposed to the public internet. Use only in isolated development/demo environments.

### 4.2 Authorization Model (Future - NOT IMPLEMENTED IN v1.0)

**Conceptual Roles** (for documentation only, not enforced):
- `customer`: Access own claims, upload images, accept/appeal estimates
- `adjustor`: Review claims, provide manual estimates, approve/deny
- `admin`: Initiate payments, close claims, system-level operations
- `ai_agent`: Generate AI estimates, flag for human review

**⚠️ Note**: Role-based access control is **NOT implemented** in v1.0. All endpoints can be called by any client without restriction.

### 4.3 Future Security Implementation (v2.0+)

When security is added in future versions, consider:
- **JWT Bearer tokens**: `Authorization: Bearer <jwt_token>`
- **API Keys**: `X-API-Key: <api_key>`
- **Session management**: Cookie-based sessions
- **RBAC**: Role checks in dependencies
- **Audit logging**: Track all security events

**Security headers** (future):
```http
Authorization: Bearer <jwt_token>
X-Request-ID: <uuid>
X-Customer-ID: <customer_id>
```

---

## 5. Common Patterns

### 5.1 Standard Response Format

**Success Response** (2xx):
```json
{
  "data": { ... },
  "meta": {
    "timestamp": "2026-05-03T10:30:00Z",
    "request_id": "req_1234567890"
  }
}
```

**Error Response** (4xx, 5xx):
```json
{
  "error": {
    "code": "INVALID_STATE_TRANSITION",
    "message": "Cannot transition from 'claim_paid' to 'loss_approved'",
    "details": {
      "current_state": "claim_paid",
      "requested_state": "loss_approved",
      "valid_transitions": ["claim_closed"]
    }
  },
  "meta": {
    "timestamp": "2026-05-03T10:30:00Z",
    "request_id": "req_1234567890"
  }
}
```

### 5.2 Pagination

**Query Parameters**:
```
?limit=20&offset=0
```

**Response**:
```json
{
  "data": [...],
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total": 150,
    "has_more": true
  }
}
```

### 5.3 Filtering & Sorting

**Filtering**:
```
?status=human_review_pending&routed_to_traditional=false
```

**Sorting**:
```
?sort_by=fnol_date&order=desc
```

### 5.4 HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200  | OK | Successful GET, PUT |
| 201  | Created | Successful POST (resource created) |
| 204  | No Content | Successful DELETE |
| 400  | Bad Request | Invalid input, validation errors |
| 401  | Unauthorized | Missing/invalid authentication |
| 403  | Forbidden | Insufficient permissions |
| 404  | Not Found | Resource doesn't exist |
| 409  | Conflict | Invalid state transition, duplicate resource |
| 422  | Unprocessable Entity | Validation error |
| 500  | Internal Server Error | Server-side error |

---

## 6. Data Models

### 6.1 Customer

```json
{
  "customer_id": 100,
  "fname": "Jane",
  "lname": "Doe",
  "email": "jane.doe@example.com",
  "phone": "+1-555-0123",
  "address": "123 Main St, Anytown, CA 90210"
}
```

**Validation Rules**:
- `customer_id`: Integer, auto-increment starting from 100
- `email`: Valid email format
- `phone`: E.164 format
- All fields except `address` are required

### 6.2 Policy

```json
{
  "policy_number": "PA-992384-01",
  "customer_id": 100,
  "effective_date": "2024-05-01",
  "expiration_date": "2025-05-01",
  "insured_name": "Jane Doe",
  "driver_1": "Jane Doe",
  "driver_2": "John Smith",
  "driver_3": null,
  "driver_4": null,
  "liability_limit": 100000,
  "collision_deductible": 500,
  "comprehensive_deductible": 250,
  "premium_total": 1200.50
}
```

### 6.3 Vehicle

```json
{
  "vin": "1ABC23456789DEFG",
  "customer_id": 100,
  "year": 2022,
  "make": "Toyota",
  "model": "Camry",
  "color": "Silver"
}
```

**Validation Rules**:
- `vin`: 17 characters, alphanumeric
- `year`: Integer, 1900-current year

### 6.4 Claim

```json
{
  "claim_id": 1000,
  "customer_id": 100,
  "vin": "1ABC23456789DEFG",
  "policy_number": "PA-992384-01",
  "fnol_date": "2026-05-03",
  "fnol_time": "10:30:00",
  "date_of_damage": "2026-05-02",
  "is_drivable": true,
  "current_status": "loss_estimated_ai",
  "claim_closed": false,
  "claim_closed_date": null,
  "ai_estimate_accepted": false,
  "routed_to_traditional": false,
  "reason_routing_to_traditional": null,
  "active_estimate_id": "1000_1714732200",
  "claim_amount": 2500.00,
  "actual_claim_amount": null
}
```

**Validation Rules**:
- `claim_id`: Integer, auto-increment starting from 1000
- `current_status`: Must be valid state (see section 2.3)
- `date_of_damage`: Date, must be on or before `fnol_date`, cannot be in the future
- `is_drivable`: Boolean, required
- `claim_amount`: Decimal(10,2), approved amount
- `actual_claim_amount`: Decimal(10,2), actual repair cost (nullable)

### 6.5 ClaimImage

```json
{
  "image_id": "front_bumper_damage.jpg",
  "claim_id": 1000,
  "uploaded_at": "2026-05-03T10:35:00Z",
  "uploaded_by": "customer_100"
}
```

**Validation Rules**:
- `image_id`: String, the filename itself (serves as unique identifier)
- `image_id`: Allowed extensions: jpg, jpeg, png, heic
- `uploaded_by`: Format: `customer_{id}`, `adjustor_{id}`, or `admin_{id}`

### 6.6 Damage

```json
{
  "damage_id": 1,
  "claim_id": 1000,
  "estimate_id": "1000_1714732200",
  "estimate_type": "ai",
  "estimate_version": 1,
  "image_id": "front_bumper_damage.jpg",
  "generated_on_date": "2026-05-03",
  "generated_on_time": "10:36:00",
  
  // YOLO Detection Fields
  "damage_class": 7,
  "damage_confidence": 0.86,
  "damage_part": "boot-dent",
  "bounding_box": {
    "x": 120,
    "y": 200,
    "width": 150,
    "height": 100
  },
  
  // Assessment Fields (heuristic-based, VLM in future)
  "internal_damage_probability": 0.7,
  "severity": 0.8,
  "recommended_action": "de-dent-and-paint",
  "reasoning": "Boot-dent detected with 86% confidence. Damage covers 2.3% of image area. Severity: 0.8. Action: de-dent-and-paint.",
  "car_side": "back",
  "assessment_confidence": 0.9,
  
  // Cost Breakdown
  "labor_hours": 1.5,
  "state_of_work": "CA",
  "avg_labor_cost": 156.00,
  "estimated_parts_cost": 700.00,
  "estimated_total_cost": 1750.00,
  
  // Annotated Image
  "annotated_image_id": "BB-front_bumper_damage.jpg"
}
```

**Validation Rules**:
- `estimate_type`: Enum: `ai` or `human`
- `estimate_id`: Format: `{claim_id}_{timestamp}`
- `damage_class`: Integer, 0-13 (YOLO class ID, see YOLO_CLASS_NAMES)
- `damage_confidence`: Float, 0.0-1.0 (YOLO detection confidence)
- `bounding_box`: Object with `x`, `y`, `width`, `height` (integers, pixel coordinates)
- `internal_damage_probability`: Float, 0.0-1.0
- `severity`: Float, 0.0-1.0
- `recommended_action`: Enum: `repaint`, `de-dent`, `replace`, `de-dent-and-paint`
- `reasoning`: String, max 1000 chars
- `car_side`: Enum: `front`, `back`, `driver_side`, `passenger_side`
- `assessment_confidence`: Float, 0.0-1.0 (assessment quality confidence)
- `annotated_image_id`: String, filename of image with bounding boxes (optional)

### 6.7 ClaimEvent

```json
{
  "claim_id": 1000,
  "event_id": 1,
  "event_date": "2026-05-03",
  "event_time": "10:30:00",
  "status": "FNOL",
  "action": "upload_damage_photos",
  "action_by": "customer",
  "action_by_identity": "customer_100",
  "comments": "Uploaded 3 damage photos"
}
```

**Validation Rules**:
- `status`: Valid claim state (see section 2.3)
- `action`: Valid action (see section 8.1)
- `action_by`: Enum: `customer`, `AI agent`, `adjustor`, `admin`

### 6.8 EstimateResponse (Composite)

```json
{
  "estimate_id": "1000_1714732200",
  "estimate_type": "ai",
  "estimate_version": 1,
  "claim_id": 1000,
  "damages": [
    { 
      "damage_id": 1,
      "damage_part": "boot-dent",
      "severity": 0.8,
      "estimated_cost": 1750.00
    }
  ],
  "total_estimated_cost": 1750.00,
  "confidence_score": 0.86,
  "fraud_risk_score": 0.05,
  "generated_at": "2026-05-03T10:36:00Z"
}
```

---

## 7. API Endpoints

### 7.1 Customers API

#### 7.1.1 Get Customer Details

**Endpoint**: `GET /api/v1/customers/{customer_id}`

**Description**: Retrieve customer information

**Path Parameters**:
- `customer_id` (integer, required): Customer ID

**Response** (200 OK):
```json
{
  "data": {
    "customer_id": 100,
    "fname": "Jane",
    "lname": "Doe",
    "email": "jane.doe@example.com",
    "phone": "+1-555-0123",
    "address": "123 Main St, Anytown, CA 90210"
  }
}
```

**Errors**:
- `404 Not Found`: Customer does not exist

---

#### 7.1.2 Get Customer Policies

**Endpoint**: `GET /api/v1/customers/{customer_id}/policies`

**Description**: Retrieve all policies for a customer

**Path Parameters**:
- `customer_id` (integer, required): Customer ID

**Response** (200 OK):
```json
{
  "data": [
    {
      "policy_number": "PA-992384-01",
      "effective_date": "2024-05-01",
      "expiration_date": "2025-05-01",
      "premium_total": 1200.50,
      "insured_name": "Jane Doe"
    }
  ]
}
```

**Errors**:
- `404 Not Found`: Customer does not exist

---

#### 7.1.3 Get Policy Vehicles

**Endpoint**: `GET /api/v1/customers/{customer_id}/policies/vehicles`

**Description**: Retrieve all vehicles covered under customer's policies

**Path Parameters**:
- `customer_id` (integer, required): Customer ID

**Query Parameters**:
- `policy_number` (string, optional): Filter by specific policy

**Response** (200 OK):
```json
{
  "data": [
    {
      "vin": "1ABC23456789DEFG",
      "year": 2022,
      "make": "Toyota",
      "model": "Camry",
      "color": "Silver",
      "policy_number": "PA-992384-01"
    }
  ]
}
```

---

#### 7.1.4 Create Claim (Draft)

**Endpoint**: `POST /api/v1/customers/{customer_id}/claims`

**Description**: Create a new claim in draft state

**Path Parameters**:
- `customer_id` (integer, required): Customer ID

**Request Body**:
```json
{
  "vin": "1ABC23456789DEFG",
  "policy_number": "PA-992384-01",
  "fnol_date": "2026-05-03",
  "fnol_time": "10:30:00",
  "date_of_damage": "2026-05-02",
  "is_drivable": true,
  "incident_description": "Rear-ended at traffic light"
}
```

**Response** (201 Created):
```json
{
  "data": {
    "claim_id": 1000,
    "customer_id": 100,
    "vin": "1ABC23456789DEFG",
    "policy_number": "PA-992384-01",
    "fnol_date": "2026-05-03",
    "fnol_time": "10:30:00",
    "date_of_damage": "2026-05-02",
    "is_drivable": true,
    "current_status": "draft"
  }
}
```

**State Machine Impact**:
- **Creates state**: `draft`
- **Logs event**: `action: "create_claim"`, `action_by: "customer"`

**Validation**:
- VIN must exist for customer
- Policy must be active (effective_date ≤ fnol_date ≤ expiration_date)
- Policy must cover the vehicle (VIN)
- date_of_damage must be on or before fnol_date

**Errors**:
- `404 Not Found`: Customer, vehicle, or policy not found
- `400 Bad Request`: Policy doesn't cover vehicle
- `422 Unprocessable Entity`: Validation error (invalid dates, etc.)

---

#### 7.1.5 Submit Claim for Processing

**Endpoint**: `POST /api/v1/customers/{customer_id}/claims/{claim_id}/submit`

**Description**: Submit draft claim for processing (draft → FNOL transition)

**Path Parameters**:
- `customer_id` (integer, required): Customer ID
- `claim_id` (integer, required): Claim ID

**Request Body**: None

**Response** (200 OK):
```json
{
  "data": {
    "claim_id": 1000,
    "customer_id": 100,
    "vin": "1ABC23456789DEFG",
    "policy_number": "PA-992384-01",
    "fnol_date": "2026-05-03",
    "fnol_time": "10:30:00",
    "date_of_damage": "2026-05-02",
    "is_drivable": true,
    "current_status": "FNOL"
  }
}
```

**State Machine Impact**:
- **Transitions**: `draft` → `FNOL`
- **Logs event**: `action: "submit_claim"`, `action_by: "customer"`

**Validation**:
- Claim must be in `draft` state
- Claim must belong to customer

**Errors**:
- `404 Not Found`: Claim not found or doesn't belong to customer
- `400 Bad Request`: Invalid state transition (claim not in draft state)

---

#### 7.1.6 Get Customer Claims

**Endpoint**: `GET /api/v1/customers/{customer_id}/claims`

**Description**: Retrieve all claims for a customer

**Path Parameters**:
- `customer_id` (integer, required): Customer ID

**Query Parameters**:
- `status` (string, optional): Filter by claim status
- `limit` (integer, optional, default=20): Pagination limit
- `offset` (integer, optional, default=0): Pagination offset

**Response** (200 OK):
```json
{
  "data": [
    {
      "claim_id": 1000,
      "vin": "1ABC23456789DEFG",
      "fnol_date": "2026-05-03",
      "current_status": "customer_decision_pending",
      "claim_amount": 2500.00
    }
  ],
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total": 1
  }
}
```

---

#### 7.1.7 Get Claim Details

**Endpoint**: `GET /api/v1/customers/{customer_id}/claims/{claim_id}`

**Description**: Retrieve detailed claim information

**Path Parameters**:
- `customer_id` (integer, required): Customer ID
- `claim_id` (integer, required): Claim ID

**Response** (200 OK):
```json
{
  "data": {
    "claim_id": 1000,
    "customer_id": 100,
    "vin": "1ABC23456789DEFG",
    "policy_number": "PA-992384-01",
    "fnol_date": "2026-05-03",
    "fnol_time": "10:30:00",
    "date_of_damage": "2026-05-02",
    "is_drivable": true,
    "current_status": "customer_decision_pending",
    "claim_closed": false,
    "ai_estimate_accepted": false,
    "claim_amount": 2500.00,
    "active_estimate": {
      "estimate_id": "1000_1714732200",
      "total_cost": 2500.00,
      "damages_count": 2
    },
    "images": [
      {
        "image_id": "front_bumper_damage.jpg",
        "uploaded_at": "2026-05-03T10:35:00Z"
      }
    ],
    "events": [
      {
        "event_id": 1,
        "event_date": "2026-05-03",
        "status": "FNOL",
        "action": "create_claim"
      }
    ]
  }
}
```

**Errors**:
- `404 Not Found`: Claim does not exist or doesn't belong to customer
- `403 Forbidden`: Customer doesn't own this claim

---

#### 7.1.8 Upload Claim Image

**Endpoint**: `POST /api/v1/customers/{customer_id}/claims/{claim_id}/images`

**Description**: Upload damage photo to claim (one image per request)

**Path Parameters**:
- `customer_id` (integer, required): Customer ID
- `claim_id` (integer, required): Claim ID

**Request Body** (multipart/form-data):
```
file: <binary image data>
```

**Request Headers**:
```
Content-Type: multipart/form-data
```

**Upload Examples**:

**cURL:**
```bash
curl -X POST \
  http://localhost:8000/api/v1/customers/100/claims/1000/images \
  -F "file=@front_bumper_damage.jpg"
```

**Python (requests):**
```python
import requests
url = "http://localhost:8000/api/v1/customers/100/claims/1000/images"
files = {"file": open("front_bumper_damage.jpg", "rb")}
response = requests.post(url, files=files)
```

**JavaScript (Fetch):**
```javascript
const formData = new FormData();
formData.append("file", fileInput.files[0]);

fetch("/api/v1/customers/100/claims/1000/images", {
  method: "POST",
  body: formData
});
```

**Response** (201 Created):
```json
{
  "data": {
    "image_id": "front_bumper_damage.jpg",
    "claim_id": 1000,
    "uploaded_at": "2026-05-03T10:35:00Z",
    "uploaded_by": "customer_100"
  }
}
```

**State Machine Impact**:
- **Transitions**: `FNOL` → `image_uploaded` (on first image)
- **Subsequent uploads**: Stay in `image_uploaded` state
- **Logs event**: `action: "upload_damage_photos"`, `action_by: "customer"`

**YOLO Processing Flow:**
1. Image saved to filesystem: `uploads/{claim_id}/{filename}`
2. YOLO model runs inference on image
3. For each detection:
   - Extract `damage_class`, `confidence`, `bounding_box` (x, y, width, height)
   - Calculate `severity` from bounding box area relative to image size
   - Determine `car_side` from bounding box position in image
   - Estimate `internal_damage_probability` (heuristic based on damage type)
   - Assign `recommended_action` based on damage class
   - Generate `reasoning` text explaining the assessment
4. Save annotated image with bounding boxes: `uploads/{claim_id}/BB-{filename}`
5. Create Damage records in database (one per detection)
6. Log event: "YOLO detected {N} damages in {filename}"

**Annotated Images:**
- Generated automatically if `YOLO_SAVE_ANNOTATED_IMAGES` config is `true`
- Filename format: `BB-{original_filename}` (e.g., `BB-front_bumper_damage.jpg`)
- Stored in same directory as original image
- Contains bounding boxes drawn over detected damages with class labels
- Can be retrieved via same image endpoint by using the annotated image_id
- Useful for review, debugging, and customer communication

**Validation Rules**:
- **File size**: Max 10MB per image
- **File types**: jpg, jpeg, png, heic (case-insensitive)
- **Max images**: 20 images per claim
- **Filename**: Original filename preserved, must be unique per claim
- **Valid states**: Can only upload in `FNOL` or `image_uploaded` states

**Filename Handling**:
- Original filename is preserved (e.g., `front_bumper_damage.jpg`)
- Filename serves as `image_id` in the database
- Duplicate filenames for same claim are **rejected** with 409 error
- Client must rename file or delete existing image before re-uploading

**Storage Location**:
- **Directory structure**: `{IMAGES_ROOT_FOLDER}/{claim_id}/{filename}`
- **Root folder**: Configurable via `IMAGES_ROOT_FOLDER` environment variable (default: `uploads`)
- **Per-claim subfolder**: Each claim gets its own subdirectory named by `claim_id`
- **Example path**: `uploads/1000/front_bumper_damage.jpg`
- **Benefits**:
  - Easy to locate all images for a specific claim
  - Prevents filename collisions across different claims
  - Simple cleanup when archiving/deleting claims
  - Efficient filesystem organization

**Errors**:
- `400 Bad Request`: Invalid file type, file too large, or no filename
- `409 Conflict`: 
  - Duplicate filename for this claim
  - Maximum images (20) reached
  - Invalid state for upload (e.g., claim already has AI estimate)
- `404 Not Found`: Claim does not exist

---

#### 7.1.8a Complete Claim Filing Workflow (Customer Portal)

**Overview**: This describes the complete end-to-end workflow for customers filing claims with photo upload through the customer portal UI.

**Workflow Steps:**

**Step 1: Create Claim in Draft State**
```
POST /api/v1/customers/{customer_id}/claims
```
- Customer selects vehicle and provides incident details
- Claim is created with `status = "draft"`
- Claim ID is returned and stored in UI state
- Customer proceeds to image upload page

**Step 2: Upload Damage Photos** (Multiple calls, one per image)
```
POST /api/v1/customers/{customer_id}/claims/{claim_id}/images
```
- Customer uploads 1-20 images of vehicle damage
- Each upload triggers automatic YOLO analysis
- Damages are detected and saved to database
- UI shows upload progress and analysis status
- Claim remains in `draft` state during uploads

**Step 3: Submit Claim for Processing**
```
POST /api/v1/customers/{customer_id}/claims/{claim_id}/submit
```
- After all images uploaded, customer clicks "Submit Claim"
- Claim transitions from `draft` → `FNOL` state
- AI estimate is generated (if not already done)
- Customer is redirected to claim detail page
- Claim enters processing workflow

**Alternative Path: No Photos Available**
- If customer cannot provide photos:
  - Claim is created in draft
  - Immediately submitted (draft → FNOL)
  - Routed to traditional adjustor review
  - No image upload step

**State Persistence:**
- Draft claims are saved in database
- Customer can navigate away and return later
- Images are stored even before final submission
- Claim ID persists throughout workflow

**UI Route Flow:**
```
/claims/new                          → Create draft claim
/claims/{claim_id}/upload           → Upload images (draft state)
POST submit                         → Transition to FNOL
/claims/{claim_id}                  → View claim details
```

**Key Design Decisions:**
- ✅ **Draft State First**: Claim created before image upload to capture claim ID
- ✅ **Incremental Upload**: Images uploaded one-by-one with progress tracking
- ✅ **Deferred Submission**: Claim stays in draft until customer explicitly submits
- ✅ **Automatic AI Analysis**: YOLO runs during upload, not after submission
- ✅ **Flexible Exit**: Customer can abandon mid-upload, claim remains as draft

---

#### 7.1.9 Get Claim Image (Serve Image File)

**Endpoint**: `GET /api/v1/customers/{customer_id}/claims/{claim_id}/images/{image_id}`

**Description**: Retrieve/serve a damage photo (original or annotated with bounding boxes)

**Path Parameters**:
- `customer_id` (integer, required): Customer ID
- `claim_id` (integer, required): Claim ID
- `image_id` (string, required): Image filename (e.g., `front_bumper_damage.jpg`)

**Query Parameters**:
- `annotated` (string, optional): Set to `"yes"` to retrieve the YOLO-annotated version with bounding boxes
  - Default: returns original image
  - `?annotated=yes`: returns annotated image (`BB-{image_id}`)

**Request Examples**:

**cURL (Original Image):**
```bash
curl http://localhost:8000/api/v1/customers/100/claims/1000/images/front_bumper_damage.jpg \
  --output front_bumper.jpg
```

**cURL (Annotated Image with Bounding Boxes):**
```bash
curl "http://localhost:8000/api/v1/customers/100/claims/1000/images/front_bumper_damage.jpg?annotated=yes" \
  --output front_bumper_annotated.jpg
```

**JavaScript (React Image Component):**
```javascript
// Original image
<img src={`/api/v1/customers/${customerId}/claims/${claimId}/images/${imageId}`} />

// Annotated image
<img src={`/api/v1/customers/${customerId}/claims/${claimId}/images/${imageId}?annotated=yes`} />
```

**Response** (200 OK):
- **Content-Type**: `image/jpeg`, `image/png`, or `image/heic` (based on file type)
- **Body**: Binary image data (streamed)

**File Resolution**:
1. If `annotated=yes` query parameter is present:
   - Look for annotated file: `uploads/{claim_id}/BB-{image_id}`
   - If not found, return 404 error
2. If `annotated` is omitted or set to any other value:
   - Return original file: `uploads/{claim_id}/{image_id}`

**Caching Headers** (Optional, for performance):
```
Cache-Control: public, max-age=3600
ETag: <file-hash>
```

**Errors**:
- `404 Not Found`: Image file does not exist on filesystem
  - Original image not found: `Image not found: {image_id}`
  - Annotated image not found: `Annotated image not found: BB-{image_id}`
- `403 Forbidden`: Customer doesn't own this claim
- `500 Internal Server Error`: File read error

**Security Considerations**:
- ⚠️ **Path Traversal**: Validate `image_id` to prevent directory traversal attacks (e.g., `../../etc/passwd`)
- ⚠️ **Authorization**: Verify customer owns the claim before serving images (production requirement)
- ⚠️ **File Type Validation**: Ensure served files are images, not executable files

**Implementation Notes**:
- Use FastAPI's `FileResponse` for efficient file streaming
- Set appropriate `Content-Type` based on file extension
- Log access for audit purposes (customer viewed image)
- Consider CDN caching for production deployments

---

#### 7.1.10 Delete Claim Image

**Endpoint**: `DELETE /api/v1/customers/{customer_id}/claims/{claim_id}/images/{image_id}`

**Description**: Delete an uploaded damage photo (also deletes associated damages)

**Path Parameters**:
- `customer_id` (integer, required): Customer ID
- `claim_id` (integer, required): Claim ID
- `image_id` (integer, required): Image ID

**Response** (204 No Content)

**State Machine Impact**:
- **Logs event**: `action: "delete_image"`, `action_by: "customer"`
- **Database**: Cascade deletes damages associated with image_id

**Validation**:
- Can only delete if claim status is `FNOL` or `image_uploaded`
- Cannot delete if claim has AI estimate generated

**Errors**:
- `404 Not Found`: Image does not exist
- `409 Conflict`: Cannot delete image after AI estimate generated

---

#### 7.1.10 Accept Estimate

**Endpoint**: `POST /api/v1/customers/{customer_id}/claims/{claim_id}/accept`

**Description**: Customer accepts the AI or human-reviewed estimate

**Path Parameters**:
- `customer_id` (integer, required): Customer ID
- `claim_id` (integer, required): Claim ID

**Request Body**:
```json
{
  "estimate_id": "1000_1714732200"
}
```

**Response** (200 OK):
```json
{
  "data": {
    "claim_id": 1000,
    "current_status": "loss_approved",
    "accepted_estimate_id": "1000_1714732200",
    "claim_amount": 2500.00
  }
}
```

**State Machine Impact**:
- **Transitions**: `customer_decision_pending` → `loss_approved`
- **Next state**: `loss_approved` → `sent_for_payment`
- **Logs event**: `action: "accept_estimate"`, `action_by: "customer"`

**Validation**:
- Claim must be in `customer_decision_pending` state
- Estimate must exist and belong to claim

**Errors**:
- `409 Conflict`: Invalid state transition
- `404 Not Found`: Estimate not found

---

#### 7.1.11 Appeal Estimate

**Endpoint**: `POST /api/v1/customers/{customer_id}/claims/{claim_id}/appeal`

**Description**: Customer rejects estimate and requests human review

**Path Parameters**:
- `customer_id` (integer, required): Customer ID
- `claim_id` (integer, required): Claim ID

**Request Body**:
```json
{
  "estimate_id": "1000_1714732200",
  "reason": "Estimate seems too low, missing rear bumper damage"
}
```

**Response** (200 OK):
```json
{
  "data": {
    "claim_id": 1000,
    "current_status": "loss_appealed",
    "next_status": "human_review_pending"
  }
}
```

**State Machine Impact**:
- **Transitions**: `customer_decision_pending` → `loss_appealed` → `human_review_pending`
- **Logs event**: `action: "appeal_estimate"`, `action_by: "customer"`

**Errors**:
- `409 Conflict`: Invalid state transition

---

### 7.2 Claims API (Internal/Admin)

#### 7.2.1 Get Claim (Admin)

**Endpoint**: `GET /api/v1/claims/{claim_id}`

**Description**: Retrieve claim details (admin/adjustor view with full details)

**Path Parameters**:
- `claim_id` (integer, required): Claim ID

**Response** (200 OK):
```json
{
  "data": {
    "claim_id": 1000,
    "customer": {
      "customer_id": 100,
      "fname": "Jane",
      "lname": "Doe",
      "email": "jane.doe@example.com"
    },
    "vehicle": {
      "vin": "1ABC23456789DEFG",
      "year": 2022,
      "make": "Toyota",
      "model": "Camry"
    },
    "current_status": "human_review_pending",
    "is_drivable": true,
    "ai_estimate_accepted": false,
    "routed_to_traditional": false,
    "claim_amount": null,
    "fraud_risk_score": 0.05,
    "confidence_score": 0.86,
    "images": [...],
    "damages": [...],
    "events": [...]
  }
}
```

---

#### 7.2.2 Update Claim State

**Endpoint**: `PUT /api/v1/claims/{claim_id}/state`

**Description**: Manually update claim state (admin only)

**Path Parameters**:
- `claim_id` (integer, required): Claim ID

**Request Body**:
```json
{
  "new_status": "human_review_completed",
  "reason": "Manual override by admin"
}
```

**Response** (200 OK):
```json
{
  "data": {
    "claim_id": 1000,
    "previous_status": "human_review_pending",
    "current_status": "human_review_completed"
  }
}
```

**State Machine Impact**:
- **Validates transition**: Checks if transition is valid
- **Logs event**: `action: "state_transition"`, `action_by: "admin"`

**Errors**:
- `409 Conflict`: Invalid state transition

---

#### 7.2.3 Generate AI Estimate

**Endpoint**: `POST /api/v1/claims/{claim_id}/estimate/ai`

**Description**: Trigger AI damage estimation (called by AI agent or admin)

**Path Parameters**:
- `claim_id` (integer, required): Claim ID

**Request Body**:
```json
{
  "image_ids": ["front_bumper_damage.jpg", "rear_damage.jpg", "side_panel.jpg"]
}
```

**Response** (201 Created):
```json
{
  "data": {
    "estimate_id": "1000_1714732200",
    "estimate_type": "ai",
    "estimate_version": 1,
    "claim_id": 1000,
    "damages": [
      {
        "damage_id": 1,
        "image_id": "front_bumper_damage.jpg",
        "damage_part": "boot-dent",
        "severity": 0.8,
        "estimated_cost": 1750.00
      }
    ],
    "total_estimated_cost": 2500.00,
    "confidence_score": 0.86,
    "fraud_risk_score": 0.05
  }
}
```

**State Machine Impact**:
- **Transitions**: `image_uploaded` → `loss_estimated_ai`
- **Next transitions**:
  - If confidence > 0.55 AND fraud < 0.1 → `customer_decision_pending`
  - If fraud > 0.1 OR confidence 0.35-0.55 → `human_review_pending`
  - If confidence < 0.35 → `routed_to_traditional`
- **Logs event**: `action: "generate_estimate"`, `action_by: "AI agent"`

**Business Logic**:
1. Process each image with CV model
2. Generate damage assessments
3. Calculate total cost
4. Compute confidence and fraud scores
5. Determine next state based on thresholds
6. Update claim status

**Errors**:
- `409 Conflict`: Claim not in valid state for AI estimation
- `400 Bad Request`: No images provided or images don't exist

---

#### 7.2.4 Generate Human Estimate

**Endpoint**: `POST /api/v1/claims/{claim_id}/estimate/human`

**Description**: Adjustor provides manual estimate (override or revision)

**Path Parameters**:
- `claim_id` (integer, required): Claim ID

**Request Body**:
```json
{
  "damages": [
    {
      "damage_part": "boot-dent",
      "severity": 0.9,
      "labor_hours": 2.0,
      "estimated_parts_cost": 800.00,
      "estimated_total_cost": 2000.00,
      "reasoning": "Additional internal damage to trunk latch",
      "image_id": "front_bumper_damage.jpg"
    }
  ],
  "adjustor_comments": "Revised estimate after manual inspection"
}
```

**Response** (201 Created):
```json
{
  "data": {
    "estimate_id": "1000_1714732300",
    "estimate_type": "human",
    "estimate_version": 2,
    "total_estimated_cost": 2000.00
  }
}
```

**State Machine Impact**:
- **Logs event**: `action: "revised_estimate"`, `action_by: "adjustor"`

**Errors**:
- `403 Forbidden`: User is not an adjustor or admin

---

#### 7.2.5 Human Review Decision

**Endpoint**: `POST /api/v1/claims/{claim_id}/human/review`

**Description**: Adjustor approves, denies, or routes claim after review

**Path Parameters**:
- `claim_id` (integer, required): Claim ID

**Request Body**:
```json
{
  "decision": "approved",
  "estimate_id": "1000_1714732300",
  "comments": "Estimate approved with minor adjustments"
}
```

**Decision Options**:
- `approved`: Approve claim, send revised estimate to customer
- `denied`: Deny appeal, route to traditional
- `route_to_traditional`: Complex case requiring physical inspection

**Response** (200 OK):
```json
{
  "data": {
    "claim_id": 1000,
    "review_decision": "approved",
    "current_status": "human_review_completed",
    "next_status": "customer_decision_pending"
  }
}
```

**State Machine Impact**:
- **Transitions**: `human_review_pending` → `human_review_completed`
- **Next transitions**:
  - `approved` → `customer_decision_pending` (present revised estimate)
  - `denied` or `route_to_traditional` → `routed_to_traditional`
- **Logs event**: 
  - `action: "approve_claim"` (if approved)
  - `action: "denied_appeal"` (if denied)
  - `action: "route_to_traditional"` (if routed)
  - `action_by: "adjustor"`

---

#### 7.2.6 Get Claim Damages

**Endpoint**: `GET /api/v1/claims/{claim_id}/damages`

**Description**: Retrieve all damage assessments for a claim

**Path Parameters**:
- `claim_id` (integer, required): Claim ID

**Query Parameters**:
- `estimate_type` (string, optional): Filter by `ai` or `human`
- `estimate_version` (integer, optional): Filter by version

**Response** (200 OK):
```json
{
  "data": [
    {
      "damage_id": 1,
      "estimate_id": "1000_1714732200",
      "estimate_type": "ai",
      "estimate_version": 1,
      "damage_part": "boot-dent",
      "estimated_total_cost": 1750.00
    }
  ]
}
```

---

#### 7.2.7 Get Specific Damage

**Endpoint**: `GET /api/v1/claims/{claim_id}/damages/{damage_id}`

**Description**: Retrieve detailed damage assessment

**Path Parameters**:
- `claim_id` (integer, required): Claim ID
- `damage_id` (integer, required): Damage ID

**Response** (200 OK):
```json
{
  "data": {
    "damage_id": 1,
    "claim_id": 1000,
    "estimate_id": "1000_1714732200",
    "estimate_type": "ai",
    "image_id": "front_bumper_damage.jpg",
    "damage_part": "boot-dent",
    "severity": 0.8,
    "internal_damage_probability": 0.7,
    "recommended_action": "de-dent-and-paint",
    "reasoning": "The trunk lid shows significant denting...",
    "labor_hours": 1.5,
    "avg_labor_cost": 156.00,
    "estimated_parts_cost": 700.00,
    "estimated_total_cost": 1750.00
  }
}
```

---

#### 7.2.8 Get Claim Events

**Endpoint**: `GET /api/v1/claims/{claim_id}/events`

**Description**: Retrieve claim event history (audit trail)

**Path Parameters**:
- `claim_id` (integer, required): Claim ID

**Query Parameters**:
- `action_by` (string, optional): Filter by actor type
- `limit` (integer, optional, default=50): Pagination limit
- `offset` (integer, optional, default=0): Pagination offset

**Response** (200 OK):
```json
{
  "data": [
    {
      "event_id": 1,
      "claim_id": 1000,
      "event_date": "2026-05-03",
      "event_time": "10:30:00",
      "status": "FNOL",
      "action": "create_claim",
      "action_by": "customer",
      "action_by_identity": "customer_100",
      "comments": ""
    },
    {
      "event_id": 2,
      "status": "image_uploaded",
      "action": "upload_damage_photos",
      "action_by": "customer",
      "comments": "Uploaded 3 images"
    }
  ],
  "pagination": {
    "limit": 50,
    "offset": 0,
    "total": 2
  }
}
```

---

#### 7.2.9 Initiate Payment

**Endpoint**: `POST /api/v1/claims/{claim_id}/payment/initiate`

**Description**: Initiate payment processing for approved claim (admin only)

**Path Parameters**:
- `claim_id` (integer, required): Claim ID

**Request Body**:
```json
{
  "payment_amount": 2500.00,
  "payment_method": "ach_transfer",
  "comments": "Payment initiated for claim 1000"
}
```

**Response** (200 OK):
```json
{
  "data": {
    "claim_id": 1000,
    "current_status": "sent_for_payment",
    "payment_amount": 2500.00,
    "payment_initiated_at": "2026-05-03T11:00:00Z"
  }
}
```

**State Machine Impact**:
- **Transitions**: `loss_approved` → `sent_for_payment`
- **Logs event**: `action: "initiate_payment"`, `action_by: "admin"`

**Validation**:
- Claim must be in `loss_approved` state
- Payment amount must match `claim_amount`

**Errors**:
- `409 Conflict`: Invalid state transition or amount mismatch

---

#### 7.2.10 Confirm Payment

**Endpoint**: `PUT /api/v1/claims/{claim_id}/payment/confirm`

**Description**: Confirm payment has been processed (admin only)

**Path Parameters**:
- `claim_id` (integer, required): Claim ID

**Request Body**:
```json
{
  "payment_confirmation_id": "PAY-123456789",
  "payment_completed_at": "2026-05-03T11:30:00Z"
}
```

**Response** (200 OK):
```json
{
  "data": {
    "claim_id": 1000,
    "current_status": "claim_paid",
    "payment_confirmed_at": "2026-05-03T11:30:00Z"
  }
}
```

**State Machine Impact**:
- **Transitions**: `sent_for_payment` → `claim_paid`
- **Next transition**: `claim_paid` → `claim_closed` (manual or automated)
- **Logs event**: `action: "payment_sent"`, `action_by: "admin"`

**Errors**:
- `409 Conflict`: Claim not in `sent_for_payment` state

---

#### 7.2.11 Get Cost Estimate

**Endpoint**: `POST /api/v1/cost/estimate`

**Description**: Calculate repair cost estimation for a damage report (used internally by AI agent)

**Request Body**:
```json
{
  "damage_report": {
    "id": 1,
    "class": 7,
    "confidence": 0.86,
    "part": "boot-dent"
  },
  "assessment": {
    "internal_damage_probability": 0.7,
    "severity": 0.8,
    "recommended_action": "de-dent-and-paint",
    "reasoning": "The trunk lid (boot) shows significant denting...",
    "car_side": "back",
    "confidence": 0.9
  },
  "state": "CA"
}
```

**Response** (200 OK):
```json
{
  "data": {
    "damage_part": "boot-dent",
    "severity": 0.8,
    "labor_hours": 2.5,
    "avg_labor_cost": 156.00,
    "estimated_parts_cost": 850.00,
    "estimated_total_cost": 1240.00,
    "breakdown": {
      "labor_cost": 390.00,
      "parts_cost": 850.00,
      "total": 1240.00
    },
    "confidence": 0.86,
    "notes": "Estimate based on severity 0.8 and internal damage probability 0.7"
  }
}
```

**Cost Calculation Logic**:
1. **Base labor hours**: Determined by damage part and severity
2. **Labor cost**: `labor_hours × avg_labor_cost` (state-specific rates)
3. **Parts cost**: Based on damage part, severity, and internal damage probability
4. **Total cost**: `labor_cost + parts_cost`

**State-Specific Labor Rates**:
| State | Avg Labor Cost ($/hour) |
|-------|-------------------------|
| CA    | $156.00                |
| TX    | $125.00                |
| NY    | $175.00                |
| FL    | $135.00                |
| Default | $140.00             |

**Damage Part Base Costs** (examples):
| Part | Base Labor Hours | Base Parts Cost |
|------|------------------|-----------------|
| boot-dent | 1.5 - 3.0 | $500 - $1200 |
| front-bumper-dent | 1.0 - 2.5 | $300 - $800 |
| door-scratch | 0.5 - 1.5 | $200 - $600 |
| paint-damage | 1.0 - 2.0 | $150 - $400 |

**Severity Multipliers**:
- Light (0.0 - 0.3): 0.7x multiplier
- Moderate (0.3 - 0.6): 1.0x multiplier
- Severe (0.6 - 1.0): 1.5x multiplier

**Internal Damage Adjustment**:
- If `internal_damage_probability > 0.5`: Add 25% to total cost
- If `internal_damage_probability > 0.7`: Add 50% to total cost

**Use Cases**:
1. **AI Estimate Generation**: Called during AI damage detection
2. **Human Review**: Adjustor can request cost recalculation
3. **What-if Analysis**: Test different severity levels

**Validation**:
- `severity`: Must be between 0.0 and 1.0
- `confidence`: Must be between 0.0 and 1.0
- `part`: Must be valid damage part name
- `state`: Optional, defaults to "CA"

**Errors**:
- `400 Bad Request`: Invalid severity, confidence, or part name
- `422 Unprocessable Entity`: Missing required fields

---

#### 7.2.12 Close Claim

**Endpoint**: `PUT /api/v1/claims/{claim_id}/close`

**Description**: Close claim (terminal state)

**Path Parameters**:
- `claim_id` (integer, required): Claim ID

**Request Body**:
```json
{
  "actual_claim_amount": 2450.00,
  "closure_reason": "Payment completed, claim resolved",
  "closed_by": "admin_1"
}
```

**Response** (200 OK):
```json
{
  "data": {
    "claim_id": 1000,
    "current_status": "claim_closed",
    "claim_closed": true,
    "claim_closed_date": "2026-05-03",
    "actual_claim_amount": 2450.00
  }
}
```

**State Machine Impact**:
- **Transitions**: 
  - `claim_paid` → `claim_closed`
  - `traditional_processing_active` → `claim_closed`
- **Logs event**: `action: "close_claim"`, `action_by: "admin"`

**Validation**:
- Valid source states: `claim_paid`, `traditional_processing_active`
- `actual_claim_amount` should be provided if available

---

### 7.3 Adjustors API

**NEW in v1.1:** Endpoints for adjustor workload management and claim assignment.

#### 7.3.1 List All Adjustors with Workload

**Endpoint**: `GET /api/v1/adjustors`

**Purpose**: Get all adjustors with their current workload statistics. Used by Customer Portal for auto-assignment when claims enter human review.

**Query Parameters**:
- `status_filter` (optional, string): Filter by adjustor status
  - Values: `active`, `inactive`
  - Default: Return all adjustors

**Response** (200 OK):
```json
[
  {
    "adjustor_id": "ADJ-001",
    "name": "Sarah Chen",
    "email": "sarah.chen@acme-insurance.com",
    "role": "Senior Adjustor",
    "status": "active",
    "pending_reviews": 3,
    "completed_today": 2,
    "completed_this_week": 12
  },
  {
    "adjustor_id": "ADJ-002",
    "name": "Michael Torres",
    "email": "michael.torres@acme-insurance.com",
    "role": "Collision Specialist",
    "status": "active",
    "pending_reviews": 1,
    "completed_today": 5,
    "completed_this_week": 18
  }
]
```

**Use Case**:
- Customer Portal calls this endpoint to find adjustor with shortest queue
- Selects adjustor with minimum `pending_reviews` count
- Then calls assign endpoint to assign the claim

**Example Request**:
```bash
# Get all active adjustors
curl http://localhost:8000/api/v1/adjustors?status_filter=active
```

---

#### 7.3.2 Get Adjustor Pending Claims

**Endpoint**: `GET /api/v1/adjustors/{adjustor_id}/claims/pending`

**Purpose**: Get paginated list of claims in `human_review_pending` status.

**Path Parameters**:
- `adjustor_id` (required, string): Adjustor identifier (e.g., "ADJ-001")

**Query Parameters**:
- `search` (optional, string): Search by claim ID, customer name, VIN, or policy number
- `sort` (optional, string): Sort order
  - Values: `oldest` (default), `newest`, `highest_amount`, `lowest_amount`, `customer_name`
- `page` (optional, integer): Page number (default: 1)
- `limit` (optional, integer): Items per page (default: 20, max: 100)

**Response** (200 OK):
```json
{
  "total": 2,
  "page": 1,
  "limit": 20,
  "total_pages": 1,
  "claims": [
    {
      "claim_id": 2001,
      "customer_id": 103,
      "customer_name": "Alice Williams",
      "vin": "1HGCM82633A123456",
      "vehicle": "2022 Honda Accord Silver",
      "policy_number": "POL-2026-004",
      "fnol_date": "2026-05-04",
      "ai_estimate_total": 2850.00,
      "reason_for_review": "customer_appeal",
      "time_in_queue": "1d 5h",
      "current_status": "human_review_pending"
    }
  ]
}
```

**Example Request**:
```bash
# Get pending claims for adjustor ADJ-001, sorted by oldest first
curl "http://localhost:8000/api/v1/adjustors/ADJ-001/claims/pending?sort=oldest"
```

---

#### 7.3.3 Get Adjustor Statistics

**Endpoint**: `GET /api/v1/adjustors/{adjustor_id}/statistics`

**Purpose**: Get workload and performance metrics for an adjustor.

**Path Parameters**:
- `adjustor_id` (required, string): Adjustor identifier

**Response** (200 OK):
```json
{
  "pending_reviews": 2,
  "completed_today": 0,
  "completed_this_week": 5,
  "average_review_time_minutes": 8.0,
  "total_reviews_all_time": 47
}
```

**Example Request**:
```bash
curl http://localhost:8000/api/v1/adjustors/ADJ-001/statistics
```

---

#### 7.3.4 Assign Claim to Adjustor

**Endpoint**: `POST /api/v1/adjustors/{adjustor_id}/claims/{claim_id}/assign`

**Purpose**: Assign a specific claim to a specific adjustor. Used by Customer Portal auto-assignment logic.

**Path Parameters**:
- `adjustor_id` (required, string): Adjustor identifier (e.g., "ADJ-001")
- `claim_id` (required, integer): Claim identifier

**Request Body**: None (assignment parameters are in URL path)

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Claim 2001 assigned to Sarah Chen",
  "data": {
    "claim_id": 2001,
    "adjustor_id": "ADJ-001",
    "adjustor_name": "Sarah Chen",
    "assigned_at": "2026-05-05T14:30:22",
    "event_id": 15
  }
}
```

**Error Responses**:

**404 Not Found** - Adjustor not found or not active:
```json
{
  "detail": "Active adjustor ADJ-999 not found"
}
```

**404 Not Found** - Claim not found:
```json
{
  "detail": "Claim 9999 not found"
}
```

**400 Bad Request** - Claim not in correct status:
```json
{
  "detail": "Claim must be in human_review_pending status, currently: customer_decision_pending"
}
```

**Validation Rules**:
- Claim must be in `human_review_pending` status
- Adjustor must exist and have `status = 'active'`
- Creates assignment event in `claims_events` table with:
  - `action`: `assign_to_adjustor`
  - `action_by`: `AI agent` (auto-assignment system)
  - `comments`: "Claim assigned to adjustor {name} ({id})"

**Example Request**:
```bash
# Assign claim 2001 to adjustor ADJ-001
curl -X POST http://localhost:8000/api/v1/adjustors/ADJ-001/claims/2001/assign
```

**State Transition**:
- Claim remains in `human_review_pending` status
- Assignment is logged as an event, not a state change
- Adjustor can now see claim in their review queue

**Integration with Customer Portal**:
1. Customer Portal detects claim is in `human_review_pending`
2. Calls `GET /api/v1/adjustors?status_filter=active`
3. Selects adjustor with minimum `pending_reviews`
4. Calls `POST /api/v1/adjustors/{selected_id}/claims/{claim_id}/assign`
5. Shows success message with adjustor name

---

## 8. State Machine Integration

### 8.1 Action to State Transition Mapping

| Action | Current State | Next State | Actor |
|--------|---------------|------------|-------|
| `create_claim` | — | `FNOL` | customer |
| `upload_damage_photos` | `FNOL` | `image_uploaded` | customer |
| `delete_image` | `image_uploaded` | `image_uploaded` | customer |
| `generate_estimate` | `image_uploaded` | `loss_estimated_ai` | AI agent |
| `flag_for_human_review` | `loss_estimated_ai` | `human_review_pending` | AI agent |
| — | `loss_estimated_ai` | `customer_decision_pending` | system |
| `accept_estimate` | `customer_decision_pending` | `loss_approved` | customer |
| `appeal_estimate` | `customer_decision_pending` | `loss_appealed` | customer |
| — | `loss_appealed` | `human_review_pending` | system |
| `assign_to_adjustor` | `human_review_pending` | `human_review_pending` | AI agent (system) |
| — | `loss_approved` | `sent_for_payment` | system |
| `approve_claim` | `human_review_pending` | `human_review_completed` | adjustor |
| `approved_appeal` | `human_review_completed` | `customer_decision_pending` | adjustor |
| `denied_appeal` | `human_review_completed` | `routed_to_traditional` | adjustor |
| `route_to_traditional` | `human_review_completed` | `routed_to_traditional` | adjustor |
| — | `routed_to_traditional` | `traditional_processing_active` | system |
| `initiate_payment` | `loss_approved` | `sent_for_payment` | admin |
| `payment_sent` | `sent_for_payment` | `claim_paid` | admin |
| `close_claim` | `claim_paid` | `claim_closed` | admin |
| `close_claim` | `traditional_processing_active` | `claim_closed` | admin |

### 8.2 State Transition Validation Rules

**Validation Logic**:
```python
VALID_TRANSITIONS = {
    "FNOL": ["image_uploaded"],
    "image_uploaded": ["loss_estimated_ai"],
    "loss_estimated_ai": ["customer_decision_pending", "human_review_pending"],
    "customer_decision_pending": ["loss_approved", "loss_appealed"],
    "loss_approved": ["sent_for_payment"],
    "loss_appealed": ["human_review_pending"],
    "human_review_pending": ["human_review_completed"],
    "human_review_completed": ["customer_decision_pending", "routed_to_traditional"],
    "sent_for_payment": ["claim_paid"],
    "claim_paid": ["claim_closed"],
    "routed_to_traditional": ["traditional_processing_active"],
    "traditional_processing_active": ["claim_closed"],
    "claim_closed": []  # Terminal state
}
```

**Transition Validation Function**:
```python
def validate_transition(current_state: str, new_state: str) -> bool:
    """Validate if state transition is allowed"""
    valid_next_states = VALID_TRANSITIONS.get(current_state, [])
    return new_state in valid_next_states
```

### 8.3 Event Logging Requirements

**Every state transition MUST log an event**:

```python
def log_claim_event(
    claim_id: int,
    status: str,
    action: str,
    action_by: str,
    action_by_identity: str,
    comments: str = ""
):
    """Log claim event to claims_events table"""
    event = ClaimEvent(
        claim_id=claim_id,
        event_date=date.today(),
        event_time=datetime.now().time(),
        status=status,
        action=action,
        action_by=action_by,
        action_by_identity=action_by_identity,
        comments=comments
    )
    db.add(event)
    db.commit()
```

---

## 9. Error Handling

### 9.1 Standard Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "additional context"
    }
  },
  "meta": {
    "timestamp": "2026-05-03T10:30:00Z",
    "request_id": "req_1234567890",
    "path": "/api/v1/claims/1000"
  }
}
```

### 9.2 Error Code Catalog

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `RESOURCE_NOT_FOUND` | 404 | Resource doesn't exist |
| `INVALID_STATE_TRANSITION` | 409 | State transition not allowed |
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `DUPLICATE_RESOURCE` | 409 | Resource already exists |
| `MAX_IMAGES_EXCEEDED` | 400 | Maximum images per claim reached |
| `INVALID_FILE_TYPE` | 400 | Unsupported file type |
| `FILE_TOO_LARGE` | 400 | File exceeds size limit |
| `POLICY_NOT_ACTIVE` | 400 | Policy expired or not yet effective |
| `VEHICLE_NOT_COVERED` | 400 | Vehicle not on policy |
| `ESTIMATE_NOT_FOUND` | 404 | Estimate doesn't exist |
| `PAYMENT_MISMATCH` | 409 | Payment amount doesn't match claim |
| `INTERNAL_ERROR` | 500 | Server error |

### 9.3 Validation Error Format

**Validation errors return detailed field-level errors**:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "errors": [
        {
          "field": "fnol_date",
          "message": "Date cannot be in the future",
          "type": "value_error"
        },
        {
          "field": "vin",
          "message": "VIN must be exactly 17 characters",
          "type": "value_error"
        }
      ]
    }
  }
}
```

### 9.4 Exception Handling Strategy

**FastAPI Exception Handlers**:

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(StateTransitionError)
async def state_transition_handler(request: Request, exc: StateTransitionError):
    return JSONResponse(
        status_code=409,
        content={
            "error": {
                "code": "INVALID_STATE_TRANSITION",
                "message": str(exc),
                "details": {
                    "current_state": exc.current_state,
                    "requested_state": exc.new_state,
                    "valid_transitions": exc.valid_transitions
                }
            }
        }
    )

@app.exception_handler(ResourceNotFoundError)
async def not_found_handler(request: Request, exc: ResourceNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "RESOURCE_NOT_FOUND",
                "message": f"{exc.resource_type} not found",
                "details": {"resource_id": exc.resource_id}
            }
        }
    )
```

---

## 10. Implementation Guide

### 10.1 FastAPI Project Structure

```
app/
├── main.py                  # FastAPI app initialization, middleware, CORS
├── config.py                # Settings (database URL, env vars)
├── database.py              # SQLAlchemy engine, session management
├── dependencies.py          # Dependency injection (get_db, get_current_user)
│
├── models/                  # SQLAlchemy ORM models (database tables)
│   ├── __init__.py
│   ├── customer.py          # Customer, Policy, Vehicle models
│   ├── claim.py             # Claim, ClaimImage models
│   ├── damage.py            # Damage model
│   └── claim_event.py       # ClaimEvent model
│
├── schemas/                 # Pydantic models (request/response validation)
│   ├── __init__.py
│   ├── customer.py          # CustomerResponse, CustomerCreate
│   ├── claim.py             # ClaimResponse, ClaimCreate, ClaimUpdate
│   ├── damage.py            # DamageResponse, EstimateResponse
│   └── common.py            # PaginationParams, ErrorResponse
│
├── routers/                 # API route handlers
│   ├── __init__.py
│   ├── customers.py         # /api/v1/customers endpoints
│   └── claims.py            # /api/v1/claims endpoints
│
├── services/                # Business logic layer
│   ├── __init__.py
│   ├── claim_service.py     # Claim CRUD operations
│   ├── estimate_service.py  # AI/human estimate generation
│   ├── state_machine.py     # State transition validation
│   ├── event_logger.py      # Event logging
│   └── payment_service.py   # Payment initiation/confirmation
│
├── exceptions.py            # Custom exception classes
├── constants.py             # Enums, constants (states, actions)
│
└── tests/
    ├── __init__.py
    ├── conftest.py          # pytest fixtures
    ├── test_customers.py    # Customer API tests
    ├── test_claims.py       # Claims API tests
    └── test_state_machine.py # State transition tests
```

### 10.2 Database Connection (SQLAnywhere)

**config.py**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlanywhere://user:password@localhost:2638/insurance_db"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    
    class Config:
        env_file = ".env"

settings = Settings()
```

**database.py**:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True  # Verify connections before using
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Connection String Format**:
```
sqlanywhere://[user[:password]@][host[:port]]/[dbname]
```

### 10.3 Error Handling Patterns

**exceptions.py**:
```python
class AppException(Exception):
    """Base exception for application errors"""
    pass

class ResourceNotFoundError(AppException):
    def __init__(self, resource_type: str, resource_id: int):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(f"{resource_type} {resource_id} not found")

class StateTransitionError(AppException):
    def __init__(self, current_state: str, new_state: str, valid_transitions: list):
        self.current_state = current_state
        self.new_state = new_state
        self.valid_transitions = valid_transitions
        super().__init__(
            f"Invalid transition from {current_state} to {new_state}. "
            f"Valid: {valid_transitions}"
        )

class ValidationError(AppException):
    def __init__(self, errors: list):
        self.errors = errors
        super().__init__("Validation failed")
```

**main.py** (exception handlers):
```python
from fastapi import FastAPI
from app.exceptions import StateTransitionError, ResourceNotFoundError

app = FastAPI(title="Insurance Claims API", version="1.0")

@app.exception_handler(StateTransitionError)
async def state_transition_handler(request, exc):
    return JSONResponse(status_code=409, content={...})

@app.exception_handler(ResourceNotFoundError)
async def not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={...})
```

### 10.4 Testing Strategy

**conftest.py** (test fixtures):
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Test database
TEST_DATABASE_URL = "sqlanywhere://test_user:test_pass@localhost:2638/test_db"
engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    session = TestSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    """FastAPI test client"""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
```

**test_claims.py**:
```python
def test_create_claim_fnol(client, db_session):
    """Test FNOL creation"""
    # Setup: Create customer, vehicle, policy
    customer = Customer(customer_id=100, fname="Jane", lname="Doe", ...)
    db_session.add(customer)
    db_session.commit()
    
    # Act: Create claim
    response = client.post(
        "/api/v1/customers/100/claims",
        json={
            "vin": "1ABC23456789DEFG",
            "policy_number": "PA-992384-01",
            "fnol_date": "2026-05-03",
            "fnol_time": "10:30:00",
            "date_of_damage": "2026-05-02",
            "is_drivable": True
        }
    )
    
    # Assert
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["current_status"] == "FNOL"
    assert data["customer_id"] == 100

def test_invalid_state_transition(client, db_session):
    """Test invalid state transition is rejected"""
    # Setup: Claim in 'claim_paid' state
    claim = Claim(claim_id=1000, current_status="claim_paid", ...)
    db_session.add(claim)
    db_session.commit()
    
    # Act: Try to transition to invalid state
    response = client.put(
        "/api/v1/claims/1000/state",
        json={"new_status": "loss_approved"}
    )
    
    # Assert
    assert response.status_code == 409
    error = response.json()["error"]
    assert error["code"] == "INVALID_STATE_TRANSITION"
```

---

## 11. Configuration Management

### 11.1 Configuration File (`api-config.yaml`)

**⚠️ Configuration is managed via YAML file, NOT environment variables.**

Create `api-config.yaml` file in project root:

```yaml
# API Configuration
api:
  title: "Insurance Claims API"
  version: "v1"
  debug: true
  host: "0.0.0.0"
  port: 8000

# Database Configuration
database:
  url: "sqlanywhere://user:password@localhost:2638/insurance_db"
  pool_size: 5
  max_overflow: 10
  echo: false

# Image Storage Configuration
storage:
  images_root_folder: "uploads"
  max_upload_size_mb: 10
  allowed_image_types:
    - "jpg"
    - "jpeg"
    - "png"
    - "heic"
  max_images_per_claim: 20

# AI/State Machine Configuration
ai:
  # Path to SOP document (AI agent instructions)
  sop_claims_document: "policies/damage_triage.md"
  
  # Path to claims rules YAML (business rules and thresholds)
  claims_rules_yaml: "policies/rules.yaml"
  
  # Inline thresholds (can be overridden by claims_rules_yaml)
  confidence:
    high_threshold: 0.55
    low_threshold: 0.35
  fraud:
    risk_threshold: 0.1
  estimate:
    human_review_threshold: 5000.00

# Logging Configuration
logging:
  level: "INFO"
  file: "logs/api.log"
  max_bytes: 10485760  # 10MB
  backup_count: 5
  format: "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

# CORS Configuration
cors:
  allow_origins:
    - "*"
  allow_credentials: true
  allow_methods:
    - "*"
  allow_headers:
    - "*"
```

### 11.2 Development vs Production Configuration

**Development** (`api-config.yaml`):
```yaml
api:
  debug: true
  host: "localhost"
  port: 8000

database:
  url: "sqlanywhere://dev_user:dev_pass@localhost:2638/dev_db"
  echo: true  # Log SQL queries

logging:
  level: "DEBUG"

storage:
  images_root_folder: "uploads_dev"
```

**Production** (`api-config.production.yaml`):
```yaml
api:
  debug: false
  host: "0.0.0.0"
  port: 8000

database:
  url: "sqlanywhere://prod_user:prod_pass@db.prod.com:2638/prod_db"
  echo: false
  pool_size: 20
  max_overflow: 40

logging:
  level: "WARNING"

storage:
  images_root_folder: "/var/app/uploads"
```

**⚠️ Production Deployment Warning**: 

Version 1.0 is a **PROTOTYPE** and should **NOT** be deployed to production environments. This version:
- Has **NO authentication or authorization**
- Has **NO security controls**
- Is intended for **isolated development/demo environments only**

If you must deploy for demonstration purposes:
- Use a **private network** or VPN
- **Do NOT expose to public internet**
- Use **test/synthetic data only** (no real customer PII)
- Add a reverse proxy with basic auth as a temporary measure
- Plan to upgrade to v2.0 with proper security before any production use

### 11.3 Configuration File Selection

**Specify configuration file at startup:**

```bash
# Use default api-config.yaml
uvicorn app.main:app --reload

# Use specific configuration file
CONFIG_FILE=api-config.production.yaml uvicorn app.main:app

# Or pass as command-line argument (if implemented)
python -m app.main --config api-config.production.yaml
```

**Configuration Loader** (in `config.py`):
```python
import os
from pathlib import Path

config_file = os.getenv("CONFIG_FILE", "api-config.yaml")
settings = Settings(config_path=config_file)
```

### 11.4 External Rules and SOP Documents

**Claims Rules File** (`policies/rules.yaml`):

The main configuration references an external rules file for business logic:

```yaml
# Referenced from api-config.yaml: ai.claims_rules_yaml
version: "1.0"
confidence:
  high_threshold: 0.55
  low_threshold: 0.35
fraud:
  risk_threshold: 0.1
estimate:
  human_review_threshold: 5000.00
  auto_approve_max: 2500.00
# ... additional business rules
```

**Purpose**: 
- Centralized business rules that can be updated without changing code
- Versioned for audit trail
- Can be updated by business analysts without developer involvement

**SOP Document** (`policies/damage_triage.md`):

Standard Operating Procedures for AI agent decision-making:

```markdown
# Damage Triage SOP

## AI Agent Instructions

### High Confidence (>0.55)
- Present estimate directly to customer
- Include breakdown of damages
- Provide repair recommendations

### Medium Confidence (0.35-0.55)
- Flag for human review
- Highlight areas of uncertainty
- Request adjustor validation

### Low Confidence (<0.35)
- Route to traditional process
- Recommend physical inspection
```

**Purpose**:
- Provides context and instructions to AI agent
- Documents business logic and decision criteria
- Can be used for LLM prompt engineering in future implementations

**Benefits**:
1. **Separation of Concerns**: Business rules separate from code
2. **Easy Updates**: Change thresholds without redeployment
3. **Auditability**: Version control for compliance
4. **Flexibility**: Different rules for different environments
5. **Documentation**: SOP serves as living documentation

---

## 12. References

### 12.1 Internal Documentation

- **State Machine**: [claims-state-machine.mmd](./diagrams/claims-state-machine.mmd)
- **Database ERD**: [claim-database-erd.mmd](./diagrams/claim-database-erd.mmd)
- **Design Thoughts**: [Thoughts.md](./Thoughts.md)
- **Color Palette**: [color-palette-dark.css](./diagrams/color-palette-dark.css)

### 12.2 External Documentation

- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Pydantic**: https://docs.pydantic.dev/
- **SQLAnywhere Python Driver**: https://pypi.org/project/sqlanydb/
- **pytest**: https://docs.pytest.org/

### 12.3 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-05-03 | Initial API specifications |

---

**END OF DOCUMENT**
