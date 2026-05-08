"""
API router for adjustor-related endpoints.
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from src.api.database import get_db
from src.api.services.adjustor_service import AdjustorService
from src.api.schemas.adjustor import PendingClaimSummary, AdjustorStatistics, AdjustorWithWorkload
from typing import List, Optional
from datetime import datetime

router = APIRouter()


@router.get("/count")
def get_adjustor_count(db: Session = Depends(get_db)):
    """
    Get total number of adjustors in the database.

    Returns:
    - **count**: Number of adjustors
    - **has_adjustors**: Boolean indicating if database has adjustors

    Used by adjustor login screen to determine if database needs seeding.
    """
    from src.api.models.adjustor import Adjustor
    count = db.query(Adjustor).count()
    return {
        "count": count,
        "has_adjustors": count > 0
    }


@router.get("", response_model=List[AdjustorWithWorkload])
def list_adjustors(
    status_filter: Optional[str] = Query(None, description="Filter by status: active, inactive"),
    db: Session = Depends(get_db)
):
    """
    Get all adjustors with their current workload statistics.

    Used by Customer Portal to auto-assign claims to adjustor with shortest queue.

    **Query Parameters:**
    - `status_filter` (optional): Filter by 'active' or 'inactive' status

    **Returns:**
    - List of adjustors with workload statistics (pending_reviews, completed counts)
    """
    from src.api.models.adjustor import Adjustor

    # Query adjustors
    query = db.query(Adjustor)

    # Apply status filter
    if status_filter:
        query = query.filter(Adjustor.status == status_filter)

    adjustors = query.all()

    # Enhance each adjustor with workload stats
    service = AdjustorService(db)
    result = []

    for adjustor in adjustors:
        stats = service.get_statistics(adjustor.adjustor_id)
        result.append(AdjustorWithWorkload(
            adjustor_id=adjustor.adjustor_id,
            name=adjustor.name,
            email=adjustor.email,
            role=adjustor.role,
            status=adjustor.status,
            pending_reviews=stats["pending_reviews"],
            completed_today=stats["completed_today"],
            completed_this_week=stats["completed_this_week"]
        ))

    return result


@router.get("/{adjustor_id}/claims/pending")
def get_pending_claims(
    adjustor_id: str,
    search: Optional[str] = Query(None, description="Search by claim ID, customer name, VIN, or policy number"),
    sort: Optional[str] = Query("oldest", description="Sort option: oldest, newest, highest_amount, lowest_amount, customer_name"),
    filter: Optional[str] = Query(None, description="Filter option (reserved for future use)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get claims pending human review with filtering, sorting, and pagination.

    Returns a paginated list of claims in human_review_pending status.
    """
    service = AdjustorService(db)

    # Get pending claims with filters
    results, total_count = service.get_pending_claims(adjustor_id, {
        'search': search,
        'sort': sort,
        'filter': filter,
        'page': page,
        'limit': limit
    })

    # Format response
    claims = []
    for claim, customer, vehicle in results:
        # Calculate time in queue
        time_in_queue = _calculate_time_in_queue(claim.fnol_date, claim.fnol_time)

        # Calculate AI estimate total from damages (more reliable than claim_amount)
        from src.api.models.damage import Damage
        ai_estimate_total = 0.0

        if claim.active_estimate_id:
            # Get all damages for the active estimate
            damages = db.query(Damage).filter(
                Damage.claim_id == claim.claim_id,
                Damage.estimate_id == claim.active_estimate_id
            ).all()

            # Sum up AI total costs
            for damage in damages:
                if damage.ai_total_cost:
                    ai_estimate_total += float(damage.ai_total_cost)

        # Fallback to claim_amount if no damages found
        if ai_estimate_total == 0.0 and claim.claim_amount:
            ai_estimate_total = float(claim.claim_amount)

        # Determine reason for review (PRIORITY ORDER)
        # 1. Fraud signals (highest priority)
        # Check if claim was routed due to fraud (score > 0.7 OR fraud event recommendation)
        fraud_score = float(claim.overall_fraud_risk_score) if claim.overall_fraud_risk_score else 0.0
        is_fraud_routed = False

        if fraud_score > 0.7:
            is_fraud_routed = True
        elif fraud_score > 0:
            # Check if fraud detection recommended human review
            from src.api.models.claim_event import ClaimEvent
            from src.api.constants import ClaimAction

            fraud_event = db.query(ClaimEvent).filter(
                ClaimEvent.claim_id == claim.claim_id,
                ClaimEvent.action == ClaimAction.ASSESS_FRAUD_RISK.value
            ).first()

            if fraud_event and fraud_event.comments and 'HUMAN_REVIEW' in fraud_event.comments:
                is_fraud_routed = True

        if is_fraud_routed:
            reason_for_review = "fraud_signals"
        # 2. Customer appeal (check both appeal_count field and events as fallback)
        elif claim.appeal_count and claim.appeal_count > 0:
            reason_for_review = "customer_appeal"
        elif claim.first_appeal_reason or claim.first_appeal_date:
            # Fallback: appeal fields are set but appeal_count wasn't updated
            reason_for_review = "customer_appeal"
        else:
            # Final fallback: Check claim events for appeal action
            from src.api.models.claim_event import ClaimEvent
            from src.api.constants import ClaimAction

            appeal_event = db.query(ClaimEvent).filter(
                ClaimEvent.claim_id == claim.claim_id,
                ClaimEvent.action == ClaimAction.APPEAL_ESTIMATE.value
            ).first()

            if appeal_event:
                reason_for_review = "customer_appeal"
            else:
                # 3. Low confidence or no damage detected by AI (default)
                reason_for_review = "low_confidence"

        claim_data = {
            "claim_id": claim.claim_id,
            "customer_id": customer.customer_id,
            "customer_name": f"{customer.fname} {customer.lname}",
            "vin": claim.vin,
            "vehicle": f"{vehicle.year} {vehicle.make} {vehicle.model} {vehicle.color}",
            "policy_number": claim.policy_number,
            "fnol_date": claim.fnol_date,
            "ai_estimate_total": ai_estimate_total,
            "reason_for_review": reason_for_review,  # Changed from review_reason to match frontend expectation
            "time_in_queue": time_in_queue,
            "current_status": claim.current_status
        }

        # Add fraud data if fraud signals exist
        if reason_for_review == "fraud_signals":
            claim_data["fraud_risk_score"] = fraud_score
            # Get top 3 fraud signals for queue display
            from src.api.models.fraud_signal import FraudSignal
            top_signals = db.query(FraudSignal).filter(
                FraudSignal.claim_id == claim.claim_id
            ).order_by(FraudSignal.severity.desc()).limit(3).all()
            claim_data["fraud_signals"] = [s.description for s in top_signals]

        claims.append(claim_data)

    return {
        "total": total_count,
        "page": page,
        "limit": limit,
        "total_pages": (total_count + limit - 1) // limit,
        "claims": claims
    }


