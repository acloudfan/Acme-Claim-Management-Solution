"""
Customer API router for customer CRUD, claims, images, events, and policies.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from src.api.database import get_db
from src.api.schemas.claim import ClaimResponse, ClaimCreate, ClaimImageResponse
from src.api.schemas.customer import CustomerResponse, CustomerCreate, CustomerUpdate, CustomerPatch
from src.api.schemas.claim_event import ClaimEventResponse, ClaimEventSummary
from src.api.schemas.policy import PolicyResponse
from src.api.services.claim_service import ClaimService
from src.api.services.customer_service import CustomerService
from src.api.services.event_service import EventService
from src.api.services.image_service import ImageService
from src.api.services.policy_service import PolicyService
from src.api.services.event_logger import log_event
from src.api.constants import ClaimAction, ActorType, ClaimState
from src.api.exceptions import ResourceNotFoundError, ValidationError
from typing import List, Optional

router = APIRouter()

# ============================================================================
# Customer CRUD Operations
# ============================================================================

@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Get customer details"
)
def get_customer(
    customer_id: int,
    include_policies: bool = Query(False, description="Include related policies and vehicles"),
    db: Session = Depends(get_db)
):
    """
    Get customer by ID.

    - **customer_id**: Customer identifier
    - **include_policies**: Include related policies and vehicles (default: false)

    Returns customer details with optional policy/vehicle relationships.
    """
    service = CustomerService(db)
    try:
        customer = service.get_customer(customer_id, include_policies)
        return customer
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new customer"
)
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db)
):
    """
    Create new customer account.

    Required fields:
    - **fname**: Customer first name
    - **lname**: Customer last name
    - **email**: Valid email address (unique)
    - **phone**: Contact phone number

    Optional fields:
    - **address**: Street address
    """
    service = CustomerService(db)
    try:
        customer = service.create_customer(customer_data)
        return customer
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Update customer (full update)"
)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db)
):
    """
    Update customer details (full update - all fields required).

    - **customer_id**: Customer identifier
    - **customer_data**: Complete customer data

    All fields must be provided. Use PATCH for partial updates.
    """
    service = CustomerService(db)
    try:
        customer = service.update_customer(customer_id, customer_data)
        return customer
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.patch(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Update customer (partial update)"
)
def patch_customer(
    customer_id: int,
    customer_data: CustomerPatch,
    db: Session = Depends(get_db)
):
    """
    Partially update customer details.

    - **customer_id**: Customer identifier
    - **customer_data**: Fields to update (all optional)

    Only provided fields will be updated. Omitted fields remain unchanged.
    """
    service = CustomerService(db)
    try:
        customer = service.patch_customer(customer_id, customer_data)
        return customer
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# ============================================================================
# Policy Operations
# ============================================================================

@router.get(
    "/{customer_id}/policies",
    response_model=List[PolicyResponse],
    summary="List customer policies"
)
def list_customer_policies(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all policies for a customer.

    - **customer_id**: Customer identifier

    Returns all policies associated with the customer, including:
    - Policy details (number, dates, coverage, premium)
    - Associated vehicles for each policy

    **Read-only operation** - Policies cannot be created/modified via API yet.
    """
    service = PolicyService(db)

    try:
        policies = service.get_customer_policies(customer_id)
        return policies
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get(
    "/{customer_id}/policies/{policy_number}",
    response_model=PolicyResponse,
    summary="Get policy details"
)
def get_customer_policy(
    customer_id: int,
    policy_number: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information for a specific policy.

    - **customer_id**: Customer identifier
    - **policy_number**: Policy number (e.g., "POL-2026-001")

    Returns:
    - Complete policy information
    - All vehicles covered under the policy
    - Coverage details (liability, collision, comprehensive)
    - Premium and deductible information

    **Read-only operation**
    """
    service = PolicyService(db)

    try:
        policy = service.get_policy(customer_id, policy_number)
        return policy
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

# ============================================================================
# Claim Operations
# ============================================================================

@router.post(
    "/{customer_id}/claims",
    response_model=ClaimResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new claim in draft state"
)
def create_claim(
    customer_id: int,
    claim_data: ClaimCreate,
    db: Session = Depends(get_db)
):
    """
    Create new claim for customer in draft state.

    - **customer_id**: Customer identifier
    - **vin**: Vehicle identification number (17 characters)
    - **policy_number**: Insurance policy number
    - **fnol_date**: Date of first notice
    - **fnol_time**: Time of first notice
    - **date_of_damage**: Date when damage occurred
    - **is_drivable**: Whether vehicle is drivable

    The claim is created in 'draft' state. Use the submit endpoint to move to FNOL.
    """
    service = ClaimService(db)
    claim = service.create_claim(customer_id, claim_data)
    return claim

@router.post(
    "/{customer_id}/claims/{claim_id}/submit",
    response_model=ClaimResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit claim for processing"
)
def submit_claim(
    customer_id: int,
    claim_id: int,
    db: Session = Depends(get_db)
):
    """
    Submit claim for processing (DRAFT -> FNOL transition).

    - **customer_id**: Customer identifier
    - **claim_id**: Claim identifier

    Transitions claim from 'draft' state to 'FNOL' (First Notice of Loss).
    After submission, claim enters the processing workflow.
    """
    service = ClaimService(db)
    try:
        claim = service.submit_claim(claim_id, customer_id)
        return claim
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post(
    "/{customer_id}/claims/{claim_id}/request-human-review",
    response_model=ClaimResponse,
    status_code=status.HTTP_200_OK,
    summary="Request human review for claim"
)
def request_human_review(
    customer_id: int,
    claim_id: int,
    db: Session = Depends(get_db)
):
    """
    Request human review for claim (no damages detected or customer requested).

    - **customer_id**: Customer identifier
    - **claim_id**: Claim identifier

    Transitions claim to 'human_review_pending' state.
    Used when AI cannot detect damage or customer prefers human assessment.
    """
    service = ClaimService(db)
    try:
        claim = service.get_claim(claim_id)

        # Transition through required states to reach human review pending
        if claim.current_status == ClaimState.DRAFT.value:
            # draft → FNOL
            claim = service.update_claim_status(
                claim_id=claim_id,
                new_status=ClaimState.FNOL,
                actor_type=ActorType.CUSTOMER,
                actor_identity=f"customer_{customer_id}",
                comments="Claim submitted - no damage detected by AI"
            )

        if claim.current_status == ClaimState.FNOL.value:
            # FNOL → IMAGE_UPLOADED
            claim = service.update_claim_status(
                claim_id=claim_id,
                new_status=ClaimState.IMAGE_UPLOADED,
                actor_type=ActorType.CUSTOMER,
                actor_identity=f"customer_{customer_id}",
                comments="Images uploaded for AI analysis"
            )

        if claim.current_status == ClaimState.IMAGE_UPLOADED.value:
            # IMAGE_UPLOADED → LOSS_ESTIMATED_AI (with $0 estimate since no damage)
            claim = service.update_claim_status(
                claim_id=claim_id,
                new_status=ClaimState.LOSS_ESTIMATED_AI,
                actor_type=ActorType.AI_AGENT,
                actor_identity="damage_detector_ai",
                comments="No damage detected - estimate: $0"
            )

        # Finally transition to human review pending
        if claim.current_status == ClaimState.LOSS_ESTIMATED_AI.value:
            # LOSS_ESTIMATED_AI → HUMAN_REVIEW_PENDING
            claim = service.update_claim_status(
                claim_id=claim_id,
                new_status=ClaimState.HUMAN_REVIEW_PENDING,
                actor_type=ActorType.CUSTOMER,
                actor_identity=f"customer_{customer_id}",
                comments="Customer requested human review - no AI damage detection"
            )

        return claim
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post(
    "/{customer_id}/claims/{claim_id}/accept-estimate",
    response_model=ClaimResponse,
    status_code=status.HTTP_200_OK,
    summary="Accept AI estimate and process for payment"
)
def accept_estimate(
    customer_id: int,
    claim_id: int,
    db: Session = Depends(get_db)
):
    """
    Accept AI estimate and transition to payment processing.

    - **customer_id**: Customer identifier
    - **claim_id**: Claim identifier

    State transitions:
    1. customer_decision_pending → loss_approved (customer accepts)
    2. loss_approved → sent_for_payment (initiate payment)

    Customer must be in customer_decision_pending state to accept.
    """
    service = ClaimService(db)
    try:
        claim = service.accept_estimate(claim_id=claim_id, customer_id=customer_id)
        return claim
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post(
    "/{customer_id}/claims/{claim_id}/appeal-estimate",
    status_code=status.HTTP_200_OK,
    summary="Appeal AI or human-reviewed estimate"
)
def appeal_estimate(
    customer_id: int,
    claim_id: int,
    appeal_data: dict,
    db: Session = Depends(get_db)
):
    """
    Appeal AI or human-reviewed estimate.

    - **customer_id**: Customer identifier
    - **claim_id**: Claim identifier
    - **reason**: Customer's reason for appealing (required in request body)

    First Appeal (AI estimate):
    - customer_decision_pending → loss_appealed → human_review_pending

    Second Appeal (Human-reviewed estimate):
    - customer_decision_pending → loss_appealed → routed_to_traditional

    Returns appeal_type ('first' or 'second') and updated claim.
    """
    from pydantic import BaseModel, Field

    class AppealRequest(BaseModel):
        reason: str = Field(..., min_length=1, max_length=500)

    try:
        # Validate request body
        appeal_request = AppealRequest(**appeal_data)

        service = ClaimService(db)
        result = service.appeal_estimate(
            claim_id=claim_id,
            customer_id=customer_id,
            reason=appeal_request.reason
        )

        return {
            "claim": result["claim"],
            "appeal_type": result["appeal_type"],
            "message": (
                "Appeal submitted for human review" if result["appeal_type"] == "first"
                else "Claim routed to traditional processing"
            )
        }
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/{customer_id}/claims",
    response_model=List[ClaimResponse],
    summary="Get customer claims"
)
def get_customer_claims(
    customer_id: int,
    status: str = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get all claims for customer with optional filtering.

    - **customer_id**: Customer identifier
    - **status**: Optional filter by claim status
    - **limit**: Maximum number of results (default: 20)
    - **offset**: Number of results to skip (default: 0)
    """
    service = ClaimService(db)
    claims = service.get_customer_claims(customer_id, status, limit, offset)
    return claims

@router.get(
    "/{customer_id}/claims/{claim_id}",
    response_model=ClaimResponse,
    summary="Get specific claim"
)
def get_claim(
    customer_id: int,
    claim_id: int,
    db: Session = Depends(get_db)
):
    """
    Get specific claim by ID with damage assessment.

    - **customer_id**: Customer identifier
    - **claim_id**: Claim identifier

    Returns claim with nested damage_assessment containing:
    - total_estimated_cost: Sum of all damage costs
    - damage_count: Number of damages
    - damages: Array of damage details (all fields from damages table)
    """
    service = ClaimService(db)
    claim_dict = service.get_claim_with_damages(claim_id)

    # Verify claim belongs to customer
    if claim_dict['customer_id'] != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Claim does not belong to this customer"
        )

    return claim_dict

