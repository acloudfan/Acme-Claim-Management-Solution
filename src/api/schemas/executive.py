"""
Pydantic Schemas for Executive Portal API
Handles requests/responses for Business Intelligence dashboard
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from datetime import date, datetime


# ============================================================================
# KPI Schemas
# ============================================================================

class KPIValue(BaseModel):
    """Single KPI metric value with trend"""
    current_value: float = Field(..., description="Current KPI value")
    unit: str = Field(..., description="Unit of measurement (days, percent, dollars)")
    trend: Literal["up", "down", "stable"] = Field(..., description="Trend direction")
    change_percent: float = Field(..., description="Percentage change vs previous period")
    previous_value: Optional[float] = Field(None, description="Previous period value")
    target: Optional[float] = Field(None, description="Target/benchmark value")
    status: Literal["good", "warning", "critical"] = Field(..., description="Status indicator")


class KPISummary(BaseModel):
    """Summary statistics for dashboard"""
    total_claims: int = Field(..., description="Total claims in period")
    ai_enabled_claims: int = Field(..., description="Claims processed with AI")
    traditional_claims: int = Field(..., description="Claims processed traditionally")
    ai_auto_approved_claims: int = Field(..., description="AI auto-approved claims (STP)")
    ai_human_reviewed_claims: int = Field(..., description="AI claims with human review")
    ai_adoption_rate: float = Field(..., description="Percentage of AI-enabled claims")
    total_savings: float = Field(..., description="Total dollar savings from AI")
    accuracy_within_tolerance: float = Field(..., description="Percentage within ±10%")


class KPIResponse(BaseModel):
    """Response for GET /api/v1/executive/kpis"""
    last_updated: datetime = Field(..., description="Timestamp of last data refresh")
    time_period: str = Field(..., description="Time period filter applied")
    date_range: Dict[str, str] = Field(..., description="Start and end dates")
    kpis: Dict[str, KPIValue] = Field(..., description="4 core KPIs")
    summary: KPISummary = Field(..., description="Dashboard summary statistics")


# ============================================================================
# Trend Schemas
# ============================================================================

class TrendDataPoint(BaseModel):
    """Single data point in time series"""
    period: str = Field(..., description="Period identifier (YYYY-MM)")
    period_label: str = Field(..., description="Human-readable label (January 2026)")
    value: float = Field(..., description="KPI value for this period")
    claim_count: int = Field(..., description="Number of claims in period")
    ai_enabled_count: int = Field(..., description="AI-enabled claims in period")
    traditional_count: int = Field(..., description="Traditional claims in period")


class ChartConfig(BaseModel):
    """Chart configuration for frontend"""
    chart_type: str = Field(..., description="Chart type (bar_line_hybrid, stacked_bar, area, line)")
    x_axis: str = Field(..., description="X-axis data key")
    y_axis: str = Field(..., description="Y-axis data key")
    bar_data: Optional[str] = Field(None, description="Bar chart data key")
    line_data: Optional[str] = Field(None, description="Line chart data key")
    color_scheme: str = Field(..., description="Color scheme (blue, green, red)")


class TrendDataResponse(BaseModel):
    """Response for GET /api/v1/executive/trends/{kpi_name}"""
    kpi_name: str = Field(..., description="KPI identifier")
    granularity: str = Field(..., description="Time granularity (daily, weekly, monthly)")
    data_points: List[TrendDataPoint] = Field(..., description="Time series data")
    chart_config: ChartConfig = Field(..., description="Chart configuration")


# ============================================================================
# Query Schemas
# ============================================================================

class QueryRequest(BaseModel):
    """Request for POST /api/v1/executive/query"""
    query_type: Literal["preset", "custom"] = Field(..., description="Query type")
    preset_id: Optional[str] = Field(None, description="Preset query ID")
    custom_query: Optional[str] = Field(None, description="Custom NLP query text")
    time_range: Dict[str, str] = Field(..., description="Date range filter")


class QueryDataPoint(BaseModel):
    """Single data point in query result"""
    category: str = Field(..., description="Category label")
    count: int = Field(..., description="Count value")
    percent: float = Field(..., description="Percentage of total")
    value: Optional[float] = Field(None, description="Additional numeric value")


class QuerySummary(BaseModel):
    """Summary of query results"""
    total_claims: int = Field(..., description="Total claims matching query")
    ai_enabled_only: bool = Field(False, description="Whether query filtered to AI claims only")
    additional_stats: Optional[Dict[str, Any]] = Field(None, description="Additional statistics")


class QueryResponse(BaseModel):
    """Response for POST /api/v1/executive/query"""
    query_id: str = Field(..., description="Query identifier")
    query_text: str = Field(..., description="Human-readable query text")
    result_type: str = Field(..., description="Result visualization type")
    data: List[QueryDataPoint] = Field(..., description="Query result data")
    summary: QuerySummary = Field(..., description="Result summary")
    chart_config: ChartConfig = Field(..., description="Chart configuration")
    raw_data_csv_url: Optional[str] = Field(None, description="URL to download raw CSV")


# ============================================================================
# Drill-Down Schemas
# ============================================================================

class ClaimDamage(BaseModel):
    """Damage detail for drill-down"""
    part: str = Field(..., description="Damaged part")
    severity: str = Field(..., description="Severity (minor, moderate, severe)")
    cost: float = Field(..., description="Repair cost for this damage")


class ClaimEvent(BaseModel):
    """Event in claim timeline"""
    date: str = Field(..., description="Event date")
    status: str = Field(..., description="Event status")
    action_by: str = Field(..., description="Who performed action")


class ClaimDrillDownResponse(BaseModel):
    """Response for GET /api/v1/executive/drilldown/{claim_id}"""
    claim_id: int = Field(..., description="Claim ID")
    customer_name: str = Field(..., description="Customer name")
    policy_number: str = Field(..., description="Policy number")
    vehicle: str = Field(..., description="Vehicle description")
    fnol_date: str = Field(..., description="FNOL date")
    claim_closed_date: Optional[str] = Field(None, description="Claim closed date")
    cycle_time_days: float = Field(..., description="Cycle time in days")
    processing_path: str = Field(..., description="Processing path")
    cost_estimated: float = Field(..., description="Estimated cost")
    cost_actual: float = Field(..., description="Actual cost")
    cost_accuracy_percent: float = Field(..., description="Accuracy percentage")
    within_tolerance: bool = Field(..., description="Within ±10% tolerance")
    fraud_detected: bool = Field(..., description="Fraud detected flag")
    damages: List[ClaimDamage] = Field(default_factory=list, description="List of damages")
    events: List[ClaimEvent] = Field(default_factory=list, description="Claim timeline")


# ============================================================================
# Export Schemas
# ============================================================================

class ExportRequest(BaseModel):
    """Query parameters for export endpoints"""
    kpi: str = Field("all", description="KPI to export (all, cycle_time, auto_adj_rate, etc.)")
    time_period: str = Field("last_quarter", description="Time period filter")
    include_charts: bool = Field(True, description="Include charts in PDF export")
    chart_ids: Optional[str] = Field(None, description="Comma-separated chart IDs for PNG export")


# ============================================================================
# Time Period Schemas
# ============================================================================

class TimePeriod(BaseModel):
    """Time period filter"""
    period_type: Literal["last_week", "last_month", "last_quarter", "custom"] = Field(
        ..., description="Period type"
    )
    start_date: Optional[date] = Field(None, description="Start date (required for custom)")
    end_date: Optional[date] = Field(None, description="End date (required for custom)")


# ============================================================================
# Preset Query Definitions
# ============================================================================

PRESET_QUERIES = {
    "processing_path": {
        "id": "processing_path",
        "label": "Claims by Processing Path",
        "description": "How many claims were auto-approved vs human-reviewed?",
        "chart_type": "stacked_bar"
    },
    "adjustment_rate": {
        "id": "adjustment_rate",
        "label": "Adjustment Rate Analysis",
        "description": "How many estimates needed adjustment during repairs?",
        "chart_type": "bar"
    },
    "human_intervention": {
        "id": "human_intervention",
        "label": "Human Intervention Trends",
        "description": "Show human review rate trend over 3 months",
        "chart_type": "line"
    },
    "fraud_effectiveness": {
        "id": "fraud_effectiveness",
        "label": "Fraud Detection Effectiveness",
        "description": "What's the fraud detection rate by month?",
        "chart_type": "line"
    }
}
