-- ============================================================================
-- Agent System Database Migration
-- ============================================================================
-- This migration adds tables and columns to support LLM agent integration
-- All new columns are nullable for backward compatibility
-- ============================================================================

-- Agent Usage Logs Table
-- Tracks all LLM API calls for cost monitoring and usage analysis
CREATE TABLE IF NOT EXISTS agent_usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    agent_name VARCHAR(100) NOT NULL,
    llm_provider VARCHAR(50),
    llm_model VARCHAR(100),
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    estimated_cost_usd DECIMAL(10, 6) DEFAULT 0.0,
    duration_ms INTEGER DEFAULT 0,
    claim_id INTEGER NULL,
    customer_id INTEGER NULL,
    request_type VARCHAR(50),
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT NULL,
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Fraud Signals Table
-- Stores detailed fraud detection results for each claim
CREATE TABLE IF NOT EXISTS fraud_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id INTEGER NOT NULL,
    detection_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    overall_risk_score DECIMAL(3, 2),
    signal_type VARCHAR(100),
    severity DECIMAL(3, 2),
    description TEXT,
    evidence JSON,
    agent_version VARCHAR(50),
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);

-- Risk Assessments Table
-- Stores actuarial risk analysis results for each claim
CREATE TABLE IF NOT EXISTS risk_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id INTEGER NOT NULL,
    assessment_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    risk_score DECIMAL(3, 2),
    cost_deviation_pct DECIMAL(5, 2),
    risk_factors JSON,
    recommendation VARCHAR(50),
    reasoning TEXT,
    confidence DECIMAL(3, 2),
    agent_version VARCHAR(50),
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);

-- ============================================================================
-- Add Agent-Related Columns to Existing Tables
-- ============================================================================

-- Damages Table Enhancements
-- Add columns for agent-enhanced damage analysis (all nullable)
ALTER TABLE damages ADD COLUMN enhanced_severity DECIMAL(3, 2) NULL;
ALTER TABLE damages ADD COLUMN internal_damage_probability DECIMAL(3, 2) NULL;
ALTER TABLE damages ADD COLUMN ai_generated_probability DECIMAL(3, 2) NULL;
ALTER TABLE damages ADD COLUMN fraud_risk_score DECIMAL(3, 2) NULL;
ALTER TABLE damages ADD COLUMN risk_score DECIMAL(3, 2) NULL;
ALTER TABLE damages ADD COLUMN agent_reasoning TEXT NULL;
ALTER TABLE damages ADD COLUMN secondary_damages_predicted JSON NULL;

-- Claims Table Enhancements
-- Add columns for aggregate agent scores (all nullable)
ALTER TABLE claims ADD COLUMN overall_fraud_risk_score DECIMAL(3, 2) NULL;
ALTER TABLE claims ADD COLUMN overall_risk_score DECIMAL(3, 2) NULL;
ALTER TABLE claims ADD COLUMN agent_flags JSON NULL;

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_agent_usage_logs_claim_id ON agent_usage_logs(claim_id);
CREATE INDEX IF NOT EXISTS idx_agent_usage_logs_customer_id ON agent_usage_logs(customer_id);
CREATE INDEX IF NOT EXISTS idx_agent_usage_logs_timestamp ON agent_usage_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_agent_usage_logs_agent_name ON agent_usage_logs(agent_name);

CREATE INDEX IF NOT EXISTS idx_fraud_signals_claim_id ON fraud_signals(claim_id);
CREATE INDEX IF NOT EXISTS idx_fraud_signals_timestamp ON fraud_signals(detection_timestamp);

CREATE INDEX IF NOT EXISTS idx_risk_assessments_claim_id ON risk_assessments(claim_id);
CREATE INDEX IF NOT EXISTS idx_risk_assessments_timestamp ON risk_assessments(assessment_timestamp);

-- ============================================================================
-- Migration Complete
-- ============================================================================