@router.delete(
    "/{customer_id}/claims/{claim_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete draft claim"
)
def delete_claim(
    customer_id: int,
    claim_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a claim (only allowed in draft state).

    - **customer_id**: Customer identifier
    - **claim_id**: Claim identifier

    **Business Rule:** Only draft claims can be deleted.
    Once a claim is submitted (FNOL state), it cannot be deleted.

    This endpoint will cascade delete:
    - All claim images
    - All damage assessments
    - All claim events
    """
    service = ClaimService(db)
    try:
        service.delete_claim(claim_id, customer_id)
        return None
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post(
    "/{customer_id}/claims/{claim_id}/images",
    status_code=status.HTTP_201_CREATED,
    summary="Upload damage photo"
)
def upload_claim_image(
    customer_id: int,
    claim_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload damage photo to claim.

    **Business Rule:** Images can ONLY be uploaded when claim is in 'draft' state.

    Flow:
    1. Verify claim is in draft state (ERROR if not)
    2. Store image file
    3. YOLO analyzes image automatically
    4. Damage report created and added to claim
    5. Event logged
    6. NO status change (remains draft)

    - **file**: Image file (jpg, png, heic)
    - Maximum size: 10MB (configurable)
    - File must have unique name within claim
    """
    image_service = ImageService(db)

    try:
        image = image_service.upload_image(
            claim_id,
            file,
            f"customer_{customer_id}"
        )
        return {
            "image_id": image.image_id,
            "claim_id": claim_id,
            "uploaded_at": image.uploaded_at.isoformat()
        }
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get(
    "/{customer_id}/claims/{claim_id}/images/{image_id}",
    response_class=FileResponse,
    summary="Get claim image file"
)
def get_claim_image(
    customer_id: int,
    claim_id: int,
    image_id: str,
    annotated: Optional[str] = Query(None, description="Set to 'yes' for annotated image with bounding boxes"),
    db: Session = Depends(get_db)
):
    """
    Serve a damage photo (original or annotated with bounding boxes).

    - **customer_id**: Customer identifier
    - **claim_id**: Claim identifier
    - **image_id**: Image filename (e.g., 'front_bumper.jpg')
    - **annotated**: Query param - set to 'yes' to get YOLO-annotated version

    Query examples:
    - Original: GET /customers/100/claims/1000/images/front.jpg
    - Annotated: GET /customers/100/claims/1000/images/front.jpg?annotated=yes

    Returns FileResponse with appropriate Content-Type header.
    Annotated images are stored with 'BB-' prefix (e.g., 'BB-front.jpg').
    """
    # Validate image_id to prevent path traversal attacks
    if ".." in image_id or "/" in image_id or "\\" in image_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image_id: path traversal not allowed"
        )

    # Verify claim exists and belongs to customer
    claim_service = ClaimService(db)
    try:
        claim = claim_service.get_claim(claim_id)

        # For prototype: skip strict customer ownership check
        # Production: verify claim.customer_id == customer_id
        if claim.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Claim does not belong to this customer"
            )
    except ResourceNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim {claim_id} not found"
        )

    # Determine file path
    from src.api.config import get_settings
    config = get_settings()
    images_root = config.IMAGES_ROOT_FOLDER

    if annotated == "yes":
        # Serve annotated image with bounding boxes
        filename = f"BB-{image_id}"
    else:
        # Serve original image
        filename = image_id

    file_path = Path(images_root) / str(claim_id) / filename

    # Check file exists
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image not found: {filename}"
        )

    # Determine media type from extension
    ext = file_path.suffix.lower()
    media_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".heic": "image/heic"
    }
    media_type = media_type_map.get(ext, "application/octet-stream")

    # Return file with appropriate headers including CORS
    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        headers={
            "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
            "Content-Disposition": f'inline; filename="{filename}"',
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )

