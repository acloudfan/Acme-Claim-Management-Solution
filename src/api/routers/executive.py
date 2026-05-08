"""
Executive Portal API Router
Provides Business Intelligence dashboard endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from typing import Optional, Literal
from datetime import datetime, date, timedelta
import sqlite3
import json
from pathlib import Path

from ..schemas.executive import (
    KPIResponse, KPIValue, KPISummary,
    TrendDataResponse, TrendDataPoint, ChartConfig,
    QueryRequest, QueryResponse, QueryDataPoint, QuerySummary,
    ClaimDrillDownResponse, ClaimDamage, ClaimEvent,
    PRESET_QUERIES
)

router = APIRouter(prefix="/executive", tags=["executive"])

# Database paths
WAREHOUSE_DB = Path("claims-warehouse.db")
MAIN_DB = Path("claims.db")


def get_warehouse_conn():
    """Get connection to warehouse database"""
    if not WAREHOUSE_DB.exists():
        raise HTTPException(status_code=500, detail="Warehouse database not found")
    return sqlite3.connect(str(WAREHOUSE_DB))


def get_main_conn():
    """Get connection to main database"""
    if not MAIN_DB.exists():
        raise HTTPException(status_code=500, detail="Main database not found")
    return sqlite3.connect(str(MAIN_DB))


def parse_time_period(time_period: str) -> tuple[date, date]:
    """Parse time period string to start/end dates

    For demo purposes, we use the warehouse data date range (Oct 2025 - Mar 2026)
    Default shows all 6 months of available data.
    """
    # Warehouse data range: Oct 2025 - Mar 2026 (6 months)
    if time_period == "last_week":
        # Last week of March 2026
        end_date = date(2026, 3, 31)
        start_date = date(2026, 3, 24)
    elif time_period == "last_month":
        # March 2026 only
        end_date = date(2026, 3, 31)
        start_date = date(2026, 3, 1)
    elif time_period == "last_quarter":
        # Last 3 months: Jan-Mar 2026
        end_date = date(2026, 3, 31)
        start_date = date(2026, 1, 1)
    elif time_period == "all" or time_period == "six_months":
        # All 6 months: Oct 2025 - Mar 2026
        end_date = date(2026, 3, 31)
        start_date = date(2025, 10, 1)
    else:
        # Default to all 6 months
        end_date = date(2026, 3, 31)
        start_date = date(2025, 10, 1)

    return start_date, end_date


@router.get("/kpis", response_model=KPIResponse)
async def get_kpis(
    time_period: str = Query("last_quarter", description="Time period filter"),
    start_date: Optional[str] = Query(None, description="Custom start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Custom end date (YYYY-MM-DD)"),
    compare_to_previous: bool = Query(True, description="Include comparison to previous period")
):
    """
    Fetch all 4 core KPI metrics with current values, trends, and comparisons

    Returns:
        - Cycle Time (avg days)
        - Auto-Adjudication Rate (%)
        - Cost per Claim ($)
        - Fraud Detection Rate (%)
    """
    conn = get_warehouse_conn()
    cursor = conn.cursor()

    # Parse dates
    if time_period == "custom" and start_date and end_date:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    else:
        start, end = parse_time_period(time_period)

    # Calculate previous period dates (same duration)
    duration_days = (end - start).days
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=duration_days)

    # KPI 1: Cycle Time Savings (Days saved by AI vs traditional processing)
    cursor.execute("""
        SELECT
            AVG(CASE WHEN ai_enabled = 1 THEN cycle_time_days ELSE NULL END) as ai_avg,
            SUM(CASE WHEN ai_enabled = 1 THEN 1 ELSE 0 END) as ai_count,
            (SELECT AVG(CASE WHEN ai_enabled = 1 THEN cycle_time_days ELSE NULL END)
             FROM claims_warehouse
             WHERE fnol_date BETWEEN ? AND ?) as ai_prev_avg
        FROM claims_warehouse
        WHERE fnol_date BETWEEN ? AND ?
    """, (prev_start.isoformat(), prev_end.isoformat(), start.isoformat(), end.isoformat()))

    row = cursor.fetchone()
    current_ai_cycle = row[0] or 0
    ai_claim_count = row[1] or 0
    previous_ai_cycle = row[2] or 0

    # Calculate days saved per claim and total days saved
    traditional_baseline = 19.3
    days_saved_per_claim = traditional_baseline - current_ai_cycle
    total_days_saved = days_saved_per_claim * ai_claim_count

    # Trend compared to previous period
    prev_days_saved = traditional_baseline - previous_ai_cycle if previous_ai_cycle else 0
    savings_change = ((days_saved_per_claim - prev_days_saved) / prev_days_saved * 100) if prev_days_saved else 0
    cycle_trend = "up" if savings_change > 5 else "down" if savings_change < -5 else "stable"

    cycle_time_kpi = KPIValue(
        current_value=round(days_saved_per_claim, 1),
        unit="days_saved",
        trend=cycle_trend,
        change_percent=round((days_saved_per_claim / traditional_baseline * 100), 1),  # % of baseline saved
        previous_value=round(traditional_baseline, 1) if compare_to_previous else None,
        target=15.8,  # Target: Save 15.8 days (get AI to 3.5 days)
        status="good" if days_saved_per_claim > 14 else "warning" if days_saved_per_claim > 9 else "critical"
    )

    # KPI 2: Auto-Adjudication Rate
    cursor.execute("""
        SELECT
            SUM(CASE WHEN auto_adjudicated = 1 THEN 1 ELSE 0 END) * 100.0 /
            NULLIF(SUM(CASE WHEN ai_enabled = 1 THEN 1 ELSE 0 END), 0) as current_rate,
            (SELECT SUM(CASE WHEN auto_adjudicated = 1 THEN 1 ELSE 0 END) * 100.0 /
                    NULLIF(SUM(CASE WHEN ai_enabled = 1 THEN 1 ELSE 0 END), 0)
             FROM claims_warehouse
             WHERE fnol_date BETWEEN ? AND ? AND ai_enabled = 1) as previous_rate
        FROM claims_warehouse
        WHERE fnol_date BETWEEN ? AND ? AND ai_enabled = 1
    """, (prev_start.isoformat(), prev_end.isoformat(), start.isoformat(), end.isoformat()))

    row = cursor.fetchone()
    current_auto = row[0] or 0
    previous_auto = row[1] or 0
    auto_change = ((current_auto - previous_auto) / previous_auto * 100) if previous_auto else 0
    auto_trend = "up" if auto_change > 5 else "down" if auto_change < -5 else "stable"

    auto_adj_kpi = KPIValue(
        current_value=round(current_auto, 1),
        unit="percent",
        trend=auto_trend,
        change_percent=round(auto_change, 1),
        previous_value=round(previous_auto, 1) if compare_to_previous else None,
        target=70.0,  # Target: 70% of AI-enabled claims are auto-adjudicated
        status="good" if current_auto >= 65 else "warning" if current_auto >= 50 else "critical"
    )

    # KPI 3: Total Savings (Operational cost savings from AI processing)
    cursor.execute("""
        SELECT
            SUM(CASE WHEN ai_enabled = 1 THEN 1 ELSE 0 END) as ai_count,
            SUM(CASE WHEN ai_enabled = 1 THEN cost_operational ELSE 0 END) as ai_cost,
            (SELECT SUM(CASE WHEN ai_enabled = 1 THEN 1 ELSE 0 END)
             FROM claims_warehouse
             WHERE fnol_date BETWEEN ? AND ?) as prev_ai_count,
            (SELECT SUM(CASE WHEN ai_enabled = 1 THEN cost_operational ELSE 0 END)
             FROM claims_warehouse
             WHERE fnol_date BETWEEN ? AND ?) as prev_ai_cost
        FROM claims_warehouse
        WHERE fnol_date BETWEEN ? AND ?
    """, (prev_start.isoformat(), prev_end.isoformat(),
          prev_start.isoformat(), prev_end.isoformat(),
          start.isoformat(), end.isoformat()))

    row = cursor.fetchone()
    ai_count = row[0] or 0
    ai_cost = row[1] or 0
    prev_ai_count = row[2] or 0
    prev_ai_cost = row[3] or 0

    # Calculate savings (baseline $325/claim - actual AI cost)
    ai_baseline_cost = ai_count * 325.0
    current_savings = ai_baseline_cost - ai_cost

    prev_baseline_cost = prev_ai_count * 325.0
    prev_savings = prev_baseline_cost - prev_ai_cost

    savings_change = ((current_savings - prev_savings) / prev_savings * 100) if prev_savings else 0
    savings_trend = "up" if savings_change > 5 else "down" if savings_change < -5 else "stable"

    savings_kpi = KPIValue(
        current_value=round(current_savings, 0),
        unit="dollars",
        trend=savings_trend,
        change_percent=round((current_savings / ai_baseline_cost * 100), 1) if ai_baseline_cost else 0,  # % saved
        previous_value=round(ai_baseline_cost, 0) if compare_to_previous else None,  # Show baseline
        target=None,  # No specific target, more is better
        status="good" if current_savings > 0 else "critical"
    )

    # Summary statistics including processing path breakdown
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN ai_enabled = 1 THEN 1 ELSE 0 END) as ai_count,
            SUM(CASE WHEN processing_path = 'traditional' THEN 1 ELSE 0 END) as traditional_count,
            SUM(CASE WHEN processing_path = 'ai_auto_approved' THEN 1 ELSE 0 END) as ai_auto_count,
            SUM(CASE WHEN processing_path = 'ai_human_reviewed' THEN 1 ELSE 0 END) as ai_reviewed_count,
            SUM(cost_operational) as total_operational_cost,
            SUM(CASE WHEN ai_enabled = 1 THEN cost_operational ELSE 0 END) as ai_operational_cost,
            SUM(CASE WHEN within_tolerance = 1 THEN 1 ELSE 0 END) * 100.0 /
            NULLIF(SUM(CASE WHEN ai_enabled = 1 THEN 1 ELSE 0 END), 0) as accuracy
        FROM claims_warehouse
        WHERE fnol_date BETWEEN ? AND ?
    """, (start.isoformat(), end.isoformat()))

    row = cursor.fetchone()
    total_claims = row[0] or 0
    ai_enabled_claims = row[1] or 0
    traditional_claims = row[2] or 0
    ai_auto_approved_claims = row[3] or 0
    ai_human_reviewed_claims = row[4] or 0
    total_operational_cost = row[5] or 0
    ai_operational_cost = row[6] or 0
    accuracy = row[7] or 0

    # Calculate savings (only AI-enabled claims generate savings)
    # If AI claims were processed traditionally, they would cost: ai_claims × $325
    # Actual AI operational cost is less, so savings = difference
    ai_traditional_baseline = ai_enabled_claims * 325.0
    total_savings = ai_traditional_baseline - ai_operational_cost

    summary = KPISummary(
        total_claims=total_claims,
        ai_enabled_claims=ai_enabled_claims,
        traditional_claims=traditional_claims,
        ai_auto_approved_claims=ai_auto_approved_claims,
        ai_human_reviewed_claims=ai_human_reviewed_claims,
        ai_adoption_rate=round((ai_enabled_claims / total_claims * 100) if total_claims else 0, 1),
        total_savings=round(total_savings, 2),
        accuracy_within_tolerance=round(accuracy, 1)
    )

    conn.close()

    return KPIResponse(
        last_updated=datetime.now(),
        time_period=time_period,
        date_range={"start": start.isoformat(), "end": end.isoformat()},
        kpis={
            "cycle_time_savings": cycle_time_kpi,
            "total_savings": savings_kpi,
            "auto_adjudication_rate": auto_adj_kpi
        },
        summary=summary
    )


