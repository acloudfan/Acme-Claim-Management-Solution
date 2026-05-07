"""
Damage Detector - YOLO Integration

Integrates YOLOv11 model for car damage detection.
Model: vineetsarpal/yolov11n-car-damage (HuggingFace)
"""

from typing import List, Dict, Optional
from pathlib import Path
import logging

from ultralytics import YOLO
from huggingface_hub import hf_hub_download
from PIL import Image
import cv2
import numpy as np

from src.api.config import settings

logger = logging.getLogger(__name__)

# YOLO class names (14 damage types)
YOLO_CLASS_NAMES = {
    0: 'Front-windscreen-damage',
    1: 'Headlight-damage',
    2: 'Rear-windscreen-Damage',
    3: 'Runningboard-Damage',
    4: 'Sidemirror-Damage',
    5: 'Taillight-Damage',
    6: 'bonnet-dent',
    7: 'boot-dent',
    8: 'doorouter-dent',
    9: 'fender-dent',
    10: 'front-bumper-dent',
    11: 'quaterpanel-dent',
    12: 'rear-bumper-dent',
    13: 'roof-dent'
}

class DamageDetector:
    """Damage detection using YOLO model"""

    def __init__(self, model_path: Optional[str] = None, device: Optional[str] = None):
        """
        Initialize damage detector.

        Args:
            model_path: Path to YOLO model (HF repo or local path). If None, uses config.
            device: Device for inference (cpu, cuda, mps). If None, uses config.
        """
        # Load configuration
        self.model_source = settings.YOLO_MODEL_SOURCE
        self.model_path = model_path or settings.YOLO_MODEL_PATH
        self.device = device or settings.YOLO_DEVICE
        self.confidence_threshold = settings.YOLO_CONFIDENCE_THRESHOLD
        self.save_annotated = settings.YOLO_SAVE_ANNOTATED_IMAGES
        self.annotated_prefix = settings.YOLO_ANNOTATED_IMAGE_PREFIX

        # Load model
        self.model = self._load_model()

        logger.info(
            f"DamageDetector initialized: source={self.model_source}, "
            f"model={self.model_path}, device={self.device}, "
            f"confidence_threshold={self.confidence_threshold}"
        )

    def _load_model(self) -> YOLO:
        """Load YOLO model from HuggingFace or local path"""
        try:
            if self.model_source == "huggingface":
                logger.info(f"Downloading model from HuggingFace: {self.model_path}")
                model_file = hf_hub_download(
                    repo_id=self.model_path,
                    filename="best.pt"
                )
                model = YOLO(model_file)
                logger.info("Model loaded from HuggingFace successfully")
            else:
                logger.info(f"Loading local model: {self.model_path}")
                model = YOLO(self.model_path)
                logger.info("Local model loaded successfully")

            # Log class names
            logger.info(f"Model classes: {model.names}")

            return model

        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise RuntimeError(f"YOLO model initialization failed: {e}")

    def detect_damages(
        self,
        image_path: Path,
        save_annotated_path: Optional[Path] = None
    ) -> List[Dict]:
        """
        Detect damages in image using YOLO.

        Args:
            image_path: Path to damage image
            save_annotated_path: Optional path to save annotated image with bounding boxes

        Returns:
            List of damage detections with format:
            [
                {
                    "damage_class": 7,
                    "confidence": 0.86,
                    "damage_part": "boot-dent",
                    "bounding_box": {"x": 120, "y": 200, "width": 150, "height": 100},
                    "severity": 0.8,
                    "internal_damage_probability": 0.7,
                    "recommended_action": "de-dent-and-paint",
                    "reasoning": "...",
                    "car_side": "back",
                    "assessment_confidence": 0.85
                }
            ]
        """
        if not image_path.exists():
            logger.error(f"Image not found: {image_path}")
            raise FileNotFoundError(f"Image file not found: {image_path}")

        logger.info(f"Running YOLO inference on: {image_path.name}")

        # Run YOLO inference
        results = self.model.predict(
            source=str(image_path),
            conf=self.confidence_threshold,
            device=self.device,
            verbose=False
        )

        # Parse results
        damages = []
        result = results[0]  # Single image

        if len(result.boxes) == 0:
            logger.warning(f"No damages detected in {image_path.name}")
            return damages

        logger.info(f"Detected {len(result.boxes)} damage(s) in {image_path.name}")

        # Read image for size calculation
        image = cv2.imread(str(image_path))
        image_height, image_width = image.shape[:2]
        image_area = image_height * image_width

        for i, box in enumerate(result.boxes):
            class_id = int(box.cls)
            confidence = float(box.conf)
            damage_part = self.model.names[class_id]

            # Extract bounding box (xyxy format)
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            bbox = {
                "x": int(x1),
                "y": int(y1),
                "width": int(x2 - x1),
                "height": int(y2 - y1)
            }

            # Calculate damage area
            damage_area = bbox["width"] * bbox["height"]
            area_ratio = damage_area / image_area

            # Assess damage (heuristic - will be replaced by VLM later)
            assessment = self._assess_damage(
                damage_part=damage_part,
                confidence=confidence,
                bbox=bbox,
                area_ratio=area_ratio,
                image_width=image_width,
                image_height=image_height
            )

            damage = {
                "damage_class": class_id,
                "confidence": round(confidence, 2),
                "damage_part": damage_part,
                "bounding_box": bbox,
                **assessment
            }

            damages.append(damage)
            logger.info(
                f"  Damage {i+1}: {damage_part} "
                f"(confidence={confidence:.2f}, severity={assessment['severity']:.2f})"
            )

        # Save annotated image if requested
        if save_annotated_path or self.save_annotated:
            self._save_annotated_image(result, save_annotated_path or self._get_annotated_path(image_path))

        return damages

    def _assess_damage(
        self,
        damage_part: str,
        confidence: float,
        bbox: Dict[str, int],
        area_ratio: float,
        image_width: int,
        image_height: int
    ) -> Dict:
        """
        Assess damage severity and characteristics (heuristic-based).

        TODO: Replace with VLM assessment in future version.

        Args:
            damage_part: Name of damaged part
            confidence: YOLO confidence score
            bbox: Bounding box dict
            area_ratio: Damage area / image area
            image_width: Image width in pixels
            image_height: Image height in pixels

        Returns:
            Assessment dict with severity, internal_damage_probability, etc.
        """
        # Calculate severity from area ratio (0-1 scale)
        if area_ratio < 0.05:
            severity = 0.3  # Light damage
        elif area_ratio < 0.15:
            severity = 0.6  # Moderate damage
        else:
            severity = 0.9  # Severe damage

        # Estimate internal damage probability
        # Higher for windscreen, headlight, taillight (exposes internals)
        if any(x in damage_part.lower() for x in ['windscreen', 'headlight', 'taillight']):
            internal_damage_prob = 0.8
        elif 'bumper' in damage_part.lower():
            internal_damage_prob = 0.6
        elif 'dent' in damage_part.lower():
            internal_damage_prob = 0.4 if severity > 0.6 else 0.2
        else:
            internal_damage_prob = 0.3

        # Determine recommended action
        if any(x in damage_part.lower() for x in ['windscreen', 'headlight', 'taillight', 'mirror']):
            action = "replace"
        elif 'dent' in damage_part.lower():
            action = "de-dent-and-paint" if severity > 0.5 else "de-dent"
        else:
            action = "repaint"

        # Determine car side from bbox position
        center_x = bbox["x"] + bbox["width"] / 2
        center_y = bbox["y"] + bbox["height"] / 2

        if center_y < image_height * 0.4:
            car_side = "front"
        elif center_y > image_height * 0.6:
            car_side = "back"
        elif center_x < image_width * 0.5:
            car_side = "driver_side"
        else:
            car_side = "passenger_side"

        # Generate reasoning
        reasoning = (
            f"{damage_part.replace('-', ' ').title()} detected with "
            f"{confidence:.0%} confidence. Damage covers {area_ratio:.1%} of image area "
            f"({bbox['width']}x{bbox['height']}px). "
            f"Severity assessed as {severity:.1f} based on damage extent. "
            f"Recommended action: {action}."
        )

        return {
            "severity": round(severity, 2),
            "internal_damage_probability": round(internal_damage_prob, 2),
            "recommended_action": action,
            "reasoning": reasoning,
            "car_side": car_side,
            "assessment_confidence": round(confidence * 0.95, 2)  # Slightly lower than detection confidence
        }

    def _get_annotated_path(self, original_path: Path) -> Path:
        """Generate path for annotated image"""
        return original_path.parent / f"{self.annotated_prefix}{original_path.name}"

    def _save_annotated_image(self, result, save_path: Path):
        """Save image with bounding boxes drawn"""
        try:
            # Get annotated image from YOLO result
            annotated_img = result.plot()

            # Save to file
            cv2.imwrite(str(save_path), annotated_img)
            logger.info(f"Annotated image saved: {save_path.name}")

        except Exception as e:
            logger.error(f"Failed to save annotated image: {e}")


# Singleton instance
_detector_instance = None

def get_damage_detector() -> DamageDetector:
    """Get singleton damage detector instance"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = DamageDetector()
    return _detector_instance
