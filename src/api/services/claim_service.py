"""
Claim service for claim CRUD operations and state management.
"""
from sqlalchemy.orm import Session
from src.api.models.claim import Claim, ClaimImage
from src.api.models.damage import Damage
from src.api.schemas.claim import ClaimCreate, ClaimUpdate
from src.api.services.base_service import BaseService
from src.api.services.event_logger import log_event
from src.api.services.state_machine import validate_transition, get_valid_transitions
from src.api.constants import ClaimState, ClaimAction, ActorType
from src.api.exceptions import ResourceNotFoundError, StateTransitionError
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal

class ClaimService(BaseService):
    """Service for claim operations"""

    @log_event(action=ClaimAction.CREATE_CLAIM, actor_type=ActorType.CUSTOMER)
    def create_claim(self, customer_id: int, claim_data: ClaimCreate) -> Claim:
        """
        Create new claim in draft state and set labor rate based on customer's state.

        Args:
            customer_id: Customer ID
            claim_data: Claim creation data

        Returns:
            Created Claim instance
        """
        from src.api.models.customer import Customer
        from src.api.services.cost_service import STATE_LABOR_RATES

        # Get customer to retrieve state
        customer = self.db.query(Customer).filter(
            Customer.customer_id == customer_id
        ).first()

        if not customer:
            from src.api.exceptions import ResourceNotFoundError
            raise ResourceNotFoundError("Customer", customer_id)

        # Determine labor rate from customer's state
        customer_state = customer.state or "CA"  # Default to CA if no state
        labor_rate = STATE_LABOR_RATES.get(customer_state, STATE_LABOR_RATES["DEFAULT"])

        claim = Claim(
            customer_id=customer_id,
            vin=claim_data.vin,
            policy_number=claim_data.policy_number,
            fnol_date=claim_data.fnol_date,
            fnol_time=claim_data.fnol_time,
            date_of_damage=claim_data.date_of_damage,
            is_drivable=claim_data.is_drivable,
            incident_description=claim_data.incident_description,  # NEW: Save customer's description
            current_status=ClaimState.DRAFT.value,
            state_avg_labor_cost=Decimal(str(labor_rate)),  # NEW
            labor_rate_state=customer_state,  # NEW
            labor_rate_source="customer_state"  # NEW
        )

        self.db.add(claim)
        self.commit()
        self.refresh(claim)

        self.logger.info(f"Created claim {claim.claim_id} in draft state for customer {customer_id} with labor rate ${labor_rate}/hr ({customer_state})")
        return claim

    @log_event(action=ClaimAction.SUBMIT_CLAIM, actor_type=ActorType.CUSTOMER)
    def submit_claim(self, claim_id: int, customer_id: int) -> Claim:
        """
        Submit claim for processing (DRAFT -> FNOL transition).

        Args:
            claim_id: Claim ID
            customer_id: Customer ID (for verification)

        Returns:
            Updated Claim instance

        Raises:
            ResourceNotFoundError: If claim not found
            StateTransitionError: If claim not in draft state
        """
        claim = self.get_claim(claim_id)

        # Verify claim belongs to customer
        if claim.customer_id != customer_id:
            raise ResourceNotFoundError("Claim", claim_id)

        # Transition from draft to FNOL
        claim = self.update_claim_status(
            claim_id=claim_id,
            new_status=ClaimState.FNOL,
            actor_type=ActorType.CUSTOMER,
            actor_identity=f"customer_{customer_id}",
            comments="Claim submitted for processing"
        )

        self.logger.info(f"Claim {claim_id} submitted for processing (DRAFT -> FNOL)")
        return claim

    def get_claim(self, claim_id: int) -> Claim:
        """Get claim by ID"""
        claim = self.db.query(Claim).filter(Claim.claim_id == claim_id).first()
        if not claim:
            raise ResourceNotFoundError("Claim", claim_id)
        return claim

    @staticmethod
    def get_effective_estimate(damage: Damage) -> Dict[str, Any]:
        """
        Get the effective estimate for a damage (adjustor if available, else AI).

        Args:
            damage: Damage model instance

        Returns:
            Dictionary with effective estimate values and source (keys match DamageResponse schema)
        """
        if damage.adjustor_labor_hours is not None:
            # Adjustor has modified this damage
            return {
                'labor_hours': float(damage.adjustor_labor_hours),
                'estimated_parts_cost': float(damage.adjustor_parts_cost),
                'estimated_total_cost': float(damage.adjustor_total_cost),
                'estimate_source': 'adjustor'
            }
        else:
            # Use original AI estimate
            return {
                'labor_hours': float(damage.ai_labor_hours),
                'estimated_parts_cost': float(damage.ai_parts_cost),
                'estimated_total_cost': float(damage.ai_total_cost),
                'estimate_source': 'ai'
            }

    def get_claim_with_damages(self, claim_id: int) -> Dict[str, Any]:
        """
        Get claim by ID with damage assessment included.

        Args:
            claim_id: Claim ID

        Returns:
            Dictionary with claim data and damage_assessment

        Raises:
            ResourceNotFoundError: If claim doesn't exist
        """
        claim = self.get_claim(claim_id)

        # Get all damages for this claim
        damages = self.db.query(Damage).filter(Damage.claim_id == claim_id).all()

        # Build damage assessment
        damage_assessment = None
        if damages:
            # Calculate total using effective estimates (adjustor if available, else AI)
            total_cost = sum(self.get_effective_estimate(d)['estimated_total_cost'] for d in damages)

            self.logger.info(f"Building damage assessment with NEW DUAL-COLUMN SCHEMA for {len(damages)} damages")
            damage_list = []
            for d in damages:
                effective = self.get_effective_estimate(d)

                try:
                    damage_dict = {
                        'damage_id': d.damage_id,
                        'estimate_id': d.estimate_id,
                        'image_id': d.image_id,
                        'estimate_type': d.estimate_type,

                        # YOLO Detection Fields
                        'damage_class': d.damage_class,
                        'damage_confidence': float(d.damage_confidence) if d.damage_confidence else None,
                        'damage_part': d.damage_part,
                        'bounding_box': {
                            'x': d.bounding_box_x,
                            'y': d.bounding_box_y,
                            'width': d.bounding_box_width,
                            'height': d.bounding_box_height
                        } if all([d.bounding_box_x is not None, d.bounding_box_y is not None,
                                  d.bounding_box_width is not None, d.bounding_box_height is not None]) else None,

                        # Assessment Fields
                        'internal_damage_probability': float(d.internal_damage_probability) if d.internal_damage_probability else None,
                        'severity': float(d.severity),
                        'recommended_action': d.recommended_action,
                        'reasoning': d.reasoning,
                        'car_side': d.car_side,
                        'assessment_confidence': float(d.assessment_confidence) if d.assessment_confidence else None,
                        'damage_summary': d.damage_summary,  # Damage assessment summary from LLM agent

                        # Effective Cost Breakdown (adjustor if available, else AI)
                        'labor_hours': effective['labor_hours'],
                        'estimated_parts_cost': effective['estimated_parts_cost'],
                        'estimated_total_cost': effective['estimated_total_cost'],
                        'estimate_source': effective['estimate_source'],

                        # AI Estimate (baseline - always included)
                        'ai_labor_hours': float(d.ai_labor_hours),
                        'ai_parts_cost': float(d.ai_parts_cost),
                        'ai_total_cost': float(d.ai_total_cost),

                        # Adjustor Estimate (if reviewed)
                        'adjustor_labor_hours': float(d.adjustor_labor_hours) if d.adjustor_labor_hours is not None else None,
                        'adjustor_parts_cost': float(d.adjustor_parts_cost) if d.adjustor_parts_cost is not None else None,
                        'adjustor_total_cost': float(d.adjustor_total_cost) if d.adjustor_total_cost is not None else None,
                        'reviewed_by_adjustor': d.reviewed_by_adjustor,
                        'adjustor_note': d.adjustor_note,
                        'reviewed_at': d.reviewed_at.isoformat() if d.reviewed_at else None,

                        # Annotated Image
                        'annotated_image_id': d.annotated_image_id,

                        # DEPRECATED field
                        'avg_labor_cost': None
                    }

                    # Debug: log what we're adding
                    self.logger.info(f"Damage {d.damage_id}: reviewed_by_adjustor={damage_dict.get('reviewed_by_adjustor')}, ai_total_cost={damage_dict.get('ai_total_cost')}")

                    damage_list.append(damage_dict)
                except Exception as e:
                    self.logger.error(f"!!!!! ERROR building damage dict for damage_id {d.damage_id}: {e}", exc_info=True)
                    print(f"!!!!! ERROR building damage dict for damage_id {d.damage_id}: {e}")
                    import traceback
                    traceback.print_exc()
                    # Fall back to minimal dict
                    damage_dict = {
                        'damage_id': d.damage_id,
                        'estimate_id': d.estimate_id,
                        'image_id': d.image_id,
                        'estimate_type': d.estimate_type,
                        'damage_part': d.damage_part,
                        'severity': float(d.severity),
                        'estimated_total_cost': effective['estimated_total_cost'],
                        'labor_hours': effective['labor_hours'],
                        'estimated_parts_cost': effective['estimated_parts_cost'],
                    }
                    damage_list.append(damage_dict)

            damage_assessment = {
                'total_estimated_cost': total_cost,
                'damage_count': len(damages),
                'damages': damage_list
            }

        # Build claim dict
        claim_dict = {
            'claim_id': claim.claim_id,
            'customer_id': claim.customer_id,
            'vin': claim.vin,
            'policy_number': claim.policy_number,
            'fnol_date': claim.fnol_date,
            'fnol_time': claim.fnol_time,
            'date_of_damage': claim.date_of_damage,
            'is_drivable': claim.is_drivable,
            'incident_description': claim.incident_description,
            'current_status': claim.current_status,
            'claim_closed': claim.claim_closed,
            'claim_closed_date': claim.claim_closed_date,
            'ai_estimate_accepted': claim.ai_estimate_accepted,
            'routed_to_traditional': claim.routed_to_traditional,
            'reason_routing_to_traditional': claim.reason_routing_to_traditional,
            'active_estimate_id': claim.active_estimate_id,
            'claim_amount': claim.claim_amount,
            'actual_claim_amount': claim.actual_claim_amount,
            'state_avg_labor_cost': float(claim.state_avg_labor_cost) if claim.state_avg_labor_cost else None,
            'labor_rate_state': claim.labor_rate_state,
            'labor_rate_source': claim.labor_rate_source,
            'appeal_count': claim.appeal_count,  # NEW
            'first_appeal_reason': claim.first_appeal_reason,  # NEW
            'first_appeal_date': claim.first_appeal_date,  # NEW
            'second_appeal_reason': claim.second_appeal_reason,  # NEW
            'second_appeal_date': claim.second_appeal_date,  # NEW
            'damage_assessment': damage_assessment
        }

        self.logger.info(f"Retrieved claim {claim_id} with {len(damages)} damages")
        return claim_dict

    def get_customer_claims(
        self,
        customer_id: int,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Claim]:
        """Get claims for customer with optional filtering"""
        query = self.db.query(Claim).filter(Claim.customer_id == customer_id)

        if status:
            query = query.filter(Claim.current_status == status)

        return query.order_by(Claim.claim_id.desc()).offset(offset).limit(limit).all()

    def update_claim_status(
        self,
        claim_id: int,
        new_status: ClaimState,
        actor_type: ActorType = ActorType.ADMIN,
        actor_identity: str = "system",
        comments: str = ""
    ) -> Claim:
        """
        Update claim status with state machine validation.

        Args:
            claim_id: Claim ID
            new_status: Target state
            actor_type: Who is making the change
            actor_identity: Actor identifier
            comments: Optional comments

        Returns:
            Updated Claim instance

        Raises:
            StateTransitionError: If transition is invalid
        """
        claim = self.get_claim(claim_id)
        current_status = ClaimState(claim.current_status)

        # Validate state transition
        if not validate_transition(current_status, new_status):
            raise StateTransitionError(
                current_status.value,
                new_status.value,
                get_valid_transitions(current_status)
            )

        # Update status
        claim.current_status = new_status.value
        self.commit()

        self.logger.info(
            f"Claim {claim_id} transitioned: {current_status.value} → {new_status.value}"
        )

        return claim

    def get_claim_images(self, claim_id: int) -> List[ClaimImage]:
        """Get all images for a claim"""
        return self.db.query(ClaimImage).filter(ClaimImage.claim_id == claim_id).all()

    @log_event(action=ClaimAction.CLAIM_DELETED, actor_type=ActorType.CUSTOMER)
    def delete_claim(self, claim_id: int, customer_id: int) -> None:
        """
        Delete a claim (only allowed in draft state).

        Args:
            claim_id: Claim ID
            customer_id: Customer ID (for verification)

        Raises:
            ResourceNotFoundError: If claim not found
            StateTransitionError: If claim is not in draft state
        """
        claim = self.get_claim(claim_id)

        # Verify claim belongs to customer
        if claim.customer_id != customer_id:
            raise ResourceNotFoundError("Claim", claim_id)

        # Only allow deletion of draft claims
        if claim.current_status != ClaimState.DRAFT.value:
            from src.api.exceptions import ValidationError
            raise ValidationError(
                f"Only draft claims can be deleted. Current status: {claim.current_status}"
            )

        # Delete physical image files from filesystem
        from pathlib import Path
        from src.api.config import settings
        images_root = Path(settings.IMAGES_ROOT_FOLDER)
        claim_dir = images_root / str(claim_id)

        if claim_dir.exists() and claim_dir.is_dir():
            import shutil
            shutil.rmtree(claim_dir)
            self.logger.info(f"Deleted image directory for claim {claim_id}")

        # Delete claim from database (cascade will delete images, damages, events)
        self.db.delete(claim)
        self.commit()

        self.logger.info(f"Deleted claim {claim_id} for customer {customer_id}")

    def accept_estimate(self, claim_id: int, customer_id: int) -> Claim:
        """
        Accept AI estimate and process for payment.

        Transitions:
        1. customer_decision_pending → loss_approved (with ACCEPT_ESTIMATE event)
        2. loss_approved → sent_for_payment (with INITIATE_PAYMENT event)

        Args:
            claim_id: Claim ID
            customer_id: Customer ID (for verification)

        Returns:
            Updated Claim instance

        Raises:
            ResourceNotFoundError: If claim not found
            StateTransitionError: If claim is not in customer_decision_pending state
        """
        from src.api.models.claim_event import ClaimEvent
        from datetime import date, datetime

        claim = self.get_claim(claim_id)

        # Verify claim belongs to customer
        if claim.customer_id != customer_id:
            raise ResourceNotFoundError("Claim", claim_id)

        # Verify claim is in customer_decision_pending state
        if claim.current_status != ClaimState.CUSTOMER_DECISION_PENDING.value:
            from src.api.exceptions import StateTransitionError
            raise StateTransitionError(
                claim.current_status,
                ClaimState.LOSS_APPROVED.value,
                [ClaimState.LOSS_APPROVED.value]
            )

        # Calculate claim_amount from damages if not already set
        if claim.claim_amount is None:
            from src.api.models.damage import Damage
            from sqlalchemy import func

            total_ai_cost = self.db.query(func.sum(Damage.ai_total_cost)).filter(
                Damage.claim_id == claim_id
            ).scalar()

            if total_ai_cost:
                claim.claim_amount = float(total_ai_cost)
                self.logger.info(f"Calculated claim_amount for claim {claim_id}: ${claim.claim_amount:.2f}")

        # Transition 1: customer_decision_pending → loss_approved
        claim.current_status = ClaimState.LOSS_APPROVED.value
        claim.ai_estimate_accepted = True
        self.commit()

        # Log ACCEPT_ESTIMATE event
        amount_str = f"${claim.claim_amount:.2f}" if claim.claim_amount is not None else "TBD"
        event1 = ClaimEvent(
            claim_id=claim_id,
            event_date=date.today(),
            event_time=datetime.now().time(),
            status=claim.current_status,
            action=ClaimAction.ACCEPT_ESTIMATE.value,
            action_by=ActorType.CUSTOMER.value,
            action_by_identity=f"customer_{customer_id}",
            comments=f"Customer accepted AI estimate of {amount_str}"
        )
        self.db.add(event1)
        self.db.commit()

        self.logger.info(
            f"Claim {claim_id} transitioned to LOSS_APPROVED "
            f"(customer {customer_id} accepted estimate)"
        )

        # Transition 2: loss_approved → sent_for_payment
        claim.current_status = ClaimState.SENT_FOR_PAYMENT.value
        self.commit()

        # Log INITIATE_PAYMENT event
        event2 = ClaimEvent(
            claim_id=claim_id,
            event_date=date.today(),
            event_time=datetime.now().time(),
            status=claim.current_status,
            action=ClaimAction.INITIATE_PAYMENT.value,
            action_by=ActorType.ADMIN.value,
            action_by_identity="system",
            comments=f"Payment processing initiated for {amount_str}"
        )
        self.db.add(event2)
        self.db.commit()

        self.logger.info(
            f"Claim {claim_id} transitioned to SENT_FOR_PAYMENT "
            f"(payment processing initiated)"
        )

        return claim

    def appeal_estimate(self, claim_id: int, customer_id: int, reason: str) -> dict:
        """
        Appeal AI or human-reviewed estimate.

        First Appeal (AI estimate):
        - customer_decision_pending → loss_appealed (with APPEAL_ESTIMATE event)
        - loss_appealed → human_review_pending (automatic transition for human review)

        Second Appeal (Human-reviewed estimate):
        - customer_decision_pending → loss_appealed (with APPEAL_ESTIMATE event)
        - loss_appealed → routed_to_traditional (route to traditional processing)

        Args:
            claim_id: Claim ID
            customer_id: Customer ID (for verification)
            reason: Customer's reason for appealing

        Returns:
            Dictionary with claim and appeal_type ('first' or 'second')

        Raises:
            ResourceNotFoundError: If claim not found
            StateTransitionError: If claim is not in customer_decision_pending state
        """
        from src.api.models.claim_event import ClaimEvent
        from datetime import date, datetime

        claim = self.get_claim(claim_id)

        # Verify claim belongs to customer
        if claim.customer_id != customer_id:
            raise ResourceNotFoundError("Claim", claim_id)

        # Verify claim is in customer_decision_pending state
        if claim.current_status != ClaimState.CUSTOMER_DECISION_PENDING.value:
            from src.api.exceptions import StateTransitionError
            raise StateTransitionError(
                claim.current_status,
                ClaimState.LOSS_APPEALED.value,
                [ClaimState.LOSS_APPEALED.value]
            )

        # Determine if this is first or second appeal by checking claim events
        events = self.db.query(ClaimEvent).filter(
            ClaimEvent.claim_id == claim_id
        ).all()

        # Check if there was a human review completed event (indicates second appeal)
        has_human_review = any(
            event.action == ClaimAction.REVISED_ESTIMATE.value or
            event.status == ClaimState.HUMAN_REVIEW_COMPLETED.value
            for event in events
        )

        appeal_type = 'second' if has_human_review else 'first'

        # Update appeal tracking fields in claim
        claim.appeal_count = 2 if has_human_review else 1
        if appeal_type == 'first':
            claim.first_appeal_reason = reason
            claim.first_appeal_date = date.today()
        else:
            claim.second_appeal_reason = reason
            claim.second_appeal_date = date.today()

        # Transition: customer_decision_pending → loss_appealed
        claim.current_status = ClaimState.LOSS_APPEALED.value
        self.commit()

        # Log APPEAL_ESTIMATE event
        event_comment = (
            "Customer appealed human-reviewed estimate" if has_human_review
            else "Customer appealed AI estimate"
        )
        event_comment += f". Reason: {reason}"

        event1 = ClaimEvent(
            claim_id=claim_id,
            event_date=date.today(),
            event_time=datetime.now().time(),
            status=claim.current_status,
            action=ClaimAction.APPEAL_ESTIMATE.value,
            action_by=ActorType.CUSTOMER.value,
            action_by_identity=f"customer_{customer_id}",
            comments=event_comment
        )
        self.db.add(event1)
        self.db.commit()

        self.logger.info(
            f"Claim {claim_id} transitioned to LOSS_APPEALED "
            f"({appeal_type} appeal by customer {customer_id})"
        )

        # Second transition based on appeal type
        if appeal_type == 'first':
            # First appeal: route to human review
            claim.current_status = ClaimState.HUMAN_REVIEW_PENDING.value
            self.commit()

            # Log FLAG_FOR_HUMAN_REVIEW event
            event2 = ClaimEvent(
                claim_id=claim_id,
                event_date=date.today(),
                event_time=datetime.now().time(),
                status=claim.current_status,
                action=ClaimAction.FLAG_FOR_HUMAN_REVIEW.value,
                action_by=ActorType.AI_AGENT.value,
                action_by_identity="system",
                comments="First appeal - flagged for human adjuster review"
            )
            self.db.add(event2)
            self.db.commit()

            self.logger.info(
                f"Claim {claim_id} transitioned to HUMAN_REVIEW_PENDING "
                f"(first appeal - human review required)"
            )
        else:
            # Second appeal: route to traditional processing
            claim.current_status = ClaimState.ROUTED_TO_TRADITIONAL.value
            claim.routed_to_traditional = True
            claim.reason_routing_to_traditional = "Customer appealed human-reviewed estimate (second appeal)"
            self.commit()

            # Log ROUTE_TO_TRADITIONAL event
            event2 = ClaimEvent(
                claim_id=claim_id,
                event_date=date.today(),
                event_time=datetime.now().time(),
                status=claim.current_status,
                action=ClaimAction.ROUTE_TO_TRADITIONAL.value,
                action_by=ActorType.ADMIN.value,
                action_by_identity="system",
                comments="Second appeal - routed to traditional claim processing"
            )
            self.db.add(event2)
            self.db.commit()

            self.logger.info(
                f"Claim {claim_id} transitioned to ROUTED_TO_TRADITIONAL "
                f"(second appeal - traditional processing)"
            )

        return {
            "claim": claim,
            "appeal_type": appeal_type
        }

    def complete_review(self, claim_id: int, review_data: Dict) -> Dict:
        """
        Complete human review of a claim and transition to appropriate state.

        Args:
            claim_id: Claim identifier
            review_data: Dictionary with review action, notes, and optional revised estimate

        Returns:
            Dictionary with claim status and event information

        Raises:
            ResourceNotFoundError: If claim not found
            ValueError: If claim not in human_review_pending state
        """
        # Get claim
        claim = self.get_claim(claim_id)

        # Validate state
        if claim.current_status != ClaimState.HUMAN_REVIEW_PENDING.value:
            raise ValueError(
                f"Claim must be in human_review_pending state, "
                f"currently: {claim.current_status}"
            )

        # Extract review data
        action = review_data['action']
        customer_note = review_data['customer_note']
        internal_note = review_data['internal_note']
        adjustor_id = review_data.get('adjustor_id', 'UNKNOWN')

        # Update claim status to human_review_completed first
        claim.current_status = ClaimState.HUMAN_REVIEW_COMPLETED.value

        # If revised estimate, update claim amount
        revised_total = None
        if action == 'revised_estimate' and review_data.get('revised_estimate_total'):
            revised_total = review_data['revised_estimate_total']
            claim.claim_amount = revised_total

        # Update labor rate if changed
        if review_data.get('labor_rate_state'):
            claim.labor_rate_state = review_data['labor_rate_state']
        if review_data.get('state_avg_labor_cost'):
            claim.state_avg_labor_cost = review_data['state_avg_labor_cost']

        # Update individual damages if provided
        damages_data = review_data.get('damages')
        self.logger.info(f"Processing damage updates for claim {claim_id}: {damages_data}")

        if damages_data:
            from src.api.models.damage import Damage
            for damage_update in damages_data:
                damage_id = damage_update['damage_id']

                # Check if this is a manual damage (string ID starting with "manual_")
                if isinstance(damage_id, str) and damage_id.startswith('manual_'):
                    # Create new manual damage entry
                    self.logger.info(f"Creating manual damage: {damage_update}")

                    # Map severity string to numeric value
                    severity_map = {'light': 0.3, 'moderate': 0.6, 'severe': 0.9}
                    severity_value = severity_map.get(damage_update.get('severity'), 0.5)

                    # Generate estimate_id for manual entry
                    estimate_id = f"manual_{claim_id}_{damage_id}"

                    labor_hours = damage_update.get('labor_hours', 0)
                    parts_cost = damage_update.get('parts_cost', 0)
                    labor_cost = float(labor_hours) * float(claim.state_avg_labor_cost or 0)
                    total_cost = labor_cost + float(parts_cost)

                    new_damage = Damage(
                        claim_id=claim_id,
                        estimate_id=estimate_id,
                        image_id=damage_update.get('image_id') or 'manual_entry',
                        damage_part=damage_update.get('damage_part') or damage_update.get('location', 'Unknown'),
                        severity=severity_value,
                        damage_confidence=1.0,  # Manual entries have full confidence
                        estimate_type='human',
                        # Bounding box not applicable for manual entries
                        bounding_box_x=None,
                        bounding_box_y=None,
                        bounding_box_width=None,
                        bounding_box_height=None,
                        # AI columns - set to 0 for manual entries (NOT NULL constraint)
                        ai_labor_hours=0.0,
                        ai_parts_cost=0.0,
                        ai_total_cost=0.0,
                        # Store actual values in adjustor columns
                        adjustor_labor_hours=labor_hours,
                        adjustor_parts_cost=parts_cost,
                        adjustor_total_cost=total_cost,
                        adjustor_note=damage_update.get('adjustor_note'),
                        reviewed_by_adjustor=True,
                        reviewed_at=datetime.now()
                    )

                    self.db.add(new_damage)
                    self.logger.info(f"Created manual damage for claim {claim_id}: {estimate_id}")

                else:
                    # Update existing damage
                    damage = self.db.query(Damage).filter(
                        Damage.damage_id == damage_id
                    ).first()

                    if damage:
                        # Update ADJUSTOR columns (AI columns remain untouched)
                        if 'labor_hours' in damage_update:
                            damage.adjustor_labor_hours = damage_update['labor_hours']
                        if 'parts_cost' in damage_update:
                            damage.adjustor_parts_cost = damage_update['parts_cost']

                        # Calculate adjustor total cost
                        if damage.adjustor_labor_hours is not None and damage.adjustor_parts_cost is not None:
                            labor_cost = float(damage.adjustor_labor_hours) * float(claim.state_avg_labor_cost or 0)
                            damage.adjustor_total_cost = labor_cost + float(damage.adjustor_parts_cost)

                        if 'adjustor_note' in damage_update:
                            damage.adjustor_note = damage_update['adjustor_note']

                        # Mark as reviewed by adjustor
                        damage.reviewed_by_adjustor = True
                        damage.reviewed_at = datetime.now()

                        self.logger.info(
                            f"Updated damage {damage.damage_id}: "
                            f"AI: {damage.ai_labor_hours}h/${damage.ai_parts_cost} → "
                            f"Adjustor: {damage.adjustor_labor_hours}h/${damage.adjustor_parts_cost} "
                            f"(reviewed_by_adjustor={damage.reviewed_by_adjustor})"
                        )

        self.commit()

        # Create event for human review completion
        from src.api.models.claim_event import ClaimEvent

        # Determine the appropriate action enum value
        if action == 'denied_appeal':
            action_enum = ClaimAction.DENIED_APPEAL
        elif action == 'route_to_traditional':
            action_enum = ClaimAction.ROUTE_TO_TRADITIONAL
        else:
            action_enum = ClaimAction.REVISED_ESTIMATE

        event = ClaimEvent(
            claim_id=claim_id,
            event_date=date.today(),
            event_time=datetime.now().time(),
            status=ClaimState.HUMAN_REVIEW_COMPLETED.value,
            action=action_enum.value,
            action_by=ActorType.ADJUSTOR.value,
            action_by_identity=adjustor_id,
            comments=f"Customer Note: {customer_note} | Internal Note: {internal_note}"
        )

        self.db.add(event)
        self.commit()

        # Handle routing to traditional processing
        if action == 'route_to_traditional':
            claim.current_status = ClaimState.ROUTED_TO_TRADITIONAL.value
            claim.routed_to_traditional = True
            claim.reason_routing_to_traditional = customer_note
            self.commit()

            # Create event for routing to traditional
            event2 = ClaimEvent(
                claim_id=claim_id,
                event_date=date.today(),
                event_time=datetime.now().time(),
                status=ClaimState.ROUTED_TO_TRADITIONAL.value,
                action=ClaimAction.ROUTE_TO_TRADITIONAL.value,
                action_by=ActorType.ADJUSTOR.value,
                action_by_identity=adjustor_id,
                comments=f"Routed to traditional processing: {customer_note}"
            )

            self.db.add(event2)
            self.commit()

            self.logger.info(
                f"Routed claim {claim_id} to traditional processing"
            )

            return {
                "claim_id": claim_id,
                "current_status": claim.current_status,
                "next_status": ClaimState.ROUTED_TO_TRADITIONAL.value,
                "revised_estimate_total": None,
                "event_id": event.event_id
            }

        # Transition to customer_decision_pending (for denied_appeal or revised_estimate)
        claim.current_status = ClaimState.CUSTOMER_DECISION_PENDING.value
        self.commit()

        # Create event for transition to customer decision pending
        event2 = ClaimEvent(
            claim_id=claim_id,
            event_date=date.today(),
            event_time=datetime.now().time(),
            status=ClaimState.CUSTOMER_DECISION_PENDING.value,
            action=ClaimAction.PRESENT_ESTIMATE_TO_CUSTOMER.value,
            action_by=ActorType.AI_AGENT.value,
            action_by_identity="system",
            comments="Human review completed, presenting estimate to customer"
        )

        self.db.add(event2)
        self.commit()

        self.logger.info(
            f"Completed review for claim {claim_id} with action {action}"
        )

        return {
            "claim_id": claim_id,
            "current_status": claim.current_status,
            "next_status": ClaimState.CUSTOMER_DECISION_PENDING.value,
            "revised_estimate_total": revised_total or claim.claim_amount,
            "event_id": event.event_id
        }

    def update_labor_rate(
        self,
        claim_id: int,
        new_labor_rate: Decimal,
        adjustor_id: str
    ) -> Claim:
        """
        Update claim labor rate (adjustor override).
        Recalculates all damage costs using new rate.

        Args:
            claim_id: Claim ID
            new_labor_rate: New labor rate in $/hour
            adjustor_id: Adjustor making the change

        Returns:
            Updated Claim instance

        Raises:
            ResourceNotFoundError: If claim not found
        """
        claim = self.get_claim(claim_id)

        old_rate = claim.state_avg_labor_cost

        # Update claim labor rate
        claim.state_avg_labor_cost = new_labor_rate
        claim.labor_rate_source = "adjustor_override"

        # Recalculate all damages' total costs
        for damage in claim.damages:
            labor_cost = float(damage.labor_hours) * float(new_labor_rate)
            damage.estimated_total_cost = Decimal(str(labor_cost)) + damage.estimated_parts_cost

        self.commit()

        # Log event
        from src.api.models.claim_event import ClaimEvent
        event = ClaimEvent(
            claim_id=claim_id,
            event_date=date.today(),
            event_time=datetime.now().time(),
            status=claim.current_status,
            action=ClaimAction.UPDATE_LABOR_RATE.value,
            action_by=ActorType.ADJUSTOR.value,
            action_by_identity=adjustor_id,
            comments=f"Labor rate changed from ${old_rate}/hr to ${new_labor_rate}/hr"
        )
        self.db.add(event)
        self.db.commit()

        self.logger.info(
            f"Updated labor rate for claim {claim_id}: ${old_rate}/hr → ${new_labor_rate}/hr"
        )

        return claim