@router.get("/{adjustor_id}/statistics", response_model=AdjustorStatistics)
def get_statistics(
    adjustor_id: str,
    db: Session = Depends(get_db)
):
    """
    Get workload statistics for an adjustor.

    Returns pending reviews count, completed counts, and performance metrics.
    """
    service = AdjustorService(db)
    return service.get_statistics(adjustor_id)


@router.post("/{adjustor_id}/claims/{claim_id}/assign")
def assign_claim(
    adjustor_id: str,
    claim_id: int,
    db: Session = Depends(get_db)
):
    """
    Assign a claim to a specific adjustor.

    Used by Customer Portal auto-assignment logic when claim enters human review.

    **Path Parameters:**
    - `adjustor_id`: Adjustor identifier (e.g., "ADJ-001")
    - `claim_id`: Claim identifier

    **Validation:**
    - Claim must be in `human_review_pending` status
    - Adjustor must be active
    - Creates assignment event in `claims_events` table

    **Returns:**
    - Success confirmation with adjustor name and assignment timestamp
    """
    from src.api.models.claim import Claim
    from src.api.models.adjustor import Adjustor
    from src.api.models.claim_event import ClaimEvent
    from src.api.constants import ClaimState, ClaimAction, ActorType
    from datetime import date, datetime

    # Verify adjustor exists and is active
    adjustor = db.query(Adjustor).filter(
        Adjustor.adjustor_id == adjustor_id,
        Adjustor.status == 'active'
    ).first()

    if not adjustor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Active adjustor {adjustor_id} not found"
        )

    # Verify claim exists and is in human_review_pending status
    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()

    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim {claim_id} not found"
        )

    if claim.current_status != ClaimState.HUMAN_REVIEW_PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Claim must be in human_review_pending status, currently: {claim.current_status}"
        )

    # Assign claim to adjustor
    claim.assigned_adjustor_id = adjustor_id
    db.add(claim)

    # Create assignment event
    event = ClaimEvent(
        claim_id=claim_id,
        event_date=date.today(),
        event_time=datetime.now().time(),
        status=claim.current_status,
        action=ClaimAction.ASSIGN_TO_ADJUSTOR.value,
        action_by=ActorType.AI_AGENT.value,
        action_by_identity="auto_assignment_system",
        comments=f"Claim assigned to adjustor {adjustor.name} ({adjustor_id})"
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return {
        "success": True,
        "message": f"Claim {claim_id} assigned to {adjustor.name}",
        "data": {
            "claim_id": claim_id,
            "adjustor_id": adjustor_id,
            "adjustor_name": adjustor.name,
            "assigned_at": datetime.now().isoformat(),
            "event_id": event.event_id
        }
    }


def _calculate_time_in_queue(fnol_date, fnol_time) -> str:
    """
    Calculate how long a claim has been in the queue.

    Args:
        fnol_date: Date claim was submitted
        fnol_time: Time claim was submitted

    Returns:
        Human-readable time string (e.g., "2h", "1d 3h")
    """
    from datetime import datetime, timedelta

    # Combine date and time
    if fnol_time:
        claim_datetime = datetime.combine(fnol_date, fnol_time)
    else:
        claim_datetime = datetime.combine(fnol_date, datetime.min.time())

    # Calculate time difference
    now = datetime.now()
    diff = now - claim_datetime

    # Format as human-readable string
    if diff.days > 0:
        hours = diff.seconds // 3600
        if hours > 0:
            return f"{diff.days}d {hours}h"
        return f"{diff.days}d"
    else:
        hours = diff.seconds // 3600
        if hours > 0:
            return f"{hours}h"
        minutes = (diff.seconds % 3600) // 60
        return f"{minutes}m"
