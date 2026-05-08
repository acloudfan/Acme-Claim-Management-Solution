# Executive Portal - Design Specification

**Last Updated:** 2026-05-07  
**Status:** Design Phase  
**Purpose:** Business Intelligence Dashboard for executives and insurance operations managers

---

## 1. Overview

**ACME Claims : Executive Portal** provides a Business Intelligence dashboard for both C-suite executives and insurance operations managers to monitor the impact of AI adoption on claim processing efficiency, cost, and accuracy.

This eliminates the need for manual reporting and provides real-time insights into business KPIs with interactive visualizations.

### 1.1 Key Features

- **KPI Dashboard**: 3 core metrics (Cycle Time Savings, Total Savings, Auto-Adjudication Rate)
- **Historical Trends**: 6-month progressive AI adoption timeline showing improvement (Oct 2025 - Mar 2026)
- **AI Processed Claims Chart**: Pie chart showing distribution of processing paths (Traditional, AI Auto-Approved, AI + Human Review)
- **Demo Data Disclaimer**: Transparent notice about synthetic data, extrapolation methodology, and industry averages
- **NLP Query Interface**: Hybrid dropdown (presets) + optional free-text for custom reports
- **Interactive Visualizations**: Bar + Line hybrid charts, time filtering, chart type toggles
- **Export Capabilities**: PDF reports, CSV data, PNG charts for presentations (positioned at bottom of sidebar)
- **Data Warehouse**: Claim-level records (4,500 claims) with drill-down capability
- **Extrapolation View**: Scale 4,500 claims (1% sample) → 450,000 claims for realistic projections (100x factor)
- **No Authentication**: Open access for demo/prototype environments

### 1.2 Target Audience

**Dual Audience Approach:**

1. **C-Suite Executives** (Strategic View)
   - High-level KPIs: ROI, cost savings, business impact
   - Board-ready metrics with trend indicators
   - Focus: "Is AI adoption successful?"

2. **Insurance Operations Managers** (Tactical View)
   - Operational metrics: cycle time, human review rate, accuracy
   - Day-to-day performance monitoring
   - Focus: "How can we optimize processes?"

**Design Philosophy:** Balanced view showing both current snapshot (big numbers) AND historical trends (charts).

### 1.3 Out of Scope (Future Enhancements)

- Real-time data streaming (static snapshots only in MVP)
- User authentication and role-based views
- Advanced drill-down (claim-level details in modal)
- Predictive analytics and forecasting
- Alert thresholds and notifications
- Multi-year historical data (3 months only for demo)

---

## 2. Architecture

### 2.1 Technology Stack

```
Frontend:
- Vite + React 18
- React Router v7
- Tailwind CSS v3
- Recharts v2.x (charting library)
- Axios for API calls
- Lucide React for icons

Backend Integration:
- REST API: /api/v1/executive/*
- Warehouse DB: claims-warehouse.db (separate SQLite database)
- Main DB Link: claim_id FK to claims.db for drill-down
```

### 2.2 Project Structure

The Executive Portal is an **independent React application** following the same pattern as Customer, Adjustor, and Admin portals:

```
src/ui/executive/
├── public/
│   ├── executive-portal-config.yaml   # Portal-specific configuration
│   └── index.html
├── src/
│   ├── main.jsx                        # Entry point with config loader
│   ├── App.jsx                         # Router + Routes
│   ├── context/
│   │   └── AuthContext.jsx             # Authentication (no-auth mode)
│   ├── pages/
│   │   ├── LoginPage.jsx               # Minimal login (no password)
│   │   ├── DashboardPage.jsx           # Main BI dashboard
│   │   └── NotFoundPage.jsx
│   ├── components/
│   │   ├── common/                     # Reused from other portals
│   │   │   ├── Button.jsx
│   │   │   ├── Card.jsx
│   │   │   ├── Badge.jsx
│   │   │   ├── Modal.jsx
│   │   │   └── Spinner.jsx
│   │   └── dashboard/                  # Executive-specific
│   │       ├── KPICard.jsx             # Big number + trend + mini chart
│   │       ├── TrendChart.jsx          # Bar + Line hybrid chart
│   │       ├── QueryInterface.jsx      # Hybrid dropdown + free-text
│   │       ├── FilterSidebar.jsx       # Time filtering + export options
│   │       ├── QuickStats.jsx          # Summary statistics card
│   │       ├── SampleDataDistribution.jsx  # Data methodology & distribution table
│   │       └── DrillDownModal.jsx      # Claim-level details modal
│   ├── api/
│   │   ├── client.js                   # Axios client
│   │   ├── config.js                   # Load executive-portal-config.yaml
│   │   └── executive.js                # Executive API endpoints
│   └── utils/
│       ├── formatters.js               # Number, currency, percentage formatters
│       ├── chartConfig.js              # Recharts theme and defaults
│       └── constants.js                # KPI definitions, preset queries
├── package.json
├── vite.config.js
└── tailwind.config.js
```

---

## 3. Data Model

### 3.1 Warehouse Database Schema

**Database:** `claims-warehouse.db` (separate from main `claims.db`)

**Table:** `claims_warehouse` (flat/denormalized structure for fast analytics)

```sql
CREATE TABLE claims_warehouse (
    -- Primary Key
    warehouse_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Link to Main Database
    claim_id INTEGER NOT NULL,  -- FK to claims.db -> claims.claim_id
    
    -- Time Dimensions
    fnol_date DATE NOT NULL,
    fnol_datetime TIMESTAMP NOT NULL,
    claim_closed_date DATE,
    claim_closed_datetime TIMESTAMP,
    month INTEGER NOT NULL,     -- 1-12
    week INTEGER NOT NULL,      -- 1-52
    day_of_week INTEGER NOT NULL,  -- 1=Monday, 7=Sunday
    quarter TEXT NOT NULL,      -- 'Q1', 'Q2', 'Q3', 'Q4'
    year INTEGER NOT NULL,
    
    -- Customer/Policy Dimensions
    customer_id INTEGER NOT NULL,
    policy_number TEXT NOT NULL,
    vehicle_vin TEXT NOT NULL,
    vehicle_make TEXT,
    vehicle_model TEXT,
    vehicle_year INTEGER,
    
    -- Processing Path
    damage_type TEXT NOT NULL,      -- 'body' (35% - AI eligible) or 'internal' (65% - NOT AI eligible)
    ai_eligible BOOLEAN NOT NULL,   -- TRUE if body damage (35%), FALSE if internal damage (65%)
    customer_ai_consent BOOLEAN,    -- TRUE if customer opted into AI (80-85% of eligible)
    processing_path TEXT NOT NULL,  -- 'ai_auto_approved', 'ai_human_reviewed', 'traditional'
    ai_enabled BOOLEAN NOT NULL,    -- TRUE if AI processing, FALSE if traditional
    ai_adoption_phase TEXT NOT NULL,  -- 'pre_ai', 'partial_ai', 'full_ai' (for 3-month timeline)
    
    -- KPI 1: Cycle Time
    cycle_time_days REAL NOT NULL,  -- Days from FNOL to claim closed
    cycle_time_hours REAL,          -- Hours for more granular analysis
    
    -- KPI 2: Auto-Adjudication
    auto_adjudicated BOOLEAN NOT NULL,  -- TRUE if no human review
    human_review_required BOOLEAN NOT NULL,
    human_review_reason TEXT,       -- 'customer_appeal', 'low_confidence', 'high_value', 'fraud_detected'
    
    -- KPI 3: Cost per Claim
    cost_estimated REAL NOT NULL,   -- AI estimated cost
    cost_actual REAL NOT NULL,      -- Actual repair cost
    cost_operational REAL NOT NULL, -- Operational cost to process claim
    cost_savings_factor REAL,       -- 0.9 (AI accepted), 0.8 (AI appealed), 1.0 (traditional)
    cost_total REAL NOT NULL,       -- cost_actual + cost_operational
    
    -- KPI 4: Fraud Detection
    is_fraudulent BOOLEAN NOT NULL,  -- Ground truth: is this claim actually fraudulent?
    fraud_detected BOOLEAN NOT NULL, -- Did our AI fraud detection catch it?
    fraud_risk_score REAL,          -- 0.0-1.0 (from fraud agent)
    fraud_type TEXT,                -- 'color_mismatch', 'make_model_mismatch', 'ai_generated_image'
    
    -- Accuracy Metrics
    cost_accuracy_percent REAL,    -- abs(estimated - actual) / actual * 100
    within_tolerance BOOLEAN,      -- TRUE if accuracy <= 10%
    
    -- Claim Details
    claim_amount REAL NOT NULL,
    damage_count INTEGER,          -- Number of damages in claim
    image_count INTEGER,           -- Number of images uploaded
    
    -- Derived Flags
    is_closed BOOLEAN NOT NULL,
    routed_to_traditional BOOLEAN NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for fast querying
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);

-- Indexes for Performance
CREATE INDEX idx_warehouse_fnol_date ON claims_warehouse(fnol_date);
CREATE INDEX idx_warehouse_month ON claims_warehouse(month);
CREATE INDEX idx_warehouse_processing_path ON claims_warehouse(processing_path);
CREATE INDEX idx_warehouse_ai_enabled ON claims_warehouse(ai_enabled);
CREATE INDEX idx_warehouse_ai_adoption_phase ON claims_warehouse(ai_adoption_phase);
CREATE INDEX idx_warehouse_claim_id ON claims_warehouse(claim_id);
```

### 3.2 Data Distribution (200 Claims, 3 Months)

**Month 1 (January 2026): Pre-AI Baseline**
- Total claims: 50
- AI-enabled: 10 (20%)
- Traditional: 40 (80%)
- AI adoption phase: 'pre_ai'

**Month 2 (February 2026): Partial AI Adoption**
- Total claims: 70
- AI-enabled: 35 (50%)
- Traditional: 35 (50%)
- AI adoption phase: 'partial_ai'

**Month 3 (March 2026): Full AI Adoption**
- Total claims: 80
- AI-enabled: 80 (100%)
- Traditional: 0 (0%)
- AI adoption phase: 'full_ai'

**Total:** 200 claims, 125 AI-enabled (62.5%), 75 traditional (37.5%)

### 3.3 KPI Calculation Logic

**KPI 1: Average Cycle Time (Days) - AI-Enabled Claims Only**

**Calculation Logic:**
```sql
-- Current period: AI-enabled claims average
SELECT AVG(cycle_time_days) 
FROM claims_warehouse 
WHERE ai_enabled = 1 
  AND fnol_date BETWEEN ? AND ?;

-- Baseline comparison: Traditional processing average (19.3 days)
-- Improvement % = (19.3 - AI_avg) / 19.3 * 100
```

**Rationale:**
- Shows the cycle time performance of AI-enabled claims
- Compares against traditional baseline (19.3 days industry average)
- Demonstrates time savings achieved by AI processing
- Traditional claims are NOT included in the average (they serve as the baseline)

**Expected Results:**
- Traditional baseline: 19.3 days (industry average)
- AI (auto-approved): ~4 days
- AI (human-reviewed): ~15 days
- **Weighted AI average: ~7-8 days**
- **Improvement vs traditional: ~60% reduction**

**Breakdown by Processing Path:**
```sql
SELECT 
    processing_path,
    COUNT(*) as count,
    AVG(cycle_time_days) as avg_cycle_time
FROM claims_warehouse
GROUP BY processing_path;
```

Expected:
- `traditional`: 3,670 claims @ 19.3 days (baseline - not in KPI calc)
- `ai_auto_approved`: 551 claims @ 4.0 days (fast)
- `ai_human_reviewed`: 279 claims @ 15.0 days (moderate)
- **AI weighted avg**: (551×4.0 + 279×15.0) / 830 = 7.7 days

