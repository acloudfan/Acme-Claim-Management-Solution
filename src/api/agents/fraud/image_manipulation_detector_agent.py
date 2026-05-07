"""
Image Manipulation Detector Agent - Phase 1 Vision Agent
Detects edited or manipulated images using EXIF analysis and vision LLM.
"""
import logging
from typing import Dict, Any, List
from datetime import datetime

from ..base_agent import BaseAgent, AgentResult
from ..llm.base import BaseLLMClient, Message
from .utils import build_evidence_dict

logger = logging.getLogger(__name__)


class ImageManipulationDetectorAgent(BaseAgent):
    """
    Vision agent that detects image manipulation and editing.

    Uses:
    1. EXIF metadata analysis (TODO - requires PIL/exifread library)
    2. Vision LLM to detect visual manipulation artifacts
    """

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute image manipulation detection.

        Args:
            input_data: Dict with:
                - images: List of dicts with image_id, image_bytes, file_path

        Returns:
            AgentResult with manipulation detection results
        """
        start_time = datetime.now()

        try:
            images = input_data['images']

            logger.info(f"Image manipulation detection: Analyzing {len(images)} images")

            if not images:
                return self._create_result(
                    success=True,
                    data={
                        'signal_type': 'image_manipulation',
                        'severity': 0.0,
                        'description': 'No images to analyze',
                        'evidence': build_evidence_dict(
                            phase='phase1',
                            agent_name='ImageManipulationDetectorAgent',
                            signal_type='image_manipulation',
                            severity=0.0,
                            description='No images provided for manipulation detection',
                            details={}
                        )
                    }
                )

            # Analyze images (limit to 5 for efficiency)
            analysis_images = images[:5]
            manipulation_results = []
            total_input_tokens = 0
            total_output_tokens = 0

            for img in analysis_images:
                # TODO: EXIF metadata analysis
                # This would check for:
                # - Software field (Photoshop, GIMP, etc.)
                # - Edit timestamps
                # - Modification history
                # - Missing or inconsistent metadata
                exif_data = self._analyze_exif(img.get('file_path', ''))

                # Vision LLM analysis for visual manipulation artifacts
                system_prompt = """You are an image forensics specialist for insurance fraud detection.

Your task:
1. Analyze the image for signs of digital manipulation or editing
2. Look for common manipulation artifacts
3. Assess the probability that this image has been edited

Common manipulation indicators:
- Cloning artifacts (repeated patterns or textures)
- Inconsistent shadows or lighting
- Mismatched edges or borders (signs of copy-paste)
- Unnatural color transitions
- Pixelation or blurriness in specific areas only
- Perspective inconsistencies
- Compression artifacts in specific regions (signs of splicing)
- Object edges that don't match the background

Important:
- Normal photo compression artifacts are NOT manipulation
- Consider that mobile photos may have natural imperfections
- Only flag if you see clear signs of intentional editing"""

                user_prompt = """Analyze this vehicle damage image for signs of digital manipulation or editing.

Questions:
1. Does this image show signs of being edited or manipulated?
2. What specific manipulation artifacts do you observe (if any)?
3. Are there inconsistencies in lighting, shadows, or perspectives?
4. What is the probability this image has been edited?

