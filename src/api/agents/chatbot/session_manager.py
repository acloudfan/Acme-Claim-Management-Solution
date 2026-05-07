"""
In-memory session manager for chatbot conversations.
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid

from ..llm.base import Message

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages chatbot conversation sessions in memory.

    Features:
    - In-memory storage (ephemeral, resets on server restart)
    - 30-minute session timeout
    - Automatic session cleanup
    - Per-customer session tracking
    """

    def __init__(self, timeout_minutes: int = 30, max_messages: int = 50):
        """
        Initialize session manager.

        Args:
            timeout_minutes: Session timeout in minutes (default 30)
            max_messages: Maximum messages to keep per session (default 50)
        """
        self._sessions: Dict[str, Dict] = {}
        self._timeout_minutes = timeout_minutes
        self._max_messages = max_messages
        logger.info(f"SessionManager initialized with {timeout_minutes}min timeout")

    def create_session(self, customer_id: int) -> str:
        """
        Create a new chat session.

        Args:
            customer_id: Customer ID

        Returns:
            New session ID (UUID)
        """
        session_id = str(uuid.uuid4())

        self._sessions[session_id] = {
            'customer_id': customer_id,
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'history': [],
            'message_count': 0
        }

        logger.info(f"Created session {session_id} for customer {customer_id}")
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Get session data by ID.

        Args:
            session_id: Session ID

        Returns:
            Session dict or None if not found/expired
        """
        if session_id not in self._sessions:
            return None

        session = self._sessions[session_id]

        # Check if expired
        timeout = timedelta(minutes=self._timeout_minutes)
        if datetime.now() - session['last_activity'] > timeout:
            logger.info(f"Session {session_id} expired")
            del self._sessions[session_id]
            return None

        return session

    def update_session(self, session_id: str, user_message: str, assistant_response: str) -> bool:
        """
        Update session with new messages.

        Args:
            session_id: Session ID
            user_message: User's message
            assistant_response: Assistant's response

        Returns:
            True if updated, False if session not found
        """
        session = self.get_session(session_id)
        if not session:
            return False

        # Add messages to history
        session['history'].append(Message(role='user', content=user_message))
        session['history'].append(Message(role='assistant', content=assistant_response))

        # Update activity time
        session['last_activity'] = datetime.now()
        session['message_count'] += 2

        # Trim history if too long
        if len(session['history']) > self._max_messages:
            # Keep last max_messages
            session['history'] = session['history'][-self._max_messages:]
            logger.info(f"Trimmed session {session_id} history to {self._max_messages} messages")

        return True

    def get_history(self, session_id: str) -> List[Message]:
        """
        Get conversation history for a session.

        Args:
            session_id: Session ID

        Returns:
            List of Message objects, or empty list if session not found
        """
        session = self.get_session(session_id)
        if not session:
            return []

        return session['history']

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session ID

        Returns:
            True if deleted, False if not found
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Deleted session {session_id}")
            return True
        return False

    def cleanup_expired_sessions(self) -> int:
        """
        Remove all expired sessions.

        Returns:
            Number of sessions cleaned up
        """
        timeout = timedelta(minutes=self._timeout_minutes)
        now = datetime.now()

        expired = [
            session_id
            for session_id, session in self._sessions.items()
            if now - session['last_activity'] > timeout
        ]

        for session_id in expired:
            del self._sessions[session_id]

        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")

        return len(expired)

    def get_active_session_count(self) -> int:
        """Get count of active sessions"""
        return len(self._sessions)

    def get_customer_sessions(self, customer_id: int) -> List[str]:
        """
        Get all active session IDs for a customer.

        Args:
            customer_id: Customer ID

        Returns:
            List of session IDs
        """
        return [
            session_id
            for session_id, session in self._sessions.items()
            if session['customer_id'] == customer_id
        ]


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """
    Get global session manager instance (singleton pattern).

    Returns:
        SessionManager instance
    """
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
