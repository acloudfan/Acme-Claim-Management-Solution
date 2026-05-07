"""
State machine validation for claim state transitions.
"""
from src.api.constants import ClaimState, VALID_TRANSITIONS
from typing import List

def validate_transition(current_state: ClaimState, new_state: ClaimState) -> bool:
    """
    Validate if state transition is allowed.

    Args:
        current_state: Current claim state
        new_state: Target state

    Returns:
        True if transition is valid, False otherwise
    """
    valid_next_states = VALID_TRANSITIONS.get(current_state, [])
    return new_state in valid_next_states

def get_valid_transitions(current_state: ClaimState) -> List[ClaimState]:
    """Get list of valid next states"""
    return VALID_TRANSITIONS.get(current_state, [])

def is_terminal_state(state: ClaimState) -> bool:
    """Check if state is terminal (no valid transitions)"""
    return len(VALID_TRANSITIONS.get(state, [])) == 0
