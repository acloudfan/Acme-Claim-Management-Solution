"""
AI-Generated Image Detector Agent - Phase 1 Vision Agent
Detects AI-generated or synthetic images (deepfakes).
"""
import logging
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseAgent, AgentResult
from ..llm.base import BaseLLMClient, Message
from .utils import build_evidence_dict

logger = logging.getLogger(__name__)


class AIGeneratedDetectorAgent(BaseAgent):
    """
    Vision agent that detects AI-generated or synthetic images.

    Uses Vision LLM to:
    1. Analyze images for signs of AI generation (artifacts, inconsistencies)
    2. Detect deepfake indicators
    3. Flag suspicious images as potential fraud
    """

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute AI-generated image detection.

        Args:
            input_data: Dict with:
                - images: List of dicts with image_id, image_bytes

        Returns:
            AgentResult with AI-generated detection results
        """
        start_time = datetime.now()

        try:
            images = input_data['images']

            logger.info(f"AI-generated detection: Analyzing {len(images)} images")

            if not images:
                return self._create_result(
                    success=True,
                    data={
                        'signal_type': 'ai_generated',
                        'severity': 0.0,
                        'description': 'No images to analyze',
                        'evidence': build_evidence_dict(
                            phase='phase1',
                            agent_name='AIGeneratedDetectorAgent',
                            signal_type='ai_generated',
                            severity=0.0,
                            description='No images provided for AI-generated detection',
                            details={}
                        )
                    }
                )

            # Analyze all images (or limit to first 5 for efficiency)
            analysis_images = images[:5]
            detection_results = []
            total_input_tokens = 0
            total_output_tokens = 0

            for img in analysis_images:
                system_prompt = """You are an AI-generated image detection specialist for insurance fraud detection.

Your task:
1. Analyze the image for signs of AI generation or manipulation
2. Look for common AI artifacts and inconsistencies
3. Assess the probability that this image is synthetic or AI-generated

Common AI generation indicators:
- Unusual patterns in reflections or shadows
- Inconsistent lighting across the scene
- Unnatural textures or repeating patterns
- Distorted or impossible geometry
- Blurred or inconsistent details (especially in backgrounds)
- Artifacts around edges or in fine details
- Unrealistic physics or perspectives
- "Too perfect" or overly smooth surfaces

Important:
- Real photos can have compression artifacts - don't confuse these with AI generation
- Be conservative - only flag if you see multiple strong indicators
- Consider that genuine accident photos may look chaotic or poorly composed"""

                user_prompt = """Analyze this vehicle damage image for signs of AI generation or synthesis.

Questions:
1. Does this image show signs of being AI-generated or synthetic?
2. What specific indicators do you observe (if any)?
3. How confident are you in this assessment?
4. What is the probability this is AI-generated vs a genuine photo?

Respond in this format:
AI_GENERATED: [yes/no/unsure]
PROBABILITY_AI: [0.0-1.0, where 1.0 = definitely AI-generated]
CONFIDENCE: [0.0-1.0]
INDICATORS: [list specific signs you observed, or "none"]
REASONING: [brief explanation]"""

                messages = [Message(role='user', content=user_prompt)]

                # Determine image format
                image_format = 'image/jpeg'
                if img['image_id'].lower().endswith('.png'):
                    image_format = 'image/png'

                # Call vision LLM
                response = self.llm_client.chat_with_image(
                    system=system_prompt,
                    messages=messages,
                    image_data=img['image_bytes'],
                    image_format=image_format,
                    temperature=0.1,
                    max_tokens=700
                )

                total_input_tokens += response.input_tokens
                total_output_tokens += response.output_tokens

                # Parse response
                parsed = self._parse_response(response.content)
                detection_results.append({
                    'image_id': img['image_id'],
                    'ai_generated': parsed.get('ai_generated', False),
                    'probability': parsed.get('probability', 0.0),
                    'confidence': parsed.get('confidence', 0.0),
                    'indicators': parsed.get('indicators', ''),
                    'reasoning': parsed.get('reasoning', ''),
                    'raw_response': response.content
                })

            # Aggregate results
            suspicious_count = sum(1 for r in detection_results if r['ai_generated'])
            avg_probability = sum(r['probability'] for r in detection_results) / len(detection_results)
            max_probability = max(r['probability'] for r in detection_results)

            # Calculate overall severity
            # High severity if multiple images are suspicious or if any single image has very high probability
            overall_severity = max(avg_probability, max_probability * 0.8)

            description = self._build_description(detection_results, overall_severity, suspicious_count)

            execution_time_ms = self._measure_execution_time(start_time)

            result_data = {
                'signal_type': 'ai_generated',
                'severity': overall_severity,
                'description': description,
                'evidence': build_evidence_dict(
                    phase='phase1',
                    agent_name='AIGeneratedDetectorAgent',
                    signal_type='ai_generated',
                    severity=overall_severity,
                    description=description,
                    details={
                        'images_analyzed': len(detection_results),
                        'suspicious_count': suspicious_count,
                        'avg_probability': avg_probability,
                        'max_probability': max_probability,
                        'detection_results': detection_results
                    }
                )
            }

            logger.info(f"AI-generated detection completed: severity={overall_severity:.2f}, suspicious={suspicious_count}/{len(detection_results)}")

            return self._create_result(
                success=True,
                data=result_data,
                execution_time_ms=execution_time_ms,
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens
            )

        except Exception as e:
            logger.error(f"AI-generated detection failed: {e}", exc_info=True)
            return self._create_result(
                success=False,
                data={
                    'signal_type': 'ai_generated',
                    'severity': 0.0,
                    'description': f'AI-generated detection failed: {str(e)}'
                },
                error=str(e)
            )

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse structured response from LLM"""
        result = {
            'ai_generated': False,
            'probability': 0.0,
            'confidence': 0.0,
            'indicators': '',
            'reasoning': ''
        }

        lines = response_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('AI_GENERATED:'):
                ai_text = line.split(':', 1)[1].strip().lower()
                result['ai_generated'] = 'yes' in ai_text
            elif line.startswith('PROBABILITY_AI:'):
                try:
                    result['probability'] = float(line.split(':', 1)[1].strip())
                except ValueError:
                    pass
            elif line.startswith('CONFIDENCE:'):
                try:
                    result['confidence'] = float(line.split(':', 1)[1].strip())
                except ValueError:
                    pass
            elif line.startswith('INDICATORS:'):
                result['indicators'] = line.split(':', 1)[1].strip()
            elif line.startswith('REASONING:'):
                result['reasoning'] = line.split(':', 1)[1].strip()

        return result

    def _build_description(self, results: List[Dict], severity: float, suspicious_count: int) -> str:
        """Build human-readable description"""
        if severity == 0.0:
            return "No signs of AI-generated images detected. All images appear to be genuine photos."
        elif severity < 0.3:
            return f"Low probability of AI generation. {suspicious_count}/{len(results)} images show minor artifacts, likely compression or camera artifacts."
        elif severity < 0.6:
            indicators = []
            for r in results:
                if r['ai_generated'] and r['indicators']:
                    indicators.append(r['indicators'])
            return f"Moderate probability of AI generation detected in {suspicious_count}/{len(results)} images. Indicators: {'; '.join(indicators[:2])}"
        else:
            return f"HIGH probability of AI-generated images detected. {suspicious_count}/{len(results)} images show strong signs of synthetic generation or deepfake artifacts."
