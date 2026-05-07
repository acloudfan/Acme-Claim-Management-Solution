"""
Fraud Detection Supervisor Agent
Orchestrates all fraud detection phases and aggregates results.
"""
import logging
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session

from ..base_agent import BaseAgent, AgentResult
from ..llm.base import BaseLLMClient
from ..llm.config import load_llm_config, get_llm_client
from src.api.config import settings
from src.api.models.fraud_signal import FraudSignal

from .utils import (
    load_claim_images,
    get_claim_context,
    build_evidence_dict
)
from .color_verification_agent import ColorVerificationAgent
from .make_model_verification_agent import MakeModelVerificationAgent
from .ai_generated_detector_agent import AIGeneratedDetectorAgent
from .image_manipulation_detector_agent import ImageManipulationDetectorAgent
from .behavior_pattern_agent import BehaviorPatternAgent

logger = logging.getLogger(__name__)


class FraudDetectionSupervisor(BaseAgent):
    """
    Fraud Detection Supervisor - orchestrates all fraud detection phases.

    Flow:
    1. Phase 1: Run enabled vision agents in parallel (color, make/model, AI-generated, manipulation)
       - Each check can be independently enabled/disabled in config
       - Disabled checks contribute 0 risk (assume passed)
    2. Phase 2: Run enabled static checks in parallel (VIN, claim frequency, velocity)
       - Each check can be independently enabled/disabled in config
       - Disabled checks contribute 0 risk (assume passed)
    3. Aggregate Phase 1 + 2 signals and calculate combined risk score
    4. Phase 3 Decision:
       - If phase3.enabled=false: Skip Phase 3
       - If phase3.always_run=true: Always run behavioral analysis
       - Else: Use thresholds for borderline detection:
         * risk >= skip_phase3_high_threshold: Skip (clear high risk)
         * risk < skip_phase3_low_threshold: Skip (clear low risk)
         * Otherwise: Run Phase 3 (borderline case)
    5. Calculate final risk score and make recommendation
    6. Store fraud signals in database
    """

    def __init__(self, llm_client: BaseLLMClient, config: Dict[str, Any], db: Session):
        """
        Initialize fraud detection supervisor.

        Args:
            llm_client: Default LLM client (for text analysis)
            config: Agent configuration
            db: Database session
        """
        super().__init__(llm_client, config)
        self.db = db

        # Get vision LLM client (may be different from text LLM)
        vision_provider = settings.DEFAULT_VISION_MODEL
        vision_config = load_llm_config(vision_provider, settings.config)
        self.vision_client = get_llm_client(vision_config)

        # Initialize sub-agents
        self.color_agent = ColorVerificationAgent(self.vision_client, config)
        self.make_model_agent = MakeModelVerificationAgent(self.vision_client, config)
        self.ai_gen_agent = AIGeneratedDetectorAgent(self.vision_client, config)
        self.manipulation_agent = ImageManipulationDetectorAgent(self.vision_client, config)
        self.behavior_agent = BehaviorPatternAgent(llm_client, config)  # Uses text LLM

        # Load configurations
        self.high_risk_threshold = settings.FRAUD_HIGH_RISK_THRESHOLD
        self.medium_risk_threshold = settings.FRAUD_MEDIUM_RISK_THRESHOLD

        self.phase1_config = settings.get_fraud_phase1_config()
        self.phase2_config = settings.get_fraud_phase2_config()
        self.phase3_config = settings.get_fraud_phase3_config()

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute fraud detection supervision.

        Args:
            input_data: Dict with:
                - claim_id: int - Claim ID to analyze

        Returns:
            AgentResult with fraud detection results
        """
        start_time = datetime.now()

        try:
            claim_id = input_data['claim_id']
            logger.info(f"=== FRAUD DETECTION STARTED for claim {claim_id} ===")

            # Load claim context and images
            claim_context = get_claim_context(claim_id, self.db)
            images = load_claim_images(claim_id)

            if not images:
                logger.warning(f"No images found for claim {claim_id}")
                return self._create_no_images_result(claim_id)

            # PHASE 1: Vision Agents (run enabled agents in parallel)
            logger.info(f"Phase 1: Running vision agents in parallel...")
            phase1_results = await self._run_phase1(images, claim_context)
            phase1_signals = [r.data for r in phase1_results if r.success]

            # Calculate Phase 1 risk score with enabled checks only
            phase1_score = self._calculate_phase_score(phase1_signals, self.phase1_config)
            logger.info(f"Phase 1 score: {phase1_score:.2f}")

            # PHASE 2: Static Checks (run in parallel) - TODOs
            logger.info(f"Phase 2: Running static checks... (TODOs - skipping for now)")
            phase2_signals = []
            phase2_score = 0.0

            # Combine Phase 1 + 2 scores
            combined_score = (phase1_score + phase2_score) / 2 if phase2_score > 0 else phase1_score
            logger.info(f"Combined Phase 1+2 score: {combined_score:.2f}")

            # Decision: Should we run Phase 3?
            run_phase3 = self._should_run_phase3(combined_score)

            # PHASE 3: Behavioral Analysis (conditional)
            phase3_signal = None
            phase3_score = 0.0

            if run_phase3:
                logger.info(f"Phase 3: Running behavioral analysis (borderline case: {combined_score:.2f})")
                phase3_result = await self._run_phase3(claim_context, phase1_signals, phase2_signals)
                if phase3_result.success:
                    phase3_signal = phase3_result.data
                    phase3_score = phase3_signal.get('severity', 0.0)
                    logger.info(f"Phase 3 score: {phase3_score:.2f}")
            else:
                reason = "high risk" if combined_score >= self.skip_phase3_high else "low risk"
                logger.info(f"Phase 3: SKIPPED (clear {reason})")

            # Calculate final risk score
            final_risk_score = self._calculate_final_risk(
                combined_score,
                phase3_score,
                phase3_signal is not None
            )

            # Make recommendation
            recommendation = self._make_recommendation(final_risk_score)

            # Aggregate all evidence
            all_signals = phase1_signals + phase2_signals
            if phase3_signal:
                all_signals.append(phase3_signal)

            # Store fraud signals in database
            self._store_fraud_signals(claim_id, final_risk_score, all_signals)

            # Aggregate token usage
            total_input_tokens = sum(r.input_tokens for r in phase1_results)
            total_output_tokens = sum(r.output_tokens for r in phase1_results)

            execution_time_ms = self._measure_execution_time(start_time)

            result_data = {
                'claim_id': claim_id,
                'final_risk_score': final_risk_score,
                'recommendation': recommendation,
                'phase1_score': phase1_score,
                'phase2_score': phase2_score,
                'phase3_score': phase3_score,
                'phase3_executed': phase3_signal is not None,
                'all_signals': all_signals,
                'summary': self._build_summary(final_risk_score, recommendation, all_signals)
            }

            logger.info(f"=== FRAUD DETECTION COMPLETED: Risk={final_risk_score:.2f}, Recommendation={recommendation} ===")

            return self._create_result(
                success=True,
                data=result_data,
                execution_time_ms=execution_time_ms,
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens
            )

        except Exception as e:
            logger.error(f"Fraud detection supervisor failed: {e}", exc_info=True)
            return self._create_result(
                success=False,
                data={'claim_id': input_data.get('claim_id'), 'error': str(e)},
                error=str(e)
            )

    async def _run_phase1(self, images: List[Dict], claim_context: Dict) -> List[AgentResult]:
        """Run enabled Phase 1 vision agents in parallel"""
        vehicle = claim_context.get('vehicle', {})
        tasks = []
        agent_names = []

        # Check which agents are enabled and build task list
        if self.phase1_config.get('color_verification', {}).get('enabled', True):
            color_input = {
                'images': images,
                'expected_color': vehicle.get('color'),
                'vehicle_info': vehicle
            }
            tasks.append(self.color_agent.execute(color_input))
            agent_names.append('color_verification')

        if self.phase1_config.get('make_model_verification', {}).get('enabled', True):
            make_model_input = {
                'images': images,
                'expected_make': vehicle.get('make'),
                'expected_model': vehicle.get('model'),
                'expected_year': vehicle.get('year')
            }
            tasks.append(self.make_model_agent.execute(make_model_input))
            agent_names.append('make_model_verification')

        if self.phase1_config.get('ai_generated_detection', {}).get('enabled', True):
            ai_gen_input = {'images': images}
            tasks.append(self.ai_gen_agent.execute(ai_gen_input))
            agent_names.append('ai_generated_detection')

        if self.phase1_config.get('manipulation_detection', {}).get('enabled', True):
            manipulation_input = {'images': images}
            tasks.append(self.manipulation_agent.execute(manipulation_input))
            agent_names.append('manipulation_detection')

        if not tasks:
            logger.warning("No Phase 1 agents enabled")
            return []

        logger.info(f"Running {len(tasks)} enabled Phase 1 agents: {', '.join(agent_names)}")

        # Run enabled agents in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Phase 1 agent {agent_names[i]} failed: {result}")
                # Create failure result
                final_results.append(AgentResult(
                    success=False,
                    data={'severity': 0.0, 'signal_type': agent_names[i]},
                    error=str(result)
                ))
            else:
                final_results.append(result)

        return final_results

    async def _run_phase3(self, claim_context: Dict, phase1: List, phase2: List) -> AgentResult:
        """Run Phase 3 behavioral analysis"""
        # TODO: Load damage details from database if available
        damage_details = []

        behavior_input = {
            'claim_context': claim_context,
            'phase1_signals': phase1,
            'phase2_signals': phase2,
            'damage_details': damage_details
        }

        return await self.behavior_agent.execute(behavior_input)

    def _calculate_phase_score(self, signals: List[Dict], phase_config: Dict) -> float:
        """
        Calculate weighted phase score considering only enabled checks.
        Disabled checks contribute 0 risk (assume passed).

        Args:
            signals: List of signal dictionaries with 'signal_type' and 'severity'
            phase_config: Phase configuration with check names, enabled flags, and weights

        Returns:
            Weighted score between 0.0 and 1.0
        """
        if not signals:
            return 0.0

        # Map signal types to their config keys
        signal_type_mapping = {
            'color_mismatch': 'color_verification',
            'make_model_mismatch': 'make_model_verification',
            'ai_generated': 'ai_generated_detection',
            'image_manipulation': 'manipulation_detection',
            'vin_format': 'vin_format_validation',
            'vin_year': 'vin_year_consistency',
            'claim_frequency': 'claim_frequency',
            'claim_velocity': 'claim_velocity'
        }

        total_weighted_score = 0.0
        total_weight = 0.0

        for signal in signals:
            signal_type = signal.get('signal_type', '')
            severity = signal.get('severity', 0.0)

            # Map signal type to config key
            config_key = signal_type_mapping.get(signal_type, signal_type)
            check_config = phase_config.get(config_key, {})

            # Check if this check is enabled (default to True for backward compatibility)
            if isinstance(check_config, dict):
                enabled = check_config.get('enabled', True)
                weight = check_config.get('weight', 0.0)
            else:
                # Old format: just weight values
                enabled = True
                weight = check_config

            if enabled:
                total_weighted_score += severity * weight
                total_weight += weight

        # Normalize by total weight of enabled checks
        if total_weight > 0:
            return total_weighted_score / total_weight
        else:
            return 0.0

    def _should_run_phase3(self, combined_score: float) -> bool:
        """Determine if Phase 3 should run based on configuration and combined score"""
        # Check if Phase 3 is enabled
        if not self.phase3_config.get('enabled', True):
            return False

        # Check if always_run is enabled
        if self.phase3_config.get('always_run', False):
            logger.info("Phase 3 always_run=true, executing behavioral analysis")
            return True

        # Use thresholds for borderline detection
        skip_high = self.phase3_config.get('skip_phase3_high_threshold', 0.8)
        skip_low = self.phase3_config.get('skip_phase3_low_threshold', 0.3)

        if combined_score >= skip_high:
            return False  # Clear high risk, skip Phase 3
        if combined_score < skip_low:
            return False  # Clear low risk, skip Phase 3
        return True  # Borderline, run Phase 3

    def _calculate_final_risk(self, combined_score: float, phase3_score: float, phase3_ran: bool) -> float:
        """Calculate final risk score"""
        if not phase3_ran:
            # Phase 3 didn't run, use combined score
            return combined_score

        # Phase 3 ran, blend with combined score
        phase3_weight = self.phase3_config.get('weight', 0.4)
        phases12_weight = 1.0 - phase3_weight

        final_score = (combined_score * phases12_weight) + (phase3_score * phase3_weight)
        return min(1.0, final_score)

    def _make_recommendation(self, risk_score: float) -> str:
        """Make recommendation based on risk score"""
        if risk_score >= self.high_risk_threshold:
            return "REJECT"
        elif risk_score >= self.medium_risk_threshold:
            return "HUMAN_REVIEW"
        else:
            return "APPROVE"

    def _store_fraud_signals(self, claim_id: int, overall_risk: float, signals: List[Dict]):
        """Store fraud signals in database"""
        try:
            for signal in signals:
                fraud_signal = FraudSignal(
                    claim_id=claim_id,
                    detection_timestamp=datetime.utcnow(),
                    overall_risk_score=overall_risk,
                    signal_type=signal.get('signal_type'),
                    severity=signal.get('severity'),
                    description=signal.get('description'),
                    evidence=signal.get('evidence'),
                    agent_version='v1.0'
                )
                self.db.add(fraud_signal)

            self.db.commit()
            logger.info(f"Stored {len(signals)} fraud signals for claim {claim_id}")

        except Exception as e:
            logger.error(f"Failed to store fraud signals: {e}")
            self.db.rollback()

    def _build_summary(self, risk_score: float, recommendation: str, signals: List[Dict]) -> str:
        """Build human-readable summary"""
        risk_level = "HIGH" if risk_score >= self.high_risk_threshold else \
                     "MEDIUM" if risk_score >= self.medium_risk_threshold else "LOW"

        high_severity_signals = [s for s in signals if s.get('severity', 0) >= 0.6]

        summary = f"Fraud Risk: {risk_level} ({risk_score:.2f})\n"
        summary += f"Recommendation: {recommendation}\n\n"

        if high_severity_signals:
            summary += "Key Concerns:\n"
            for sig in high_severity_signals[:3]:  # Top 3
                summary += f"  - {sig.get('signal_type')}: {sig.get('description', '')[:100]}\n"
        else:
            summary += "No major fraud indicators detected.\n"

        return summary

    def _create_no_images_result(self, claim_id: int) -> AgentResult:
        """Create result when no images are available"""
        return self._create_result(
            success=True,
            data={
                'claim_id': claim_id,
                'final_risk_score': 0.0,
                'recommendation': 'APPROVE',
                'summary': 'No images available for fraud detection analysis.'
            }
        )
