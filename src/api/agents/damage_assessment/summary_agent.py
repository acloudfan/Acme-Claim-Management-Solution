"""
Damage Assessment Agent
Analyzes damage images and provides structured assessment using vision LLM.
"""
import logging
import json
from typing import Dict, Any
from datetime import datetime

from ..base_agent import BaseAgent, AgentResult
from ..llm.base import BaseLLMClient, Message

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert auto claim adjustor.

You receive damage assessment report from the field.

The damage assessment report consists of 2 parts:
1. A list of damages along with the confidence score assigned to each damage
   Example: [{'id': 1, 'class': 10, 'confidence': 0.52}]
2. Image of the damage with each damage enclosed in a bounding box

Your task is to analyze the provided image and return a structured JSON response that strictly follows the given schema.

Field guidance:
For each damage, you will add the following information:
- damage_summary: Overall summary of the damage in 2-3 sentences (customer-friendly, plain English)
- internal_damage_probability: Score between 0 and 1. Higher score indicates high chance of internal damage (e.g., exposed engine with visible dent has high chance)
- severity: How bad is the damage, score between 0 and 1. 1 means very labor intensive
- recommended_action: categorical - repaint | de-dent | replace | de-dent-and-paint
- reasoning: Assessment report explaining the damage and why you recommended the action
- car_side: categorical - front | back | passenger_side | driver_side
- damage_assessment_confidence: How confident are you with your reasoning, score between 0 and 1

Example output format:
{
  "damage_summary": "The trunk lid shows significant denting with visible creasing...",
  "assessment": {
    "internal_damage_probability": 0.7,
    "severity": 0.8,
    "recommended_action": "de-dent-and-paint",
    "reasoning": "The trunk lid shows significant denting with visible creasing and deformation...",
    "car_side": "back",
    "damage_assessment_confidence": 0.9
  }
}

