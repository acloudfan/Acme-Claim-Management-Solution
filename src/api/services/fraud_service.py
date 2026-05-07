"""
Fraud detection service for running fraud analysis on claims.
"""
import logging
import asyncio
from typing import Dict, Any
from sqlalchemy.orm import Session

from src.api.config import settings
from src.api.agents.fraud.fraud_supervisor import FraudDetectionSupervisor
from src.api.agents.llm.factory import get_llm_client
from src.api.models.claim import Claim

logger = logging.getLogger(__name__)


class FraudDetectionService:
    """
    Service for running fraud detection on claims.

    This service acts as a bridge between the API layer and the fraud detection agents.
    """

    def __init__(self, db: Session):
        """
        Initialize fraud detection service.

        Args:
            db: Database session
        """
        self.db = db

    def run_fraud_detection(self, claim_id: int) -> Dict[str, Any]:
        """
        Run fraud detection analysis on a claim.

        This method:
        1. Checks if fraud detection is enabled
        2. Creates the fraud supervisor agent
        3. Runs the analysis (async)
        4. Returns the results

        Args:
            claim_id: Claim ID to analyze

        Returns:
            Dict with fraud analysis results including:
                - final_risk_score: float (0.0-1.0)
                - recommendation: str (APPROVE/HUMAN_REVIEW/REJECT)
                - summary: str - Human-readable summary
                - all_signals: List of fraud signals detected

        Raises:
            Exception: If fraud detection fails
        """
        if not settings.FRAUD_DETECTOR_ENABLED:
            logger.info("Fraud detection is disabled, skipping analysis")
            return {
                'final_risk_score': 0.0,
                'recommendation': 'APPROVE',
                'summary': 'Fraud detection disabled',
                'all_signals': []
            }

        try:
            logger.info(f"Running fraud detection for claim {claim_id}")

            # Get LLM clients
            from ..agents.llm.config import load_llm_config, get_llm_client as get_client

            # Load default provider for text LLM
            default_provider = settings.DEFAULT_LLM_PROVIDER
            llm_config = load_llm_config(default_provider, settings.config)
            llm_client = get_client(llm_config)

            # Create fraud supervisor
            config = {}  # Can pass additional config if needed
            supervisor = FraudDetectionSupervisor(llm_client, config, self.db)

            # Run fraud detection (async)
            input_data = {'claim_id': claim_id}
            result = asyncio.run(supervisor.execute(input_data))

            if not result.success:
                logger.error(f"Fraud detection failed for claim {claim_id}: {result.error}")
                # Return low risk on failure (innocent until proven guilty)
                return {
                    'final_risk_score': 0.15,  # Low risk on failure
                    'recommendation': 'APPROVE',
                    'summary': f'Fraud detection unavailable - proceeding with low risk default',
                    'all_signals': []
                }

            logger.info(
                f"Fraud detection completed for claim {claim_id}: "
                f"Risk={result.data['final_risk_score']:.2f}, "
                f"Recommendation={result.data['recommendation']}"
            )

            return result.data

        except Exception as e:
            logger.error(f"Fraud detection service error for claim {claim_id}: {e}", exc_info=True)
            # Return low risk on error (innocent until proven guilty)
            return {
                'final_risk_score': 0.15,
                'recommendation': 'APPROVE',
                'summary': f'Fraud detection unavailable - proceeding with low risk default',
                'all_signals': []
            }

    def update_claim_fraud_score(self, claim_id: int, risk_score: float):
        """
        Update claim's fraud risk score in database.

        Args:
            claim_id: Claim ID
            risk_score: Fraud risk score (0.0-1.0)
        """
        try:
            claim = self.db.query(Claim).filter(Claim.claim_id == claim_id).first()
            if claim:
                claim.overall_fraud_risk_score = risk_score
                self.db.commit()
                logger.info(f"Updated fraud risk score for claim {claim_id}: {risk_score:.2f}")
        except Exception as e:
            logger.error(f"Failed to update fraud score for claim {claim_id}: {e}")
            self.db.rollback()
