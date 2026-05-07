"""
Color Verification Agent - Phase 1 Vision Agent
Verifies that vehicle color in images matches policy records.
"""
import logging
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseAgent, AgentResult
from ..llm.base import BaseLLMClient, Message
from .utils import build_evidence_dict

logger = logging.getLogger(__name__)


class ColorVerificationAgent(BaseAgent):
    """
    Vision agent that verifies vehicle color matches policy records.

    Uses Vision LLM to:
    1. Identify vehicle color in uploaded images
    2. Compare against policy records
    3. Flag mismatches as potential fraud signals
    """

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute color verification.

        Args:
            input_data: Dict with:
                - images: List of dicts with image_id, image_bytes
                - expected_color: str - Color from policy records
                - vehicle_info: dict - Year, make, model

        Returns:
            AgentResult with color verification results
        """
        start_time = datetime.now()

        try:
            images = input_data['images']
            expected_color = input_data.get('expected_color', 'unknown')
            vehicle_info = input_data.get('vehicle_info', {})

            logger.info(f"Color verification: Expected={expected_color}, Images={len(images)}")

            if not images:
                return self._create_result(
                    success=True,
                    data={
                        'signal_type': 'color_verification',
                        'severity': 0.0,
                        'description': 'No images to analyze',
                        'evidence': build_evidence_dict(
                            phase='phase1',
                            agent_name='ColorVerificationAgent',
                            signal_type='color_verification',
                            severity=0.0,
                            description='No images provided for color verification',
                            details={'expected_color': expected_color}
                        )
                    }
                )

            # Analyze first few images (limit to 3 for efficiency)
            analysis_images = images[:3]
            color_results = []
            total_input_tokens = 0
            total_output_tokens = 0

            for img in analysis_images:
                # Build prompt
                system_prompt = """You are a vehicle color verification specialist for insurance fraud detection.

Your task:
1. Identify the PRIMARY color of the vehicle in the image
2. Compare it to the expected color from policy records
3. Report if there is a mismatch (potential fraud indicator)

Important:
- Focus on the MAIN body color, ignore trim or accent colors
- Account for lighting variations (bright sun, shade, etc.)
- Minor shade differences (e.g., "dark blue" vs "navy blue") are NOT mismatches
- Only flag CLEAR color differences (e.g., "red" vs "blue")
- Be conservative - only flag obvious mismatches"""

                user_prompt = f"""Analyze this vehicle image.

Expected color from policy: {expected_color}
Vehicle: {vehicle_info.get('year', 'Unknown')} {vehicle_info.get('make', 'Unknown')} {vehicle_info.get('model', 'Unknown')}

Questions:
1. What is the PRIMARY body color of the vehicle in this image?
2. Does it match the expected color "{expected_color}"?
3. If there is a mismatch, how significant is it? (minor shade difference vs completely different color)

Respond in this format:
DETECTED_COLOR: [color you see]
MATCHES_EXPECTED: [yes/no]
CONFIDENCE: [0.0-1.0]
MISMATCH_SEVERITY: [0.0-1.0, where 1.0 = completely different color]
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
                    max_tokens=500
                )

                total_input_tokens += response.input_tokens
                total_output_tokens += response.output_tokens

                # Parse response
                parsed = self._parse_response(response.content)
                color_results.append({
                    'image_id': img['image_id'],
                    'detected_color': parsed.get('detected_color', 'unknown'),
                    'matches': parsed.get('matches', True),
                    'confidence': parsed.get('confidence', 0.0),
                    'mismatch_severity': parsed.get('mismatch_severity', 0.0),
                    'reasoning': parsed.get('reasoning', ''),
                    'raw_response': response.content
                })

            # Aggregate results
            mismatch_count = sum(1 for r in color_results if not r['matches'])
            avg_mismatch_severity = sum(r['mismatch_severity'] for r in color_results) / len(color_results)

            # Calculate overall severity
            # If majority of images show mismatch, it's more severe
            overall_severity = avg_mismatch_severity * (mismatch_count / len(color_results))

            description = self._build_description(expected_color, color_results, overall_severity)

            execution_time_ms = self._measure_execution_time(start_time)

            result_data = {
                'signal_type': 'color_verification',
                'severity': overall_severity,
                'description': description,
                'evidence': build_evidence_dict(
                    phase='phase1',
                    agent_name='ColorVerificationAgent',
                    signal_type='color_verification',
                    severity=overall_severity,
                    description=description,
                    details={
                        'expected_color': expected_color,
                        'images_analyzed': len(color_results),
                        'mismatch_count': mismatch_count,
                        'color_results': color_results
                    }
                )
            }

            logger.info(f"Color verification completed: severity={overall_severity:.2f}, mismatches={mismatch_count}/{len(color_results)}")

            return self._create_result(
                success=True,
                data=result_data,
                execution_time_ms=execution_time_ms,
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens
            )

        except Exception as e:
            logger.error(f"Color verification failed: {e}", exc_info=True)
            return self._create_result(
                success=False,
                data={
                    'signal_type': 'color_verification',
                    'severity': 0.0,
                    'description': f'Color verification failed: {str(e)}'
                },
                error=str(e)
            )

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse structured response from LLM"""
        result = {
            'detected_color': 'unknown',
            'matches': True,
            'confidence': 0.0,
            'mismatch_severity': 0.0,
            'reasoning': ''
        }

        lines = response_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('DETECTED_COLOR:'):
                result['detected_color'] = line.split(':', 1)[1].strip()
            elif line.startswith('MATCHES_EXPECTED:'):
                matches_text = line.split(':', 1)[1].strip().lower()
                result['matches'] = 'yes' in matches_text
            elif line.startswith('CONFIDENCE:'):
                try:
                    result['confidence'] = float(line.split(':', 1)[1].strip())
                except ValueError:
                    pass
            elif line.startswith('MISMATCH_SEVERITY:'):
                try:
                    result['mismatch_severity'] = float(line.split(':', 1)[1].strip())
                except ValueError:
                    pass
            elif line.startswith('REASONING:'):
                result['reasoning'] = line.split(':', 1)[1].strip()

        return result

    def _build_description(self, expected: str, results: List[Dict], severity: float) -> str:
        """Build human-readable description"""
        mismatch_count = sum(1 for r in results if not r['matches'])

        if severity == 0.0:
            return f"Vehicle color matches expected: {expected}"
        elif severity < 0.3:
            return f"Minor color inconsistencies detected. Expected {expected}, but {mismatch_count}/{len(results)} images show slight differences."
        elif severity < 0.7:
            return f"Moderate color mismatch detected. Expected {expected}, but {mismatch_count}/{len(results)} images show different colors."
        else:
            colors_detected = [r['detected_color'] for r in results if not r['matches']]
            return f"Significant color mismatch detected. Expected {expected}, but images show {', '.join(colors_detected)}."