@router.get(
    "/{customer_id}/claims/{claim_id}/images/{image_id}/annotated",
    response_class=FileResponse,
    summary="Get annotated claim image with bounding boxes"
)
def get_annotated_claim_image(
    customer_id: int,
    claim_id: int,
    image_id: str,
    db: Session = Depends(get_db)
):
    """
    Serve damage photo annotated with YOLO bounding boxes.

    - **customer_id**: Customer identifier
    - **claim_id**: Claim identifier
    - **image_id**: Image filename (e.g., 'front_bumper.jpg')

    Returns FileResponse with annotated image (stored with 'BB-' prefix).
    Returns 404 if annotated version does not exist.
    """
    # Validate image_id to prevent path traversal attacks
    if ".." in image_id or "/" in image_id or "\\" in image_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image_id: path traversal not allowed"
        )

    # Verify claim exists and belongs to customer
    claim_service = ClaimService(db)
    try:
        claim = claim_service.get_claim(claim_id)
        if claim.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Claim does not belong to this customer"
            )
    except ResourceNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim {claim_id} not found"
        )

    # Determine file path for annotated image
    from src.api.config import get_settings
    config = get_settings()
    images_root = config.IMAGES_ROOT_FOLDER

    filename = f"BB-{image_id}"
    file_path = Path(images_root) / str(claim_id) / filename

    # Check file exists
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Annotated image not found: {filename}"
        )

    # Determine media type from extension
    ext = file_path.suffix.lower()
    media_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".heic": "image/heic"
    }
    media_type = media_type_map.get(ext, "application/octet-stream")

    # Return file with appropriate headers including CORS
    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        headers={
            "Cache-Control": "public, max-age=3600",
            "Content-Disposition": f'inline; filename="{filename}"',
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )

