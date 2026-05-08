-- Claims Warehouse Database Schema
-- Purpose: Separate analytics database for Executive Portal
-- Database: claims-warehouse.db

DROP TABLE IF EXISTS claims_warehouse;

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
    fraud_detected BOOLEAN NOT NULL,
    fraud_risk_score REAL,          -- 0.0-1.0 (from fraud agent)
    fraud_type TEXT,                -- 'color_mismatch', 'make_model_mismatch', 'ai_generated_image'

    -- Accuracy Metrics
    cost_accuracy_percent REAL,    -- abs(estimated - actual) / actual * 100
    within_tolerance BOOLEAN,      -- TRUE if accuracy <= 10%

    -- Claim Details
    claim_amount REAL NOT NULL,
    damage_count INTEGER DEFAULT 0,          -- Number of damages in claim
    image_count INTEGER DEFAULT 0,           -- Number of images uploaded

    -- Derived Flags
    is_closed BOOLEAN NOT NULL DEFAULT 1,
    routed_to_traditional BOOLEAN NOT NULL DEFAULT 0,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Key (logical reference to claims.db)
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);

-- Indexes for Performance
CREATE INDEX idx_warehouse_fnol_date ON claims_warehouse(fnol_date);
CREATE INDEX idx_warehouse_month ON claims_warehouse(month);
CREATE INDEX idx_warehouse_processing_path ON claims_warehouse(processing_path);
CREATE INDEX idx_warehouse_ai_enabled ON claims_warehouse(ai_enabled);
CREATE INDEX idx_warehouse_ai_adoption_phase ON claims_warehouse(ai_adoption_phase);
CREATE INDEX idx_warehouse_claim_id ON claims_warehouse(claim_id);
CREATE INDEX idx_warehouse_quarter ON claims_warehouse(quarter);
CREATE INDEX idx_warehouse_year ON claims_warehouse(year);

-- Validation Views for KPI Calculations

-- View: Monthly KPI Summary
CREATE VIEW IF NOT EXISTS monthly_kpi_summary AS
SELECT
    month,
    year,
    quarter,
    COUNT(*) as total_claims,
    SUM(CASE WHEN ai_enabled = 1 THEN 1 ELSE 0 END) as ai_enabled_claims,
    ROUND(SUM(CASE WHEN ai_enabled = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as ai_adoption_rate,
    ROUND(AVG(cycle_time_days), 2) as avg_cycle_time,
    ROUND(SUM(CASE WHEN auto_adjudicated = 1 THEN 1 ELSE 0 END) * 100.0 /
          NULLIF(SUM(CASE WHEN ai_enabled = 1 THEN 1 ELSE 0 END), 0), 2) as auto_adj_rate,
    ROUND(AVG(cost_total), 2) as avg_cost_per_claim,
    ROUND(SUM(CASE WHEN fraud_detected = 1 THEN 1 ELSE 0 END) * 100.0 /
          NULLIF(SUM(CASE WHEN ai_enabled = 1 THEN 1 ELSE 0 END), 0), 2) as fraud_detection_rate,
    ROUND(SUM(CASE WHEN within_tolerance = 1 THEN 1 ELSE 0 END) * 100.0 /
          NULLIF(SUM(CASE WHEN ai_enabled = 1 THEN 1 ELSE 0 END), 0), 2) as accuracy_within_tolerance
FROM claims_warehouse
GROUP BY month, year, quarter
ORDER BY year, month;

-- View: Processing Path Distribution
CREATE VIEW IF NOT EXISTS processing_path_summary AS
SELECT
    processing_path,
    COUNT(*) as claim_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims_warehouse WHERE ai_enabled = 1), 2) as percent_of_ai_claims,
    ROUND(AVG(cycle_time_days), 2) as avg_cycle_time,
    ROUND(AVG(cost_total), 2) as avg_cost
FROM claims_warehouse
WHERE ai_enabled = 1
GROUP BY processing_path;

-- View: AI vs Traditional Comparison
CREATE VIEW IF NOT EXISTS ai_vs_traditional AS
SELECT
    CASE WHEN ai_enabled = 1 THEN 'AI' ELSE 'Traditional' END as processing_type,
    COUNT(*) as claim_count,
    ROUND(AVG(cycle_time_days), 2) as avg_cycle_time,
    ROUND(AVG(cost_total), 2) as avg_cost_total,
    ROUND(AVG(cost_operational), 2) as avg_operational_cost
FROM claims_warehouse
GROUP BY ai_enabled;
