"""
Adjustor service for managing adjustor operations and claim reviews.
"""
from src.api.services.base_service import BaseService
from src.api.models.claim import Claim
from src.api.models.customer import Customer
from src.api.models.vehicle import Vehicle
from src.api.models.claim_event import ClaimEvent
from src.api.constants import ClaimState, ClaimAction, ActorType
from sqlalchemy import func, or_, cast, String
from datetime import date, datetime
from typing import Dict, List, Tuple, Optional


class AdjustorService(BaseService):
    """Service for adjustor-related operations"""

    def get_pending_claims(
        self,
        adjustor_id: str,
        filters: Dict
    ) -> Tuple[List[Tuple[Claim, Customer, Vehicle]], int]:
        """
        Get claims pending human review with filtering and pagination.

        Args:
            adjustor_id: Adjustor identifier
            filters: Dictionary containing search, sort, filter, page, and limit

        Returns:
            Tuple of (list of (Claim, Customer, Vehicle) tuples, total_count)
        """
        # Base query
        query = self.db.query(
            Claim, Customer, Vehicle
        ).join(
            Customer, Claim.customer_id == Customer.customer_id
        ).join(
            Vehicle, Claim.vin == Vehicle.vin
        ).filter(
            Claim.current_status == ClaimState.HUMAN_REVIEW_PENDING.value
        )

        # Filter by assigned adjustor (or show unassigned claims to all adjustors)
        query = query.filter(
            or_(
                Claim.assigned_adjustor_id == adjustor_id,
                Claim.assigned_adjustor_id.is_(None)
            )
        )

        # Apply search filter
        search = filters.get('search')
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    cast(Claim.claim_id, String).like(search_pattern),
                    Customer.fname.like(search_pattern),
                    Customer.lname.like(search_pattern),
                    Claim.vin.like(search_pattern),
                    Claim.policy_number.like(search_pattern)
                )
            )

        # Get total count before pagination
        total_count = query.count()

        # Apply sort
        sort_option = filters.get('sort', 'oldest')
        if sort_option == 'oldest':
            query = query.order_by(Claim.fnol_date.asc(), Claim.fnol_time.asc())
        elif sort_option == 'newest':
            query = query.order_by(Claim.fnol_date.desc(), Claim.fnol_time.desc())
        elif sort_option == 'highest_amount':
            query = query.order_by(Claim.claim_amount.desc())
        elif sort_option == 'lowest_amount':
            query = query.order_by(Claim.claim_amount.asc())
        elif sort_option == 'customer_name':
            query = query.order_by(Customer.lname.asc(), Customer.fname.asc())

        # Apply pagination
        page = filters.get('page', 1)
        limit = filters.get('limit', 20)
        offset = (page - 1) * limit

        query = query.offset(offset).limit(limit)

        results = query.all()
        return results, total_count

    def get_statistics(self, adjustor_id: str) -> Dict:
        """
        Get workload statistics for an adjustor.

        Args:
            adjustor_id: Adjustor identifier

        Returns:
            Dictionary with statistics
        """
        # Pending reviews (assigned to this adjustor or unassigned)
        pending = self.db.query(Claim).filter(
            Claim.current_status == ClaimState.HUMAN_REVIEW_PENDING.value,
            or_(
                Claim.assigned_adjustor_id == adjustor_id,
                Claim.assigned_adjustor_id.is_(None)
            )
        ).count()

        # Completed today (events with adjustor actions by this adjustor)
        today = date.today()
        completed_today = self.db.query(ClaimEvent).filter(
            ClaimEvent.action.in_([
                ClaimAction.DENIED_APPEAL.value,
                ClaimAction.REVISED_ESTIMATE.value,
                ClaimAction.APPROVED_APPEAL.value
            ]),
            ClaimEvent.action_by == ActorType.ADJUSTOR.value,
            ClaimEvent.action_by_identity == adjustor_id,
            ClaimEvent.event_date == today
        ).count()

        # Completed this week (last 7 days)
        from datetime import timedelta
        week_ago = today - timedelta(days=7)
        completed_this_week = self.db.query(ClaimEvent).filter(
            ClaimEvent.action.in_([
                ClaimAction.DENIED_APPEAL.value,
                ClaimAction.REVISED_ESTIMATE.value,
                ClaimAction.APPROVED_APPEAL.value
            ]),
            ClaimEvent.action_by == ActorType.ADJUSTOR.value,
            ClaimEvent.action_by_identity == adjustor_id,
            ClaimEvent.event_date >= week_ago
        ).count()

        # Total reviews all time
        total_reviews = self.db.query(ClaimEvent).filter(
            ClaimEvent.action.in_([
                ClaimAction.DENIED_APPEAL.value,
                ClaimAction.REVISED_ESTIMATE.value,
                ClaimAction.APPROVED_APPEAL.value
            ]),
            ClaimEvent.action_by == ActorType.ADJUSTOR.value,
            ClaimEvent.action_by_identity == adjustor_id
        ).count()

        # TODO: Calculate average review time (requires tracking review start/end)
        average_review_time = 8.0  # Placeholder: 8 minutes

        return {
            "pending_reviews": pending,
            "completed_today": completed_today,
            "completed_this_week": completed_this_week,
            "average_review_time_minutes": average_review_time,
            "total_reviews_all_time": total_reviews
        }

    def assign_claim_to_adjustor(
        self,
        claim_id: int,
        adjustor_id: str
    ) -> Claim:
        """
        Assign a claim to an adjustor (P2 feature, optional).

        Args:
            claim_id: Claim identifier
            adjustor_id: Adjustor identifier

        Returns:
            Updated Claim object
        """
        claim = self.db.query(Claim).filter(
            Claim.claim_id == claim_id
        ).first()

        if not claim:
            raise ValueError(f"Claim {claim_id} not found")

        # TODO: Add assigned_adjustor_id field to Claim model for P2
        # claim.assigned_adjustor_id = adjustor_id

        self.commit()
        return claim
