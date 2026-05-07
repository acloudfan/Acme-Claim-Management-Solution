"""
Constants, enums, and state machine definitions for the Insurance Claims API.
"""
from enum import Enum

# Claim States
class ClaimState(str, Enum):
    DRAFT = "draft"
    FNOL = "FNOL"
    IMAGE_UPLOADED = "image_uploaded"
    LOSS_ESTIMATED_AI = "loss_estimated_ai"
    CUSTOMER_DECISION_PENDING = "customer_decision_pending"
    LOSS_APPROVED = "loss_approved"
    LOSS_APPEALED = "loss_appealed"
    HUMAN_REVIEW_PENDING = "human_review_pending"
    HUMAN_REVIEW_COMPLETED = "human_review_completed"
    SENT_FOR_PAYMENT = "sent_for_payment"
    CLAIM_PAID = "claim_paid"
    ROUTED_TO_TRADITIONAL = "routed_to_traditional"
    TRADITIONAL_PROCESSING_ACTIVE = "traditional_processing_active"
    CLAIM_CLOSED = "claim_closed"

# Actions
class ClaimAction(str, Enum):
    # Customer actions
    CREATE_CLAIM = "create_claim"
    SUBMIT_CLAIM = "submit_claim"
    UPLOAD_DAMAGE_PHOTOS = "upload_damage_photos"
    IMAGE_DELETED = "image_deleted"
    CLAIM_DELETED = "claim_deleted"
    ACCEPT_ESTIMATE = "accept_estimate"
    APPEAL_ESTIMATE = "appeal_estimate"

    # AI agent actions
    GENERATE_ESTIMATE = "generate_estimate"
    PRESENT_ESTIMATE_TO_CUSTOMER = "present_estimate_to_customer"
    ASSESS_FRAUD_RISK = "assess_fraud_risk"
    CALCULATE_CONFIDENCE_SCORE = "calculate_confidence_score"
    FLAG_FOR_HUMAN_REVIEW = "flag_for_human_review"

    # Adjustor actions
    DENIED_APPEAL = "denied_appeal"
    APPROVED_APPEAL = "approved_appeal"
    REVISED_ESTIMATE = "revised_estimate"
    ROUTE_TO_TRADITIONAL = "route_to_traditional"
    UPDATE_LABOR_RATE = "update_labor_rate"  # NEW

    # System actions
    ASSIGN_TO_ADJUSTOR = "assign_to_adjustor"

    # Admin actions
    INITIATE_PAYMENT = "initiate_payment"
    PAYMENT_SENT = "payment_sent"
    CLOSE_CLAIM = "close_claim"

# Actor Types
class ActorType(str, Enum):
    CUSTOMER = "customer"
    AI_AGENT = "AI agent"
    ADJUSTOR = "adjustor"
    ADMIN = "admin"

# Estimate Types
class EstimateType(str, Enum):
    AI = "ai"
    HUMAN = "human"

# Valid State Transitions
VALID_TRANSITIONS = {
    ClaimState.DRAFT: [ClaimState.FNOL],
    ClaimState.FNOL: [ClaimState.IMAGE_UPLOADED, ClaimState.LOSS_ESTIMATED_AI],
    ClaimState.IMAGE_UPLOADED: [ClaimState.LOSS_ESTIMATED_AI],
    ClaimState.LOSS_ESTIMATED_AI: [
        ClaimState.CUSTOMER_DECISION_PENDING,
        ClaimState.HUMAN_REVIEW_PENDING
    ],
    ClaimState.CUSTOMER_DECISION_PENDING: [
        ClaimState.LOSS_APPROVED,
        ClaimState.LOSS_APPEALED
    ],
    ClaimState.LOSS_APPROVED: [ClaimState.SENT_FOR_PAYMENT],
    ClaimState.LOSS_APPEALED: [
        ClaimState.HUMAN_REVIEW_PENDING,
        ClaimState.ROUTED_TO_TRADITIONAL  # Second appeal routes directly to traditional
    ],
    ClaimState.HUMAN_REVIEW_PENDING: [ClaimState.HUMAN_REVIEW_COMPLETED],
    ClaimState.HUMAN_REVIEW_COMPLETED: [
        ClaimState.CUSTOMER_DECISION_PENDING,
        ClaimState.ROUTED_TO_TRADITIONAL
    ],
    ClaimState.SENT_FOR_PAYMENT: [ClaimState.CLAIM_PAID],
    ClaimState.CLAIM_PAID: [ClaimState.CLAIM_CLOSED],
    ClaimState.ROUTED_TO_TRADITIONAL: [ClaimState.TRADITIONAL_PROCESSING_ACTIVE],
    ClaimState.TRADITIONAL_PROCESSING_ACTIVE: [ClaimState.CLAIM_CLOSED],
    ClaimState.CLAIM_CLOSED: []  # Terminal state
}
