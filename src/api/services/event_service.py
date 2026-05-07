"""
Event service for claim event audit trail.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.api.models.claim_event import ClaimEvent
from src.api.services.base_service import BaseService
from src.api.constants import ActorType
from typing import Optional, List, Dict

class EventService(BaseService):
    """Service for claim event operations"""

    def get_claim_events(
        self,
        claim_id: int,
        actor_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ClaimEvent]:
        """
        Get event history for a claim.

        Args:
            claim_id: Claim ID
            actor_type: Filter by actor type (customer, AI agent, adjustor, admin)
            limit: Maximum results (default: 100, max: 500)
            offset: Pagination offset

        Returns:
            List of ClaimEvent instances in chronological order
        """
        # Cap limit at 500
        limit = min(limit, 500)

        query = self.db.query(ClaimEvent).filter(ClaimEvent.claim_id == claim_id)

        # Filter by actor type if provided
        if actor_type:
            # Validate actor type
            valid_types = [e.value for e in ActorType]
            if actor_type not in valid_types:
                self.logger.warning(f"Invalid actor_type: {actor_type}")
            else:
                query = query.filter(ClaimEvent.action_by == actor_type)

        # Order chronologically (oldest first)
        query = query.order_by(ClaimEvent.event_date.asc(), ClaimEvent.event_time.asc())

        # Pagination
        events = query.offset(offset).limit(limit).all()

        self.logger.info(
            f"Retrieved {len(events)} events for claim {claim_id} "
            f"(actor_type={actor_type}, limit={limit}, offset={offset})"
        )

        return events

    def get_event_statistics(self, claim_id: int) -> Dict[str, int]:
        """
        Get event statistics by actor type for a claim.

        Args:
            claim_id: Claim ID

        Returns:
            Dictionary with counts by actor type
        """
        # Query counts grouped by actor type
        results = self.db.query(
            ClaimEvent.action_by,
            func.count(ClaimEvent.event_id).label('count')
        ).filter(
            ClaimEvent.claim_id == claim_id
        ).group_by(
            ClaimEvent.action_by
        ).all()

        # Convert to dictionary
        stats = {
            'customer_actions': 0,
            'ai_actions': 0,
            'adjustor_actions': 0,
            'admin_actions': 0,
            'total_events': 0
        }

        for action_by, count in results:
            if action_by == ActorType.CUSTOMER.value:
                stats['customer_actions'] = count
            elif action_by == ActorType.AI_AGENT.value:
                stats['ai_actions'] = count
            elif action_by == ActorType.ADJUSTOR.value:
                stats['adjustor_actions'] = count
            elif action_by == ActorType.ADMIN.value:
                stats['admin_actions'] = count

            stats['total_events'] += count

        return stats

    def get_total_event_count(self, claim_id: int) -> int:
        """
        Get total count of events for a claim.

        Args:
            claim_id: Claim ID

        Returns:
            Total event count
        """
        count = self.db.query(func.count(ClaimEvent.event_id)).filter(
            ClaimEvent.claim_id == claim_id
        ).scalar()

        return count or 0