@router.get(
    "/{customer_id}/claims/{claim_id}/images",
    response_model=List[ClaimImageResponse],
    summary="Get claim images list"
)
def get_claim_images(
    customer_id: int,
    claim_id: int,
    db: Session = Depends(get_db)
):
    """
    Get metadata for all images in a claim (not the actual image files).

    - **customer_id**: Customer identifier
    - **claim_id**: Claim identifier

    Returns list of image metadata. To retrieve actual image files,
    use GET /{customer_id}/claims/{claim_id}/images/{image_id}
    """
    service = ClaimService(db)
    images = service.get_claim_images(claim_id)

    # Convert to response format
    return [
        {
            "image_id": img.image_id,
            "claim_id": img.claim_id,
            "uploaded_at": img.uploaded_at.isoformat(),
            "uploaded_by": img.uploaded_by
        }
        for img in images
    ]

@router.delete(
    "/{customer_id}/claims/{claim_id}/images/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete damage photo"
)
def delete_claim_image(
    customer_id: int,
    claim_id: int,
    image_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete uploaded damage photo.

    - **customer_id**: Customer identifier
    - **claim_id**: Claim identifier
    - **image_id**: Image filename
    - Cascade deletes associated damage reports
    """
    image_service = ImageService(db)

    try:
        image_service.delete_image(claim_id, image_id, f"customer_{customer_id}")
        return None
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

# ============================================================================
# Claim Events (Audit Trail)
# ============================================================================

@router.get(
    "/{customer_id}/claims/{claim_id}/events",
    response_model=ClaimEventSummary,
    summary="Get claim event history"
)
def get_claim_events(
    customer_id: int,
    claim_id: int,
    actor_type: Optional[str] = Query(None, description="Filter by actor type (customer, AI agent, adjustor, admin)"),
    limit: int = Query(100, ge=1, le=500, description="Maximum results (default: 100, max: 500)"),
    offset: int = Query(0, ge=0, description="Pagination offset (default: 0)"),
    db: Session = Depends(get_db)
):
    """
    Get event history for a claim (audit trail).

    - **customer_id**: Customer identifier (for authorization)
    - **claim_id**: Claim identifier
    - **actor_type**: Filter by actor (customer, AI agent, adjustor, admin)
    - **limit**: Maximum results (default: 100, max: 500)
    - **offset**: Pagination offset (default: 0)

    Returns events in chronological order (oldest first).
    Events provide complete audit trail of all claim actions.

    **Event Fields:**
    - event_id: Sequential event ID within claim
    - event_date: Date of action
    - event_time: Time of action
    - status: Claim status after action
    - action: Action taken (e.g., "create_claim", "upload_damage_photos")
    - action_by: Actor type (customer, AI agent, adjustor, admin)
    - action_by_identity: Specific actor identifier (e.g., "customer_100")
    - comments: Optional notes/context

    **Use Cases:**
    - Customer viewing claim timeline
    - Adjustor auditing claim history
    - Compliance/regulatory reporting
    - Debugging state transition issues
    """
    claim_service = ClaimService(db)
    event_service = EventService(db)

    try:
        # Verify claim belongs to customer
        claim = claim_service.get_claim(claim_id)
        if claim.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Claim does not belong to this customer"
            )

        # Get events
        events = event_service.get_claim_events(
            claim_id=claim_id,
            actor_type=actor_type,
            limit=limit,
            offset=offset
        )

        # Get statistics
        stats = event_service.get_event_statistics(claim_id)

        # Build response
        return ClaimEventSummary(
            total_events=stats['total_events'],
            events=events,
            customer_actions=stats['customer_actions'],
            ai_actions=stats['ai_actions'],
            adjustor_actions=stats['adjustor_actions'],
            admin_actions=stats['admin_actions']
        )

    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