**KPI 2: Auto-Adjudication Rate (%)**
```sql
SELECT 
    (COUNT(*) FILTER (WHERE auto_adjudicated = TRUE) * 100.0 / COUNT(*)) as auto_adj_rate
FROM claims_warehouse
WHERE ai_enabled = TRUE;
```

**Expected Results:**
- Month 1: ~60% (AI learning)
- Month 2: ~65% (improving)
- Month 3: ~70-75% (optimized)

**KPI 3: Cost per Claim ($)**
```sql
SELECT 
    AVG(cost_total) as avg_cost,
    AVG(CASE WHEN ai_enabled THEN cost_total * cost_savings_factor ELSE cost_total END) as avg_cost_with_savings
FROM claims_warehouse;
```

**Expected Results:**
- Traditional: ~$450/claim
- AI (accepted): $450 * 0.9 = $405/claim (10% savings)
- AI (appealed): $450 * 0.8 = $360/claim (20% savings due to faster resolution)
- Overall savings: ~18-23%

**KPI 4: Fraud Detection Rate (%)**
```sql
SELECT 
    (COUNT(*) FILTER (WHERE fraud_detected = TRUE) * 100.0 / COUNT(*)) as fraud_rate
FROM claims_warehouse
WHERE ai_enabled = TRUE;
```

**Expected Results:**
- Detection accuracy: ~85% (AI catches 85% of fraudulent claims)
- False positive rate: <5%

**Accuracy Metric: % Within ±10% Tolerance**
```sql
SELECT 
    (COUNT(*) FILTER (WHERE within_tolerance = TRUE) * 100.0 / COUNT(*)) as accuracy_rate
FROM claims_warehouse
WHERE ai_enabled = TRUE;
```

**Expected Results:** ~87-90% of AI estimates within ±10% of actual cost

---

## 4. API Endpoints

The Executive Portal integrates with backend API endpoints for warehouse queries and analytics.

### 4.1 Endpoint Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/executive/kpis` | GET | Fetch all 4 core KPI metrics with optional time filtering |
| `/api/v1/executive/trends/{kpi_name}` | GET | Time-series data for specific KPI (daily/weekly/monthly) |
| `/api/v1/executive/query` | POST | Execute preset or custom query, return chart-ready data |
| `/api/v1/executive/export/{format}` | GET | Export dashboard data (pdf/csv/png) |
| `/api/v1/executive/drilldown/{claim_id}` | GET | Fetch claim-level details for drill-down modal |

### 4.2 Detailed Specifications

#### 4.2.1 GET /api/v1/executive/kpis

**Purpose:** Fetch all 4 core KPI metrics with current values, trends, and comparisons

**Query Parameters:**
```
?time_period=last_quarter      # Options: last_week, last_month, last_quarter, custom
&start_date=2026-01-01         # Required if time_period=custom
&end_date=2026-03-31           # Required if time_period=custom
&compare_to_previous=true      # Include comparison to previous period
```

**Response Schema:**
```json
{
  "last_updated": "2026-05-07T10:30:00Z",
  "time_period": "last_quarter",
  "date_range": {
    "start": "2026-01-01",
    "end": "2026-03-31"
  },
  "kpis": {
    "cycle_time": {
      "current_value": 4.2,
      "unit": "days",
      "trend": "down",
      "change_percent": -65.0,
      "previous_value": 12.0,
      "target": 3.5,
      "status": "good"
    },
    "auto_adjudication_rate": {
      "current_value": 68.0,
      "unit": "percent",
      "trend": "up",
      "change_percent": 68.0,
      "previous_value": 0.0,
      "target": 70.0,
      "status": "good"
    },
    "cost_per_claim": {
      "current_value": 385.50,
      "unit": "dollars",
      "trend": "down",
      "change_percent": -14.3,
      "previous_value": 450.00,
      "target": 360.00,
      "status": "good"
    },
    "fraud_detection_rate": {
      "current_value": 85.0,
      "unit": "percent",
      "trend": "stable",
      "change_percent": 0.0,
      "previous_value": 85.0,
      "target": 90.0,
      "status": "good"
    }
  },
  "summary": {
    "total_claims": 200,
    "ai_enabled_claims": 125,
    "ai_adoption_rate": 62.5,
    "total_savings": 13000.00,
    "accuracy_within_tolerance": 88.5
  }
}
```

#### 4.2.2 GET /api/v1/executive/trends/{kpi_name}

**Purpose:** Fetch time-series data for specific KPI chart

**Path Parameters:**
- `kpi_name`: cycle_time | auto_adjudication_rate | cost_per_claim | fraud_detection_rate

**Query Parameters:**
```
?granularity=monthly    # Options: daily, weekly, monthly
&start_date=2026-01-01
&end_date=2026-03-31
```

**Response Schema:**
```json
{
  "kpi_name": "cycle_time",
  "granularity": "monthly",
  "data_points": [
    {
      "period": "2026-01",
      "period_label": "January 2026",
      "value": 11.2,
      "claim_count": 50,
      "ai_enabled_count": 10,
      "traditional_count": 40
    },
    {
      "period": "2026-02",
      "period_label": "February 2026",
      "value": 8.5,
      "claim_count": 70,
      "ai_enabled_count": 35,
      "traditional_count": 35
    },
    {
      "period": "2026-03",
      "period_label": "March 2026",
      "value": 4.2,
      "claim_count": 80,
      "ai_enabled_count": 80,
      "traditional_count": 0
    }
  ],
  "chart_config": {
    "chart_type": "bar_line_hybrid",
    "x_axis": "period_label",
    "y_axis": "value",
    "bar_data": "value",
    "line_data": "value",
    "color_scheme": "blue"
  }
}
```

#### 4.2.3 POST /api/v1/executive/query

**Purpose:** Execute preset or custom query

**Request Body:**
```json
{
  "query_type": "preset",           // 'preset' or 'custom'
  "preset_id": "processing_path",   // Required if query_type=preset
  "custom_query": null,             // Required if query_type=custom (NLP text)
  "time_range": {
    "start_date": "2026-01-01",
    "end_date": "2026-03-31"
  }
}
```

**Preset Query IDs:**
- `processing_path` - "How many claims were auto-approved vs human-reviewed?"
- `adjustment_rate` - "How many estimates needed adjustment during repairs?"
- `human_intervention` - "Show human review rate trend over 3 months"
- `fraud_effectiveness` - "What's the fraud detection rate by month?"

**Response Schema:**
```json
{
  "query_id": "processing_path",
  "query_text": "How many claims were auto-approved vs human-reviewed in Q1?",
  "result_type": "stacked_bar_chart",
  "data": [
    {"category": "Auto-Approved", "count": 85, "percent": 68.0},
    {"category": "Human-Reviewed", "count": 40, "percent": 32.0}
  ],
  "summary": {
    "total_claims": 125,
    "ai_enabled_only": true
  },
  "chart_config": {
    "chart_type": "stacked_bar",
    "x_axis": "category",
    "y_axis": "count",
    "color_scheme": ["#3b82f6", "#f59e0b"]
  },
  "raw_data_csv_url": "/api/v1/executive/export/csv?query_id=processing_path"
}
```

#### 4.2.4 GET /api/v1/executive/export/{format}

**Purpose:** Export dashboard data in various formats

**Path Parameters:**
- `format`: pdf | csv | png

**Query Parameters:**
```
?kpi=all                   # Options: all, cycle_time, auto_adj_rate, cost_per_claim, fraud_rate
&time_period=last_quarter
&include_charts=true       # PDF only
&chart_ids=cycle_time,cost # PNG only (comma-separated)
```

**Response:**
- PDF: Binary file with dashboard snapshot
- CSV: Tabular data with headers
- PNG: Chart images as ZIP archive

**Response Headers:**
```
Content-Type: application/pdf | text/csv | image/png
Content-Disposition: attachment; filename="executive-dashboard-2026-05-07.pdf"
```

#### 4.2.5 GET /api/v1/executive/drilldown/{claim_id}

**Purpose:** Fetch claim-level details for drill-down modal

**Path Parameters:**
- `claim_id`: Integer (FK to claims.db)

**Response Schema:**
```json
{
  "claim_id": 1023,
  "customer_name": "John Doe",
  "policy_number": "PA-992384-01",
  "vehicle": "2015 Toyota Corolla",
  "fnol_date": "2026-03-15",
  "claim_closed_date": "2026-03-19",
  "cycle_time_days": 4,
  "processing_path": "ai_auto_approved",
  "cost_estimated": 2500.00,
  "cost_actual": 2450.00,
  "cost_accuracy_percent": 2.0,
  "within_tolerance": true,
  "fraud_detected": false,
  "damages": [
    {"part": "front_bumper", "severity": "moderate", "cost": 1200.00},
    {"part": "hood", "severity": "minor", "cost": 1250.00}
  ],
  "events": [
    {"date": "2026-03-15", "status": "FNOL", "action_by": "customer"},
    {"date": "2026-03-15", "status": "AI_ESTIMATE_GENERATED", "action_by": "AI"},
    {"date": "2026-03-16", "status": "CUSTOMER_APPROVED", "action_by": "customer"},
    {"date": "2026-03-19", "status": "CLAIM_PAID", "action_by": "admin"}
  ]
}
```

---

## 5. User Interface Design

