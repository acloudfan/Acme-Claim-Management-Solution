"""
Estimate service for generating AI and human damage estimates.
"""
from sqlalchemy.orm import Session
from src.api.models.damage import Damage
from src.api.models.claim import Claim
from src.api.models.claim_event import ClaimEvent
from src.api.services.base_service import BaseService
from src.api.services.cost_service import CostService
from src.api.services.claim_service import ClaimService
from src.api.ai.damage_detector import get_damage_detector
from src.api.constants import EstimateType, ClaimState, ClaimAction, ActorType
from src.api.config import settings
from src.api.services.event_logger import log_event
from typing import List, Dict
from pathlib import Path
from datetime import datetime, date
import math
import asyncio

class EstimateService(BaseService):
    """Service for generating damage estimates"""

    def __init__(self, db: Session):
        super().__init__(db)
        self.cost_service = CostService(db)
        self.claim_service = ClaimService(db)

    @staticmethod
    def round_labor_hours(hours: float) -> float:
        """
        Round labor hours UP to nearest 0.5 increment.

        Industry standard: Labor is billed in 0.5 hour increments.

        Examples:
            0.1 → 0.5
            1.2 → 1.5
            2.0 → 2.0
            2.3 → 2.5
            3.7 → 4.0

        Args:
            hours: Raw labor hours (can be any float)

        Returns:
            Rounded labor hours (always in 0.5 increments)
        """
        return math.ceil(hours * 2) / 2

    def generate_ai_estimate(
        self,
        claim_id: int,
        image_ids: List[str],
        state: str = "CA"  # DEPRECATED: kept for backward compatibility, ignored
    ) -> Dict:
        """
        Generate AI damage estimate for claim.
        Uses claim's labor rate instead of state parameter.

        Args:
            claim_id: Claim ID
            image_ids: List of image IDs to analyze
            state: DEPRECATED - State code (ignored, uses claim.state_avg_labor_cost)

        Returns:
            Dictionary with estimate details
        """
        # Get claim to retrieve labor rate
        claim = self.claim_service.get_claim(claim_id)
        labor_rate = float(claim.state_avg_labor_cost) if claim.state_avg_labor_cost else 140.00

        # Delete any existing AI estimates for this claim to avoid duplicates
        self.db.query(Damage).filter(
            Damage.claim_id == claim_id,
            Damage.estimate_type == EstimateType.AI.value
        ).delete()
        self.db.commit()
        self.logger.info(f"Cleared existing AI estimates for claim {claim_id}")

        detector = get_damage_detector()
        estimate_id = f"{claim_id}_{int(datetime.now().timestamp())}"

        damages = []
        total_cost = 0.0

        # NOTE: Damage assessment now runs per-image during upload (see image_service.py)
        # This method only reads existing damage records from database that were created during upload

        # Retrieve existing damage records for this claim (created during image upload)
        existing_damages = self.db.query(Damage).filter(
            Damage.claim_id == claim_id,
            Damage.image_id.in_(image_ids)
        ).all()

        # Process existing damage records
        for damage in existing_damages:
                # Damage records already exist with assessments and costs from upload
                # Just accumulate totals and add to list
                damages.append(damage)
                total_cost += float(damage.ai_total_cost or 0.0)

        # Update claim with estimate info
        claim.active_estimate_id = estimate_id
        claim.claim_amount = total_cost

        # Calculate average confidence across all damages
        avg_confidence = 0.0
        if damages:
            total_confidence = sum(d.damage_confidence for d in damages)
            avg_confidence = total_confidence / len(damages)

        # Confidence threshold for automatic approval
        CONFIDENCE_THRESHOLD = 0.55

        # Transition to appropriate state based on confidence
        # Can transition from either IMAGE_UPLOADED or FNOL state
        if claim.current_status in [ClaimState.IMAGE_UPLOADED.value, ClaimState.FNOL.value]:
            if avg_confidence >= CONFIDENCE_THRESHOLD:
                # High confidence: transition to LOSS_ESTIMATED_AI first
                claim.current_status = ClaimState.LOSS_ESTIMATED_AI.value
                self.commit()

                # Log estimate generation event
                event1 = ClaimEvent(
                    claim_id=claim_id,
                    event_date=date.today(),
                    event_time=datetime.now().time(),
                    status=claim.current_status,
                    action=ClaimAction.GENERATE_ESTIMATE.value,
                    action_by=ActorType.AI_AGENT.value,
                    action_by_identity="damage_detector_ai",
                    comments=f"AI estimate generated with {len(damages)} damages. Avg confidence: {avg_confidence:.2f}"
                )
                self.db.add(event1)
                self.db.commit()

                self.logger.info(
                    f"Transitioned claim {claim_id} to LOSS_ESTIMATED_AI "
                    f"(avg confidence: {avg_confidence:.2f} >= {CONFIDENCE_THRESHOLD})"
                )

                # Automatically transition to CUSTOMER_DECISION_PENDING for high confidence
                claim.current_status = ClaimState.CUSTOMER_DECISION_PENDING.value
                self.commit()

                # Log presentation event
                event2 = ClaimEvent(
                    claim_id=claim_id,
                    event_date=date.today(),
                    event_time=datetime.now().time(),
                    status=claim.current_status,
                    action=ClaimAction.PRESENT_ESTIMATE_TO_CUSTOMER.value,
                    action_by=ActorType.AI_AGENT.value,
                    action_by_identity="system",
                    comments=f"High-confidence estimate (${total_cost:.2f}) presented to customer for decision"
                )
                self.db.add(event2)
                self.db.commit()

                self.logger.info(
                    f"Transitioned claim {claim_id} to CUSTOMER_DECISION_PENDING "
                    f"(high confidence estimate ready for customer decision)"
                )
            else:
                # Low confidence: route to human review
                claim.current_status = ClaimState.HUMAN_REVIEW_PENDING.value
                self.commit()

                # Log estimate generation and routing to human review
                event3 = ClaimEvent(
                    claim_id=claim_id,
                    event_date=date.today(),
                    event_time=datetime.now().time(),
                    status=claim.current_status,
                    action=ClaimAction.GENERATE_ESTIMATE.value,
                    action_by=ActorType.AI_AGENT.value,
                    action_by_identity="damage_detector_ai",
                    comments=f"AI estimate generated with {len(damages)} damages. Avg confidence: {avg_confidence:.2f} - routed to human review"
                )
                self.db.add(event3)
                self.db.commit()

                self.logger.info(
                    f"Transitioned claim {claim_id} to HUMAN_REVIEW_PENDING "
                    f"(avg confidence: {avg_confidence:.2f} < {CONFIDENCE_THRESHOLD})"
                )
        else:
            self.logger.warning(
                f"Cannot transition claim {claim_id} from status: {claim.current_status}"
            )

        self.logger.info(
            f"Generated AI estimate {estimate_id} for claim {claim_id}: "
            f"${total_cost:.2f} across {len(damages)} damages, "
            f"avg confidence: {avg_confidence:.2f}"
        )

        return {
            "estimate_id": estimate_id,
            "claim_id": claim_id,
            "total_cost": total_cost,
            "damages_count": len(damages),
            "damages": damages,
            "avg_confidence": avg_confidence,
            "status": claim.current_status
        }

    def get_estimate_damages(self, estimate_id: str) -> List[Damage]:
        """Get all damages for an estimate"""
        return self.db.query(Damage).filter(
            Damage.estimate_id == estimate_id
        ).all()

    def get_claim_estimates(self, claim_id: int) -> List[str]:
        """Get all estimate IDs for a claim"""
        results = self.db.query(Damage.estimate_id).filter(
            Damage.claim_id == claim_id
        ).distinct().all()
        return [r[0] for r in results]

    # TODO: ClaimSummaryAgent - TBD
    # When continue button is clicked, run aggregate claim-level summary agent
    # This will generate an overall claim summary based on all damages
    # See: src/api/agents/damage_assessment/ for reference implementation
