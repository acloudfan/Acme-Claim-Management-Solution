"""
Make/Model Verification Agent - Phase 1 Vision Agent
Verifies that vehicle make/model in images matches policy records.
"""
import logging
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseAgent, AgentResult
from ..llm.base import BaseLLMClient, Message
from .utils import build_evidence_dict

logger = logging.getLogger(__name__)


class MakeModelVerificationAgent(BaseAgent):
    """
    Vision agent that verifies vehicle make/model matches policy records.

    Uses Vision LLM to:
    1. Identify vehicle make, model, and approximate year
    2. Compare against policy records
    3. Flag mismatches as potential fraud signals
    """

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute make/model verification.

        Args:
            input_data: Dict with:
                - images: List of dicts with image_id, image_bytes
                - expected_make: str
                - expected_model: str
                - expected_year: int

        Returns:
            AgentResult with make/model verification results
        """
        start_time = datetime.now()

        try:
            images = input_data['images']
            expected_make = input_data.get('expected_make', 'unknown')
            expected_model = input_data.get('expected_model', 'unknown')
            expected_year = input_data.get('expected_year', 0)

            logger.info(f"Make/model verification: Expected={expected_year} {expected_make} {expected_model}, Images={len(images)}")

            if not images:
                return self._create_result(
                    success=True,
                    data={
                        'signal_type': 'make_model_verification',
                        'severity': 0.0,
                        'description': 'No images to analyze',
                        'evidence': build_evidence_dict(
                            phase='phase1',
                            agent_name='MakeModelVerificationAgent',
                            signal_type='make_model_verification',
                            severity=0.0,
                            description='No images provided for make/model verification',
                            details={'expected': f"{expected_year} {expected_make} {expected_model}"}
                        )
                    }
                )

            # Analyze first few clear vehicle images (limit to 3)
            analysis_images = images[:3]
            verification_results = []
            total_input_tokens = 0
            total_output_tokens = 0

            for img in analysis_images:
                system_prompt = """You are a vehicle identification specialist for insurance fraud detection.

Your task:
1. Identify the vehicle make (manufacturer), model, and approximate year/generation
2. Compare ONLY THE MAKE (manufacturer) to the expected vehicle from policy records
3. Report make mismatches as potential fraud signals