### 5.1 Layout Structure

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  ACME Claims : Executive Portal                    Last Updated: 10:30 AM       │
│  Business Intelligence Dashboard                   [Refresh Data]               │
├───────────────────────────────────────────────────────┬─────────────────────────┤
│                                                       │  Filters & Actions       │
│  💬 Ask a question or select a preset query          │  ┌───────────────────┐   │
│  ┌─────────────────────────────────────────────────┐ │  │ Time Period       │   │
│  │ [Dropdown: Select preset ▼] or [Free text...]  │ │  │ ○ Last Week       │   │
│  │ [Generate Report 🔍]                            │ │  │ ○ Last Month      │   │
│  └─────────────────────────────────────────────────┘ │  │ ● Last Quarter    │   │
│                                                       │  │ ○ Custom Range    │   │
│  ┌──────────── KPI Cards (Grid 2x2) ──────────────┐ │  └───────────────────┘   │
│  │                                                  │ │  ┌───────────────────┐   │
│  │  ┌─────────────┐  ┌─────────────┐              │ │  │ Export Options    │   │
│  │  │ Cycle Time  │  │ Auto-Adj    │              │ │  │ [📄 PDF Report]   │   │
│  │  │  4.2 days   │  │   68%       │              │ │  │ [📊 CSV Data]     │   │
│  │  │  ↓65%       │  │  ↑68%       │              │ │  │ [📈 Charts PNG]   │   │
│  │  │  ────────── │  │  ────────── │              │ │  └───────────────────┘   │
│  │  │ [Mini Chart]│  │ [Mini Chart]│              │ │  ┌───────────────────┐   │
│  │  └─────────────┘  └─────────────┘              │ │  │ Quick Stats       │   │
│  │                                                  │ │  │ Total Claims: 200 │   │
│  │  ┌─────────────┐  ┌─────────────┐              │ │  │ AI-Enabled: 125   │   │
│  │  │ Cost/Claim  │  │ Fraud Rate  │              │ │  │ AI Adoption: 62%  │   │
│  │  │  $385       │  │   85%       │              │ │  │ Avg Savings: 23%  │   │
│  │  │  ↓14%       │  │  ─          │              │ │  │ Accuracy: 88.5%   │   │
│  │  │  ────────── │  │  ────────── │              │ │  └───────────────────┘   │
│  │  │ [Mini Chart]│  │ [Mini Chart]│              │ │                          │
│  │  └─────────────┘  └─────────────┘              │ │  ┌───────────────────┐   │
│  │                                                  │ │  │ Extrapolation     │   │
│  └──────────────────────────────────────────────────┘ │  │ 200 → 20,000 Q    │   │
│                                                       │  │ Projected Savings │   │
│  ┌──────────── Detailed Charts ────────────────────┐ │  │ $2.6M/quarter     │   │
│  │                                                  │ │  └───────────────────┘   │
│  │  Chart 1: Cycle Time Trend (Bar + Line)         │ │                          │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │                          │
│  │  [Interactive Recharts visualization]           │ │                          │
│  │                                                  │ │                          │
│  │  Chart 2: Processing Path Mix (Stacked Bar)     │ │                          │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │                          │
│  │  [Interactive Recharts visualization]           │ │                          │
│  │                                                  │ │                          │
│  │  Chart 3: Cost Savings (Area Chart)             │ │                          │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │                          │
│  │  [Interactive Recharts visualization]           │ │                          │
│  │                                                  │ │                          │
│  │  Chart 4: Fraud Detection (Line Chart)          │ │                          │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │                          │
│  │  [Interactive Recharts visualization]           │ │                          │
│  └──────────────────────────────────────────────────┘ │                          │
│                                                       │                          │
│  ┌──────────── Sample Data Distribution ──────────┐ │                          │
│  │ Data Source: 4,500 sample claims (1% of actual)│ │                          │
│  │ Extrapolation: 100x (750 → 75,000 per month)   │ │                          │
│  │                                                  │ │                          │
│  │ Month     | Claims | Auto-Adj % | Threshold    │ │                          │
│  │ Oct 2025  |   750  |    18.4%   | $4,000       │ │                          │
│  │ Nov 2025  |   750  |    20.1%   | $4,500       │ │                          │
│  │ Dec 2025  |   750  |    32.7%   | $5,000       │ │                          │
│  │ Jan 2026  |   750  |    37.6%   | $5,500       │ │                          │
│  │ Feb 2026  |   750  |    51.1%   | $6,000       │ │                          │
│  │ Mar 2026  |   750  |    58.7%   | $6,500       │ │                          │
│  └──────────────────────────────────────────────────┘ │                          │
└───────────────────────────────────────────────────────┴─────────────────────────┘
```

### 5.2 Page Descriptions

#### 5.2.1 Login Page (`/login`)

**Purpose:** Minimal entry point (no authentication required for prototype)

**UI Elements:**
- Executive Portal logo/title
- "Enter Portal" button (no credentials required)
- Auto-redirect if localStorage has `executive_id`

**Behavior:**
- On click: Store `executive_id = "exec_001"` in localStorage → redirect to `/dashboard`
- No API validation (prototype mode)

---

#### 5.2.2 Dashboard Page (`/dashboard`)

**Purpose:** Main Business Intelligence dashboard

**Layout:** 70/30 split (main dashboard / filters sidebar)

##### Left Section (70%): Main Dashboard

**Demo Data Disclaimer (Top)**
- Prominent notice positioned at the very top of the dashboard
- Explains:
  - Dashboard is for demo purposes only
  - Data is synthetic, generated using industry averages
  - Dataset: 750 samples per month (4,500 total over 6 months)
  - Represents 1% of average monthly auto-claims in North America
  - Data extrapolated by factor of 100x for realistic projections
  - Link to detailed "Sample Data Distribution" section (anchor scroll)
- Background: Light blue info banner with icon
- Non-intrusive but clearly visible

**AI Processed Claims Pie Chart**
- Visual breakdown of claim processing paths
- Positioned below disclaimer
- Shows distribution of:
  - Traditional Processing (~81%)
  - AI Auto-Approved (~12%)
  - AI + Human Review (~7%)
- Color-coded with legend
- Interactive hover tooltips showing claim counts and percentages
- Helps executives understand the current state of AI adoption at a glance
- Title changed from "Processing Mix" to "AI Processed Claims"

**KPI Cards (1x3 Grid)**
- 3 core KPIs displayed as cards (removed Cost per Claim and Fraud Detection)
- Cards: Cycle Time Savings, Total Savings, Auto-Adjudication Rate
- Each card shows:
  - Big number (current value)
  - Trend indicator (↑/↓ with color)
  - Change percentage vs baseline/previous
  - Mini bar chart (6 months)
  - Target benchmark line
  - "View Details" link for drill-down

**Detailed Charts (Stacked Vertically - 1x3 Grid)**
- Chart 1: Cycle Time Savings Trend (Bar Chart)
- Chart 2: Total Savings Trend (Bar Chart)
- Chart 3: Auto-Adjudication Rate (Bar Chart)

**Query Interface (Positioned before Query Results)**
- Hybrid dropdown + free-text input
- 4 preset queries in dropdown
- "Generate Report" button
- Positioned immediately before Query Results section

**Query Results (Conditional - only shown when query executed)**
- Displays query results below Query Interface
- Shows table format with data

**Sample Data Distribution Section (Bottom)**
- Detailed breakdown of synthetic data methodology
- Monthly distribution table showing sample sizes and metrics
- Anchor target for disclaimer link

**Assumptions and References (Bottom)**
- Detailed assumptions about AI processing
- Industry references and citations
- Methodology notes

##### Right Section (30%): Filters & Actions

**Time Period Filter**
- Radio buttons: All Data (6 Months), Last Quarter, Last Month, Last Week, Custom Range
- Custom range: Date pickers for start/end dates
- Apply button (updates all charts)

**Quick Stats Card**
- Total Claims
- AI-Enabled Claims
- AI Adoption Rate
- Total Savings
- Accuracy Within Tolerance

**Extrapolation Card**
- Shows "4,500 claims → 450,000 claims" projection
- Projected savings scaled by 100x
- Current sample and projected quarterly volumes

**Export Options (Moved to Bottom of Sidebar)**
- [📄 PDF Report] - Full dashboard as PDF
- [📊 CSV Data] - Raw data table
- [📈 Charts PNG] - All charts as PNG images
- Note: Export functionality coming in Phase 5

---

### 5.3 Component Design

#### 5.3.0 Contextual Narratives (Help System)

**Purpose:** Provide business-focused explanations for each dashboard component

**Implementation:**
- Each major component (KPI cards, charts, AI Processed Claims) includes an info icon (ℹ️) in the header
- Clicking the icon opens a modal/popover with a narrative explanation
- Narratives are written for business personas (C-suite, operations managers)
- Include industry terminology, examples, and cross-references to other dashboard sections
- Help text explains: what is shown, why it matters, how to interpret, and what actions to take

**Narrative Topics:**
1. **Cycle Time Savings KPI** - Explains days saved vs traditional baseline, STP efficiency
2. **Total Savings KPI** - Explains operational cost reduction, ROI calculation
3. **Auto-Adjudication Rate KPI** - Explains STP vs human review, progressive improvement
4. **AI Processed Claims Chart** - Explains processing path distribution, eligibility constraints
5. **Trend Charts** - Explains monthly progression, seasonal patterns, target achievement
6. **Query Interface** - Explains preset queries, custom questions, drill-down capabilities

**UI Pattern:**
```
┌─────────────────────────────────┐
│ Cycle Time Savings    ℹ️        │  ← Click info icon
│                                 │
│     11.6 days   ↑60.1%         │
│     ...                         │
└─────────────────────────────────┘

Modal opens:
┌──────────────────────────────────────────┐
│ ⚠️  AI Generated Summary                 │  ← Disclaimer banner
├──────────────────────────────────────────┤
│ 📊 Cycle Time Savings                    │
│                                          │
│ This metric shows the operational       │
│ efficiency gained by AI-enabled claims  │
│ processing. Traditional claims take     │
│ 19.3 days on average (industry          │
│ baseline), while AI-enabled claims      │
│ are processed in just 7.7 days...       │
│                                          │
│ [Got it]                                 │
└──────────────────────────────────────────┘
```

**Important:** All narrative modals MUST display an "AI Generated Summary" disclaimer banner at the top to indicate the content is AI-generated and may require verification.

#### 5.3.1 KPICard Component

**Purpose:** Display single KPI with current value, trend, and mini chart

**Props:**
```jsx
<KPICard
  title="Average Cycle Time"
  currentValue={4.2}
  unit="days"
  trend="down"          // 'up', 'down', 'stable'
  changePercent={-65.0}
  previousValue={12.0}
  target={3.5}
  status="good"         // 'good', 'warning', 'critical'
  miniChartData={[
    { month: 'Jan', value: 11.2 },
    { month: 'Feb', value: 8.5 },
    { month: 'Mar', value: 4.2 }
  ]}
  onDrillDown={() => showDetailedChart('cycle_time')}
/>
```

**UI Layout:**
```
┌───────────────────────────────────┐
│ Average Cycle Time                │
│                                   │
│     4.2 days   ↓65%              │ (Big number + trend)
│     vs 12.0 days                 │ (Comparison)
│                                   │
│  ┌─────────────────────────────┐ │ (Mini chart)
│  │ ▂▅█                         │ │
│  │ Jan  Feb  Mar               │ │
│  └─────────────────────────────┘ │
│                                   │
│  Target: 3.5 days   [Details →] │ (Target + drill-down)
└───────────────────────────────────┘
```

**Visual States:**
- **Good:** Green border, green trend arrow
- **Warning:** Yellow border, yellow trend arrow
- **Critical:** Red border, red trend arrow

**Implementation:**
```jsx
const KPICard = ({ title, currentValue, unit, trend, changePercent, target, miniChartData }) => {
  const trendIcon = trend === 'up' ? '↑' : trend === 'down' ? '↓' : '─';
  const trendColor = (trend === 'up' && shouldGoUp(title)) || (trend === 'down' && !shouldGoUp(title))
    ? 'text-green-600' : trend === 'stable' ? 'text-gray-600' : 'text-red-600';

  return (
    <Card className="p-6">
      <h3 className="text-sm font-medium text-gray-700">{title}</h3>
      <div className="mt-4 flex items-baseline justify-between">
        <p className="text-4xl font-semibold text-gray-900">
          {formatValue(currentValue, unit)}
        </p>
        <span className={`text-xl ${trendColor}`}>
          {trendIcon}{Math.abs(changePercent)}%
        </span>
      </div>
      <ResponsiveContainer width="100%" height={60}>
        <BarChart data={miniChartData}>
          <Bar dataKey="value" fill="#3b82f6" />
          <Line type="monotone" dataKey="value" stroke="#ef4444" />
        </BarChart>
      </ResponsiveContainer>
      {target && <p className="text-xs text-gray-500 mt-2">Target: {formatValue(target, unit)}</p>}
    </Card>
  );
};
```

---

#### 5.3.2 TrendChart Component

**Purpose:** Display detailed trend chart (Bar + Line Hybrid)

**Props:**
```jsx
<TrendChart
  title="Cycle Time Trend"
  kpiName="cycle_time"
  data={trendData}
  chartType="bar_line_hybrid"  // 'bar_line_hybrid', 'stacked_bar', 'area', 'line'
  xAxis="period_label"
  yAxis="value"
  color="#3b82f6"
  showLegend={true}
  enableDrillDown={true}
  onBarClick={(dataPoint) => openDrillDownModal(dataPoint)}
