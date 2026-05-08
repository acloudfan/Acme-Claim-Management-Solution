# Adjustor Portal UI Design Document
## AI-Powered Auto Insurance Claims Management - Human Review Interface

**Version:** 1.1  
**Date:** 2026-05-05  
**Status:** Design Document  
**Target Audience:** Insurance Adjustors (Human Reviewers)  
**Company:** ACME Insurance

---

## Table of Contents

1. [Overview](#1-overview)
2. [Design Philosophy](#2-design-philosophy)
3. [Technology Stack](#3-technology-stack)
4. [Project Structure](#4-project-structure)
5. [Authentication & Authorization](#5-authentication--authorization)
6. [User Flow](#6-user-flow)
7. [Page-by-Page Design](#7-page-by-page-design)
8. [Component Library](#8-component-library)
9. [API Integration](#9-api-integration)
10. [State Management](#10-state-management)
11. [Business Logic](#11-business-logic)
12. [Development Guidelines](#12-development-guidelines)

---

## 1. Overview

### 1.1 Purpose

The Adjustor Portal is a React-based web application that enables human insurance adjustors to:
- Review claims flagged for human review (low AI confidence or customer appeals)
- View AI-generated damage assessments with annotated images
- Add damages missed by AI detection
- Adjust cost estimates (labor rates, hours, parts costs)
- Approve or deny customer appeals with detailed notes
- Track review workload and statistics

### 1.2 Key Features

- ✅ **Workload Dashboard**: View pending claims queue with statistics
- ✅ **Detailed Claim Review**: Access full claim history, images, AI estimates
- ✅ **Image Analysis Tools**: Zoom/pan on damage photos with AI bounding boxes and confidence scores
- ✅ **Manual Damage Entry**: Add damages AI missed with cost estimation
- ✅ **Cost Adjustment Interface**: Modify labor rates, hours, parts costs with notes
- ✅ **Dual-Note System**: Customer-facing notes + internal notes for audit trail
- ✅ **Decision Actions**: Deny appeal (uphold AI) or revise estimate
- ✅ **Event Timeline**: Full audit trail of claim lifecycle

### 1.3 Design Philosophy

**Professional Corporate Theme** (distinct from customer portal):
- **Utilitarian**: Data-dense interface optimized for efficiency
- **Professional**: Corporate color scheme (darker, more formal than customer portal)
- **Transparent**: Clear reasoning behind AI decisions and adjustor overrides
- **Efficient**: Keyboard shortcuts, bulk actions, minimal clicks
- **Desktop-Only**: Optimized for professional workstation use

**Branding:**
- **Company Name:** ACME Insurance
- **Logo Location:** `src/common/assets/ACME-logo.png`
- **Logo Placement:** Top-left corner of header on all pages (similar to customer portal)
- **Logo Size:** ~120-150px width, maintain aspect ratio
- **Logo Link:** Links to Dashboard page (`/dashboard`) when clicked

**Color Palette** (Corporate Theme):
- Primary: Dark blue-gray (#1E3A5F) — Trust, professionalism
- Accent: Amber (#F59E0B) — Action items, warnings
- Success: Emerald (#10B981) — Approved actions
- Error: Rose (#EF4444) — Denied appeals, critical issues
- Neutral: Cool grays (#374151, #6B7280, #9CA3AF) — Background hierarchy

### 1.4 Key Differences from Customer Portal

| Aspect | Customer Portal | Adjustor Portal |
|--------|----------------|-----------------|
| **Audience** | Policyholders | Professional adjustors |
| **Design** | Friendly, approachable (GEICO-style) | Corporate, utilitarian |
| **Data Density** | Simplified, curated | Detailed, comprehensive |
| **Actions** | Submit, accept, appeal | Review, adjust, approve/deny |
| **Tone** | Reassuring, transparent | Analytical, precise |
| **Auth** | Email + password | Adjustor ID dropdown + password |

---

## 2. Design Philosophy

### 2.1 Design Principles

**1. Efficiency Over Aesthetics**
- Dense information display (tables, compact cards)
- Keyboard shortcuts for common actions
- Minimal animation/decoration
- Fast load times

**2. Transparency & Auditability**
- Every adjustment requires a note
- Dual-note system (customer vs. internal)
- Full event timeline visible
- AI confidence scores always displayed

**3. Decision Support**
- Side-by-side comparison of AI vs. manual adjustments
- Cost impact calculations (before/after)
- Statistical context (average repair costs, typical labor hours)
- Historical data (adjustor's past decisions)

**4. Error Prevention**
- Validation on all cost inputs
- Warnings for unusual adjustments (>50% change)
- Confirm dialogs for final submission
- Auto-save draft notes

---

## 3. Technology Stack

### 3.1 Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 19.2.5 | UI framework |
| **React Router** | 7.14.2 | Routing |
| **Vite** | Latest | Build tool (fast dev server, HMR) |
| **Tailwind CSS** | 3.4.19 | Utility-first styling (custom corporate theme) |
| **Axios** | 1.16.0 | HTTP client with interceptors |
| **js-yaml** | 4.1.1 | Configuration file parsing |
| **lucide-react** | 1.14.0 | Icon library |
| **react-zoom-pan-pinch** | 3.4.4 | Image zoom/pan controls |

### 3.2 Backend API (Already Exists, Extensions Needed)

- **FastAPI** (Python) — REST API server
- **SQLAlchemy** — ORM for PostgreSQL/SQLite
- **Pydantic** — Request/response validation

### 3.3 Development Tools

- **ESLint** — Code linting
- **PostCSS** — CSS processing (autoprefixer)
- **Vite Dev Server** — Hot module replacement

---

## 4. Project Structure

```
src/ui/adjustor/
├── public/
│   ├── adjustor-portal-config.yaml    # Configuration (API URL, features)
│   └── assets/                        # Static images, logos
│
├── src/
│   ├── api/                           # Backend API integration
│   │   ├── client.js                  # Axios instance (interceptors, auth headers)
│   │   ├── config.js                  # YAML config loader
│   │   ├── adjustors.js               # Adjustor endpoints (pending claims, workload)
│   │   └── claims.js                  # Claim review endpoints (review/complete, add/update damages)
│   │
│   ├── components/                    # Reusable UI components
│   │   ├── common/                    # Shared components (copied from customer portal)
│   │   │   ├── Button.jsx
│   │   │   ├── Card.jsx
│   │   │   ├── Input.jsx
│   │   │   ├── Textarea.jsx
│   │   │   ├── Modal.jsx
│   │   │   ├── Badge.jsx
│   │   │   └── Spinner.jsx
│   │   │
│   │   ├── layout/                    # Page layout components
│   │   │   ├── Layout.jsx             # Main layout wrapper
│   │   │   ├── Header.jsx             # Adjustor navigation header
│   │   │   └── Footer.jsx             # Standard footer
│   │   │
│   │   └── claims/                    # Claim-specific components
│   │       ├── ClaimCard.jsx          # Claim summary card (queue view)
│   │       ├── DamageList.jsx         # List of damages with costs
│   │       ├── DamageEditor.jsx       # Edit existing damage costs
│   │       ├── DamageCreator.jsx      # Add new manual damage
│   │       ├── ImageViewer.jsx        # Zoom/pan image with bounding boxes
│   │       ├── CostSummary.jsx        # Before/after cost comparison
│   │       ├── EventTimeline.jsx      # Claim event history
│   │       └── NotesEditor.jsx        # Dual-note editor (customer + internal)
│   │
│   ├── context/                       # React Context for global state
│   │   └── AuthContext.jsx            # Adjustor authentication
│   │
│   ├── hooks/                         # Custom React hooks
│   │   ├── useAuth.js                 # Authentication hook
│   │   └── useDamageCalculator.js     # Cost calculation logic
│   │
│   ├── pages/                         # Full page components
│   │   ├── LoginPage.jsx              # Adjustor login (ID + password)
│   │   ├── DashboardPage.jsx          # Workload dashboard (statistics + filters)
│   │   ├── ClaimQueuePage.jsx         # Pending claims list
│   │   ├── ClaimDetailPage.jsx        # Full claim review page
│   │   └── ReviewCompletePage.jsx     # Final review submission
│   │
│   ├── utils/                         # Utility functions
│   │   ├── constants.js               # Status, severity, actor types (reuse from customer)
│   │   ├── formatters.js              # Date, currency, phone formatting (reuse)
│   │   ├── validators.js              # Input validation (cost ranges, required fields)
│   │   └── calculations.js            # Cost calculations (labor + parts)
│   │
│   ├── App.jsx                        # Root component (routing)
│   ├── main.jsx                       # Entry point
│   └── index.css                      # Global Tailwind + custom styles
│
├── .env                               # Environment variables (API URL)
├── vite.config.js                     # Vite build configuration
├── tailwind.config.js                 # Tailwind theme (corporate colors)
├── postcss.config.js                  # PostCSS plugins
├── package.json                       # Dependencies
└── README.md                          # Setup instructions
```

---

## 5. Authentication & Authorization

### 5.1 Authentication Model

**Mock Authentication** (for demo/prototype):

**Login Flow:**
1. Adjustor selects ID from dropdown:
   - `ADJ-001` — Sarah Chen (Senior Adjustor)
   - `ADJ-002` — Michael Torres (Collision Specialist)
   - `ADJ-003` — Emily Watson (Claims Supervisor)
2. Enters hardcoded password: `adjustor123`
3. On success:
   - Store `adjustor_id` in localStorage
   - Store `adjustor_name` in localStorage
   - Redirect to Dashboard

**AuthContext API:**
```javascript
{
  adjustorId: string | null,
  adjustor: { id, name, email, role } | null,
  loading: boolean,
  login(adjustorId: string, password: string): Promise<void>,
  logout(): void,
  isAuthenticated(): boolean
}
```

### 5.2 Authorization (Future Enhancement)

**Current:** No role-based access control (all adjustors see all claims)

**Future:** Role-based permissions:
- **Senior Adjustor**: Review any claim, approve >$10K estimates
- **Specialist**: Review claims in specialty area (collision, flood, etc.)
- **Supervisor**: Audit adjustor decisions, reassign claims

---

## 6. User Flow

### 6.1 High-Level Flow

```
┌─────────────┐
│ Login Page  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Dashboard       │ ← Statistics + Quick Actions
│ - Pending: 12  │
│ - Today: 5      │
│ - Avg Time: 8m │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│ Claim Queue Page    │ ← List of all pending claims
│ [Filter] [Sort]     │
│ ┌─────────────────┐ │
│ │ Claim #1001     │ │ ← Click to review
│ │ Claim #1002     │ │
│ └─────────────────┘ │
└───────────┬─────────┘
            │
            ▼
┌──────────────────────────┐
│ Claim Detail Page        │
│ ┌──────────────────────┐ │
│ │ Customer Info        │ │
│ │ Vehicle Details      │ │
│ │ AI Estimate Summary  │ │
│ │ Images (zoom/pan)    │ │
│ │ Damages List         │ │
│ └──────────────────────┘ │
│ [Edit Costs] [Add Damage]│
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ Review Complete Page     │
│ ┌──────────────────────┐ │
│ │ Action Choice:       │ │
│ │ ○ Deny Appeal        │ │ ← No changes, uphold AI
│ │ ○ Revise Estimate    │ │ ← Made changes
│ │                      │ │
│ │ Customer Note:       │ │ ← Visible to customer
│ │ [Text area]          │ │
│ │                      │ │
│ │ Internal Note:       │ │ ← Audit only
│ │ [Text area]          │ │
│ └──────────────────────┘ │
│ [Submit Review]          │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ Confirmation Modal       │
│ "Review submitted        │
│  Claim #1001 returned    │
│  to customer"            │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ Return to Dashboard      │
└──────────────────────────┘
```

### 6.2 Detailed Workflows

#### Workflow A: Deny Appeal (No Changes)

1. Adjustor reviews claim
2. Agrees with AI estimate
3. Clicks **"Deny Appeal"** action
4. Enters **Customer Note**: "After careful review, the AI estimate is accurate. The damages identified match standard repair costs for your vehicle."
5. Enters **Internal Note**: "Reviewed all images. AI detection accurate. Costs within range for 2022 Honda Accord rear-end collision."
6. Submits review
7. System:
   - Records `DENIED_APPEAL` action
   - Updates status: `human_review_pending` → `human_review_completed`
   - Triggers customer notification
   - Returns claim to customer portal in `customer_decision_pending` state
   - Customer sees same estimate with adjustor note

#### Workflow B: Revise Estimate (With Changes)

**Scenario:** Adjustor increases labor hours and adjusts parts cost

1. Adjustor reviews claim
2. Identifies issues:
   - AI missed scratches on door
   - Labor hours too low (AI: 2h, should be 3h)
   - Parts cost underestimated
3. Actions:
   - **Add New Damage**: Click "Add Manual Damage"
     - Select: "Scratch - Front Driver Door"
     - Enter description: "3-inch vertical scratch, paint depth"
     - Enter costs: Labor 1.5h, Parts $200, Total $434
     - Add note: "Visible in image IMG_003, missed by AI"
   - **Adjust Existing Damage**: Click "Edit" on "Dent - Rear Bumper"
     - Change labor hours: 2 → 3
     - Change parts cost: $500 → $650
     - Add note: "Bumper replacement needed, not just repair"
4. Review cost summary:
   - **Original AI Estimate**: $1,750
   - **Revised Estimate**: $2,584 (+$834, +47.6%)
5. Select **"Revise Estimate"** action
6. Enter **Customer Note**: "We've completed our review and made adjustments to the estimate based on additional damages and parts availability. The revised total is $2,584."
7. Enter **Internal Note**: "AI missed door scratch in IMG_003. Bumper damage requires replacement per OEM specs, not repair. Labor adjusted to match shop manual."
8. Submit review
9. System:
   - Records `REVISED_ESTIMATE` action
   - Creates new estimate_id (e.g., `1001_human_20260505_143022`)
   - Inserts new Damage record (scratch)
   - Updates existing Damage records (bumper)
   - Updates claim.active_estimate_id
   - Updates status: `human_review_pending` → `human_review_completed`
   - Returns claim to `customer_decision_pending`
   - Customer sees revised estimate with adjustor notes

---

## 7. Page-by-Page Design

### 7.1 Login Page

**Path:** `/login`

**Layout:**
- Centered login card (max-width: 400px)
- Corporate branding (logo, title)
- Professional, minimal design

**Components:**
```
┌─────────────────────────────┐
│    [ACME Logo]              │
│    ACME Insurance           │
│    Adjustor Portal          │
│                             │
│  Adjustor ID:               │
│  [Dropdown ▼]               │
│  ○ ADJ-001 - Sarah Chen     │
│  ○ ADJ-002 - Michael Torres │
│  ○ ADJ-003 - Emily Watson   │
│                             │
│  Password:                  │
│  [••••••••••]               │
│                             │
│  [Login Button]             │
│                             │
│  Version 1.1 | 2026-05-05   │
└─────────────────────────────┘
```

**Branding:**
- Display ACME logo at top of login card
- Logo source: `src/common/assets/ACME-logo.png`
- Logo size: ~80-100px width on login page (smaller than header)
- Company name: "ACME Insurance - Adjustor Portal"

**Fields:**
- **Adjustor ID**: Select dropdown
  - Options: ADJ-001, ADJ-002, ADJ-003 (with names)
  - Required, no validation beyond non-empty
- **Password**: Password input
  - Hardcoded: `adjustor123`
  - Client-side validation only

**Actions:**
- **Login Button**: Validate credentials, store in localStorage, redirect to `/dashboard`

**Error Handling:**
- Invalid password: Show error message below form
- Network error: Show "Unable to connect to server" message

---

### 7.2 Dashboard Page

**Path:** `/dashboard`

**Purpose:** High-level overview of adjustor's workload

**Layout:**
```
┌────────────────────────────────────────────────────────────┐
│  Header: [Logo] ACME Insurance Adjustor Portal  [Sarah Chen ▼]  │
└────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────┐
│         Workload Summary             │
│  ┌──────────┐ ┌──────────┐ ┌────────┐
│  │ Pending  │ │ Today    │ │ Avg    │
│  │   12     │ │   5      │ │  8m    │
│  └──────────┘ └──────────┘ └────────┘
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│  Recent Pending Claims               │
│  [View All →]                        │
│                                      │
│  ┌─────────────────────────────────┐│
│  │ #1001 | Jane Smith | $1,234     ││ ← Click to review
│  │ 2022 Honda Accord | 2h ago      ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │ #1002 | Bob Johnson | $3,456    ││
│  │ 2021 Tesla Model S | 5h ago     ││
│  └─────────────────────────────────┘│
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│  Quick Actions                       │
│  [View Queue] [My Stats] [Help]     │
└──────────────────────────────────────┘
```

**Sections:**

**1. Workload Summary (Stat Cards)**
- **Pending Reviews**: Count of claims in `human_review_pending` status
- **Completed Today**: Count of reviews completed by adjustor today
- **Average Review Time**: Avg time between claim entering queue and completion

**2. Recent Pending Claims (Table/List)**
- Show 5 most recent claims
- Columns:
  - Claim ID
  - Customer Name
  - Vehicle (Year Make Model)
  - AI Estimate Total
  - Time in Queue
- Click row to navigate to Claim Detail Page
- **"View All →"** button navigates to Claim Queue Page

**3. Quick Actions (Button Group)**
- **View Queue**: Navigate to `/claims/queue`
- **My Stats**: (Future) Adjustor performance metrics
- **Help**: (Future) Documentation/training resources

**Data Source:**
- `GET /api/v1/adjustors/{adjustor_id}/claims/pending?limit=5&sort=newest`
- `GET /api/v1/adjustors/{adjustor_id}/statistics`

---

### 7.3 Claim Queue Page

**Path:** `/claims/queue`

**Purpose:** Full list of all pending claims with filtering/sorting

**Layout:**
```
┌────────────────────────────────────────────────────────────┐
│  Header: [Logo] ACME Insurance Adjustor Portal  [Sarah Chen ▼]  │
└────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  Pending Claims (12)                                     │
│                                                          │
│  Filters: [All] [Appeals] [Low Confidence] [No Damage]  │
│  Sort:    [Oldest ▼] [Highest Amount] [Customer Name]   │
│  Search:  [🔍 Search by claim ID, customer name...]      │
└──────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│  Claim ID │ Customer     │ FNOL Date  │ Reason        │ AI Est │ Age │
│  ────────────────────────────────────────────────────────────────  │
│  1001     │ Jane Smith   │ 05/01/26   │ Low Conf      │ $1,234 │ 2h  │
│  1002     │ Bob Johnson  │ 05/01/26   │ Appeal        │ $3,456 │ 5h  │
│  1003     │ Alice Brown  │ 04/30/26   │ Low Conf      │ $2,100 │ 1d  │
│  ...                                                                │
└────────────────────────────────────────────────────────────────────┘

[< Prev] [1] [2] [3] [Next >]
```

**Features:**

**1. Filter Chips (Multi-Select)**
- **All**: Show all pending claims
- **Appeals**: Customer appealed AI estimate
- **Low Confidence**: AI confidence < 0.55
- **No Damage**: AI detected 0 damages (requested human review)

**2. Sort Dropdown**
- **Oldest First** (default): Sort by time in queue
- **Highest Amount**: Sort by AI estimate total (descending)
- **Customer Name**: Alphabetical

**3. Search Bar**
- Real-time search by:
  - Claim ID (exact match)
  - Customer name (fuzzy match)
  - VIN (partial match)

**4. Table Columns**
- **Claim ID**: Link to Claim Detail Page
- **Customer**: Name (link to claim)
- **FNOL Date**: First Notice of Loss date (MM/DD/YY format)
- **Reason**: Why claim is in queue
  - "Low Confidence" - AI confidence below threshold
  - "Appeal" - Customer appealed the AI estimate
  - "No Damage" - AI detected 0 damages
- **AI Estimate**: Total cost from AI analysis
- **Age**: Time since FNOL (hours if < 24h, days otherwise)
  - Format: "2h", "5h", "1d", "3d", etc.
  - Minimum display: "1 hour" (even if < 1 hour)

**5. Pagination**
- 20 claims per page
- Standard pagination controls

**Data Source:**
- `GET /api/v1/adjustors/{adjustor_id}/claims/pending`
- Query params: `filter`, `sort`, `search`, `page`, `limit`

**Actions:**
- Click any row → Navigate to `/claims/{claim_id}/review`

---

### 7.4 Claim Detail Page (Review Page)

**Path:** `/claims/{claim_id}/review`

**Purpose:** Main review interface with all claim details, images, damages, and editing tools

**Layout:** 70/30 Split-Screen Layout
- **Left Side (70%)**: Scrollable claim details, images, damages, review actions
- **Right Side (30%)**: Fixed AI Research Assistant (Chatbot) for adjustor queries

**Layout (Split-Screen with Chatbot):**

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  Header: [← Back to Queue] Claim #1001 Review                               │
└──────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────┬────────────────────────────────┐
│  LEFT PANEL (70% WIDTH) - Scrollable       │  RIGHT PANEL (30%) - Fixed     │
│  ═══════════════════════════════════════    │  ══════════════════════════    │

│                                              │                                │
│  Section 1: CLAIM OVERVIEW                  │  ┌──────────────────────────┐  │
│  ┌─────────────────┐ ┌─────────────────┐   │  │ 🤖 AI Research Assistant│  │
│  │ Customer Info   │ │ Vehicle Info    │   │  │                          │  │
│  │ Jane Smith      │ │ 2022 Honda      │   │  │ Ask about:               │  │
│  │ jane@email.com  │ │ Accord Silver   │   │  │ • Repair procedures      │  │
│  │ 555-1234        │ │ VIN: 1HGBH...   │   │  │ • Parts pricing          │  │
│  └─────────────────┘ └─────────────────┘   │  │ • Labor standards        │  │
│                                              │  │ • Policy coverage        │  │
│  ┌───────────────────────────────────────┐  │  │ • Damage assessment      │  │
│  │ Policy: POL-2026-001                  │  │  └──────────────────────────┘  │
│  │ FNOL Date: May 1, 2026 2:15 PM       │  │                                │
│  │ Damage Date: May 1, 2026              │  │  [Chat Messages]               │
│  │ Vehicle Drivable: Yes                 │  │  ┌──────────────────────────┐  │
│  └───────────────────────────────────────┘  │  │ 💬 You: What's the       │  │
│                                              │  │    typical repair time   │  │
│  ┌──────────────────────────────────────┐   │  │    for a rear bumper?    │  │
│  │ Section 2: AI ESTIMATE SUMMARY       │   │  └──────────────────────────┘  │
│  │ AI Estimate Total: $1,234.00         │   │  ┌──────────────────────────┐  │
│  │ Damages Detected: 2                  │   │  │ 🤖 Assistant: For a 2022 │  │
│  │ Average Confidence: 87%              │   │  │    Honda Accord rear     │  │
│  │ Reason for Review: Customer appealed │   │  │    bumper replacement... │  │
│  └──────────────────────────────────────┘   │  └──────────────────────────┘  │
│                                              │                                │
│  Section 3: DAMAGE IMAGES...                │  [Input Box]                   │
│  (continues scrolling...)                   │  ┌──────────────────────────┐  │
│                                              │  │ Type your question...    │  │
└─────────────────────────────────────────────┴──│ [Send]                   │  │
                                                 └──────────────────────────┘  │
                                                 └────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  Section 2: AI ESTIMATE SUMMARY                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ AI Estimate Total: $1,234.00                        │ │
│  │ Damages Detected: 2                                 │ │
│  │ Average Confidence: 87%                             │ │
│  │ Current Total: $1,234.00                            │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  Section 2.5: CUSTOMER APPEAL (if appeal exists)         │
│  ⚠️  Customer Appeal                                     │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ 🛑 First Appeal (May 2, 2026):                      │ │
│  │                                                     │ │
│  │ "The estimate seems too low. The front bumper      │ │
│  │  damage is more severe than indicated and will     │ │
│  │  require complete replacement, not just repair."   │ │
│  │                                                     │ │
│  │ [Yellow highlighted box with italic quoted text]   │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  Note: Only displayed if first_appeal_reason or         │
│        second_appeal_reason exists in claim data        │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  Section 3: DAMAGE IMAGES (with zoom/pan)                │
│  ┌──────────────────────────────────────────┐            │
│  │  [<] [>] Image 1 of 3                    │            │
│  │                                           │            │
│  │  ┌───────────────────────────────────┐   │            │
│  │  │  [Damage Photo with Bounding Box] │   │            │
│  │  │  🔍 Zoom In/Out  ↔ Pan           │   │            │
│  │  │                                   │   │            │
│  │  │  🟦 Dent - Rear Bumper (87%)     │   │            │
│  │  └───────────────────────────────────┘   │            │
│  │                                           │            │
│  │  [Show Original] [Show All Boxes]        │            │
│  └──────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  Section 3.5: LABOR RATE CONFIGURATION                   │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Labor Rate Information                              │ │
│  │                                                     │ │
│  │ State:  [CA ▼]                    (editable)       │ │
│  │                                                     │ │
│  │ Average Labor Cost: [$156.00/hour]  (editable)    │ │
│  │                                                     │ │
│  │ Note: Changing labor rate will recalculate all     │ │
│  │       damage estimates                             │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  Section 4: DAMAGES LIST (Editable)                      │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ AI-Detected Damages (2)    [+ Add Manual Damage]   │ │
│  │                                                     │ │
│  │ ┌─────────────────────────────────────────────────┐│ │
│  │ │ 1. Dent - Rear Bumper               [Edit]     ││ │
│  │ │    Severity: Moderate | Confidence: 87%        ││ │
│  │ │    Labor Cost: $312                            ││ │
│  │ │    Parts: $500                                 ││ │
│  │ │    Total: $812                                 ││ │
│  │ │    Image: IMG_001.jpg                          ││ │
│  │ └─────────────────────────────────────────────────┘│ │
│  │                                                     │ │
│  │ ┌─────────────────────────────────────────────────┐│ │
│  │ │ 2. Scratch - Rear Quarter Panel     [Edit]     ││ │
│  │ │    Severity: Light | Confidence: 92%           ││ │
│  │ │    Labor Cost: $234                            ││ │
│  │ │    Parts: $188                                 ││ │
│  │ │    Total: $422                                 ││ │
│  │ │    Image: IMG_002.jpg                          ││ │
│  │ └─────────────────────────────────────────────────┘│ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  Total: $1,234.00                                        │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  Section 5: EVENT TIMELINE                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ SLA Metrics                                         │ │
│  │ ┌──────────────────────┬────────────────────────┐   │ │
│  │ │ Time Since FNOL      │ SLA Time Remaining     │   │ │
│  │ │ 0 days, 0.7 hrs      │ 47.3 hrs (🟢 On Track)│   │ │
│  │ └──────────────────────┴────────────────────────┘   │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  [Expand/Collapse Events]                                │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ ● May 2, 2026 3:00 PM - Routed to Human Review     │ │
│  │ ● May 2, 2026 2:25 PM - Customer Appealed          │ │
│  │ ● May 2, 2026 2:21 PM - AI Estimate Generated      │ │
│  │ ● May 2, 2026 2:20 PM - Claim Submitted (FNOL)     │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  Note: SLA Metrics always visible. Events list can be   │
│        toggled. Events displayed in REVERSE chronological│
│        order (newest first). Each event shows date/time.│
│                                                          │
│  SLA Metrics:                                            │
│  • Time Since FNOL: Days and hours since FNOL event     │
│  • SLA Time Remaining: Hours until 48-hour SLA breach   │
│  • Color Codes:                                          │
│    🟢 Green: > 24 hours remaining                       │
│    🟡 Amber: 12-24 hours remaining                      │
│    🔴 Red: < 12 hours remaining                         │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  Section 6: REVIEW ACTIONS                               │
│  [Complete Review →]                                     │
└──────────────────────────────────────────────────────────┘
```

**Key Interactions:**

**1. Edit Existing Damage (Modal)**
- Click **[Edit]** button on damage card
- Opens modal with fields:
  - **Labor Hours**: Input (decimal, 0.1-100)
  - **Labor Rate**: Input ($/hour, 50-500)
  - **Parts Cost**: Input ($, 0-50000)
  - **Adjustor Note** (required): Textarea (e.g., "Increased labor to 3h per shop manual")
  - **Total**: Auto-calculated (read-only)
- Validation:
  - Warn if change > 50% from AI estimate
  - Require note if any field changes
- **[Save]** button: Update damage, recalculate total
- **[Cancel]** button: Discard changes

**2. Add Manual Damage (Modal)**
- Click **[+ Add Manual Damage]** button
- Opens modal with fields:
  - **Damage Type**: Dropdown (Scratch, Dent, Broken Part, Paint Damage, Glass Damage, etc.)
  - **Location**: Dropdown (Front Bumper, Rear Bumper, Hood, Roof, Doors, etc.)
  - **Description**: Textarea (required, e.g., "3-inch vertical scratch on driver door")
  - **Severity**: Dropdown (Light, Moderate, Severe)
  - **Image ID**: Dropdown (select from uploaded images)
  - **Labor Hours**: Input (required)
  - **Labor Rate**: Input (pre-filled with claim average, editable)
  - **Parts Cost**: Input (required)
  - **Adjustor Note** (required): Textarea (e.g., "Visible in IMG_003, missed by AI")
  - **Total**: Auto-calculated
- **[Add Damage]** button: Insert new damage row
- **[Cancel]** button: Discard

**3. Image Viewer**
- **Zoom Controls**: Zoom in/out buttons or scroll wheel
- **Pan**: Click and drag to pan
- **Navigation**: Left/right arrows to cycle through images
- **Toggle Boxes**: Show/hide AI bounding boxes
- **Original View**: Show original image without annotations
- **Confidence Display**: Hover over bounding box shows confidence %

**4. Customer Appeal Section (Section 2.5)**
- **Display Condition**: Only shown if `first_appeal_reason` OR `second_appeal_reason` exists
- **Location**: Between "AI Estimate Summary" and "Damage Images"
- **Visual Design**:
  - Yellow warning theme (bg-yellow-50, border-yellow-400)
  - Warning triangle icon on left
  - Card title: "Customer Appeal"
  - Badge indicating "First Appeal" or "Second Appeal"
- **Content for First Appeal**:
  - Label: "First Appeal (date)"
  - Appeal reason text in quoted, italic format
  - Light yellow background (bg-yellow-100) for quoted text
- **Content for Second Appeal**:
  - Shows both first and second appeals chronologically
  - Each appeal has its own date and quoted reason
  - Clearly distinguishes between first and second appeal
- **Purpose**: Provides immediate context to adjustor about why customer disputed the AI estimate
- **Data Source**:
  - `claim.first_appeal_reason` (Text)
  - `claim.first_appeal_date` (Date)
  - `claim.second_appeal_reason` (Text)
  - `claim.second_appeal_date` (Date)
  - `claim.appeal_count` (0, 1, or 2)

**5. Event Timeline (Section 5)**
- **SLA Metrics Header** (NEW - 2026-05-06):
  - **Display Location**: Top of Event Timeline section, above event list
  - **Layout**: Two-column grid display
  - **Metrics**:
    - **Time Since FNOL**: 
      - Format: "X days, Y.Z hrs" (e.g., "1 day, 3.5 hrs")
      - If < 30 minutes: show as "0.5 hr"
      - If < 1 hour: show as "0.X hr" (rounded to 1 decimal)
      - Calculated from FNOL event timestamp to current time
    - **SLA Time Remaining**:
      - Format: "XX.X hrs (Status)" (e.g., "47.3 hrs (🟢 On Track)")
      - SLA Threshold: 48 hours from FNOL
      - Color Coding:
        - 🟢 **Green** (bg-green-50, text-green-700): > 24 hours remaining - "On Track"
        - 🟡 **Amber** (bg-amber-50, text-amber-700): 12-24 hours remaining - "Warning"
        - 🔴 **Red** (bg-red-50, text-red-700): < 12 hours remaining - "At Risk"
      - If breached (< 0 hours): Show "BREACHED" in red with exclamation icon
  - **Calculation Logic**:
    - Find FNOL event: action = "claim_submitted" or action = "submit_claim"
    - FNOL timestamp = event_date + event_time
    - Time since FNOL = Current time - FNOL timestamp
    - SLA deadline = FNOL timestamp + 48 hours
    - Time remaining = SLA deadline - Current time
  - **Visual Design**:
    - Two-column card layout above timeline
    - Each metric in its own card with icon
    - Color-coded backgrounds for SLA remaining
    - Bold, prominent typography
- **Display Order**: Reverse chronological (newest event first)
- **Date/Time Format**: "Month DD, YYYY H:MM AM/PM" (e.g., "May 2, 2026 3:00 PM")
- **Event Structure**:
  - Colored indicator dot (blue=customer, green=AI/system, amber=adjustor)
  - Actor label (Customer, AI, Adjustor, System)
  - Action description (e.g., "Claim Submitted", "Customer Appealed")
  - Date and time stamp
  - Status badge (if applicable)
  - Expandable details (comments, metadata)
- **Visual Design**:
  - Vertical timeline with connecting lines
  - Timeline line runs from top to bottom (following reverse chronological order)
  - Actor-specific colored dots
  - Expandable cards for events with additional details
- **Data Source**:
  - Events fetched via `GET /customers/{customer_id}/claims/{claim_id}/events`
  - Events array sorted newest-first before display
  - Each event includes: `event_id`, `event_date`, `event_time`, `action`, `action_by`, `status`, `comments`
- **Implementation Notes**:
  - Sort events by `event_date` DESC, `event_time` DESC
  - Combine `event_date` and `event_time` for display formatting
  - Show most recent 10 events by default, with "Load more" option
  - Update SLA metrics in real-time (re-calculate on component render)

**6. Complete Review Button**
- Navigates to `/claims/{claim_id}/review/complete`
- Carries forward all damage edits/additions

**7. AI Research Assistant (Right Panel - 30% width)**
- **Purpose**: Conversational AI assistant to help adjustors with research during claim review
- **Features**:
  - Natural language question answering
  - Context-aware responses based on current claim
  - Research capabilities:
    - Repair procedures and best practices
    - Parts pricing and availability
    - Labor time standards (Mitchell, AllData, etc.)
    - Policy coverage interpretation
    - Damage assessment guidelines
    - Industry standards and regulations
  - Chat history preserved during session
  - Copy/paste functionality for responses
- **Implementation**: Phase 9 (Future - Chatbot Integration)
- **UI Placement**: Fixed right sidebar (30% width), always visible while scrolling left panel
- **Design**: Professional chat interface with clear distinction between user and assistant messages

**Note:** The AI Research Assistant will be implemented in a future phase. For Phase 8 implementation, the layout should reserve the 30% right panel with a placeholder indicating "AI Research Assistant - Coming Soon".

---

### 7.5 Review Complete Page

**Path:** `/claims/{claim_id}/review/complete`

**Purpose:** Final submission page with action selection and notes

**Layout:**
```
┌────────────────────────────────────────────────────────────┐
│  Header: [← Back to Review] Complete Review - Claim #1001 │
└────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  Cost Summary                                            │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Original AI Estimate:     $1,234.00                 │ │
│  │ Revised Estimate:         $2,584.00                 │ │
│  │ ───────────────────────────────────────             │ │
│  │ Change:                   +$1,350 (+109%)           │ │
│  │                                                     │ │
│  │ Changes Made:                                       │ │
│  │ • Added 1 manual damage (+$434)                     │ │
│  │ • Adjusted 1 existing damage (+$916)                │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  Review Decision                                         │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ What action should be taken?                        │ │
│  │                                                     │ │
│  │ ○ Deny Appeal (No changes, uphold AI estimate)     │ │
│  │ ● Revise Estimate (Changes made, send to customer) │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  Customer Note (Visible to Customer) *                   │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ We've completed our review and made adjustments     │ │
│  │ to the estimate based on additional damages and...  │ │
│  │                                                     │ │
│  └─────────────────────────────────────────────────────┘ │
│  (This note will be displayed to the customer)           │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  Internal Note (For Audit Trail Only) *                  │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ AI missed door scratch in IMG_003. Bumper damage    │ │
│  │ requires replacement per OEM specs, not repair...   │ │
│  │                                                     │ │
│  └─────────────────────────────────────────────────────┘ │
│  (Internal only - NOT visible to customer)               │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  [Submit Review]                    [← Back to Edit]     │
└──────────────────────────────────────────────────────────┘
```

**Fields:**

**1. Cost Summary (Read-Only)**
- Show before/after comparison
- Highlight % change
- List changes made (added damages, adjusted damages)
- Warning if change > 100%

**2. Review Decision (Radio Buttons)**
- **Deny Appeal**: No changes made (or changes are corrections, not increases)
  - Use action: `denied_appeal`
  - Customer sees original AI estimate with adjustor note
- **Revise Estimate**: Changes made, send back to customer
  - Use action: `revised_estimate`
  - Customer sees updated estimate with adjustor note
- **Route to Traditional Processing**: AI/adjustor cannot accurately assess damage
  - Use action: `route_to_traditional`
  - Claim transitions to `routed_to_traditional` status
  - Customer sees notice that claim is being processed traditionally
  - Physical inspection may be scheduled
  - Use when:
    - Damage too complex for remote assessment
    - Missing critical angles/images
    - Structural damage requiring in-person inspection
    - ML unable to capture damage accurately

**3. Customer Note (Textarea, Required)**
- Placeholder: "Explain your decision to the customer..."
- Max length: 1000 characters
- Validation: Required if submitting
- Examples:
  - Deny: "After careful review, the AI estimate is accurate..."
  - Revise: "We've adjusted the estimate to include additional damages..."

**4. Internal Note (Textarea, Required)**
- Placeholder: "Internal notes for audit trail (not visible to customer)..."
- Max length: 2000 characters
- Validation: Required if submitting
- Examples:
  - "AI detection accurate. Costs within normal range."
  - "AI missed scratch in IMG_003. Bumper requires replacement per OEM specs."

**Actions:**

**Submit Review Button:**
1. Validate:
   - Review decision selected
   - Both notes filled
   - Confirm if cost change > 100%
2. Show confirmation modal:
   - "Submit review for Claim #1001?"
   - "This action will return the claim to the customer."
   - **[Confirm]** / **[Cancel]**
3. On confirm:
   - Call `POST /api/v1/claims/{claim_id}/review/complete`
   - Body: `{ action, customer_note, internal_note, revised_estimate_total }`
   - On success:
     - Show success toast: "Review submitted for Claim #1001"
     - Redirect to Dashboard
   - On error:
     - Show error message: "Failed to submit review. Please try again."

**Back to Edit Button:**
- Navigate back to `/claims/{claim_id}/review`
- Preserve all edits (stored in component state or localStorage)

---

## 8. Component Library

### 8.1 Shared Components (Copied from Customer Portal)

**Location:** `src/components/common/`

These components will be copied from the customer portal with minimal changes (only theme/colors):

| Component | Purpose | Props | Notes |
|-----------|---------|-------|-------|
| `Button.jsx` | Action buttons | `variant` (primary/secondary/danger/ghost), `size`, `loading`, `disabled` | Update colors for corporate theme |
| `Card.jsx` | Content containers | `title`, `actions`, `padding`, `className` | No changes needed |
| `Input.jsx` | Form inputs | `label`, `type`, `error`, `required`, `disabled`, `value`, `onChange` | No changes |
| `Textarea.jsx` | Multi-line inputs | `label`, `rows`, `error`, `required`, `value`, `onChange` | No changes |
| `Modal.jsx` | Dialogs | `isOpen`, `onClose`, `title`, `size`, `children` | No changes |
| `Badge.jsx` | Status indicators | `variant`, `children` | Update colors |
| `Spinner.jsx` | Loading indicator | `size` | No changes |

#### Layout Components (Adjustor-Specific)

**Header Component:**

```jsx
// src/components/layout/Header.jsx
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export const Header = () => {
  const { adjustor, logout } = useAuth();

  return (
    <header className="bg-primary-900 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        {/* ACME Insurance Logo */}
        <Link to="/dashboard" className="flex items-center gap-3">
          <img 
            src="/src/common/assets/ACME-logo.png" 
            alt="ACME Insurance" 
            className="h-10 w-auto brightness-0 invert"
          />
          <span className="text-lg font-semibold">
            ACME Insurance - Adjustor Portal
          </span>
        </Link>

        {/* Adjustor Info & Logout */}
        <div className="flex items-center gap-4">
          {adjustor && (
            <>
              <span className="text-sm">
                {adjustor.name} ({adjustor.role})
              </span>
              <button
                onClick={logout}
                className="text-accent hover:text-accent-light font-medium text-sm"
              >
                Logout
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  );
};
```

**Implementation Notes:**
- Logo location: `src/common/assets/ACME-logo.png`
- Logo links to dashboard page (`/dashboard`)
- Logo size: ~120px width (adjustable)
- Dark header background (primary-900) requires inverted logo colors
- Header displays on all pages except login

### 8.2 New Components (Adjustor-Specific)

#### 8.2.1 ImageViewer Component

**File:** `src/components/claims/ImageViewer.jsx`

**Purpose:** Display damage images with zoom/pan and AI bounding boxes

**Props:**
```typescript
{
  images: Array<{
    image_id: string,
    image_url: string,
    uploaded_at: string
  }>,
  damages: Array<{
    damage_id: string,
    image_id: string,
    damage_part: string,
    confidence: number,
    bounding_box: { x1, y1, x2, y2 }
  }>,
  currentImageIndex: number,
  onImageChange: (index: number) => void
}
```

**Features:**
- React-zoom-pan-pinch for zoom/pan
- Overlay bounding boxes using absolute positioning
- Show confidence % on hover
- Navigation arrows (prev/next)
- Toggle switches:
  - "Show Bounding Boxes" (on/off)
  - "Show Original" (removes annotations)

**Library:** `react-zoom-pan-pinch@3.4.4`

---

#### 8.2.2 DamageList Component

**File:** `src/components/claims/DamageList.jsx`

**Purpose:** Display list of damages with costs

**Props:**
```typescript
{
  damages: Array<Damage>,
  onEdit: (damageId: string) => void,
  onDelete: (damageId: string) => void,
  readOnly: boolean
}
```

**Rendering:**
- Map over damages array
- Show each damage as a card:
  - Title: Damage type + location
  - Metadata: Severity, confidence (AI only), image ID
  - Costs: Labor (hours × rate), Parts, Total
  - Actions: [Edit] [Delete] buttons (if not readOnly)

---

#### 8.2.3 DamageEditor Component (Modal)

**File:** `src/components/claims/DamageEditor.jsx`

**Purpose:** Edit existing damage costs

**Props:**
```typescript
{
  damage: Damage | null,
  isOpen: boolean,
  onClose: () => void,
  onSave: (updatedDamage: Damage) => void
}
```

**Fields:**
- Labor Hours (input, number)
- Parts Cost (input, $)
- Adjustor Note (textarea, required if changed)
- Total (calculated, read-only, uses claim-level labor rate)

**Note:** Labor rate is NOT editable here as it is common across all damages and can be changed in the "Labor Rate Configuration" section.

**Validation:**
- Warn if change > 50%
- Require note if any cost field changes

---

#### 8.2.4 DamageCreator Component (Modal)

**File:** `src/components/claims/DamageCreator.jsx`

**Purpose:** Add new manual damage

**Props:**
```typescript
{
  claimId: number,
  images: Array<Image>,
  isOpen: boolean,
  onClose: () => void,
  onAdd: (newDamage: Damage) => void
}
```

**Fields:**
- Damage Type (dropdown)
- Location (dropdown)
- Description (textarea, required)
- Severity (dropdown)
- Image ID (dropdown, optional)
- Labor Hours (input, required)
- Labor Rate (input, required)
- Parts Cost (input, required)
- Adjustor Note (textarea, required)

**Validation:**
- All required fields must be filled
- Labor hours: 0.1-100
- Labor rate: $50-$500
- Parts cost: $0-$50,000

---

#### 8.2.5 CostSummary Component

**File:** `src/components/claims/CostSummary.jsx`

**Purpose:** Before/after cost comparison

**Props:**
```typescript
{
  originalTotal: number,
  revisedTotal: number,
  changes: Array<{
    type: 'added' | 'adjusted' | 'removed',
    description: string,
    amount: number
  }>
}
```

**Display:**
- Original AI Estimate
- Revised Estimate
- Difference ($ and %)
- List of changes:
  - "Added 1 manual damage (+$434)"
  - "Adjusted Dent - Rear Bumper (+$916)"
- Warning badge if change > 100%

---

#### 8.2.6 NotesEditor Component

**File:** `src/components/claims/NotesEditor.jsx`

**Purpose:** Dual-note editor (customer + internal)

**Props:**
```typescript
{
  customerNote: string,
  internalNote: string,
  onCustomerNoteChange: (note: string) => void,
  onInternalNoteChange: (note: string) => void,
  errors: { customerNote?: string, internalNote?: string }
}
```

**Layout:**
- Two stacked textareas
- Clear labels: "Customer Note (Visible to Customer)"
- Character counters (e.g., "245 / 1000")
- Validation messages below each textarea

---

#### 8.2.7 EventTimeline Component

**File:** `src/components/claims/EventTimeline.jsx`

**Purpose:** Visual timeline of claim events

**Props:**
```typescript
{
  events: Array<{
    event_id: number,
    event_date: string,
    event_time: string,
    status: string,
    action: string,
    action_by: string,
    action_by_identity: string,
    comments: string
  }>,
  expandable: boolean
}
```

**Display:**
- Vertical timeline (Tailwind classes)
- Show date, time, actor, action, status
- Color-coded bullets (customer = blue, AI = green, adjustor = amber)
- Expandable sections for comments

---

#### 8.2.8 SOPViewer Component

**File:** `src/components/common/SOPViewer.jsx`

**Purpose:** Display Standard Operating Procedures (SOP) document in a modal for adjustors to reference during claim review

**Props:**
```typescript
{
  isOpen: boolean,
  onClose: () => void
}
```

**Features:**
- **Floating Action Button:** Fixed position button (bottom-right corner) with FileText icon
- **Modal Display:** Full-screen modal showing the complete SOP document
- **Markdown Rendering:** Converts markdown to HTML with proper formatting
- **Always Accessible:** Available on all pages via floating button in Layout component
- **Real-time Content:** Loads latest version of sop_damage_triage.md from public folder

**Implementation:**

The SOPViewer is integrated into the Layout component as a floating action button that appears on all pages (except login):

```jsx
// In Layout.jsx
<button
  onClick={() => setShowSOP(true)}
  className="fixed bottom-6 right-6 p-4 bg-primary-600 text-white rounded-full shadow-lg hover:bg-primary-700 transition-all hover:scale-110"
  aria-label="View Standard Operating Procedures"
  title="View SOP - Damage Triage Guidelines"
>
  <FileText className="w-6 h-6" />
</button>

<SOPViewer isOpen={showSOP} onClose={() => setShowSOP(false)} />
```

**Positioning:**
- Fixed position: bottom-right corner
- Coordinates: `bottom-6` (1.5rem / 24px from bottom), `right-6` (1.5rem / 24px from right)
- Floats above all page content
- Z-index: 50 (ensures visibility above content)

**Content Source:**
- File: `public/sop_damage_triage.md` (copied from `specifications/policies/sop_damage_triage.md`)
- Updated: Automatically reflects latest SOP document
- Format: Markdown with standard sections (Overview, Thresholds, Decision Trees, Fraud Detection, etc.)

**Display Features:**
- **Header:** Document title, version, and close button
- **Scrollable Content:** Full document with formatted sections
- **Formatted Elements:** 
  - Headers (H1, H2, H3)
  - Bold and italic text
  - Code blocks and inline code
  - Lists (ordered and unordered)
  - Tables
  - Blockquotes
  - Links
- **Footer:** Document metadata and close action

**Use Cases:**
- Quick reference for confidence thresholds
- Review fraud detection protocols
- Check damage assessment guidelines
- Verify triage decision tree logic
- Reference customer appeal process
- Look up part costs and labor rates

**User Experience:**
- Icon appears in bottom-right corner of all pages
- Tooltip on hover: "View SOP - Damage Triage Guidelines"
- Click opens full-screen modal
- Easy to close and resume work
- Always visible and accessible regardless of scroll position
- Similar to chat widget positioning for familiarity

---

## 9. API Integration

### 9.1 API Client Setup

**File:** `src/api/client.js`

**Pattern:** Singleton Axios instance (same as customer portal)

```javascript
import axios from 'axios';
import config from './config';

let apiClient = null;

export const getApiClient = () => {
  if (apiClient) return apiClient;

  apiClient = axios.create({
    baseURL: config.base_url || 'http://localhost:8000/api/v1',
    timeout: config.timeout || 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor: Add adjustor ID header
  apiClient.interceptors.request.use(
    (config) => {
      const adjustorId = localStorage.getItem('adjustor_id');
      if (adjustorId) {
        config.headers['X-Adjustor-ID'] = adjustorId;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor: Handle 401 (unauthorized)
  apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        localStorage.removeItem('adjustor_id');
        localStorage.removeItem('adjustor_name');
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );

  return apiClient;
};
```

---

### 9.2 API Modules

#### 9.2.1 Adjustors API

**File:** `src/api/adjustors.js`

```javascript
import { getApiClient } from './client';

const apiClient = () => getApiClient();

/**
 * Get pending claims for adjustor
 * @param {string} adjustorId - Adjustor ID
 * @param {object} filters - Optional filters (search, sort, page, limit)
 * @returns {Promise} List of pending claims
 */
export const fetchPendingClaims = (adjustorId, filters = {}) => {
  return apiClient().get(`/adjustors/${adjustorId}/claims/pending`, {
    params: filters
  });
};

/**
 * Get adjustor workload statistics
 * @param {string} adjustorId - Adjustor ID
 * @returns {Promise} Statistics object
 */
export const fetchAdjustorStatistics = (adjustorId) => {
  return apiClient().get(`/adjustors/${adjustorId}/statistics`);
};
```

---

#### 9.2.2 Claims API (Review Operations)

**File:** `src/api/claims.js`

```javascript
import { getApiClient } from './client';

const apiClient = () => getApiClient();

/**
 * Get claim details for review
 * @param {number} claimId - Claim ID
 * @returns {Promise} Claim details with damages, images, events
 */
export const fetchClaimForReview = (claimId) => {
  return apiClient().get(`/claims/${claimId}/review`);
};

/**
 * Complete review
 * @param {number} claimId - Claim ID
 * @param {object} reviewData - Review decision data
 * @returns {Promise} Updated claim
 */
export const completeReview = (claimId, reviewData) => {
  return apiClient().post(`/claims/${claimId}/review/complete`, reviewData);
};

/**
 * Add manual damage (human-detected)
 * @param {number} claimId - Claim ID
 * @param {object} damageData - Damage details
 * @returns {Promise} Created damage
 */
export const addManualDamage = (claimId, damageData) => {
  return apiClient().post(`/claims/${claimId}/damages`, damageData);
};

/**
 * Update damage costs
 * @param {number} claimId - Claim ID
 * @param {string} damageId - Damage ID
 * @param {object} updateData - Updated cost fields
 * @returns {Promise} Updated damage
 */
export const updateDamageCosts = (claimId, damageId, updateData) => {
  return apiClient().patch(`/claims/${claimId}/damages/${damageId}`, updateData);
};

/**
 * Get claim events
 * @param {number} claimId - Claim ID
 * @returns {Promise} List of events
 */
export const fetchClaimEvents = (claimId) => {
  return apiClient().get(`/claims/${claimId}/events`);
};

/**
 * Get claim image (original)
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @param {string} imageId - Image ID
 * @returns {Promise} Image blob
 */
export const fetchClaimImage = async (customerId, claimId, imageId) => {
  const response = await apiClient().get(
    `/customers/${customerId}/claims/${claimId}/images/${imageId}`,
    { responseType: 'blob' }
  );
  return response.data;
};

/**
 * Get claim image with bounding boxes (annotated)
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @param {string} imageId - Image ID
 * @returns {Promise} Annotated image blob
 */
export const fetchAnnotatedImage = async (customerId, claimId, imageId) => {
  const response = await apiClient().get(
    `/customers/${customerId}/claims/${claimId}/images/${imageId}/annotated`,
    { responseType: 'blob' }
  );
  return response.data;
};
```

**Important: Image Access Pattern**

All image access MUST go through the API client with proper authentication headers. The pattern is:

1. **Original Images**: Use `fetchClaimImage()` to get the original uploaded image
2. **Annotated Images**: Use `fetchAnnotatedImage()` to get the image with AI bounding boxes drawn
3. **Never use direct HTTP URLs** in `<img src>` tags - always fetch via API and convert to blob URLs
4. **Authentication**: All image requests include `X-Adjustor-ID` header via API client interceptors

**Example Usage:**
```javascript
// Fetch original image
const imageBlob = await fetchClaimImage(customerId, claimId, imageId);
const imageUrl = URL.createObjectURL(imageBlob);

// Fetch annotated image (with bounding boxes)
const annotatedBlob = await fetchAnnotatedImage(customerId, claimId, imageId);
const annotatedUrl = URL.createObjectURL(annotatedBlob);

// Cleanup when component unmounts
URL.revokeObjectURL(imageUrl);
URL.revokeObjectURL(annotatedUrl);
```

---

### 9.3 Backend API Endpoints (To Be Created)

#### 9.3.1 GET /adjustors/{adjustor_id}/claims/pending

**Purpose:** Get list of claims in `human_review_pending` status

**Request:**
```
GET /api/v1/adjustors/{adjustor_id}/claims/pending
Query params:
  - search: string (optional, search by claim ID, customer name, VIN)
  - sort: string (optional, 'oldest' | 'highest_amount' | 'customer_name')
  - filter: string (optional, 'appeals' | 'low_confidence' | 'no_damage')
  - page: int (default: 1)
  - limit: int (default: 20)
```

**Response:**
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
      "current_status": "human_review_pending",
      "appeal_count": 1,
      "first_appeal_reason": "The estimate seems too low...",
      "first_appeal_date": "2026-05-02"
    }
  ]
}
```

**Note:** Appeal fields (`appeal_count`, `first_appeal_reason`, `first_appeal_date`, `second_appeal_reason`, `second_appeal_date`) are included in the response when reason_for_review is "customer_appeal".

---

#### 9.3.2 GET /adjustors/{adjustor_id}/statistics

**Purpose:** Get adjustor workload statistics

**Request:**
```
GET /api/v1/adjustors/{adjustor_id}/statistics
```

**Response:**
```json
{
  "pending_reviews": 12,
  "completed_today": 5,
  "completed_this_week": 23,
  "average_review_time_minutes": 8,
  "total_reviews_all_time": 456
}
```

---

#### 9.3.3 POST /claims/{claim_id}/review/complete

**Purpose:** Complete adjustor review and return claim to customer

**Request:**
```
POST /api/v1/claims/{claim_id}/review/complete
Body:
{
  "action": "denied_appeal" | "revised_estimate",
  "customer_note": string (required),
  "internal_note": string (required),
  "revised_estimate_total": number (required if action='revised_estimate')
}
```

**Response:**
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
   - Record event with action `DENIED_APPEAL`
   - Status: `human_review_pending` → `human_review_completed` → `customer_decision_pending`
   - Keep original AI estimate
3. If action = `revised_estimate`:
   - Record event with action `REVISED_ESTIMATE`
   - Status: `human_review_pending` → `human_review_completed` → `customer_decision_pending`
   - Update `claim.active_estimate_id` to new human estimate
   - Update `claim.claim_amount` to revised total
4. Store notes in event.comments as structured text:
   - Format: `Customer: {customer_note} | Internal: {internal_note}`
5. Trigger customer notification (email/SMS)

---

#### 9.3.4 POST /claims/{claim_id}/damages

**Purpose:** Add manual damage (human-detected, missed by AI)

**Request:**
```
POST /api/v1/claims/{claim_id}/damages
Body:
{
  "estimate_type": "human",
  "damage_part": "scratch-front-door",
  "description": string (required),
  "severity": "light" | "moderate" | "severe",
  "image_id": string (optional),
  "labor_hours": number (required),
  "labor_rate": number (required, $/hour),
  "parts_cost": number (required),
  "adjustor_note": string (required)
}
```

**Response:**
```json
{
  "damage_id": "DMG-1001-4",
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
1. Validate claim exists and is in `human_review_pending`
2. Create new Damage record with `estimate_type='human'`
3. Generate `estimate_id` = `{claim_id}_human_{timestamp}`
4. Calculate total: (labor_hours × labor_rate) + parts_cost
5. Store adjustor_note in damage metadata (or separate column)
6. Update claim.active_estimate_id if this is first human damage
7. Recalculate claim total

---

#### 9.3.5 PATCH /claims/{claim_id}/damages/{damage_id}

**Purpose:** Adjust costs for existing damage

**Request:**
```
PATCH /api/v1/claims/{claim_id}/damages/{damage_id}
Body:
{
  "labor_hours": number (optional),
  "labor_rate": number (optional, $/hour),
  "parts_cost": number (optional),
  "adjustor_note": string (required if any cost changes)
}
```

**Response:**
```json
{
  "damage_id": "DMG-1001-1",
  "claim_id": 1001,
  "labor_hours": 3.0,
  "avg_labor_cost": 156.00,
  "estimated_parts_cost": 650.00,
  "estimated_total_cost": 1118.00,
  "updated_at": "2026-05-05T14:35:00Z"
}
```

**Business Logic:**
1. Validate claim exists and is in `human_review_pending`
2. Validate damage exists and belongs to claim
3. Update cost fields (only provided fields)
4. Recalculate total: (labor_hours × labor_rate) + parts_cost
5. Store adjustor_note in damage metadata
6. Create audit event: `ADJUSTED_DAMAGE_COST`
7. Recalculate claim total

---

## 10. State Management

### 10.1 AuthContext (Adjustor-Specific)

**File:** `src/context/AuthContext.jsx`

**Pattern:** React Context API (same pattern as customer portal)

```javascript
import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

// Mock adjustor database
const ADJUSTORS = {
  'ADJ-001': { id: 'ADJ-001', name: 'Sarah Chen', role: 'Senior Adjustor', email: 'sarah.chen@acme-insurance.com' },
  'ADJ-002': { id: 'ADJ-002', name: 'Michael Torres', role: 'Collision Specialist', email: 'michael.torres@acme-insurance.com' },
  'ADJ-003': { id: 'ADJ-003', name: 'Emily Watson', role: 'Claims Supervisor', email: 'emily.watson@acme-insurance.com' }
};

export const AuthProvider = ({ children }) => {
  const [adjustorId, setAdjustorId] = useState(null);
  const [adjustor, setAdjustor] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load from localStorage on mount
    const storedId = localStorage.getItem('adjustor_id');
    if (storedId && ADJUSTORS[storedId]) {
      setAdjustorId(storedId);
      setAdjustor(ADJUSTORS[storedId]);
    }
    setLoading(false);
  }, []);

  const login = async (selectedAdjustorId, password) => {
    // Mock validation
    if (password !== 'adjustor123') {
      throw new Error('Invalid password');
    }

    if (!ADJUSTORS[selectedAdjustorId]) {
      throw new Error('Invalid adjustor ID');
    }

    // Store in localStorage
    localStorage.setItem('adjustor_id', selectedAdjustorId);
    localStorage.setItem('adjustor_name', ADJUSTORS[selectedAdjustorId].name);

    // Update state
    setAdjustorId(selectedAdjustorId);
    setAdjustor(ADJUSTORS[selectedAdjustorId]);
  };

  const logout = () => {
    localStorage.removeItem('adjustor_id');
    localStorage.removeItem('adjustor_name');
    setAdjustorId(null);
    setAdjustor(null);
  };

  const isAuthenticated = () => !!adjustorId;

  return (
    <AuthContext.Provider value={{ adjustorId, adjustor, loading, login, logout, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

---

### 10.2 Page-Level State

**Pattern:** useState + useEffect (no global state library)

**Example (ClaimDetailPage.jsx):**
```javascript
const [claim, setClaim] = useState(null);
const [damages, setDamages] = useState([]);
const [images, setImages] = useState([]);
const [events, setEvents] = useState([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);
const [selectedImageIndex, setSelectedImageIndex] = useState(0);

// Load claim data
useEffect(() => {
  const loadClaim = async () => {
    try {
      setLoading(true);
      const response = await fetchClaimForReview(claimId);
      setClaim(response.data.claim);
      setDamages(response.data.damages);
      setImages(response.data.images);
      setEvents(response.data.events);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  loadClaim();
}, [claimId]);
```

**Claim Object Structure:**

The `claim` object includes appeal tracking fields (added 2026-05-06):
```javascript
{
  claim_id: 1001,
  customer_id: 101,
  // ... other fields ...
  ai_estimate_total: 1234.00,
  appeal_count: 1,                           // 0, 1, or 2
  first_appeal_reason: "The estimate...",    // Text or null
  first_appeal_date: "2026-05-02",           // Date or null
  second_appeal_reason: null,                // Text or null
  second_appeal_date: null                   // Date or null
}
```

---

## 11. Business Logic

### 11.1 Cost Calculation

**File:** `src/utils/calculations.js`

```javascript
/**
 * Calculate total damage cost
 * @param {number} laborHours - Labor hours
 * @param {number} laborRate - Labor rate ($/hour)
 * @param {number} partsCost - Parts cost ($)
 * @returns {number} Total cost
 */
export const calculateDamageCost = (laborHours, laborRate, partsCost) => {
  return (laborHours * laborRate) + partsCost;
};

/**
 * Calculate claim total from damages
 * @param {Array} damages - Array of damage objects
 * @returns {number} Total claim cost
 */
export const calculateClaimTotal = (damages) => {
  return damages.reduce((total, damage) => total + damage.estimated_total_cost, 0);
};

/**
 * Calculate cost change percentage
 * @param {number} original - Original cost
 * @param {number} revised - Revised cost
 * @returns {number} Percentage change
 */
export const calculateCostChangePercent = (original, revised) => {
  if (original === 0) return 0;
  return ((revised - original) / original) * 100;
};

/**
 * Check if cost change is significant (>50%)
 * @param {number} original - Original cost
 * @param {number} revised - Revised cost
 * @returns {boolean} True if change > 50%
 */
export const isSignificantChange = (original, revised) => {
  return Math.abs(calculateCostChangePercent(original, revised)) > 50;
};
```

---

### 11.2 Validation

**File:** `src/utils/validators.js`

```javascript
/**
 * Validate labor hours
 * @param {number} hours - Labor hours
 * @returns {{ valid: boolean, error: string }}
 */
export const validateLaborHours = (hours) => {
  if (hours === null || hours === undefined || hours === '') {
    return { valid: false, error: 'Labor hours is required' };
  }
  if (hours < 0.1 || hours > 100) {
    return { valid: false, error: 'Labor hours must be between 0.1 and 100' };
  }
  return { valid: true, error: null };
};

/**
 * Validate labor rate
 * @param {number} rate - Labor rate ($/hour)
 * @returns {{ valid: boolean, error: string }}
 */
export const validateLaborRate = (rate) => {
  if (rate === null || rate === undefined || rate === '') {
    return { valid: false, error: 'Labor rate is required' };
  }
  if (rate < 50 || rate > 500) {
    return { valid: false, error: 'Labor rate must be between $50 and $500/hour' };
  }
  return { valid: true, error: null };
};

/**
 * Validate parts cost
 * @param {number} cost - Parts cost ($)
 * @returns {{ valid: boolean, error: string }}
 */
export const validatePartsCost = (cost) => {
  if (cost === null || cost === undefined || cost === '') {
    return { valid: false, error: 'Parts cost is required' };
  }
  if (cost < 0 || cost > 50000) {
    return { valid: false, error: 'Parts cost must be between $0 and $50,000' };
  }
  return { valid: true, error: null };
};

/**
 * Validate review notes
 * @param {string} customerNote - Customer-facing note
 * @param {string} internalNote - Internal audit note
 * @returns {{ valid: boolean, errors: object }}
 */
export const validateReviewNotes = (customerNote, internalNote) => {
  const errors = {};

  if (!customerNote || customerNote.trim().length < 10) {
    errors.customerNote = 'Customer note must be at least 10 characters';
  }
  if (customerNote.length > 1000) {
    errors.customerNote = 'Customer note must be less than 1000 characters';
  }

  if (!internalNote || internalNote.trim().length < 10) {
    errors.internalNote = 'Internal note must be at least 10 characters';
  }
  if (internalNote.length > 2000) {
    errors.internalNote = 'Internal note must be less than 2000 characters';
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors
  };
};
```

---

## 12. Development Guidelines

### 12.1 Setup Instructions

**1. Install Dependencies:**
```bash
cd src/ui/adjustor
npm install
```

**2. Configure API:**
Edit `public/adjustor-portal-config.yaml`:
```yaml
api:
  base_url: "http://localhost:8000/api/v1"
  timeout: 30000

auth:
  mock_password: "adjustor123"

features:
  enable_zoom: true
  enable_manual_damages: true
```

**3. Run Dev Server:**
```bash
npm run dev
# Open http://localhost:5174
```

**4. Build for Production:**
```bash
npm run build
# Output: dist/
```

---

### 12.2 Coding Conventions

**1. Component Structure:**
- Functional components with hooks
- Props destructuring in function signature
- PropTypes for type checking (optional)
- Clear separation: presentation vs. logic

**2. Naming:**
- Components: PascalCase (`DamageEditor.jsx`)
- Files: Match component name
- Functions: camelCase (`calculateTotal`)
- Constants: UPPER_SNAKE_CASE (`MAX_LABOR_HOURS`)

**3. Styling:**
- Tailwind utility classes only
- No inline styles
- Corporate theme colors (see tailwind.config.js)
- Responsive breakpoints: sm, md, lg, xl

**4. Error Handling:**
- Try-catch for all API calls
- User-friendly error messages
- Loading states for async operations
- Validation before submission

**5. Comments:**
- JSDoc for exported functions
- Inline comments for complex logic
- No obvious comments

---

### 12.3 Testing Strategy (Future)

**1. Unit Tests:**
- Utility functions (calculations, validators)
- Component logic (custom hooks)

**2. Integration Tests:**
- API client calls
- Form submissions
- State management

**3. E2E Tests:**
- Full review workflow
- Image viewer interactions
- Cost adjustments

**Tools:** Jest, React Testing Library, Cypress

---

### 12.4 Accessibility

**1. Keyboard Navigation:**
- Tab order follows visual order
- Focus indicators visible
- Escape closes modals

**2. ARIA Labels:**
- Form inputs labeled
- Buttons descriptive
- Modal roles

**3. Color Contrast:**
- WCAG AA compliant
- Text readable on backgrounds

---

### 12.5 Performance

**1. Optimization:**
- Lazy load images
- Debounce search inputs
- Memoize expensive calculations

**2. Bundle Size:**
- Code splitting by route
- Tree-shaking enabled
- Analyze bundle (vite-bundle-visualizer)

---

## Appendix A: Tailwind Theme (Corporate)

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        // Corporate theme
        primary: {
          50: '#f0f4f8',
          100: '#d9e2ec',
          200: '#bcccdc',
          300: '#9fb3c8',
          400: '#829ab1',
          500: '#627d98',
          600: '#486581',
          700: '#334e68',
          800: '#243b53',
          900: '#1e3a5f', // Main brand color
        },
        accent: {
          DEFAULT: '#F59E0B', // Amber
          light: '#FCD34D',
          dark: '#D97706',
        },
        success: {
          DEFAULT: '#10B981', // Emerald
          light: '#6EE7B7',
          dark: '#047857',
        },
        error: {
          DEFAULT: '#EF4444', // Rose
          light: '#FCA5A5',
          dark: '#B91C1C',
        },
        neutral: {
          50: '#F9FAFB',
          100: '#F3F4F6',
          200: '#E5E7EB',
          300: '#D1D5DB',
          400: '#9CA3AF',
          500: '#6B7280',
          600: '#4B5563',
          700: '#374151',
          800: '#1F2937',
          900: '#111827',
        }
      }
    }
  }
}
```

---

## Appendix B: Mock Data (Development)

**Adjustors:**
```json
[
  { "id": "ADJ-001", "name": "Sarah Chen", "role": "Senior Adjustor", "email": "sarah.chen@acme-insurance.com" },
  { "id": "ADJ-002", "name": "Michael Torres", "role": "Collision Specialist", "email": "michael.torres@acme-insurance.com" },
  { "id": "ADJ-003", "name": "Emily Watson", "role": "Claims Supervisor", "email": "emily.watson@acme-insurance.com" }
]
```

**Password:** `adjustor123`

---

**End of Design Document**