IMPORTANT RULES:
- ONLY flag fraud if the MAKE (manufacturer) is different (e.g., Honda vs Toyota, BMW vs Mercedes)
- Model differences within the same make are ACCEPTABLE (e.g., BMW 3 Series vs BMW X5 is OK)
- Model year variations are ACCEPTABLE (e.g., 2015 vs 2018 is OK)
- Use visible design cues, badges, grilles, logos to identify the manufacturer
- Only flag CLEAR make mismatches (completely different manufacturer)
- If the image doesn't show enough detail, indicate low confidence"""

                user_prompt = f"""Analyze this vehicle image.

Expected vehicle from policy:
- Year: {expected_year}
- Make: {expected_make}
- Model: {expected_model}

Questions:
1. What vehicle make (manufacturer) do you see?
2. What model is this? (for reference only - model mismatch is NOT fraud)
3. What approximate year or generation? (for reference only - year mismatch is NOT fraud)
4. Does the MAKE match the expected make? (THIS IS THE ONLY FRAUD CHECK)
5. If make mismatch, how significant is it?

CRITICAL: Only set MATCHES_EXPECTED=no if the MAKE (manufacturer) is different. Model and year differences should NOT trigger fraud.

Respond in this format:
DETECTED_MAKE: [make you see]
DETECTED_MODEL: [model you see - for reference only]
DETECTED_YEAR: [approximate year or "unknown" - for reference only]
MATCHES_EXPECTED: [yes/no/unsure - based ONLY on make comparison]
CONFIDENCE: [0.0-1.0]
MISMATCH_SEVERITY: [0.0-1.0, where 1.0 = completely different manufacturer, 0.0 = same make]
REASONING: [brief explanation focusing on make identification]"""

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
                    max_tokens=600
                )

                total_input_tokens += response.input_tokens
                total_output_tokens += response.output_tokens

                # Parse response
                parsed = self._parse_response(response.content)
                verification_results.append({
                    'image_id': img['image_id'],
                    'detected_make': parsed.get('detected_make', 'unknown'),
                    'detected_model': parsed.get('detected_model', 'unknown'),
                    'detected_year': parsed.get('detected_year', 'unknown'),
                    'matches': parsed.get('matches', True),
                    'confidence': parsed.get('confidence', 0.0),
                    'mismatch_severity': parsed.get('mismatch_severity', 0.0),
                    'reasoning': parsed.get('reasoning', ''),
                    'raw_response': response.content
                })

            # Aggregate results
            mismatch_count = sum(1 for r in verification_results if not r['matches'])
            avg_mismatch_severity = sum(r['mismatch_severity'] for r in verification_results) / len(verification_results)

            # Calculate overall severity
            overall_severity = avg_mismatch_severity * (mismatch_count / len(verification_results))

            description = self._build_description(expected_year, expected_make, expected_model,
                                                  verification_results, overall_severity)

            execution_time_ms = self._measure_execution_time(start_time)

            result_data = {
                'signal_type': 'make_model_verification',
                'severity': overall_severity,
                'description': description,
                'evidence': build_evidence_dict(
                    phase='phase1',
                    agent_name='MakeModelVerificationAgent',
                    signal_type='make_model_verification',
                    severity=overall_severity,
                    description=description,
                    details={
                        'expected_make': expected_make,
                        'expected_model': expected_model,
                        'expected_year': expected_year,
                        'images_analyzed': len(verification_results),
                        'mismatch_count': mismatch_count,
                        'verification_results': verification_results
                    }
                )
            }

            logger.info(f"Make/model verification completed: severity={overall_severity:.2f}, mismatches={mismatch_count}/{len(verification_results)}")

            return self._create_result(
                success=True,
                data=result_data,
                execution_time_ms=execution_time_ms,
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens
            )

        except Exception as e:
            logger.error(f"Make/model verification failed: {e}", exc_info=True)
            return self._create_result(
                success=False,
                data={
                    'signal_type': 'make_model_verification',
                    'severity': 0.0,
                    'description': f'Make/model verification failed: {str(e)}'
                },
                error=str(e)
            )

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse structured response from LLM"""
        result = {
            'detected_make': 'unknown',
            'detected_model': 'unknown',
            'detected_year': 'unknown',
            'matches': True,
            'confidence': 0.0,
            'mismatch_severity': 0.0,
            'reasoning': ''
        }

        lines = response_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('DETECTED_MAKE:'):
                result['detected_make'] = line.split(':', 1)[1].strip()
            elif line.startswith('DETECTED_MODEL:'):
                result['detected_model'] = line.split(':', 1)[1].strip()
            elif line.startswith('DETECTED_YEAR:'):
                result['detected_year'] = line.split(':', 1)[1].strip()
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

    def _build_description(self, exp_year: int, exp_make: str, exp_model: str,
                          results: List[Dict], severity: float) -> str:
        """Build human-readable description"""
        mismatch_count = sum(1 for r in results if not r['matches'])

        if severity == 0.0:
            return f"Vehicle make matches expected: {exp_make}. Model/year variations are acceptable."
        elif severity < 0.3:
            return f"Minor inconsistencies in make identification. Expected {exp_make}, verification inconclusive."
        elif severity < 0.7:
            detected = [r['detected_make'] for r in results if not r['matches']]
            return f"Moderate make mismatch. Expected {exp_make}, but {mismatch_count}/{len(results)} images show possible different manufacturer: {', '.join(detected[:2])}"
        else:
            detected = [r['detected_make'] for r in results if not r['matches']]
            return f"Significant make mismatch detected. Expected {exp_make}, but images show different manufacturer: {', '.join(detected[:2])}. Model and year differences within same make are acceptable."