/>
```

**UI Layout:**
```
┌─────────────────────────────────────────────────┐
│ Cycle Time Trend                    [⚙ Options]│
│ ─────────────────────────────────────────────── │
│                                                 │
│  14 ┤                                           │
│  12 ┤  █                                        │
│  10 ┤  █                                        │
│   8 ┤  █  █                                     │
│   6 ┤  █  █                                     │
│   4 ┤  █  █  █                                  │
│   2 ┤  █  █  █                                  │
│   0 └─────────────────────────────────────────  │
│       Jan    Feb    Mar                         │
│                                                 │
│  Legend: █ Actual  ─ Trend Line                │
└─────────────────────────────────────────────────┘
```

**Chart Types:**
1. **Bar + Line Hybrid:** Bars for values, line for trend (default for KPIs)
2. **Stacked Bar:** Show composition (e.g., AI vs Traditional)
3. **Area Chart:** Show cumulative savings over time
4. **Line Chart:** Show accuracy/fraud rate trends

**Implementation (Recharts):**
```jsx
const TrendChart = ({ title, data, chartType, xAxis, yAxis }) => {
  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xAxis} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey={yAxis} fill="#3b82f6" />
          <Line type="monotone" dataKey={yAxis} stroke="#ef4444" strokeWidth={2} />
        </ComposedChart>
      </ResponsiveContainer>
    </Card>
  );
};
```

---

#### 5.3.3 QueryInterface Component

**Purpose:** Hybrid dropdown + free-text for custom queries

**Props:**
```jsx
<QueryInterface
  presetQueries={[
    { id: 'processing_path', label: 'Claims by Processing Path', enabled: true },
    { id: 'adjustment_rate', label: 'Adjustment Rate Analysis', enabled: true },
    { id: 'human_intervention', label: 'Human Intervention Trends', enabled: true },
    { id: 'fraud_effectiveness', label: 'Fraud Detection Effectiveness', enabled: true }
  ]}
  onQuerySubmit={(queryType, queryText) => executeQuery(queryType, queryText)}
  enableFreeText={false}  // MVP: Disable free-text, future enhancement
/>
```

**UI Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│ 💬 Ask a question or select a preset query                  │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Select a query...                                     ▼ │ │
│ │ - Claims by Processing Path                             │ │
│ │ - Adjustment Rate Analysis                              │ │
│ │ - Human Intervention Trends                             │ │
│ │ - Fraud Detection Effectiveness                         │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ [Generate Report 🔍]                                        │
└─────────────────────────────────────────────────────────────┘
```

**Future Enhancement (Free-Text):**
```
┌─────────────────────────────────────────────────────────────┐
│ 💬 Ask a question or select a preset query                  │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ [Dropdown: Select preset ▼] OR                          │ │
│ │ [Free text: Type your question here...]                 │ │
│ └─────────────────────────────────────────────────────────┘ │
│ [Generate Report 🔍]                                        │
└─────────────────────────────────────────────────────────────┘
```

**Implementation:**
```jsx
const QueryInterface = ({ presetQueries, onQuerySubmit }) => {
  const [selectedPreset, setSelectedPreset] = useState(null);
  const [customText, setCustomText] = useState('');

  const handleSubmit = () => {
    if (selectedPreset) {
      onQuerySubmit('preset', selectedPreset.id);
    } else if (customText.trim()) {
      onQuerySubmit('custom', customText);
    }
  };

  return (
    <Card className="p-4 mb-6">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-2xl">💬</span>
        <h3 className="text-lg font-medium">Ask a question or select a preset query</h3>
      </div>
      <select 
        className="w-full p-3 border rounded-lg mb-4"
        onChange={(e) => setSelectedPreset(presetQueries.find(q => q.id === e.target.value))}
      >
        <option value="">Select a query...</option>
        {presetQueries.map(query => (
          <option key={query.id} value={query.id}>{query.label}</option>
        ))}
      </select>
      <Button onClick={handleSubmit} variant="primary" icon={<Search />}>
        Generate Report
      </Button>
    </Card>
  );
};
```

---

#### 5.3.4 FilterSidebar Component

**Purpose:** Time filtering and export actions

**Props:**
```jsx
<FilterSidebar
  currentPeriod="last_quarter"
  onPeriodChange={(period, customRange) => updateDashboard(period, customRange)}
  onExport={(format) => exportDashboard(format)}
/>
```

**UI Layout:**
```
┌───────────────────────────┐
│ Time Period               │
│ ○ Last Week               │
│ ○ Last Month              │
│ ● Last Quarter            │
│ ○ Custom Range            │
│   [Start Date]            │
│   [End Date]              │
│   [Apply]                 │
└───────────────────────────┘
┌───────────────────────────┐
│ Export Options            │
│ [📄 PDF Report]           │
│ [📊 CSV Data]             │
│ [📈 Charts PNG]           │
└───────────────────────────┘
┌───────────────────────────┐
│ Quick Stats               │
│ Total Claims: 200         │
│ AI-Enabled: 125           │
│ AI Adoption: 62.5%        │
│ Avg Savings: 23%          │
│ Accuracy: 88.5%           │
└───────────────────────────┘
┌───────────────────────────┐
│ Extrapolation             │
│ Current: 200 claims       │
│ Projected: 20,000/quarter │
│ Est. Savings: $2.6M/Q     │
└───────────────────────────┘
```

---

#### 5.3.5 SampleDataDistribution Component

**Purpose:** Display the sample data distribution table showing data methodology

**Props:**
```jsx
<SampleDataDistribution
  sampleSize={4500}
  actualVolume={450000}
  extrapolationFactor={100}
  monthlyDistribution={[
    { month: 'Oct 2025', claims: 750, autoAdjPct: 18.4, threshold: 4000 },
    { month: 'Nov 2025', claims: 750, autoAdjPct: 20.1, threshold: 4500 },
    { month: 'Dec 2025', claims: 750, autoAdjPct: 32.7, threshold: 5000 },
    { month: 'Jan 2026', claims: 750, autoAdjPct: 37.6, threshold: 5500 },
    { month: 'Feb 2026', claims: 750, autoAdjPct: 51.1, threshold: 6000 },
    { month: 'Mar 2026', claims: 750, autoAdjPct: 58.7, threshold: 6500 },
  ]}
/>
```

**UI Layout:**
```
┌───────────────────────────────────────────────────────────┐
│ Sample Data Distribution & Methodology                    │
│ ───────────────────────────────────────────────────────── │
│                                                           │
│ 📊 Data Source                                            │
│ • Sample Size: 4,500 claims (1% of actual volume)         │
│ • Actual Volume: 450,000 claims (Oct 2025 - Mar 2026)    │
│ • Extrapolation Factor: 100x                              │
│ • All dashboard metrics are extrapolated values           │
│                                                           │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ Month     │ Claims │ Auto-Adj % │ Threshold │ Fraud │   │
│ │───────────│────────│────────────│───────────│───────│   │
│ │ Oct 2025  │   750  │    18.4%   │  $4,000   │ 5.8%  │   │
│ │ Nov 2025  │   750  │    20.1%   │  $4,500   │ 5.3%  │   │
│ │ Dec 2025  │   750  │    32.7%   │  $5,000   │ 9.4%  │   │
│ │ Jan 2026  │   750  │    37.6%   │  $5,500   │ 8.5%  │   │
│ │ Feb 2026  │   750  │    51.1%   │  $6,000   │ 11.7% │   │
│ │ Mar 2026  │   750  │    58.7%   │  $6,500   │ 10.5% │   │
│ │───────────│────────│────────────│───────────│───────│   │
│ │ Total     │ 4,500  │    36.4%   │    -      │ 8.4%  │   │
│ └─────────────────────────────────────────────────────┘   │
│                                                           │
│ ℹ️  Note: Dashboard displays extrapolated values (×100)   │
│    representing full operational volume                   │
└───────────────────────────────────────────────────────────┘
```

**Visual States:**
- Collapsible section with "Show/Hide Methodology" toggle
- Default: Collapsed (only visible when user clicks to expand)
- Sticky footer option for always-visible reminder

**Implementation:**
```jsx
const SampleDataDistribution = ({ sampleSize, actualVolume, extrapolationFactor, monthlyDistribution }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <Card className="mt-8 border-t-2 border-blue-200">
      <div 
        className="flex items-center justify-between cursor-pointer p-4"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-700">
            📊 Sample Data Distribution & Methodology
          </span>
          <Badge variant="info" size="sm">
            {sampleSize.toLocaleString()} samples
          </Badge>
        </div>
        <button className="text-blue-600 text-sm">
          {isExpanded ? '▼ Hide' : '▶ Show'}
        </button>
      </div>

      {isExpanded && (
        <div className="p-6 border-t">
          <div className="mb-4 bg-blue-50 p-4 rounded-lg">
            <p className="text-sm text-gray-700">
              <strong>Data Source:</strong> {sampleSize.toLocaleString()} claims (1% sample of {actualVolume.toLocaleString()} actual claims)
            </p>
            <p className="text-sm text-gray-700">
              <strong>Extrapolation:</strong> All metrics displayed are multiplied by {extrapolationFactor}× to represent full volume
            </p>
          </div>

          <table className="w-full text-sm">
            <thead className="bg-gray-100">
              <tr>
                <th className="px-4 py-2 text-left">Month</th>
                <th className="px-4 py-2 text-right">Claims</th>
                <th className="px-4 py-2 text-right">Auto-Adj %</th>
                <th className="px-4 py-2 text-right">Threshold</th>
                <th className="px-4 py-2 text-right">Fraud Det %</th>
              </tr>
            </thead>
            <tbody>
              {monthlyDistribution.map((row, idx) => (
                <tr key={idx} className="border-b hover:bg-gray-50">
                  <td className="px-4 py-2">{row.month}</td>
                  <td className="px-4 py-2 text-right">{row.claims.toLocaleString()}</td>
                  <td className="px-4 py-2 text-right">{row.autoAdjPct}%</td>
                  <td className="px-4 py-2 text-right">${row.threshold.toLocaleString()}</td>
                  <td className="px-4 py-2 text-right">{row.fraudPct}%</td>
                </tr>
              ))}
              <tr className="font-semibold bg-gray-100">
                <td className="px-4 py-2">Total</td>
                <td className="px-4 py-2 text-right">{sampleSize.toLocaleString()}</td>
                <td className="px-4 py-2 text-right" colSpan="3">
                  {(monthlyDistribution.reduce((sum, m) => sum + m.autoAdjPct, 0) / monthlyDistribution.length).toFixed(1)}% avg
                </td>
              </tr>
            </tbody>
          </table>

          <div className="mt-4 p-3 bg-yellow-50 border-l-4 border-yellow-400 rounded">
            <p className="text-xs text-gray-600">
              ℹ️ <strong>Note:</strong> All KPIs and charts on this dashboard display extrapolated values 
              (×{extrapolationFactor}) representing the full operational volume of {actualVolume.toLocaleString()} claims.
            </p>
          </div>
        </div>
      )}
    </Card>
  );
};
```

---

#### 5.3.6 DrillDownModal Component

**Purpose:** Show claim-level details when drilling down from charts

**Props:**
```jsx
<DrillDownModal
  isOpen={isDrillDownOpen}
  onClose={() => setIsDrillDownOpen(false)}
  claimId={selectedClaimId}
  claimDetails={claimDetails}
/>
```

**UI Layout:**
```
┌─────────────────────────────────────────────────┐
│ Claim Details: #1023                       [×]  │
│ ─────────────────────────────────────────────── │
│                                                 │
│ Customer: John Doe                              │
│ Policy: PA-992384-01                            │
│ Vehicle: 2015 Toyota Corolla                    │
│                                                 │
│ Processing Path: AI Auto-Approved               │
│ Cycle Time: 4 days (FNOL: 03/15 → Closed: 03/19)│
│                                                 │
│ Cost Estimated: $2,500.00                       │
│ Cost Actual: $2,450.00                          │
│ Accuracy: 2.0% ✓ Within Tolerance              │
│                                                 │
│ Damages (2):                                    │
│ - Front Bumper (Moderate): $1,200              │
│ - Hood (Minor): $1,250                         │
│                                                 │
│ Timeline:                                       │
│ 03/15  FNOL Submitted                          │
│ 03/15  AI Estimate Generated                   │
│ 03/16  Customer Approved                       │
│ 03/19  Claim Paid                              │
│                                                 │
│ [View Full Claim →]  [Export PDF]              │
└─────────────────────────────────────────────────┘
```

---

## 6. State Management

### 6.1 Authentication Context

**Session Management:**
- Uses `sessionStorage` instead of `localStorage` for automatic logout when browser closes
- Authentication tokens are cleared when user closes the browser window/tab
- Listens to `beforeunload` event to ensure cleanup on window close
- Checks API server health on mount using `/health` endpoint
- Shows error message with start instructions if API server is down
- **Security Rationale**: Prevents unauthorized access if executive forgets to logout