Respond in this format:
MANIPULATED: [yes/no/unsure]
PROBABILITY_EDITED: [0.0-1.0, where 1.0 = definitely edited]
CONFIDENCE: [0.0-1.0]
ARTIFACTS: [list specific signs, or "none"]
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
                manipulation_results.append({
                    'image_id': img['image_id'],
                    'manipulated': parsed.get('manipulated', False),
                    'probability': parsed.get('probability', 0.0),
                    'confidence': parsed.get('confidence', 0.0),
                    'artifacts': parsed.get('artifacts', ''),
                    'reasoning': parsed.get('reasoning', ''),
                    'exif_flags': exif_data.get('flags', []),
                    'raw_response': response.content
                })

            # Aggregate results
            manipulation_count = sum(1 for r in manipulation_results if r['manipulated'])
            avg_probability = sum(r['probability'] for r in manipulation_results) / len(manipulation_results)
            max_probability = max(r['probability'] for r in manipulation_results)

            # Calculate overall severity
            overall_severity = max(avg_probability, max_probability * 0.8)

            description = self._build_description(manipulation_results, overall_severity, manipulation_count)

            execution_time_ms = self._measure_execution_time(start_time)

            result_data = {
                'signal_type': 'image_manipulation',
                'severity': overall_severity,
                'description': description,
                'evidence': build_evidence_dict(
                    phase='phase1',
                    agent_name='ImageManipulationDetectorAgent',
                    signal_type='image_manipulation',
                    severity=overall_severity,
                    description=description,
                    details={
                        'images_analyzed': len(manipulation_results),
                        'manipulation_count': manipulation_count,
                        'avg_probability': avg_probability,
                        'max_probability': max_probability,
                        'manipulation_results': manipulation_results
                    }
                )
            }

            logger.info(f"Image manipulation detection completed: severity={overall_severity:.2f}, manipulated={manipulation_count}/{len(manipulation_results)}")

            return self._create_result(
                success=True,
                data=result_data,
                execution_time_ms=execution_time_ms,
                input_tokens=total_input_tokens,
                output_tokens=total_output_tokens
            )

        except Exception as e:
            logger.error(f"Image manipulation detection failed: {e}", exc_info=True)
            return self._create_result(
                success=False,
                data={
                    'signal_type': 'image_manipulation',
                    'severity': 0.0,
                    'description': f'Image manipulation detection failed: {str(e)}'
                },
                error=str(e)
            )

    def _analyze_exif(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze EXIF metadata for manipulation indicators.

        TODO: Implement using PIL/Pillow or exifread library
        - Check Software field for editing tools
        - Check modification timestamps
        - Look for missing or inconsistent metadata

        Args:
            file_path: Path to image file

        Returns:
            Dict with EXIF analysis results
        """
        # Placeholder - to be implemented
        return {
            'flags': [],
            'software': None,
            'modified': False
        }

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse structured response from LLM"""
        result = {
            'manipulated': False,
            'probability': 0.0,
            'confidence': 0.0,
            'artifacts': '',
            'reasoning': ''
        }

        lines = response_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('MANIPULATED:'):
                manip_text = line.split(':', 1)[1].strip().lower()
                result['manipulated'] = 'yes' in manip_text
            elif line.startswith('PROBABILITY_EDITED:'):
                try:
                    result['probability'] = float(line.split(':', 1)[1].strip())
                except ValueError:
                    pass
            elif line.startswith('CONFIDENCE:'):
                try:
                    result['confidence'] = float(line.split(':', 1)[1].strip())
                except ValueError:
                    pass
            elif line.startswith('ARTIFACTS:'):
                result['artifacts'] = line.split(':', 1)[1].strip()
            elif line.startswith('REASONING:'):
                result['reasoning'] = line.split(':', 1)[1].strip()

        return result

    def _build_description(self, results: List[Dict], severity: float, manipulation_count: int) -> str:
        """Build human-readable description"""
        if severity == 0.0:
            return "No signs of image manipulation detected. Images appear unedited."
        elif severity < 0.3:
            return f"Low probability of manipulation. {manipulation_count}/{len(results)} images show minor artifacts, likely camera or compression artifacts."
        elif severity < 0.6:
            artifacts = []
            for r in results:
                if r['manipulated'] and r['artifacts']:
                    artifacts.append(r['artifacts'])
            return f"Moderate probability of image editing detected in {manipulation_count}/{len(results)} images. Artifacts: {'; '.join(artifacts[:2])}"
        else:
            return f"HIGH probability of image manipulation detected. {manipulation_count}/{len(results)} images show strong signs of digital editing (Photoshop, cloning, splicing)."
