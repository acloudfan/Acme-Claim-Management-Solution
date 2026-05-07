"""
Utility functions for fraud detection agents.
"""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from src.api.models.claim import Claim, ClaimImage
from src.api.models.vehicle import Vehicle
from src.api.models.policy import Policy
from src.api.config import settings

logger = logging.getLogger(__name__)


def load_claim_images(claim_id: int) -> List[Dict[str, Any]]:
    """
    Load all images for a claim from disk.

    Args:
        claim_id: Claim ID

    Returns:
        List of dicts with image_id, file_path, and image_bytes
    """
    images_root = Path(settings.IMAGES_ROOT_FOLDER)
    claim_dir = images_root / str(claim_id)

    if not claim_dir.exists():
        logger.warning(f"No images directory found for claim {claim_id}")
        return []

    image_files = []
    for image_path in claim_dir.glob("*"):
        # Skip annotated images (BB- prefix)
        if image_path.name.startswith(settings.YOLO_ANNOTATED_IMAGE_PREFIX):
            continue

        # Skip directories
        if not image_path.is_file():
            continue

        try:
            with open(image_path, 'rb') as f:
                image_bytes = f.read()

            image_files.append({
                'image_id': image_path.name,
                'file_path': str(image_path),
                'image_bytes': image_bytes
            })
        except Exception as e:
            logger.error(f"Failed to load image {image_path}: {e}")
            continue

    logger.info(f"Loaded {len(image_files)} images for claim {claim_id}")
    return image_files


def get_claim_context(claim_id: int, db: Session) -> Dict[str, Any]:
    """
    Get all contextual information needed for fraud detection.

    Args:
        claim_id: Claim ID
        db: Database session

    Returns:
        Dict with claim, vehicle, policy, and customer information
    """
    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if not claim:
        raise ValueError(f"Claim {claim_id} not found")

    vehicle = db.query(Vehicle).filter(Vehicle.vin == claim.vin).first()
    policy = db.query(Policy).filter(Policy.policy_number == claim.policy_number).first()

    # Get claim history for this customer
    customer_claims = (
        db.query(Claim)
        .filter(Claim.customer_id == claim.customer_id)
        .filter(Claim.claim_id != claim_id)  # Exclude current claim
        .order_by(Claim.fnol_date.desc())
        .all()
    )

    context = {
        'claim': {
            'claim_id': claim.claim_id,
            'fnol_date': claim.fnol_date.isoformat() if claim.fnol_date else None,
            'date_of_damage': claim.date_of_damage.isoformat() if claim.date_of_damage else None,
            'incident_description': claim.incident_description,
            'is_drivable': claim.is_drivable,
            'claim_amount': float(claim.claim_amount) if claim.claim_amount else None,
        },
        'vehicle': {
            'vin': vehicle.vin if vehicle else None,
            'year': vehicle.year if vehicle else None,
            'make': vehicle.make if vehicle else None,
            'model': vehicle.model if vehicle else None,
            'color': vehicle.color if vehicle else None,
        },
        'policy': {
            'policy_number': policy.policy_number if policy else None,
            'start_date': policy.start_date.isoformat() if policy and policy.start_date else None,
            'end_date': policy.end_date.isoformat() if policy and policy.end_date else None,
        },
        'customer': {
            'customer_id': claim.customer_id,
            'claim_history_count': len(customer_claims),
            'recent_claims': [
                {
                    'claim_id': c.claim_id,
                    'fnol_date': c.fnol_date.isoformat() if c.fnol_date else None,
                    'claim_amount': float(c.claim_amount) if c.claim_amount else None,
                    'current_status': c.current_status,
                }
                for c in customer_claims[:5]  # Last 5 claims
            ]
        }
    }

    return context


def build_evidence_dict(
    phase: str,
    agent_name: str,
    signal_type: str,
    severity: float,
    description: str,
    details: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Build a standardized evidence dictionary for fraud signals.

    Args:
        phase: Phase number (e.g., "phase1", "phase2", "phase3")
        agent_name: Name of the agent that generated this signal
        signal_type: Type of signal (e.g., "color_mismatch", "ai_generated")
        severity: Severity score (0.0-1.0)
        description: Human-readable description
        details: Additional details specific to this signal

    Returns:
        Standardized evidence dictionary
    """
    return {
        'phase': phase,
        'agent': agent_name,
        'signal_type': signal_type,
        'severity': severity,
        'description': description,
        'details': details
    }


def calculate_weighted_score(signals: List[Dict[str, Any]], weights: Dict[str, float]) -> float:
    """
    Calculate weighted average score from multiple signals.

    Args:
        signals: List of signal dicts with 'signal_type' and 'severity'
        weights: Dict mapping signal_type to weight

    Returns:
        Weighted average score (0.0-1.0)
    """
    if not signals:
        return 0.0

    total_weight = 0.0
    weighted_sum = 0.0

    for signal in signals:
        signal_type = signal.get('signal_type', '')
        severity = signal.get('severity', 0.0)

        # Find matching weight (handle both exact match and partial match)
        weight = 0.0
        for weight_key, weight_value in weights.items():
            if weight_key in signal_type or signal_type in weight_key:
                weight = weight_value
                break

        if weight > 0:
            weighted_sum += severity * weight
            total_weight += weight

    # Normalize by total weight
    if total_weight > 0:
        return min(1.0, weighted_sum / total_weight)
    else:
        return 0.0