**API Server Detection:**
```javascript
const checkApiServer = async () => {
  try {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/health`, {
      signal: AbortSignal.timeout(5000)
    });
    if (!response.ok) throw new Error(`API returned ${response.status}`);
    setApiServerDown(false);
  } catch (error) {
    if (error.name === 'TypeError' || error.message.includes('Failed to fetch') || 
        error.name === 'TimeoutError') {
      setApiServerDown(true);
    }
  }
};
```

### 6.2 Dashboard State

```jsx
const [kpis, setKpis] = useState(null);              // KPI data from API
const [trendData, setTrendData] = useState({});      // Trend charts data
const [queryResults, setQueryResults] = useState(null); // Custom query results
const [timePeriod, setTimePeriod] = useState('last_quarter');
const [customRange, setCustomRange] = useState(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);
const [lastUpdated, setLastUpdated] = useState(null);
const [apiServerDown, setApiServerDown] = useState(false); // API health status
```

### 6.3 State Flow

```
1. Page Load:
   - fetchKPIs(timePeriod) → GET /api/v1/executive/kpis
   - setKpis(response.kpis)
   - setLastUpdated(response.last_updated)
   - fetchTrends() → GET /api/v1/executive/trends/{kpi} (4 calls in parallel)
   - setTrendData({ cycle_time: [...], auto_adj: [...], ... })
   - setLoading(false)

2. Time Period Change:
   - setTimePeriod(newPeriod)
   - Refetch all data with new time filter
   - Update all charts

3. Query Execution:
   - executeQuery(queryType, queryText) → POST /api/v1/executive/query
   - setQueryResults(response)
   - Render new chart below KPI cards

4. Export:
   - exportDashboard(format) → GET /api/v1/executive/export/{format}
   - Download file via browser

5. Drill-Down:
   - fetchClaimDetails(claimId) → GET /api/v1/executive/drilldown/{claimId}
   - Open DrillDownModal with claim details
```

---

## 7. Synthetic Data Generation

### 7.1 Overview & Data Rules

**Purpose:** Generate realistic synthetic claims data for the claims warehouse following industry benchmarks and progressive AI adoption patterns.

**Data Source:** `simulation/synthetic-data-rules.md`

**Key Constraints:**
- **Time Period:** October 2025 - March 2026 (6 months)
- **Total Claims per Month:** 75,000 claims (actual volume)
- **Sample Data:** 1% of actual (750 claims per month)
- **Total Sample Records:** 4,500 claims
- **Dashboard Display:** Results are extrapolated back to full volume

**AI Eligibility Constraint:**
- **Only body damage claims are eligible for AI auto-adjudication**
- Internal damage requires physical inspection and is NOT eligible for AI processing
- **Industry Data:** 35% of all auto insurance claims are for body work (Source: [Auto Body News - 2025 Data Points](https://www.autobodynews.com/news/2025-data-points-to-fewer-claims-more-collision-repair-complexity-in-2026))
- **AI-Eligible Claims:** 35% of all claims (body work only)
- **Non-Eligible Claims:** 65% of all claims (internal damage, mechanical, liability, etc.)

**Customer AI Adoption:**
- Not all customers will opt-in to AI processing
- Realistic customer adoption target: ~80-85% of eligible claims
- **Effective AI Adoption Rate:** 35% (eligible) × 80% (customer adoption) = **28% of total claims**

**Industry Benchmarks:**
- Fraudulent auto claims rate: 15% (industry average)
- Fraud detection target: 50% of potential fraudulent claims
- Average cycle time: 19.3 days (traditional processing)
- Average claim loss: $6,000 (repair/settlement cost paid to customer)

**Operational Cost per Claim (to process the claim):**
- Traditional/Standard processing: **$325** per claim
- AI auto-adjudicated (no human review): **$32.50** per claim (90% cheaper than traditional)
- AI auto-adjudicated with 1 human review: **$48.75** per claim (85% cheaper than traditional)

**Cost Savings Calculation:**
- Traditional operational cost: $325 (baseline)
- AI auto-approved: $325 × 0.10 = $32.50 (90% savings)
- AI with human review: $325 × 0.15 = $48.75 (85% savings)
- Savings factor for traditional: 1.0 (no savings)

---

### 7.2 Monthly Data Distribution Rules

The data generation follows a **progressive AI adoption** pattern where both the auto-adjudication threshold and fraud detection rates improve over time:

**AI Eligibility (Constant):**
- 35% of claims are body damage (AI-eligible)
- 65% of claims are internal damage (NOT AI-eligible)
- Of eligible claims, 80% of customers opt-in to AI processing

**Expected AI-Enabled Claims per Month:**
- Base eligible: 750 × 35% = 263 claims (body damage)
- Customer consent: 263 × 80% = 210 claims (consented)
- Monthly AI adoption rate applies to consented pool

| Month | Total Claims | AI Eligible (35%) | Customer Consent (80%) | AI Adoption Rate | AI-Enabled Claims | Auto-Adj Threshold | Auto-Approval Rate | Fraud Detection Rate |
|-------|--------------|-------------------|------------------------|------------------|-------------------|-------------------|-------------------|---------------------|
| Oct 2025 | 750 | 263 | 210 | 20% | ~42 | $5,500 | 70% | 40% |
| Nov 2025 | 750 | 263 | 210 | 30% | ~63 | $6,000 | 80% | 50% |
| Dec 2025 | 750 | 263 | 210 | 50% | ~105 | $6,500 | 88% | 60% |
| Jan 2026 | 750 | 263 | 210 | 100% | ~210 | $7,000 | 94% | 70% |
| Feb 2026 | 750 | 263 | 210 | 100% | ~210 | $7,500 | 97% | 80% |
| Mar 2026 | 750 | 263 | 210 | 100% | ~210 | $8,000 | 99% | 85% |

**Total:** 4,500 sample claims
- AI-Eligible: ~1,578 claims (35%)
- Customer Consented: ~1,260 claims (28%)
- AI-Enabled (weighted avg): ~840 claims (18.7%)
- Traditional: ~3,660 claims (81.3%)

**Realistic Targets:**
- AI Eligibility Rate: 35% (industry constraint - body damage only)
- Customer Adoption Rate: 80% (of eligible claims)
- Overall AI Usage: 28% maximum (35% × 80%)
- Auto-Approval Rate: Aggressive progressive improvement from 70% → 99% (of claims below threshold)
  - Simulates rapidly improving AI confidence over 6 months
  - Reduces human review requirements as system learns and confidence increases
  - Combined with increasing thresholds ($5,500 → $8,000) to expand auto-adjudication range
  - Target: Maximize auto-approval, minimize human review requirements
  - Actual final distribution: 12.2% auto-approved, 6.2% with review
  - Monthly improvement: ~3-4% increase in auto-approval rate per month

---

### 7.3 Data Generation Algorithm

**File:** `scripts/seed-claims-warehouse.py`

**High-Level Logic:**

```
For each month (Oct 2025 - Mar 2026):
    For each claim (1-750):
        1. Generate claim_amount (average $6,000, normal distribution)
        
        2. Determine AI eligibility:
           - 35% chance: damage_type = 'body', ai_eligible = TRUE
           - 65% chance: damage_type = 'internal', ai_eligible = FALSE
        
        3. Determine customer AI consent (only for eligible claims):
           - IF ai_eligible = TRUE:
               - 80% chance: customer_ai_consent = TRUE
               - 20% chance: customer_ai_consent = FALSE (customer prefers traditional)
           - IF ai_eligible = FALSE:
               - customer_ai_consent = NULL (not applicable)
        
        4. Determine if AI processing is enabled:
           - ai_enabled = (ai_eligible AND customer_ai_consent AND month_ai_adoption_rate)
           - Month AI adoption rates: Oct=20%, Nov=30%, Dec=50%, Jan=100%, Feb=100%, Mar=100%
           - For eligible+consented claims, use monthly rate to phase in AI gradually
        
        5. Determine if auto-adjudicated (only for AI-enabled claims):
           - IF ai_enabled = TRUE AND claim_amount < threshold_for_month:
               - auto_adjudicated = TRUE
           - ELSE:
               - auto_adjudicated = FALSE (human review required)
        
        3. Calculate fraud potential:
           - IF auto_adjudicated = TRUE:
               - 15% chance of being actually fraudulent
               - fraud_detected = TRUE based on month's detection rate
           - ELSE fraud_detected = FALSE (manual review catches all)
        
        4. Calculate cycle_time:
           - Auto-adjudicated: 3-5 days (gaussian, mean=4)
           - Human review: 10-20 days (gaussian, mean=15)
           - Traditional: 15-25 days (gaussian, mean=19.3)
        
        5. Calculate costs:
           - cost_estimated = claim_amount
           - cost_actual = claim_amount * (0.85 to 1.15) # ±15% variance
           - cost_operational:
               - Auto-adj (no review): $20-30
               - Auto-adj (reviewed): $40-50
               - Traditional: $200-450
           - cost_savings_factor:
               - Auto-adj (no review): 0.9
               - Auto-adj (reviewed): 0.85
               - Traditional: 1.0
        
        6. Set processing_path:
           - 'ai_auto_approved': auto-adjudicated, no human intervention
           - 'ai_human_reviewed': flagged by AI, human review required
           - 'traditional': not processed by AI
        
        7. Set ai_adoption_phase:
           - Oct-Nov 2025: 'early_adoption'
           - Dec 2025-Jan 2026: 'mid_adoption'
           - Feb-Mar 2026: 'mature_adoption'
        
        8. Generate customer/vehicle details:
           - customer_id, policy_number, vehicle_vin, make, model, year
           - Use Faker library for realistic names and data
        
        9. Calculate accuracy metrics:
           - cost_accuracy_percent = |estimated - actual| / actual * 100
           - within_tolerance = TRUE if accuracy <= 10%
```

---

### 7.4 Detailed Python Implementation

**File:** `scripts/seed-claims-warehouse.py`

```python
#!/usr/bin/env python3
"""
Seed Claims Warehouse Database with Synthetic Data

Generates 4,500 synthetic claims (750 per month for 6 months)
following the rules defined in simulation/synthetic-data-rules.md

Usage:
    python scripts/seed-claims-warehouse.py
    python scripts/seed-claims-warehouse.py --reset  # Clear and regenerate
"""

import sqlite3
import random
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker

fake = Faker()
random.seed(42)  # For reproducibility

# Constants from synthetic-data-rules.md
MONTHS = [
    {'date': '2025-10', 'month': 10, 'year': 2025, 'threshold': 4000, 'fraud_detection_rate': 0.40},
    {'date': '2025-11', 'month': 11, 'year': 2025, 'threshold': 4500, 'fraud_detection_rate': 0.50},
    {'date': '2025-12', 'month': 12, 'year': 2025, 'threshold': 5000, 'fraud_detection_rate': 0.60},
    {'date': '2026-01', 'month': 1, 'year': 2026, 'threshold': 5500, 'fraud_detection_rate': 0.70},
    {'date': '2026-02', 'month': 2, 'year': 2026, 'threshold': 6000, 'fraud_detection_rate': 0.80},
    {'date': '2026-03', 'month': 3, 'year': 2026, 'threshold': 6500, 'fraud_detection_rate': 0.85},
]

CLAIMS_PER_MONTH = 750
AVERAGE_CLAIM_AMOUNT = 6000
FRAUD_RATE_OF_AUTO_ADJ = 0.15  # 15% of auto-adjudicated claims are fraudulent
INDUSTRY_CYCLE_TIME_AVG = 19.3

# Operational cost configurations (cost to PROCESS the claim, not claim loss amount)
COST_TRADITIONAL = 325.00  # Traditional/standard processing baseline
COST_AI_AUTO_APPROVED = 32.50  # 90% cheaper (10% of traditional)
COST_AI_HUMAN_REVIEW = 48.75  # 85% cheaper (15% of traditional)

