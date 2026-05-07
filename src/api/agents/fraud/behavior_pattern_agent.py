"""
Behavior Pattern Analyzer Agent - Phase 3 Agent
Analyzes behavioral patterns for borderline fraud cases.
"""
import logging
from typing import Dict, Any, List
from datetime import datetime
import json

from ..base_agent import BaseAgent, AgentResult
from ..llm.base import BaseLLMClient, Message
from .utils import build_evidence_dict

logger = logging.getLogger(__name__)


class BehaviorPatternAgent(BaseAgent):
    """
    Behavioral pattern analyzer for borderline fraud cases (0.3-0.8 risk).

    Synthesizes all available information to detect suspicious patterns:
    1. Damage pattern coherence with incident description
    2. Story consistency across claim details
    3. Location and physics reasonableness
    """

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute behavioral pattern analysis.

        Args:
            input_data: Dict with:
                - claim_context: Dict with claim, vehicle, policy, customer info
                - phase1_signals: List of Phase 1 fraud signals
                - phase2_signals: List of Phase 2 fraud signals
                - damage_details: List of damages detected (optional)

        Returns:
            AgentResult with behavioral analysis
        """
        start_time = datetime.now()

        try:
            claim_context = input_data.get('claim_context', {})
            phase1_signals = input_data.get('phase1_signals', [])
            phase2_signals = input_data.get('phase2_signals', [])
            damage_details = input_data.get('damage_details', [])

            logger.info(f"Behavioral pattern analysis for claim {claim_context.get('claim', {}).get('claim_id')}")

            # Build comprehensive analysis prompt
            system_prompt = """You are an insurance fraud investigation specialist with expertise in behavioral pattern analysis.

Your task is to analyze claim details, damage patterns, and all available signals to detect behavioral indicators of fraud.

Focus on these key areas:

1. DAMAGE COHERENCE
   - Does the damage pattern match the incident description?
   - Are the damage locations physically plausible?
   - Is the severity consistent with the story?

2. STORY CONSISTENCY
   - Are there contradictions in the claim narrative?
   - Does the timeline make sense?
   - Are the claim details internally consistent?

3. LOCATION REASONABLENESS
   - Is the damage on the correct side of the vehicle for the described incident?
   - Do the damage patterns follow physics (impact direction, force distribution)?
   - Are there missing damages that should be present?

4. BEHAVIORAL RED FLAGS
   - NOTE: Brief or simple incident descriptions are ACCEPTABLE and NOT suspicious
   - Only flag descriptions if they contain clear contradictions or impossible scenarios
   - Unusual timing (claim filed immediately or with suspicious delay)
   - Inconsistencies with vehicle/policy records
   - Pattern of claims (if claim history available)

Be analytical and thorough. Identify specific inconsistencies or suspicious patterns. Remember: Most customers are not professional writers - focus on factual inconsistencies, not writing quality."""

            user_prompt = self._build_analysis_prompt(claim_context, phase1_signals, phase2_signals, damage_details)

            messages = [Message(role='user', content=user_prompt)]

            # Call LLM for behavioral analysis
            response = self.llm_client.chat(
                system=system_prompt,
                messages=messages,
                temperature=0.2,
                max_tokens=2048
            )

            # Parse response
            analysis = self._parse_behavioral_response(response.content)

            # Calculate severity based on findings
            severity = self._calculate_severity(analysis)

            description = self._build_description(analysis, severity)

            execution_time_ms = self._measure_execution_time(start_time)

            result_data = {
                'signal_type': 'behavioral_pattern',
                'severity': severity,
                'description': description,
                'evidence': build_evidence_dict(
                    phase='phase3',
                    agent_name='BehaviorPatternAgent',
                    signal_type='behavioral_pattern',
                    severity=severity,
                    description=description,
                    details={
                        'damage_coherence': analysis.get('damage_coherence', {}),
                        'story_consistency': analysis.get('story_consistency', {}),
                        'location_reasonableness': analysis.get('location_reasonableness', {}),
                        'behavioral_flags': analysis.get('behavioral_flags', []),
                        'overall_assessment': analysis.get('overall_assessment', ''),
                        'raw_analysis': response.content
                    }
                )
            }

            logger.info(f"Behavioral analysis completed: severity={severity:.2f}")

            return self._create_result(
                success=True,
                data=result_data,
                execution_time_ms=execution_time_ms,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens
            )

        except Exception as e:
            logger.error(f"Behavioral pattern analysis failed: {e}", exc_info=True)
            return self._create_result(
                success=False,
                data={
                    'signal_type': 'behavioral_pattern',
                    'severity': 0.0,
                    'description': f'Behavioral analysis failed: {str(e)}'
                },
                error=str(e)
            )

    def _build_analysis_prompt(self, claim_context: Dict, phase1: List, phase2: List, damages: List) -> str:
        """Build comprehensive analysis prompt with all available data"""

        claim = claim_context.get('claim', {})
        vehicle = claim_context.get('vehicle', {})
        customer = claim_context.get('customer', {})

        # Format Phase 1 signals
        phase1_summary = self._format_signals(phase1)
        phase2_summary = self._format_signals(phase2)

        # Format damages
        damages_summary = ""
        if damages:
            damages_summary = "\n".join([
                f"  - {d.get('damage_part', 'Unknown')}: {d.get('severity', 0):.2f} severity, {d.get('recommended_action', 'unknown')} recommended"
                for d in damages[:10]  # Limit to 10
            ])
        else:
            damages_summary = "  No damage details available"

        claim_amount = claim.get('claim_amount')
        claim_amount_str = f"${claim_amount:.2f}" if claim_amount is not None else "Not yet estimated"

        prompt = f"""Analyze this insurance claim for behavioral fraud patterns.

