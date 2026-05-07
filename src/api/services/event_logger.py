"""
Event logging decorator and logic for automatic audit trail.
"""
from functools import wraps
from sqlalchemy.orm import Session
from src.api.models.claim_event import ClaimEvent
from src.api.constants import ClaimAction, ActorType
from datetime import date, datetime
import logging

logger = logging.getLogger(__name__)

def log_event(action: ClaimAction, actor_type: ActorType):
    """
    Decorator to automatically log claim events.

    Usage:
        @log_event(action=ClaimAction.CREATE_CLAIM, actor_type=ActorType.CUSTOMER)
        def create_claim(self, customer_id, claim_data):
            # ... method implementation
            return claim

    The decorator expects the method to return a Claim instance.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Execute the function
            result = func(self, *args, **kwargs)

            # Extract claim_id from result
            claim_id = getattr(result, 'claim_id', None)

            if claim_id:
                try:
                    # Create event record
                    event = ClaimEvent(
                        claim_id=claim_id,
                        event_date=date.today(),
                        event_time=datetime.now().time(),
                        status=result.current_status,
                        action=action.value,
                        action_by=actor_type.value,
                        action_by_identity=_extract_actor_identity(*args, **kwargs),
                        comments=kwargs.get('comments', '')
                    )

                    self.db.add(event)
                    self.db.commit()

                    logger.info(
                        f"Logged event: claim_id={claim_id}, "
                        f"action={action.value}, actor={actor_type.value}"
                    )
                except Exception as e:
                    logger.error(f"Failed to log event: {e}")
                    # Don't fail the operation if logging fails

            return result
        return wrapper
    return decorator

def _extract_actor_identity(*args, **kwargs) -> str:
    """Extract actor identity from method arguments"""
    # Try to get from kwargs
    if 'actor_identity' in kwargs:
        return kwargs['actor_identity']

    # Try to infer from customer_id
    if 'customer_id' in kwargs:
        return f"customer_{kwargs['customer_id']}"

    # Try to get from first positional arg (after self)
    if len(args) > 0:
        if isinstance(args[0], int):
            return f"customer_{args[0]}"

    # Default
    return "system"