# Cost savings factors (what percentage of traditional cost is spent)
SAVINGS_FACTOR_AUTO = 0.10  # AI auto-approved costs 10% of traditional
SAVINGS_FACTOR_REVIEWED = 0.15  # AI + human review costs 15% of traditional
SAVINGS_FACTOR_TRADITIONAL = 1.0  # Traditional costs 100% (baseline)

ACCURACY_TOLERANCE = 0.10  # ±10%


def get_ai_adoption_phase(month_year):
    """Determine AI adoption phase based on month"""
    if month_year in ['2025-10', '2025-11']:
        return 'early_adoption'
    elif month_year in ['2025-12', '2026-01']:
        return 'mid_adoption'
    else:
        return 'mature_adoption'


def generate_claim(claim_id, month_config):
    """Generate a single synthetic claim"""
    month = month_config['month']
    year = month_config['year']
    threshold = month_config['threshold']
    fraud_detection_rate = month_config['fraud_detection_rate']
    
    # 1. Generate claim amount (normal distribution, mean=$6000, std=$2000)
    claim_amount = max(500, random.gauss(AVERAGE_CLAIM_AMOUNT, 2000))
    
    # 2. Determine if auto-adjudicated
    auto_adjudicated = claim_amount < threshold
    
    # 3. Determine processing path and AI enablement
    if auto_adjudicated:
        # 80% fully auto-approved, 20% require human review even below threshold
        if random.random() < 0.80:
            processing_path = 'ai_auto_approved'
            ai_enabled = True
            human_review_required = False
            human_review_reason = None
        else:
            processing_path = 'ai_human_reviewed'
            ai_enabled = True
            human_review_required = True
            human_review_reason = random.choice(['customer_appeal', 'low_confidence', 'fraud_detected'])
    else:
        # Above threshold - requires human review
        processing_path = 'ai_human_reviewed'
        ai_enabled = True
        human_review_required = True
        human_review_reason = 'high_value'
    
    # 4. Fraud detection (15% of auto-adjudicated claims are fraudulent)
    is_fraudulent = auto_adjudicated and random.random() < FRAUD_RATE_OF_AUTO_ADJ
    
    if is_fraudulent:
        fraud_detected = random.random() < fraud_detection_rate
        fraud_risk_score = random.uniform(0.7, 1.0) if fraud_detected else random.uniform(0.3, 0.6)
        fraud_type = random.choice(['color_mismatch', 'make_model_mismatch', 'ai_generated_image']) if fraud_detected else None
    else:
        fraud_detected = False
        fraud_risk_score = random.uniform(0.0, 0.3)
        fraud_type = None
    
    # 5. Calculate cycle time
    if processing_path == 'ai_auto_approved':
        cycle_time_days = max(1, random.gauss(4, 1))  # 3-5 days
    elif processing_path == 'ai_human_reviewed':
        cycle_time_days = max(5, random.gauss(15, 3))  # 10-20 days
    else:
        cycle_time_days = max(10, random.gauss(INDUSTRY_CYCLE_TIME_AVG, 3))  # 15-25 days
    
    cycle_time_hours = cycle_time_days * 24
    
    # 6. Calculate costs
    cost_estimated = claim_amount
    cost_actual = claim_amount * random.uniform(0.85, 1.15)  # ±15% variance
    
    if processing_path == 'ai_auto_approved':
        cost_operational = random.uniform(*COST_STP)
        cost_savings_factor = SAVINGS_FACTOR_AUTO
    elif processing_path == 'ai_human_reviewed':
        cost_operational = random.uniform(*COST_HUMAN_REVIEW)
        cost_savings_factor = SAVINGS_FACTOR_REVIEWED
    else:
        cost_operational = random.uniform(*COST_TRADITIONAL)
        cost_savings_factor = SAVINGS_FACTOR_TRADITIONAL
    
    cost_total = cost_actual + cost_operational
    
    # 7. Calculate accuracy
    cost_accuracy_percent = abs(cost_estimated - cost_actual) / cost_actual * 100
    within_tolerance = cost_accuracy_percent <= (ACCURACY_TOLERANCE * 100)
    
    # 8. Generate dates
    day = random.randint(1, 28)  # Avoid month-end edge cases
    fnol_date = datetime(year, month, day)
    fnol_datetime = fnol_date + timedelta(hours=random.randint(8, 18))  # Business hours
    claim_closed_datetime = fnol_datetime + timedelta(days=cycle_time_days)
    claim_closed_date = claim_closed_datetime.date()
    
    # 9. Generate customer/vehicle details
    customer_id = random.randint(1000, 9999)
    policy_number = f"PA-{random.randint(100000, 999999)}-{random.randint(10, 99)}"
    vehicle_vin = fake.vin()
    vehicle_make = random.choice(['Toyota', 'Honda', 'Ford', 'Chevrolet', 'Nissan', 'BMW', 'Mercedes', 'Tesla'])
    vehicle_model = random.choice(['Corolla', 'Civic', 'F-150', 'Silverado', 'Altima', '3 Series', 'C-Class', 'Model 3'])
    vehicle_year = random.randint(2015, 2025)
    
    # 10. Calculate derived fields
    week = fnol_date.isocalendar()[1]
    day_of_week = fnol_date.isoweekday()
    quarter = f"Q{(month - 1) // 3 + 1}"
    ai_adoption_phase = get_ai_adoption_phase(month_config['date'])
    is_closed = True
    routed_to_traditional = not ai_enabled
    damage_count = random.randint(1, 5)
    image_count = random.randint(3, 10)
    
    return {
        'claim_id': claim_id,
        'fnol_date': fnol_date.date(),
        'fnol_datetime': fnol_datetime,
        'claim_closed_date': claim_closed_date,
        'claim_closed_datetime': claim_closed_datetime,
        'month': month,
        'week': week,
        'day_of_week': day_of_week,
        'quarter': quarter,
        'year': year,
        'customer_id': customer_id,
        'policy_number': policy_number,
        'vehicle_vin': vehicle_vin,
        'vehicle_make': vehicle_make,
        'vehicle_model': vehicle_model,
        'vehicle_year': vehicle_year,
        'processing_path': processing_path,
        'ai_enabled': ai_enabled,
        'ai_adoption_phase': ai_adoption_phase,
        'cycle_time_days': round(cycle_time_days, 2),
        'cycle_time_hours': round(cycle_time_hours, 2),
        'auto_adjudicated': auto_adjudicated,
        'human_review_required': human_review_required,
        'human_review_reason': human_review_reason,
        'cost_estimated': round(cost_estimated, 2),
        'cost_actual': round(cost_actual, 2),
        'cost_operational': round(cost_operational, 2),
        'cost_savings_factor': cost_savings_factor,
        'cost_total': round(cost_total, 2),
        'fraud_detected': fraud_detected,
        'fraud_risk_score': round(fraud_risk_score, 3) if fraud_risk_score else None,
        'fraud_type': fraud_type,
        'cost_accuracy_percent': round(cost_accuracy_percent, 2),
        'within_tolerance': within_tolerance,
        'claim_amount': round(claim_amount, 2),
        'damage_count': damage_count,
        'image_count': image_count,
        'is_closed': is_closed,
        'routed_to_traditional': routed_to_traditional,
    }