CLAIM DETAILS:
- Claim ID: {claim.get('claim_id')}
- Date of Damage: {claim.get('date_of_damage')}
- FNOL Date: {claim.get('fnol_date')}
- Vehicle Drivable: {claim.get('is_drivable')}
- Incident Description: "{claim.get('incident_description', 'Not provided')}"
- Estimated Amount: {claim_amount_str}

VEHICLE INFORMATION:
- {vehicle.get('year')} {vehicle.get('make')} {vehicle.get('model')}
- Color: {vehicle.get('color')}
- VIN: {vehicle.get('vin')}

CUSTOMER HISTORY:
- Total Claims: {customer.get('claim_history_count', 0)}
- Recent Claims: {len(customer.get('recent_claims', []))} in history

DAMAGE ASSESSMENT:
{damages_summary}

PHASE 1 VISION SIGNALS:
{phase1_summary}

PHASE 2 STATIC CHECKS:
{phase2_summary}

IMPORTANT GUIDELINES:
- Brief or simple incident descriptions are NORMAL and ACCEPTABLE (e.g., "rear-ended", "hit parked car")
- DO NOT penalize for lack of detail in descriptions - most legitimate claims are brief
- Only flag narrative issues if there are FACTUAL CONTRADICTIONS or IMPOSSIBLE scenarios
- Focus on objective inconsistencies, not writing quality or level of detail

ANALYSIS REQUIRED:

1. DAMAGE COHERENCE
   - Does the damage pattern match the incident description?
   - Are damage locations physically plausible?
   - Score: [0.0-1.0, where 1.0 = highly suspicious]

2. STORY CONSISTENCY
   - Are there FACTUAL contradictions or inconsistencies?
   - Does the timeline make sense?
   - NOTE: Simple/brief descriptions are NOT inconsistencies
   - Score: [0.0-1.0, where 1.0 = highly suspicious]

3. LOCATION REASONABLENESS
   - Is damage on correct vehicle side for the incident?
   - Do patterns follow physics?
   - Score: [0.0-1.0, where 1.0 = highly suspicious]

4. BEHAVIORAL RED FLAGS
   - List ONLY suspicious behavioral patterns with factual basis
   - DO NOT flag: brief descriptions, simple language, or lack of detail

5. OVERALL ASSESSMENT
   - Synthesize all findings
   - Provide fraud probability: [0.0-1.0]

Respond in JSON format:
{{
  "damage_coherence": {{"score": 0.0-1.0, "reasoning": "..."}},
  "story_consistency": {{"score": 0.0-1.0, "reasoning": "..."}},
  "location_reasonableness": {{"score": 0.0-1.0, "reasoning": "..."}},
  "behavioral_flags": ["flag1", "flag2", ...],
  "fraud_probability": 0.0-1.0,
  "overall_assessment": "Detailed explanation..."
}}"""

        return prompt

    def _format_signals(self, signals: List[Dict]) -> str:
        """Format signals for prompt"""
        if not signals:
            return "  None"

        formatted = []
        for sig in signals:
            signal_type = sig.get('signal_type', 'unknown')
            severity = sig.get('severity', 0.0)
            description = sig.get('description', '')
            formatted.append(f"  - {signal_type}: severity={severity:.2f} - {description}")

        return "\n".join(formatted)

    def _parse_behavioral_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response from LLM"""
        try:
            # Try to extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1

            if start_idx >= 0 and end_idx > start_idx:
                json_text = response_text[start_idx:end_idx]
                return json.loads(json_text)
            else:
                logger.warning("Could not find JSON in behavioral analysis response")
                return self._parse_fallback(response_text)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse behavioral analysis JSON: {e}")
            return self._parse_fallback(response_text)

    def _parse_fallback(self, response_text: str) -> Dict[str, Any]:
        """Fallback parsing if JSON fails"""
        return {
            'damage_coherence': {'score': 0.5, 'reasoning': 'Could not parse structured response'},
            'story_consistency': {'score': 0.5, 'reasoning': 'Could not parse structured response'},
            'location_reasonableness': {'score': 0.5, 'reasoning': 'Could not parse structured response'},
            'behavioral_flags': [],
            'fraud_probability': 0.5,
            'overall_assessment': response_text[:500]  # First 500 chars
        }

    def _calculate_severity(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall severity from behavioral analysis"""
        # Use fraud_probability if available
        fraud_prob = analysis.get('fraud_probability', 0.5)

        # Also average the individual scores
        damage_score = analysis.get('damage_coherence', {}).get('score', 0.0)
        story_score = analysis.get('story_consistency', {}).get('score', 0.0)
        location_score = analysis.get('location_reasonableness', {}).get('score', 0.0)

        avg_score = (damage_score + story_score + location_score) / 3

        # Weight fraud_probability higher (60%) vs individual scores (40%)
        overall = (fraud_prob * 0.6) + (avg_score * 0.4)

        return min(1.0, overall)

    def _build_description(self, analysis: Dict[str, Any], severity: float) -> str:
        """Build human-readable description"""
        flags = analysis.get('behavioral_flags', [])
        assessment = analysis.get('overall_assessment', '')

        if severity < 0.3:
            return f"Behavioral analysis shows low fraud risk. {assessment[:200]}"
        elif severity < 0.6:
            return f"Behavioral analysis shows moderate concerns. Flags: {', '.join(flags[:3])}. {assessment[:200]}"
        else:
            return f"Behavioral analysis shows HIGH fraud risk. Critical flags: {', '.join(flags[:3])}. {assessment[:200]}"