CRITICAL RULES:
- Your response MUST be ONLY the JSON object - nothing else
- Do NOT use markdown formatting
- Do NOT use code blocks or ```json fences
- Do NOT add any text before or after the JSON
- The first character must be { and the last character must be }
- Output pure, raw JSON that can be parsed directly

Additional rules:
- Do NOT include fields outside the schema
- Use conservative judgment: if uncertain, prefer lower severity
- Base conclusions ONLY on visible evidence in the image
"""


class DamageSummaryAgent(BaseAgent):
    """
    Damage Assessment Agent - analyzes damage and provides structured assessment.

    Uses vision LLM to analyze damage images and provide detailed assessment
    including severity, internal damage probability, and recommended actions.
    """

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute damage assessment.

        Args:
            input_data: Dict with:
                - damage: Dict - Damage object from YOLO detection
                - image_path: str - Path to damage image
                - vehicle_info: Dict - Vehicle context (make, model, year, color)

        Returns:
            AgentResult with structured assessment data
        """
        start_time = datetime.now()
        damage = input_data.get('damage', {})
        image_path = input_data.get('image_path')
        vehicle_info = input_data.get('vehicle_info', {})

        damage_part = damage.get('damage_part', 'unknown part')
        damage_class = damage.get('damage_class', 0)
        yolo_confidence = damage.get('confidence', 0)

        logger.info(f"Analyzing damage: {damage_part} (YOLO confidence: {yolo_confidence})")

        try:
            if not image_path:
                logger.warning(f"No image available for damage {damage_part}")
                return self._create_fallback_result(damage)

            # Build user prompt with damage context
            user_prompt = self._build_user_prompt(damage, vehicle_info)

            # Read image file as bytes
            with open(image_path, 'rb') as f:
                image_bytes = f.read()

            # Determine image format
            image_format = 'image/jpeg'
            if image_path.lower().endswith('.png'):
                image_format = 'image/png'

            # Build messages list
            messages = [Message(role='user', content=user_prompt)]

            # Call vision LLM with correct API (returns ChatResponse object)
            llm_response = self.llm_client.chat_with_image(
                system=SYSTEM_PROMPT,
                messages=messages,
                image_data=image_bytes,
                image_format=image_format,
                temperature=0.3,
                max_tokens=500
            )

            # Extract response data from ChatResponse object
            response_text = llm_response.content.strip()
            input_tokens = llm_response.input_tokens
            output_tokens = llm_response.output_tokens

            # Clean up response - remove markdown code fences if present
            # LLM sometimes ignores instructions and wraps JSON in ```json ... ```
            if response_text.startswith('```'):
                # Find the actual JSON content between code fences
                lines = response_text.split('\n')
                # Remove first line (```json or ```)
                if lines[0].strip().startswith('```'):
                    lines = lines[1:]
                # Remove last line if it's closing fence
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                response_text = '\n'.join(lines).strip()

            # Parse JSON response
            try:
                assessment_data = json.loads(response_text)

                # Validate structure
                if 'damage_summary' not in assessment_data or 'assessment' not in assessment_data:
                    logger.error(f"Invalid response structure: {response_text}")
                    return self._create_fallback_result(damage)

                damage_summary = assessment_data['damage_summary']
                assessment = assessment_data['assessment']

                # Extract fields with defaults
                result_data = {
                    'damage_summary': damage_summary,
                    'internal_damage_probability': float(assessment.get('internal_damage_probability', 0.5)),
                    'severity': float(assessment.get('severity', 0.5)),
                    'recommended_action': assessment.get('recommended_action', 'assess'),
                    'reasoning': assessment.get('reasoning', ''),
                    'car_side': assessment.get('car_side', 'unknown'),
                    'assessment_confidence': float(assessment.get('damage_assessment_confidence', 0.8)),
                    'input_tokens': input_tokens,
                    'output_tokens': output_tokens
                }

                execution_time_ms = self._measure_execution_time(start_time)

                logger.info(
                    f"Assessment completed for {damage_part}: "
                    f"severity={result_data['severity']:.2f}, "
                    f"internal_prob={result_data['internal_damage_probability']:.2f}, "
                    f"action={result_data['recommended_action']}"
                )

                return self._create_result(
                    success=True,
                    data=result_data,
                    execution_time_ms=execution_time_ms,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens
                )

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM JSON response: {e}, response: {response_text}")
                return self._create_fallback_result(damage)

        except Exception as e:
            logger.error(f"Failed to assess damage {damage_part}: {e}", exc_info=True)
            # Return fallback instead of empty data to prevent None values
            return self._create_fallback_result(damage)

    def _build_user_prompt(self, damage: Dict, vehicle_info: Dict) -> str:
        """
        Build user prompt with damage and vehicle context.

        Args:
            damage: Damage dictionary from YOLO
            vehicle_info: Vehicle information

        Returns:
            Formatted prompt string
        """
        year = vehicle_info.get('year', 'Unknown')
        make = vehicle_info.get('make', 'Unknown')
        model = vehicle_info.get('model', 'Unknown')
        color = vehicle_info.get('color', 'Unknown')

        damage_part = damage.get('damage_part', 'unknown part')
        damage_class = damage.get('damage_class', 0)
        yolo_confidence = damage.get('confidence', 0)

        prompt = f"""Vehicle: {year} {make} {model} ({color})

Damage detected by AI:
- ID: {damage.get('damage_id', 'unknown')}
- Part: {damage_part}
- Class: {damage_class}
- YOLO Confidence: {yolo_confidence:.2f}

Analyze the image showing this damage and provide your expert assessment.

IMPORTANT: Return ONLY the JSON object. Your response should start with {{ and end with }}. Do NOT wrap it in markdown code blocks.

Example of correct response format:
{{"damage_summary":"The trunk shows moderate denting...","assessment":{{"internal_damage_probability":0.5,"severity":0.6,"recommended_action":"de-dent-and-paint","reasoning":"The damage requires...","car_side":"back","damage_assessment_confidence":0.8}}}}

Now provide your assessment following the exact same format (pure JSON only):"""

        return prompt

    def _create_fallback_result(self, damage: Dict) -> AgentResult:
        """
        Create fallback result when LLM call fails or no image available.

        Args:
            damage: Damage dictionary

        Returns:
            AgentResult with fallback assessment
        """
        damage_part = damage.get('damage_part', 'unknown part')

        # Use heuristic values from YOLO detection if available
        severity = damage.get('severity', 0.5)
        recommended_action = damage.get('recommended_action', 'assess')

        fallback_data = {
            'damage_summary': f"Damage detected on {damage_part}. Professional assessment recommended.",
            'internal_damage_probability': 0.5,
            'severity': severity,
            'recommended_action': recommended_action,
            'reasoning': f"Using heuristic assessment for {damage_part}. Visual inspection recommended.",
            'car_side': 'unknown',
            'assessment_confidence': 0.5,
            'input_tokens': 0,
            'output_tokens': 0
        }

        logger.info(f"Using fallback assessment for {damage_part}")

        return self._create_result(
            success=True,
            data=fallback_data,
            execution_time_ms=0
        )