def create_warehouse_schema(conn):
    """Create claims_warehouse table if it doesn't exist"""
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claims_warehouse (
            -- Primary Key
            warehouse_id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            -- Link to Main Database
            claim_id INTEGER NOT NULL,
            
            -- Time Dimensions
            fnol_date DATE NOT NULL,
            fnol_datetime TIMESTAMP NOT NULL,
            claim_closed_date DATE,
            claim_closed_datetime TIMESTAMP,
            month INTEGER NOT NULL,
            week INTEGER NOT NULL,
            day_of_week INTEGER NOT NULL,
            quarter TEXT NOT NULL,
            year INTEGER NOT NULL,
            
            -- Customer/Policy Dimensions
            customer_id INTEGER NOT NULL,
            policy_number TEXT NOT NULL,
            vehicle_vin TEXT NOT NULL,
            vehicle_make TEXT,
            vehicle_model TEXT,
            vehicle_year INTEGER,
            
            -- Processing Path
            processing_path TEXT NOT NULL,
            ai_enabled BOOLEAN NOT NULL,
            ai_adoption_phase TEXT NOT NULL,
            
            -- KPI 1: Cycle Time
            cycle_time_days REAL NOT NULL,
            cycle_time_hours REAL,
            
            -- KPI 2: Auto-Adjudication
            auto_adjudicated BOOLEAN NOT NULL,
            human_review_required BOOLEAN NOT NULL,
            human_review_reason TEXT,
            
            -- KPI 3: Cost per Claim
            cost_estimated REAL NOT NULL,
            cost_actual REAL NOT NULL,
            cost_operational REAL NOT NULL,
            cost_savings_factor REAL,
            cost_total REAL NOT NULL,
            
            -- KPI 4: Fraud Detection
            fraud_detected BOOLEAN NOT NULL,
            fraud_risk_score REAL,
            fraud_type TEXT,
            
            -- Accuracy Metrics
            cost_accuracy_percent REAL,
            within_tolerance BOOLEAN,
            
            -- Claim Details
            claim_amount REAL NOT NULL,
            damage_count INTEGER,
            image_count INTEGER,
            
            -- Derived Flags
            is_closed BOOLEAN NOT NULL,
            routed_to_traditional BOOLEAN NOT NULL,
            
            -- Metadata
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_warehouse_fnol_date ON claims_warehouse(fnol_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_warehouse_month ON claims_warehouse(month)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_warehouse_processing_path ON claims_warehouse(processing_path)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_warehouse_ai_enabled ON claims_warehouse(ai_enabled)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_warehouse_ai_adoption_phase ON claims_warehouse(ai_adoption_phase)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_warehouse_claim_id ON claims_warehouse(claim_id)')
    
    conn.commit()


def insert_claims(conn, claims):
    """Insert claims into database"""
    cursor = conn.cursor()
    
    for claim in claims:
        cursor.execute('''
            INSERT INTO claims_warehouse (
                claim_id, fnol_date, fnol_datetime, claim_closed_date, claim_closed_datetime,
                month, week, day_of_week, quarter, year,
                customer_id, policy_number, vehicle_vin, vehicle_make, vehicle_model, vehicle_year,
                processing_path, ai_enabled, ai_adoption_phase,
                cycle_time_days, cycle_time_hours,
                auto_adjudicated, human_review_required, human_review_reason,
                cost_estimated, cost_actual, cost_operational, cost_savings_factor, cost_total,
                fraud_detected, fraud_risk_score, fraud_type,
                cost_accuracy_percent, within_tolerance,
                claim_amount, damage_count, image_count,
                is_closed, routed_to_traditional
            ) VALUES (
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?,
                ?, ?, ?,
                ?, ?
            )
        ''', (
            claim['claim_id'], claim['fnol_date'], claim['fnol_datetime'], 
            claim['claim_closed_date'], claim['claim_closed_datetime'],
            claim['month'], claim['week'], claim['day_of_week'], claim['quarter'], claim['year'],
            claim['customer_id'], claim['policy_number'], claim['vehicle_vin'], 
            claim['vehicle_make'], claim['vehicle_model'], claim['vehicle_year'],
            claim['processing_path'], claim['ai_enabled'], claim['ai_adoption_phase'],
            claim['cycle_time_days'], claim['cycle_time_hours'],
            claim['auto_adjudicated'], claim['human_review_required'], claim['human_review_reason'],
            claim['cost_estimated'], claim['cost_actual'], claim['cost_operational'],
            claim['cost_savings_factor'], claim['cost_total'],
            claim['fraud_detected'], claim['fraud_risk_score'], claim['fraud_type'],
            claim['cost_accuracy_percent'], claim['within_tolerance'],
            claim['claim_amount'], claim['damage_count'], claim['image_count'],
            claim['is_closed'], claim['routed_to_traditional']
        ))
    
    conn.commit()


def print_statistics(conn):
    """Print summary statistics of generated data"""
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("CLAIMS WAREHOUSE - DATA GENERATION SUMMARY")
    print("="*80)
    
    # Total claims
    cursor.execute("SELECT COUNT(*) FROM claims_warehouse")
    total = cursor.fetchone()[0]
    print(f"\nTotal Claims Generated: {total}")
    
    # Monthly breakdown
    print("\n" + "-"*80)
    print("MONTHLY BREAKDOWN")
    print("-"*80)
    print(f"{'Month':<15} {'Claims':<10} {'Auto-Adj %':<15} {'Avg Cycle':<15} {'Fraud Det %':<15}")
    print("-"*80)
    
    cursor.execute('''
        SELECT 
            month || '-' || year as period,
            COUNT(*) as total,
            ROUND(AVG(CASE WHEN auto_adjudicated THEN 100.0 ELSE 0.0 END), 1) as auto_adj_pct,
            ROUND(AVG(cycle_time_days), 1) as avg_cycle,
            ROUND(AVG(CASE WHEN fraud_detected THEN 100.0 ELSE 0.0 END), 1) as fraud_pct
        FROM claims_warehouse
        GROUP BY year, month
        ORDER BY year, month
    ''')
    
    for row in cursor.fetchall():
        print(f"{row[0]:<15} {row[1]:<10} {row[2]:<15} {row[3]:<15} {row[4]:<15}")
    
    # Processing path distribution
    print("\n" + "-"*80)
    print("PROCESSING PATH DISTRIBUTION")
    print("-"*80)
    cursor.execute('''
        SELECT processing_path, COUNT(*), ROUND(COUNT(*) * 100.0 / ?, 1)
        FROM claims_warehouse
        GROUP BY processing_path
    ''', (total,))
    
    for row in cursor.fetchall():
        print(f"{row[0]:<30} {row[1]:<10} ({row[2]}%)")
    
    # KPI Summary
    print("\n" + "-"*80)
    print("KPI SUMMARY")
    print("-"*80)
    
    cursor.execute('''
        SELECT 
            ROUND(AVG(cycle_time_days), 2) as avg_cycle,
            ROUND(AVG(CASE WHEN auto_adjudicated THEN 100.0 ELSE 0.0 END), 1) as auto_adj_rate,
            ROUND(AVG(cost_total), 2) as avg_cost,
            ROUND(AVG(CASE WHEN fraud_detected THEN 100.0 ELSE 0.0 END), 1) as fraud_detection_rate,
            ROUND(AVG(CASE WHEN within_tolerance THEN 100.0 ELSE 0.0 END), 1) as accuracy_rate
        FROM claims_warehouse
        WHERE ai_enabled = TRUE
    ''')
    
    kpi = cursor.fetchone()
    print(f"Average Cycle Time: {kpi[0]} days")
    print(f"Auto-Adjudication Rate: {kpi[1]}%")
    print(f"Average Cost per Claim: ${kpi[2]}")
    print(f"Fraud Detection Rate: {kpi[3]}%")
    print(f"Accuracy Within Tolerance: {kpi[4]}%")
    
    print("\n" + "="*80)


def main():
    parser = argparse.ArgumentParser(description='Seed claims warehouse with synthetic data')
    parser.add_argument('--reset', action='store_true', help='Clear existing data before seeding')
    parser.add_argument('--db', default='src/data/claims-warehouse.db', help='Path to database file')
    args = parser.parse_args()
    
    # Ensure data directory exists
    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(str(db_path))
    
    # Reset if requested
    if args.reset:
        print("Resetting database...")
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS claims_warehouse")
        conn.commit()
    
    # Create schema
    create_warehouse_schema(conn)
    
    # Generate claims
    print(f"Generating {CLAIMS_PER_MONTH * len(MONTHS)} synthetic claims...")
    claim_id = 1000
    all_claims = []
    
    for month_config in MONTHS:
        print(f"  Generating {CLAIMS_PER_MONTH} claims for {month_config['date']}...")
        for _ in range(CLAIMS_PER_MONTH):
            claim = generate_claim(claim_id, month_config)
            all_claims.append(claim)
            claim_id += 1
    
    # Insert into database
    print(f"Inserting {len(all_claims)} claims into database...")
    insert_claims(conn, all_claims)
    
    # Print statistics
    print_statistics(conn)
    
    conn.close()
    print(f"\n✓ Successfully seeded {len(all_claims)} claims to {args.db}")


if __name__ == '__main__':
    main()
```

---

### 7.5 Validation Checks

After running the script, verify:

**1. Total Claims:** 4,500 claims (750 per month × 6 months)

**2. Auto-Adjudication Threshold Progression:**
```sql
SELECT 
    month || '-' || year as period,
    COUNT(*) as total_claims,
    COUNT(*) FILTER (WHERE auto_adjudicated = TRUE) as auto_adj,
    ROUND(AVG(claim_amount), 2) as avg_amount
FROM claims_warehouse
GROUP BY year, month
ORDER BY year, month;
```

**Expected:** As threshold increases ($4K → $5K), auto-adjudication rate should increase

**3. Fraud Detection Improvement:**
```sql
SELECT 
    month || '-' || year as period,
    COUNT(*) FILTER (WHERE fraud_detected = TRUE) as fraud_detected,
    COUNT(*) FILTER (WHERE auto_adjudicated = TRUE) * 0.15 as expected_fraud,
    ROUND(COUNT(*) FILTER (WHERE fraud_detected = TRUE) * 100.0 / 
          NULLIF(COUNT(*) FILTER (WHERE auto_adjudicated = TRUE), 0), 1) as detection_rate
FROM claims_warehouse
GROUP BY year, month
ORDER BY year, month;
```

**Expected:** Detection rate improves from 40% (Oct) to 85% (Mar)

**4. Cycle Time Trend:**
```sql
SELECT 
    month || '-' || year as period,
    ROUND(AVG(cycle_time_days), 2) as avg_cycle_time,
    ROUND(AVG(CASE WHEN processing_path = 'ai_auto_approved' THEN cycle_time_days END), 2) as ai_auto,
    ROUND(AVG(CASE WHEN processing_path = 'ai_human_reviewed' THEN cycle_time_days END), 2) as ai_reviewed
FROM claims_warehouse
GROUP BY year, month
ORDER BY year, month;
```

**Expected:** Auto-approved claims ~4 days, human-reviewed ~15 days

**5. Cost Savings Verification:**
```sql
SELECT 
    processing_path,
    COUNT(*) as claim_count,
    ROUND(AVG(cost_operational), 2) as avg_operational_cost,
    ROUND(AVG(cost_total), 2) as avg_total_cost,
    AVG(cost_savings_factor) as avg_savings_factor
FROM claims_warehouse
GROUP BY processing_path;
```

**Expected:**
- `ai_auto_approved`: $20-30 operational cost, 0.9 savings factor
- `ai_human_reviewed`: $40-50 operational cost, 0.85 savings factor
- `traditional`: $200-450 operational cost, 1.0 savings factor

**6. Data Integrity Checks:**
```sql
-- Check for null values in critical fields
SELECT 
    SUM(CASE WHEN claim_id IS NULL THEN 1 ELSE 0 END) as null_claim_id,
    SUM(CASE WHEN fnol_date IS NULL THEN 1 ELSE 0 END) as null_fnol_date,
    SUM(CASE WHEN claim_amount IS NULL THEN 1 ELSE 0 END) as null_amount,
    SUM(CASE WHEN processing_path IS NULL THEN 1 ELSE 0 END) as null_path
FROM claims_warehouse;

-- Check date consistency (closed >= fnol)
SELECT COUNT(*) 
FROM claims_warehouse 
WHERE claim_closed_date < fnol_date;

-- Check cost consistency (actual > 0, operational > 0)
SELECT COUNT(*) 
FROM claims_warehouse 
WHERE cost_actual <= 0 OR cost_operational <= 0;
```

**Expected:** All checks return 0 errors

---

### 7.6 Running the Script

**Prerequisites:**
```bash
pip install faker
```

**Generate Data:**
```bash
# First time (creates database)
python scripts/seed-claims-warehouse.py

# Reset and regenerate
python scripts/seed-claims-warehouse.py --reset

# Custom database location
python scripts/seed-claims-warehouse.py --db /path/to/claims-warehouse.db
```

**Verify Data:**
```bash
sqlite3 src/data/claims-warehouse.db "SELECT COUNT(*) FROM claims_warehouse;"
# Expected: 4500

sqlite3 src/data/claims-warehouse.db ".schema claims_warehouse"
# Should show full schema with indexes
```

---

### 7.7 Extrapolation to Full Volume

The dashboard displays results extrapolated from the 1% sample to full volume:

**Sample Data:** 750 claims/month  
**Actual Volume:** 75,000 claims/month  
**Extrapolation Factor:** 100x

**Example Calculation:**
```python
# Sample: 500 auto-adjudicated claims in March
# Extrapolated: 500 × 100 = 50,000 auto-adjudicated claims

# Sample: $385 average cost per claim
# Extrapolated: $385 × 75,000 = $28,875,000 total monthly cost
```

**Dashboard Display Logic:**
```javascript
// In frontend code
const extrapolationFactor = 100;
const displayValue = sampleValue * extrapolationFactor;

// Example: KPI Card
<KPICard
  title="Auto-Adjudication Rate"
  currentValue={autoAdjCount * extrapolationFactor}
  totalClaims={totalClaims * extrapolationFactor}
  percentage={autoAdjCount / totalClaims * 100}  // Percentage stays same
/>
```

---

### 7.8 Data Quality Checklist

Before deploying to production, verify:

- [ ] All 4,500 claims generated successfully
- [ ] No NULL values in required fields
- [ ] Date consistency (closed >= fnol)
- [ ] Cost values are positive
- [ ] Fraud detection rates match monthly targets (40% → 85%)
- [ ] Auto-adjudication threshold logic works correctly
- [ ] Cycle times are realistic (4 days auto, 15 days reviewed)
- [ ] Cost savings factors applied correctly
- [ ] Vehicle/customer data is realistic
- [ ] Database indexes created for performance
- [ ] Extrapolation calculations verified
- [ ] Sample data represents full population accurately

---

## 8. User Workflows

### 8.1 View KPI Dashboard (Default View)

**Scenario:** Executive logs in and wants to see current performance

**Steps:**
1. Navigate to `/login`
2. Click **[Enter Portal]**
3. Dashboard loads with default time period: "Last Quarter"
4. All 4 KPI cards display current values + trends
5. Detailed charts render below
6. Quick Stats show summary numbers in sidebar

**Expected Outcome:**
- See Cycle Time: 4.2 days (↓65%)
- See Auto-Adj Rate: 68% (↑68%)
- See Cost per Claim: $385 (↓14%)
- See Fraud Detection: 85% (stable)

---

### 8.2 Filter by Time Period

**Scenario:** Executive wants to see only last month's data

**Steps:**
1. In Filter Sidebar, select **○ Last Month**
2. All KPI cards and charts update automatically
3. Query results clear (reset to default view)
4. Quick Stats update to reflect new time range

**Expected Outcome:**
- Dashboard shows only March 2026 data (80 claims)
- KPIs reflect Month 3 performance only

---

### 8.3 Run Preset Query

**Scenario:** Operations Manager wants to analyze processing path distribution

**Steps:**
1. Click dropdown in Query Interface
2. Select **"Claims by Processing Path"**
3. Click **[Generate Report 🔍]**
4. New stacked bar chart appears below KPI cards
5. Chart shows: 85 auto-approved, 40 human-reviewed
6. Raw data table (expandable) shows claim IDs

**Expected Outcome:**
- Stacked bar chart displays processing path breakdown
- Can export query results as CSV

---

### 8.4 Export Dashboard as PDF

**Scenario:** Executive needs dashboard for board presentation

**Steps:**
1. In Filter Sidebar, click **[📄 PDF Report]**
2. Browser downloads `executive-dashboard-2026-05-07.pdf`
3. PDF contains:
   - KPI summary table
   - All 4 detailed charts
   - Quick Stats section
   - Extrapolation projections

**Expected Outcome:**
- Board-ready PDF report with all visualizations

---

### 8.5 Drill Down to Claim Details

**Scenario:** Operations Manager sees outlier in cycle time chart and wants details

**Steps:**
1. Click on specific bar in Cycle Time Trend chart
2. DrillDownModal opens with claim details
3. Modal shows:
   - Customer name, policy, vehicle
   - Cycle time breakdown
   - Cost accuracy
   - Timeline of events
4. Click **[View Full Claim →]** to open in Claims Portal

**Expected Outcome:**
- Understand why specific claim took longer
- Identify process improvements

---

## 9. Development Checklist

### Phase 1: Backend Setup
- [ ] Create `claims-warehouse.db` database
- [ ] Run warehouse schema DDL (Section 3.1)
- [ ] Create `src/data/generate_warehouse_data.py` script
- [ ] Generate 200 synthetic claims
- [ ] Validate data distribution (Section 7.2)
- [ ] Create `/api/v1/executive/*` router
- [ ] Implement GET /api/v1/executive/kpis endpoint
- [ ] Implement GET /api/v1/executive/trends/{kpi} endpoint
- [ ] Implement POST /api/v1/executive/query endpoint
- [ ] Implement GET /api/v1/executive/export/{format} endpoint
- [ ] Implement GET /api/v1/executive/drilldown/{claim_id} endpoint
- [ ] Create Pydantic schemas in `src/api/schemas/executive.py`
- [ ] Test all endpoints with curl/Postman

### Phase 2: Frontend Setup
- [ ] Create `src/ui/executive/` directory structure
- [ ] Set up package.json with dependencies (React, Recharts, Tailwind)
- [ ] Configure Vite (port 5176) and Tailwind CSS
- [ ] Create `public/executive-portal-config.yaml`
- [ ] Copy reusable components from customer/adjustor portals
- [ ] Implement AuthContext (no-auth mode)
- [ ] Implement API client with base URL from config
- [ ] Create routing structure (App.jsx, routes)

### Phase 3: Core Components
- [ ] Build KPICard component with mini chart
- [ ] Build TrendChart component (Recharts integration)
- [ ] Build QueryInterface component (dropdown only, no free-text)
- [ ] Build FilterSidebar component (time filtering)
- [ ] Build QuickStats component (summary numbers)
- [ ] Build SampleDataDistribution component (methodology & data table)
- [ ] Build DrillDownModal component

### Phase 4: Dashboard Page
- [ ] Build DashboardPage layout (70/30 split)
- [ ] Implement data fetching (fetchKPIs, fetchTrends)
- [ ] Wire up KPI cards to API data
- [ ] Render 4 detailed charts (Cycle Time, Processing Path, Cost, Fraud)
- [ ] Connect QueryInterface to POST /api/v1/executive/query
- [ ] Implement time period filtering
- [ ] Add loading states and spinners
- [ ] Add error handling and display

### Phase 5: Export & Drill-Down
- [ ] Implement PDF export functionality
- [ ] Implement CSV export functionality
- [ ] Implement PNG export functionality
- [ ] Wire up chart onClick to DrillDownModal
- [ ] Fetch claim details for drill-down
- [ ] Add "View Full Claim" link to Claims Portal

### Phase 6: Styling & Polish
- [ ] Apply Tailwind styling (consistent with other portals)
- [ ] Add responsive layout (desktop/tablet/mobile)
- [ ] Add chart color themes (green=good, red=bad)
- [ ] Add trend indicators (↑/↓ arrows with colors)
- [ ] Add loading skeletons for charts
- [ ] Add empty states ("No data for selected period")

### Phase 7: Testing
- [ ] Test KPI calculations (verify against SQL queries)
- [ ] Test time period filtering (week, month, quarter, custom)
- [ ] Test preset queries (all 4 queries)
- [ ] Test export functionality (PDF, CSV, PNG)
- [ ] Test drill-down modal
- [ ] Test responsive layout on different screen sizes
- [ ] Test error scenarios (API down, no data)

### Phase 8: Integration
- [ ] Add Executive Portal to Admin Portal's Quick Access panel
- [ ] Update `UI-ADMIN-PORTAL-DESIGN.md` to enable Executive Portal button
- [ ] Add to Makefile targets (`make run-executive-ui`)
- [ ] Test all three portals running simultaneously
- [ ] Verify portal links work from Admin Portal

### Phase 9: Documentation
- [ ] Create `src/ui/executive/README.md` with setup instructions
- [ ] Update `specifications/FILE-MANIFEST.md` with new files
- [ ] Document API endpoints in `API-BACKEND-DESIGN.md`
- [ ] Add Executive Portal section to main README
- [ ] Document synthetic data generation process
- [ ] Add troubleshooting guide

---

## 10. TODOs

### Immediate (Pre-Implementation)
1. [ ] Review and approve design document with stakeholders
2. [ ] Confirm KPI calculation formulas with business team
3. [ ] Verify port 5176 is available
4. [ ] Confirm charting library choice (Recharts recommended)

### Backend Implementation (11-24)
11. [ ] Create warehouse database schema
12. [ ] Build data generation script
13. [ ] Generate and validate 200 claims
14. [ ] Create `src/api/routers/executive.py` router
15. [ ] Implement GET /kpis endpoint
16. [ ] Implement GET /trends/{kpi} endpoint
17. [ ] Implement POST /query endpoint (preset queries only)
18. [ ] Implement GET /export/{format} endpoint
19. [ ] Implement GET /drilldown/{claim_id} endpoint
20. [ ] Create Pydantic schemas
21. [ ] Add query optimization (indexes)
22. [ ] Test all endpoints
23. [ ] Add error handling
24. [ ] Register router in main.py

### Frontend Implementation (25-50)
25. [ ] Create project structure
26. [ ] Set up package.json
27. [ ] Configure Vite and Tailwind
28. [ ] Create config file
29. [ ] Copy reusable components
30. [ ] Implement AuthContext
31. [ ] Implement API client
32. [ ] Create routing
33. [ ] Build LoginPage
34. [ ] Build KPICard component
35. [ ] Build TrendChart component (Recharts)
36. [ ] Build QueryInterface component
37. [ ] Build FilterSidebar component
38. [ ] Build QuickStats component
39. [ ] Build DrillDownModal component
40. [ ] Build DashboardPage layout
41. [ ] Implement data fetching logic
42. [ ] Wire up KPI cards
43. [ ] Render detailed charts (4 charts)
44. [ ] Connect QueryInterface to API
45. [ ] Implement time filtering
46. [ ] Add loading states
47. [ ] Add error handling
48. [ ] Implement PDF export
49. [ ] Implement CSV export
50. [ ] Implement PNG export

### Testing (51-60)
51. [ ] Test KPI calculations
52. [ ] Test time filtering
53. [ ] Test preset queries
54. [ ] Test export functionality
55. [ ] Test drill-down
56. [ ] Test responsive layout
57. [ ] Test error scenarios
58. [ ] Test cross-browser compatibility
59. [ ] Verify data accuracy
60. [ ] Load testing (200+ claims)

### Integration (61-65)
61. [ ] Add to Admin Portal Quick Access
62. [ ] Update Admin Portal design doc
63. [ ] Add Makefile targets
64. [ ] Test all portals simultaneously
65. [ ] Verify portal links

### Documentation (66-70)
66. [ ] Create Executive Portal README
67. [ ] Update FILE-MANIFEST.md
68. [ ] Document API endpoints
69. [ ] Update main README
70. [ ] Add troubleshooting guide

### Future Enhancements (71-80)
71. [ ] Implement free-text NLP queries (LLM integration)
72. [ ] Add real-time data refresh
73. [ ] Implement user authentication
74. [ ] Add predictive analytics
75. [ ] Add alert thresholds
76. [ ] Multi-year historical data
77. [ ] Advanced drill-down (multi-level)
78. [ ] Custom dashboard builder
79. [ ] Email report scheduling
80. [ ] Mobile app version

---

## 11. Open Questions & Decisions

### Q1: Which charting library - Recharts or Chart.js?
**Decision:** Recharts (recommended). Better React integration, declarative API, active development. Chart.js is lighter but imperative API.

### Q2: Should drill-down open modal or navigate to new page?
**Decision:** Modal. Faster UX, maintains dashboard context. Link to full Claims Portal for deep dive.

### Q3: Color scheme for KPIs - follow standard or create new?
**Decision:** Follow standard: Green=good/improving, Red=bad/declining, Blue=neutral, Yellow=warning. Consistent with other portals.

### Q4: How to handle "no data" states for custom date ranges?
**Decision:** Show empty state card with message: "No claims found for selected period. Try expanding date range." Include "Reset to Last Quarter" button.

### Q5: Should we show claim-level details on drill-down?
**Decision:** Yes. Show top 10 claims in modal table. Include "View All" link to export CSV with full list.

### Q6: Free-text NLP - MVP or future enhancement?
**Decision:** Future enhancement. MVP focuses on dropdown presets (4 queries). Free-text requires LLM integration, SQL generation, security validation.

### Q7: Export format - single PDF or multiple files?
**Decision:** Provide both options:
- Single PDF: All-in-one dashboard report
- Separate files: Charts as PNG ZIP, data as CSV, metadata as JSON

### Q8: Extrapolation - show in sidebar or separate page?
**Decision:** Sidebar card. Quick reference for executives. Optional "View Full Projections" link to detailed page (future).

---

## 12. Design Principles

1. **Executive-First UX:** Big numbers, clear trends, minimal clutter
2. **Dual Audience:** Serve both strategic (C-suite) and operational (managers) needs
3. **Data-Driven Storytelling:** Show AI adoption journey (3-month timeline)
4. **Interactive but Not Overwhelming:** Focus on 4 core KPIs, allow drill-down for details
5. **Export-Ready:** Board presentations, regulatory reports, stakeholder updates
6. **Consistent Branding:** Follow Customer/Adjustor/Admin portal patterns
7. **Performance:** Fast queries, cached aggregates, optimized charts
8. **Prototype Mentality:** Built for demo, not production-scale

---

## 13. Summary

The Executive Portal is a **Business Intelligence Dashboard** that provides:
- ✅ 4 Core KPIs (Cycle Time, Auto-Adj Rate, Cost, Fraud Detection)
- ✅ 3-Month AI Adoption Timeline (Pre-AI → Partial → Full)
- ✅ Interactive Charts (Bar+Line hybrid, filters, drill-down)
- ✅ NLP Query Interface (Dropdown presets, future free-text)
- ✅ Export Capabilities (PDF, CSV, PNG)
- ✅ Data Warehouse (200 claims, claim-level records)
- ✅ Extrapolation View (200 → 20,000 claims/quarter)
- ❌ No real-time data, authentication, or advanced analytics (kept simple for MVP)

**Tech Stack:** Vite + React 18, Recharts, Tailwind CSS, SQLite warehouse

**Key Files:**
- UI: `src/ui/executive/` (separate React app)
- Config: `executive-portal-config.yaml`
- API: `/api/v1/executive/*`
- Warehouse: `claims-warehouse.db`
- Data Generator: `src/data/generate_warehouse_data.py`

**Next Steps:**
1. Create warehouse database and generate synthetic data
2. Implement backend API endpoints
3. Build frontend components with Recharts
4. Test end-to-end workflows
5. Add to Admin Portal Quick Access panel

---

**Document Version:** 1.0  
**Last Updated:** 2026-05-07  
**Status:** ✅ Design Complete, Ready for Implementation
