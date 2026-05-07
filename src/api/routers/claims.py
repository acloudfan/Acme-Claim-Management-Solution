"""
Claims API router for estimate generation and claim operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header, Body
from sqlalchemy.orm import Session
from src.api.database import get_db
from src.api.schemas.damage import EstimateRequest, EstimateResponse, DamageResponse, DamageCreateRequest, DamageUpdateRequest
from src.api.schemas.review import ReviewCompleteRequest, ReviewCompleteResponse
from src.api.schemas.claim import ClaimResponse
from src.api.services.estimate_service import EstimateService
from src.api.services.claim_service import ClaimService
from src.api.services.damage_service import DamageService
from src.api.exceptions import ResourceNotFoundError
from typing import List, Optional, Dict, Any
from decimal import Decimal

router = APIRouter()

@router.post(
    "/{claim_id}/estimate",
    response_model=EstimateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate AI damage estimate"
)
def generate_estimate(
    claim_id: int,
    request: EstimateRequest,
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered damage estimate for claim.

    Analyzes uploaded images using YOLO model and calculates repair costs.

    - **claim_id**: Claim identifier
    - **image_ids**: List of image filenames to analyze
    - **state**: State code for labor rate calculation (default: CA)
    """
    service = EstimateService(db)

    try:
        result = service.generate_ai_estimate(
            claim_id=claim_id,
            image_ids=request.image_ids,
            state=request.state
        )

        # Convert damages to response format
        # Use helper to get effective estimate (adjustor if present, else AI)
        claim_service = ClaimService(db)
        damages_response = [
            DamageResponse(
                damage_id=d.damage_id,
                estimate_id=d.estimate_id,
                image_id=d.image_id,
                estimate_type=d.estimate_type,
                damage_class=d.damage_class,
                damage_confidence=float(d.damage_confidence) if d.damage_confidence else None,
                damage_part=d.damage_part,
                bounding_box={
                    "x": d.bounding_box_x,
                    "y": d.bounding_box_y,
                    "width": d.bounding_box_width,
                    "height": d.bounding_box_height
                } if d.bounding_box_x is not None else None,
                internal_damage_probability=float(d.internal_damage_probability) if d.internal_damage_probability else None,
                severity=float(d.severity),
                recommended_action=d.recommended_action,
                reasoning=d.reasoning,
                car_side=d.car_side,
                assessment_confidence=float(d.assessment_confidence) if d.assessment_confidence else None,
                # Effective estimate (adjustor if present, else AI)
                **claim_service.get_effective_estimate(d),
                # AI estimate (always included)
                ai_labor_hours=float(d.ai_labor_hours),
                ai_parts_cost=float(d.ai_parts_cost),
                ai_total_cost=float(d.ai_total_cost),
                # Adjustor estimate (nullable)
                adjustor_labor_hours=float(d.adjustor_labor_hours) if d.adjustor_labor_hours else None,
                adjustor_parts_cost=float(d.adjustor_parts_cost) if d.adjustor_parts_cost else None,
                adjustor_total_cost=float(d.adjustor_total_cost) if d.adjustor_total_cost else None,
                reviewed_by_adjustor=d.reviewed_by_adjustor,
                adjustor_note=d.adjustor_note,
                reviewed_at=d.reviewed_at.isoformat() if d.reviewed_at else None,
                annotated_image_id=d.annotated_image_id,
                avg_labor_cost=None  # DEPRECATED
            )
            for d in result["damages"]
        ]

        return EstimateResponse(
            estimate_id=result["estimate_id"],
            claim_id=result["claim_id"],
            total_cost=result["total_cost"],
            damages_count=result["damages_count"],
            damages=damages_response
        )
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get(
    "/{claim_id}/estimates/{estimate_id}",
    response_model=List[DamageResponse],
    summary="Get estimate damages"
)
def get_estimate_damages(
    claim_id: int,
    estimate_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all damage assessments for a specific estimate.

    - **claim_id**: Claim identifier
    - **estimate_id**: Estimate identifier
    """
    estimate_service = EstimateService(db)
    claim_service = ClaimService(db)
    damages = estimate_service.get_estimate_damages(estimate_id)

    return [
        DamageResponse(
            damage_id=d.damage_id,
            estimate_id=d.estimate_id,
            image_id=d.image_id,
            estimate_type=d.estimate_type,
            damage_class=d.damage_class,
            damage_confidence=float(d.damage_confidence) if d.damage_confidence else None,
            damage_part=d.damage_part,
            bounding_box={
                "x": d.bounding_box_x,
                "y": d.bounding_box_y,
                "width": d.bounding_box_width,
                "height": d.bounding_box_height
            } if d.bounding_box_x is not None else None,
            internal_damage_probability=float(d.internal_damage_probability) if d.internal_damage_probability else None,
            severity=float(d.severity),
            recommended_action=d.recommended_action,
            reasoning=d.reasoning,
            car_side=d.car_side,
            assessment_confidence=float(d.assessment_confidence) if d.assessment_confidence else None,
            # Effective estimate (adjustor if present, else AI)
            **claim_service.get_effective_estimate(d),
            # AI estimate (always included)
            ai_labor_hours=float(d.ai_labor_hours),
            ai_parts_cost=float(d.ai_parts_cost),
            ai_total_cost=float(d.ai_total_cost),
            # Adjustor estimate (nullable)
            adjustor_labor_hours=float(d.adjustor_labor_hours) if d.adjustor_labor_hours else None,
            adjustor_parts_cost=float(d.adjustor_parts_cost) if d.adjustor_parts_cost else None,
            adjustor_total_cost=float(d.adjustor_total_cost) if d.adjustor_total_cost else None,
            reviewed_by_adjustor=d.reviewed_by_adjustor,
            adjustor_note=d.adjustor_note,
            reviewed_at=d.reviewed_at.isoformat() if d.reviewed_at else None,
            annotated_image_id=d.annotated_image_id,
            avg_labor_cost=None  # DEPRECATED
        )
        for d in damages
    ]

@router.get(
    "/{claim_id}/estimates",
    response_model=List[str],
    summary="Get all estimate IDs for claim"
)
def get_claim_estimates(
    claim_id: int,
    db: Session = Depends(get_db)
):
    """
    Get list of all estimate IDs for a claim.

    - **claim_id**: Claim identifier
    """
    service = EstimateService(db)
    estimate_ids = service.get_claim_estimates(claim_id)
    return estimate_ids


@router.post(
    "/{claim_id}/review/complete",
    response_model=ReviewCompleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete human review of claim"
)
def complete_review(
    claim_id: int,
    request: ReviewCompleteRequest,
    db: Session = Depends(get_db)
):
    """
    Complete human review of a claim and transition to customer decision pending.

    Used by adjustors to:
    - Deny customer appeal (confirm AI estimate)
    - Provide revised estimate after manual review

    - **claim_id**: Claim identifier
    - **action**: 'denied_appeal' or 'revised_estimate'
    - **customer_note**: Note visible to customer (10-1000 chars)
    - **internal_note**: Internal adjustor note (10-2000 chars)
    - **revised_estimate_total**: New total if action is 'revised_estimate'
    """
    service = ClaimService(db)

    try:
        result = service.complete_review(claim_id, request.dict())
        return ReviewCompleteResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post(
    "/{claim_id}/damages",
    response_model=DamageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create manual damage entry"
)
def create_manual_damage(
    claim_id: int,
    request: DamageCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a manual damage entry added by an adjustor.

    Used when adjustor identifies damage not detected by AI or needs to
    add additional repair items.

    - **claim_id**: Claim identifier
    - **damage_part**: Part name (e.g., "Front Bumper")
    - **description**: Detailed description of damage
    - **severity**: 'light', 'moderate', or 'severe'
    - **labor_hours**: Estimated labor hours
    - **labor_rate**: Labor rate per hour
    - **parts_cost**: Cost of replacement parts
    - **adjustor_note**: Justification for manual entry
    """
    service = DamageService(db)

    try:
        damage = service.create_manual_damage(claim_id, request.dict())
        return DamageResponse.from_orm(damage)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/{claim_id}/damages/{damage_id}",
    response_model=DamageResponse,
    status_code=status.HTTP_200_OK,
    summary="Update damage costs"
)
def update_damage_costs(
    claim_id: int,
    damage_id: int,
    request: DamageUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Update cost information for an existing damage.

    Used by adjustors to revise labor hours, labor rate, or parts cost
    based on additional information or supplier quotes.

    - **claim_id**: Claim identifier (for context)
    - **damage_id**: Damage record identifier
    - **labor_hours**: Updated labor hours (optional)
    - **labor_rate**: Updated labor rate (optional)
    - **parts_cost**: Updated parts cost (optional)
    - **adjustor_note**: Reason for cost adjustment
    """
    service = DamageService(db)

    try:
        damage = service.update_damage_costs(damage_id, request.dict())
        return DamageResponse.from_orm(damage)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/{claim_id}/labor-rate",
    response_model=ClaimResponse,
    summary="Update claim labor rate"
)
def update_claim_labor_rate(
    claim_id: int,
    labor_rate: Decimal = Body(..., ge=50, le=500, description="New labor rate ($/hour)"),
    adjustor_id: str = Header(..., alias="X-Adjustor-ID"),
    db: Session = Depends(get_db)
):
    """
    Update labor rate for entire claim (adjustor override).

    - **claim_id**: Claim identifier
    - **labor_rate**: New labor rate in $/hour (50-500)
    - **X-Adjustor-ID**: Adjustor making the change (header)

    Recalculates all damage costs using the new rate.
    Logs event in claims_events table.
    """
    service = ClaimService(db)
    try:
        claim = service.update_labor_rate(claim_id, labor_rate, adjustor_id)
        # Convert to response model
        claim_dict = service.get_claim_with_damages(claim_id)
        return ClaimResponse(**claim_dict)
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get(
    "/{claim_id}/fraud-signals",
    response_model=Dict[str, Any],
    summary="Get fraud signals for claim"
)
def get_fraud_signals(
    claim_id: int,
    db: Session = Depends(get_db)
):
    """
    Get fraud detection analysis and signals for a claim.

    Returns fraud risk score and list of detected fraud signals with details.

    - **claim_id**: Claim identifier

    **Returns:**
    - overall_risk_score: Fraud risk score (0.0-1.0)
    - signals: List of fraud signals with type, severity, description, evidence
    """
    from src.api.models.claim import Claim
    from src.api.models.fraud_signal import FraudSignal

    # Get claim
    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim {claim_id} not found"
        )

    # Get fraud signals
    fraud_signals = db.query(FraudSignal).filter(
        FraudSignal.claim_id == claim_id
    ).order_by(FraudSignal.severity.desc()).all()

    # Build response
    return {
        "overall_risk_score": float(claim.overall_fraud_risk_score) if claim.overall_fraud_risk_score else 0.0,
        "signals": [signal.to_dict() for signal in fraud_signals]
    }
