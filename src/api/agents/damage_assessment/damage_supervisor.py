"""
Damage Assessment Supervisor Agent
Orchestrates damage assessment agents to enhance YOLO detection results.
"""
import logging
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session

from ..base_agent import BaseAgent, AgentResult
from ..llm.base import BaseLLMClient
from ..llm.config import load_llm_config, get_llm_client
from ..tracking import start_agent_trace, end_agent_trace, update_trace_metadata
from src.api.config import settings
from src.api.models.damage import Damage

from .summary_agent import DamageSummaryAgent

logger = logging.getLogger(__name__)


class DamageAssessmentSupervisor(BaseAgent):
    """
    Damage Assessment Supervisor - orchestrates damage assessment agents.

    Flow:
    1. After YOLO detection and heuristic assessment
    2. For each detected damage, run summary generation agent
    3. Update damages with customer-friendly summaries
    4. Track token usage and execution time

    Extensible for future agents:
    - Secondary damage predictor
    - Severity refinement
    - Repair strategy optimizer
    """

    def __init__(self, llm_client: BaseLLMClient, config: Dict[str, Any], db: Session):
        """
        Initialize damage assessment supervisor.

        Args:
            llm_client: Vision-capable LLM client
            config: Agent configuration
            db: Database session
        """
        super().__init__(llm_client, config)
        self.db = db

        # Get vision LLM client for image analysis
        vision_provider = settings.DEFAULT_VISION_MODEL
        vision_config = load_llm_config(vision_provider, settings.config)
        self.vision_client = get_llm_client(vision_config)

        # Initialize sub-agents
        summary_config = config.get('agents', {}).get('damage_assessment', {}).get('summary_agent', {})
        self.summary_agent = DamageSummaryAgent(self.vision_client, summary_config)

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute damage assessment supervision.

        Args:
            input_data: Dict with:
                - claim_id: int - Claim ID
                - damages: List[Dict] - List of damage dicts from YOLO
                - images: List[str] - List of image file paths
                - vehicle_info: Dict - Vehicle context (make, model, year, color)

        Returns:
            AgentResult with damage summaries
        """
        start_time = datetime.now()
        claim_id = input_data['claim_id']
        damages = input_data.get('damages', [])
        images = input_data.get('images', [])
        vehicle_info = input_data.get('vehicle_info', {})

        logger.info(f"=== DAMAGE ASSESSMENT STARTED for claim {claim_id} ({len(damages)} damages) ===")

        # Start Langfuse trace for this agent execution
        with start_agent_trace(
            agent_name="DamageAssessmentSupervisor",
            metadata={
                "claim_id": claim_id,
                "damage_count": len(damages),
                "image_count": len(images)
            }
        ):
            try:
                if not damages:
                    logger.warning(f"No damages to assess for claim {claim_id}")
                    return self._create_no_damages_result(claim_id)

                # Run summary agent for each damage
                summaries = await self._run_summary_agent(damages, images, vehicle_info)

                # Calculate aggregate confidence
                avg_confidence = sum(s.get('assessment_confidence', 0) for s in summaries) / len(summaries) if summaries else 0

                # Aggregate token usage
                total_input_tokens = sum(s.get('input_tokens', 0) for s in summaries)
                total_output_tokens = sum(s.get('output_tokens', 0) for s in summaries)

                execution_time_ms = self._measure_execution_time(start_time)

                # Update trace with final results
                update_trace_metadata({
                    "summaries_generated": len(summaries),
                    "avg_confidence": avg_confidence
                })

                result_data = {
                    'claim_id': claim_id,
                    'summaries': summaries,
                    'confidence': avg_confidence,
                    'summary_count': len(summaries)
                }

                logger.info(f"=== DAMAGE ASSESSMENT COMPLETED: {len(summaries)} summaries generated ===")

                return self._create_result(
                    success=True,
                    data=result_data,
                    execution_time_ms=execution_time_ms,
                    input_tokens=total_input_tokens,
                    output_tokens=total_output_tokens
                )

            except Exception as e:
                logger.error(f"Damage assessment supervisor failed: {e}", exc_info=True)
                return self._create_result(
                    success=False,
                    data={'claim_id': claim_id, 'error': str(e)},
                    error=str(e)
                )

    async def _run_summary_agent(self, damages: List[Dict], images: List[str], vehicle_info: Dict) -> List[Dict]:
        """
        Run summary agent for each damage.

        Args:
            damages: List of damage dictionaries from YOLO
            images: List of image file paths
            vehicle_info: Vehicle context

        Returns:
            List of summary results with customer_summary and confidence
        """
        # Check if summary agent is enabled
        summary_enabled = settings.SUMMARY_AGENT_ENABLED
        if not summary_enabled:
            logger.info("Summary agent disabled, skipping summary generation")
            return []

        tasks = []

        for damage in damages:
            # Find the image associated with this damage
            damage_image = None
            for img_path in images:
                # Match by filename if damage has image reference
                if damage.get('image_path') == img_path:
                    damage_image = img_path
                    break

            # If no specific match, use first image (fallback)
            if not damage_image and images:
                damage_image = images[0]

            summary_input = {
                'damage': damage,
                'image_path': damage_image,
                'vehicle_info': vehicle_info
            }
            tasks.append(self._execute_summary_for_damage(damage, summary_input))

        if not tasks:
            logger.warning("No summary tasks created")
            return []

        logger.info(f"Running summary agent for {len(tasks)} damages")

        # Run summary agents in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        summaries = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Assessment agent failed for damage {i}: {result}")
                # Use fallback values instead of None to prevent downstream errors
                summaries.append({
                    'damage_summary': None,  # OK to be None - will be omitted from UI
                    'internal_damage_probability': 0.5,  # Fallback value
                    'severity': 0.5,  # Fallback value (CRITICAL - prevents cost calc error)
                    'recommended_action': 'assess',  # Fallback value
                    'reasoning': f"Assessment failed: {str(result)}",  # Error context
                    'car_side': 'unknown',  # Fallback value
                    'assessment_confidence': 0.0,
                    'input_tokens': 0,
                    'output_tokens': 0,
                    'error': str(result)
                })
            elif result.success:
                summaries.append(result.data)
            else:
                # Use fallback values for failed assessments
                summaries.append({
                    'damage_summary': None,  # OK to be None
                    'internal_damage_probability': 0.5,  # Fallback value
                    'severity': 0.5,  # Fallback value (CRITICAL)
                    'recommended_action': 'assess',  # Fallback value
                    'reasoning': f"Assessment failed: {result.error}",
                    'car_side': 'unknown',  # Fallback value
                    'assessment_confidence': 0.0,
                    'input_tokens': 0,
                    'output_tokens': 0,
                    'error': result.error
                })

        return summaries

    async def _execute_summary_for_damage(self, damage: Dict, summary_input: Dict) -> AgentResult:
        """Execute summary agent for a single damage"""
        try:
            result = await self.summary_agent.execute(summary_input)
            if result.success:
                logger.info(
                    f"Summary generated for damage {damage.get('damage_part')}: "
                    f"input_tokens={result.input_tokens}, output_tokens={result.output_tokens}"
                )
            return result
        except Exception as e:
            logger.error(f"Failed to generate summary for damage {damage.get('damage_part')}: {e}")
            raise

    def _create_no_damages_result(self, claim_id: int) -> AgentResult:
        """Create result when no damages to assess"""
        return self._create_result(
            success=True,
            data={
                'claim_id': claim_id,
                'summaries': [],
                'confidence': 0.0,
                'summary_count': 0
            }
        )
