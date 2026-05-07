"""
Cost calculation service for damage repair estimation.
Provides cost estimates based on damage part, severity, and state.
"""
from typing import Dict, Any
from src.api.services.base_service import BaseService
import logging

logger = logging.getLogger(__name__)

# State-specific labor rates ($/hour)
STATE_LABOR_RATES = {
    "CA": 156.00,
    "TX": 125.00,
    "NY": 175.00,
    "FL": 135.00,
    "DEFAULT": 140.00
}

# Damage part base estimates
DAMAGE_PART_ESTIMATES = {
    "boot-dent": {"labor_hours": (1.5, 3.0), "parts_cost": (500, 1200)},
    "front-bumper-dent": {"labor_hours": (1.0, 2.5), "parts_cost": (300, 800)},
    "door-scratch": {"labor_hours": (0.5, 1.5), "parts_cost": (200, 600)},
    "paint-damage": {"labor_hours": (1.0, 2.0), "parts_cost": (150, 400)},
    "rear-bumper": {"labor_hours": (1.5, 2.5), "parts_cost": (400, 900)},
    "hood-dent": {"labor_hours": (2.0, 3.5), "parts_cost": (600, 1500)},
    "side-panel": {"labor_hours": (2.5, 4.0), "parts_cost": (800, 2000)},
}

class CostService(BaseService):
    """Service for calculating repair cost estimates"""

    def calculate_cost(
        self,
        damage_report: Dict,
        assessment: Dict,
        labor_rate: float  # CHANGED: Accept labor rate directly, not state
    ) -> Dict[str, Any]:
        """
        Calculate repair cost based on damage report and provided labor rate.

        Args:
            damage_report: Damage detection info (part, class, confidence)
            assessment: Damage assessment (severity, internal_damage_probability)
            labor_rate: Labor rate in $/hour (from claim.state_avg_labor_cost)

        Returns:
            Cost breakdown with labor, parts, and total
        """
        damage_part = damage_report.get("part", "unknown")
        severity = assessment.get("severity", 0.5)
        internal_damage_prob = assessment.get("internal_damage_probability", 0.0)
        confidence = damage_report.get("confidence", 0.7)

        # Get base estimates for damage part
        if damage_part in DAMAGE_PART_ESTIMATES:
            base = DAMAGE_PART_ESTIMATES[damage_part]
        else:
            # Default estimates for unknown parts
            base = {"labor_hours": (1.0, 2.0), "parts_cost": (300, 600)}
            logger.warning(f"Unknown damage part: {damage_part}, using defaults")

        # Calculate labor hours based on severity
        labor_hours = self._interpolate_labor_hours(base["labor_hours"], severity)

        # Calculate parts cost based on severity
        parts_cost = self._interpolate_parts_cost(base["parts_cost"], severity)

        # Calculate base costs
        labor_cost = labor_hours * labor_rate

        # Apply internal damage adjustment
        if internal_damage_prob > 0.7:
            adjustment_factor = 1.5  # 50% increase
        elif internal_damage_prob > 0.5:
            adjustment_factor = 1.25  # 25% increase
        else:
            adjustment_factor = 1.0

        # Apply adjustment
        adjusted_labor_cost = labor_cost * adjustment_factor
        adjusted_parts_cost = parts_cost * adjustment_factor
        total_cost = adjusted_labor_cost + adjusted_parts_cost

        return {
            "damage_part": damage_part,
            "severity": severity,
            "labor_hours": round(labor_hours, 2),
            "avg_labor_cost": labor_rate,
            "estimated_parts_cost": round(adjusted_parts_cost, 2),
            "estimated_total_cost": round(total_cost, 2),
            "breakdown": {
                "labor_cost": round(adjusted_labor_cost, 2),
                "parts_cost": round(adjusted_parts_cost, 2),
                "total": round(total_cost, 2)
            },
            "confidence": confidence,
            "notes": f"Estimate based on severity {severity} and internal damage probability {internal_damage_prob}"
        }

    def _interpolate_labor_hours(self, range_tuple: tuple, severity: float) -> float:
        """Interpolate labor hours based on severity"""
        min_hours, max_hours = range_tuple
        # Linear interpolation based on severity
        return min_hours + (max_hours - min_hours) * severity

    def _interpolate_parts_cost(self, range_tuple: tuple, severity: float) -> float:
        """Interpolate parts cost based on severity"""
        min_cost, max_cost = range_tuple
        # Linear interpolation based on severity
        return min_cost + (max_cost - min_cost) * severity