@router.get("/trends/{kpi_name}", response_model=TrendDataResponse)
async def get_trends(
    kpi_name: Literal["cycle_time_savings", "total_savings", "auto_adjudication_rate"],
    granularity: str = Query("monthly", description="Time granularity (daily, weekly, monthly)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Fetch time-series data for specific KPI chart

    Args:
        kpi_name: KPI identifier
        granularity: Time granularity (daily, weekly, monthly)
        start_date: Optional start date
        end_date: Optional end date

    Returns:
        Time series data points with chart configuration
    """
    conn = get_warehouse_conn()
    cursor = conn.cursor()

    # Parse dates (default to full 6 months: Oct 2025 - Mar 2026)
    if start_date and end_date:
        start = start_date
        end = end_date
    else:
        start = "2025-10-01"
        end = "2026-03-31"

    # Query based on granularity
    if granularity == "monthly":
        cursor.execute("""
            SELECT
                month,
                year,
                printf('%04d-%02d', year, month) as period,
                CASE month
                    WHEN 1 THEN 'January ' || year
                    WHEN 2 THEN 'February ' || year
                    WHEN 3 THEN 'March ' || year
                    WHEN 4 THEN 'April ' || year
                    WHEN 5 THEN 'May ' || year
                    WHEN 6 THEN 'June ' || year
                    WHEN 7 THEN 'July ' || year
                    WHEN 8 THEN 'August ' || year
                    WHEN 9 THEN 'September ' || year
                    WHEN 10 THEN 'October ' || year
                    WHEN 11 THEN 'November ' || year
                    WHEN 12 THEN 'December ' || year
                    ELSE month || '/' || year
                END as period_label,
                COUNT(*) as claim_count,
                SUM(CASE WHEN ai_enabled = 1 THEN 1 ELSE 0 END) as ai_count,
                SUM(CASE WHEN ai_enabled = 0 THEN 1 ELSE 0 END) as trad_count
            FROM claims_warehouse
            WHERE fnol_date BETWEEN ? AND ?
            GROUP BY month, year
            ORDER BY year, month
        """, (start, end))

        periods = cursor.fetchall()

        data_points = []
        for period_data in periods:
            month, year, period, period_label, claim_count, ai_count, trad_count = period_data

            # Calculate KPI value for this period
            if kpi_name == "cycle_time_savings":
                # Days saved: traditional baseline (19.3) - AI average
                cursor.execute("""
                    SELECT AVG(CASE WHEN ai_enabled = 1 THEN cycle_time_days ELSE NULL END)
                    FROM claims_warehouse
                    WHERE month = ? AND year = ?
                """, (month, year))
                ai_avg = cursor.fetchone()[0] or 0
                value = 19.3 - ai_avg if ai_avg > 0 else 0

            elif kpi_name == "total_savings":
                # Total savings for this period
                cursor.execute("""
                    SELECT
                        SUM(CASE WHEN ai_enabled = 1 THEN 1 ELSE 0 END) as ai_count,
                        SUM(CASE WHEN ai_enabled = 1 THEN cost_operational ELSE 0 END) as ai_cost
                    FROM claims_warehouse
                    WHERE month = ? AND year = ?
                """, (month, year))
                row = cursor.fetchone()
                ai_count_period = row[0] or 0
                ai_cost_period = row[1] or 0
                baseline = ai_count_period * 325.0
                value = baseline - ai_cost_period

            elif kpi_name == "auto_adjudication_rate":
                cursor.execute("""
                    SELECT SUM(CASE WHEN auto_adjudicated = 1 THEN 1 ELSE 0 END) * 100.0 /
                           NULLIF(SUM(CASE WHEN ai_enabled = 1 THEN 1 ELSE 0 END), 0)
                    FROM claims_warehouse
                    WHERE month = ? AND year = ? AND ai_enabled = 1
                """, (month, year))
                value = cursor.fetchone()[0] or 0

            data_points.append(TrendDataPoint(
                period=period,
                period_label=period_label,
                value=round(value, 2),
                claim_count=claim_count,
                ai_enabled_count=ai_count,
                traditional_count=trad_count
            ))

    conn.close()

    # Chart configuration
    chart_config = ChartConfig(
        chart_type="bar_line_hybrid",
        x_axis="period_label",
        y_axis="value",
        bar_data="value",
        line_data="value",
        color_scheme="blue"
    )

    return TrendDataResponse(
        kpi_name=kpi_name,
        granularity=granularity,
        data_points=data_points,
        chart_config=chart_config
    )


@router.post("/query", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    """
    Execute preset or custom query

    Supports 4 preset queries:
    - processing_path: Claims by processing path
    - adjustment_rate: Adjustment rate analysis
    - human_intervention: Human review rate trend
    - fraud_effectiveness: Fraud detection rate by month
    """
    if request.query_type == "preset":
        if not request.preset_id:
            raise HTTPException(status_code=400, detail="preset_id required for preset queries")

        if request.preset_id not in PRESET_QUERIES:
            raise HTTPException(status_code=400, detail=f"Unknown preset query: {request.preset_id}")

        preset = PRESET_QUERIES[request.preset_id]
        conn = get_warehouse_conn()
        cursor = conn.cursor()

        # Parse time range
        start = request.time_range.get("start_date", "2026-01-01")
        end = request.time_range.get("end_date", "2026-03-31")

        if request.preset_id == "processing_path":
            cursor.execute("""
                SELECT
                    processing_path,
                    COUNT(*) as count,
                    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims_warehouse
                                        WHERE ai_enabled = 1 AND fnol_date BETWEEN ? AND ?) as percent
                FROM claims_warehouse
                WHERE ai_enabled = 1 AND fnol_date BETWEEN ? AND ?
                GROUP BY processing_path
            """, (start, end, start, end))

            rows = cursor.fetchall()
            data = [
                QueryDataPoint(
                    category="Auto-Approved" if row[0] == "ai_auto_approved" else "Human-Reviewed",
                    count=row[1],
                    percent=round(row[2], 1)
                )
                for row in rows
            ]

            total_claims = sum(d.count for d in data)
            result_type = "stacked_bar_chart"

        elif request.preset_id == "adjustment_rate":
            # Placeholder: This would query actual vs estimated comparison
            data = [
                QueryDataPoint(category="Within ±10%", count=75, percent=88.0),
                QueryDataPoint(category="Outside Tolerance", count=10, percent=12.0)
            ]
            total_claims = 85
            result_type = "bar_chart"

        elif request.preset_id == "human_intervention":
            cursor.execute("""
                SELECT
                    month,
                    SUM(CASE WHEN human_review_required = 1 THEN 1 ELSE 0 END) * 100.0 /
                    NULLIF(SUM(CASE WHEN ai_enabled = 1 THEN 1 ELSE 0 END), 0) as rate
                FROM claims_warehouse
                WHERE ai_enabled = 1 AND fnol_date BETWEEN ? AND ?
                GROUP BY month
                ORDER BY month
            """, (start, end))

            rows = cursor.fetchall()
            data = [
                QueryDataPoint(
                    category=f"Month {row[0]}",
                    count=0,  # Not applicable for rate
                    percent=round(row[1], 1),
                    value=round(row[1], 1)
                )
                for row in rows
            ]
            total_claims = 0  # Not applicable
            result_type = "line_chart"

        elif request.preset_id == "fraud_effectiveness":
            cursor.execute("""
                SELECT
                    month,
                    SUM(CASE WHEN fraud_detected = 1 THEN 1 ELSE 0 END) * 100.0 /
                    NULLIF(SUM(CASE WHEN ai_enabled = 1 THEN 1 ELSE 0 END), 0) as rate
                FROM claims_warehouse
                WHERE ai_enabled = 1 AND fnol_date BETWEEN ? AND ?
                GROUP BY month
                ORDER BY month
            """, (start, end))

            rows = cursor.fetchall()
            data = [
                QueryDataPoint(
                    category=f"Month {row[0]}",
                    count=0,
                    percent=round(row[1], 1),
                    value=round(row[1], 1)
                )
                for row in rows
            ]
            total_claims = 0
            result_type = "line_chart"

        conn.close()

        chart_config = ChartConfig(
            chart_type=preset["chart_type"],
            x_axis="category",
            y_axis="count" if result_type != "line_chart" else "value",
            color_scheme="blue"
        )

        return QueryResponse(
            query_id=request.preset_id,
            query_text=preset["description"],
            result_type=result_type,
            data=data,
            summary=QuerySummary(total_claims=total_claims, ai_enabled_only=True),
            chart_config=chart_config,
            raw_data_csv_url=f"/api/v1/executive/export/csv?query_id={request.preset_id}"
        )

    else:
        # Custom NLP queries not implemented in MVP
        raise HTTPException(status_code=501, detail="Custom NLP queries not yet implemented")


@router.get("/drilldown/{claim_id}", response_model=ClaimDrillDownResponse)
async def get_claim_drilldown(claim_id: int):
    """
    Fetch claim-level details for drill-down modal

    Args:
        claim_id: Claim ID from warehouse

    Returns:
        Detailed claim information with timeline
    """
    conn_warehouse = get_warehouse_conn()
    conn_main = get_main_conn()

    cursor_warehouse = conn_warehouse.cursor()
    cursor_main = conn_main.cursor()

    # Get warehouse data
    cursor_warehouse.execute("""
        SELECT
            claim_id, customer_id, policy_number, vehicle_make, vehicle_model, vehicle_year, vehicle_vin,
            fnol_date, claim_closed_date, cycle_time_days, processing_path,
            cost_estimated, cost_actual, cost_accuracy_percent, within_tolerance,
            fraud_detected, damage_count
        FROM claims_warehouse
        WHERE claim_id = ?
    """, (claim_id,))

    row = cursor_warehouse.fetchone()
    if not row:
        conn_warehouse.close()
        conn_main.close()
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found in warehouse")

    (claim_id_db, customer_id, policy_number, vehicle_make, vehicle_model, vehicle_year, vehicle_vin,
     fnol_date, claim_closed_date, cycle_time, processing_path,
     cost_estimated, cost_actual, cost_accuracy, within_tolerance,
     fraud_detected, damage_count) = row

    # Get customer name from main database
    cursor_main.execute("""
        SELECT fname, lname
        FROM customers
        WHERE customer_id = ?
    """, (customer_id,))
    customer_row = cursor_main.fetchone()
    customer_name = f"{customer_row[0]} {customer_row[1]}" if customer_row else "Unknown Customer"

    vehicle = f"{vehicle_year} {vehicle_make} {vehicle_model}"

    # Placeholder for damages and events (would query main DB)
    damages = [
        ClaimDamage(part="Front Bumper", severity="moderate", cost=cost_actual * 0.6),
        ClaimDamage(part="Hood", severity="minor", cost=cost_actual * 0.4)
    ]

    events = [
        ClaimEvent(date=fnol_date, status="FNOL", action_by="customer"),
        ClaimEvent(date=fnol_date, status="AI_ESTIMATE_GENERATED", action_by="AI"),
        ClaimEvent(date=claim_closed_date or fnol_date, status="CLAIM_PAID", action_by="admin")
    ]

    conn_warehouse.close()
    conn_main.close()

    return ClaimDrillDownResponse(
        claim_id=claim_id,
        customer_name=customer_name,
        policy_number=policy_number,
        vehicle=vehicle,
        fnol_date=fnol_date,
        claim_closed_date=claim_closed_date,
        cycle_time_days=cycle_time,
        processing_path=processing_path,
        cost_estimated=cost_estimated,
        cost_actual=cost_actual,
        cost_accuracy_percent=cost_accuracy,
        within_tolerance=bool(within_tolerance),
        fraud_detected=bool(fraud_detected),
        damages=damages,
        events=events
    )


@router.get("/export/{format}")
async def export_dashboard(
    format: Literal["pdf", "csv", "png"],
    kpi: str = Query("all", description="KPI to export"),
    time_period: str = Query("last_quarter", description="Time period")
):
    """
    Export dashboard data in various formats

    Args:
        format: Export format (pdf, csv, png)
        kpi: KPI filter (all, cycle_time, etc.)
        time_period: Time period filter

    Returns:
        File download
    """
    # Placeholder implementation
    raise HTTPException(status_code=501, detail=f"Export format '{format}' not yet implemented")
