"""
Langfuse trace context management using propagate_attributes for sessions.

This module provides proper Langfuse session tracking using the SDK's
propagate_attributes() context manager.
"""
import logging
from contextvars import ContextVar
from typing import Optional, Dict, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Context variable for storing current session context (async-safe)
_current_session_context: ContextVar[Optional[Dict[str, Any]]] = ContextVar(
    'langfuse_session_context',
    default=None
)


@contextmanager
def start_agent_trace(
    agent_name: str,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Start a new Langfuse trace with session tracking using propagate_attributes.

    This uses Langfuse's propagate_attributes() context manager to set session_id
    on all nested observations.

    Args:
        agent_name: Name of the agent
        metadata: Optional metadata including session_id, session_type, etc.

    Usage:
        with start_agent_trace("ChatbotAgent", metadata={"session_id": "abc", "session_type": "chatbot"}):
            # All LLM calls here will be associated with session "abc"
            result = llm_client.chat(...)

    Returns:
        Context manager that yields None
    """
    from ..llm.langfuse_wrapper import get_langfuse_client, is_langfuse_enabled

    session_id = metadata.get('session_id') if metadata else None

    if session_id:
        logger.debug(f"Agent {agent_name} starting session {session_id}")
    else:
        logger.debug(f"Agent {agent_name} trace started (no session_id)")

    # Store metadata in context variable for LangfuseWrapper
    _current_session_context.set(metadata)

    # Use propagate_attributes if Langfuse is enabled and session_id exists
    if is_langfuse_enabled() and session_id:
        try:
            from langfuse import propagate_attributes

            # Use propagate_attributes to set session_id on all nested observations
            with propagate_attributes(session_id=session_id):
                try:
                    yield None
                finally:
                    # Flush traces
                    langfuse_client = get_langfuse_client()
                    if langfuse_client:
                        try:
                            langfuse_client.flush()
                            logger.debug(f"Flushed Langfuse traces for {agent_name}")
                        except Exception as e:
                            logger.warning(f"Failed to flush Langfuse: {e}")
        except ImportError:
            # Langfuse not available, just yield
            logger.debug(f"Langfuse not available for {agent_name}")
            try:
                yield None
            finally:
                pass
        except Exception as e:
            logger.warning(f"Failed to use propagate_attributes: {e}")
            try:
                yield None
            finally:
                pass
    else:
        # No Langfuse or no session_id, just yield
        try:
            yield None
        finally:
            # Try to flush anyway if Langfuse is enabled
            if is_langfuse_enabled():
                langfuse_client = get_langfuse_client()
                if langfuse_client:
                    try:
                        langfuse_client.flush()
                    except Exception as e:
                        logger.warning(f"Failed to flush Langfuse: {e}")

    # Clear context
    _current_session_context.set(None)


def get_current_trace_metadata() -> Optional[Dict[str, Any]]:
    """
    Get the current trace metadata from context.

    This is used by LangfuseWrapper to include session context in events.

    Returns:
        Dict of metadata if available, None otherwise
    """
    return _current_session_context.get()


def get_current_trace_id() -> Optional[str]:
    """
    Get the current trace ID from context.

    Returns:
        None (trace IDs are managed by Langfuse SDK internally)
    """
    return None


def get_current_trace_name() -> Optional[str]:
    """
    Get the current trace name from context.

    Returns:
        None (trace names are managed by Langfuse SDK internally)
    """
    return None


def end_agent_trace():
    """
    End the current Langfuse trace and clear context.

    Note: This is now handled by the start_agent_trace context manager.
    This function is kept for backward compatibility.
    """
    try:
        from ..llm.langfuse_wrapper import get_langfuse_client

        langfuse_client = get_langfuse_client()
        if langfuse_client:
            # Flush all pending traces to Langfuse server
            langfuse_client.flush()
            logger.debug("Flushed Langfuse traces")

    except ImportError:
        # Langfuse not available - silently skip
        pass
    except Exception as e:
        logger.warning(f"Failed to flush Langfuse traces: {e}")

    finally:
        # Clear the context metadata
        _current_session_context.set(None)


def update_trace_metadata(additional_metadata: Dict[str, Any]):
    """
    Add additional metadata to the current trace.

    This merges new metadata with existing metadata in the context.

    Args:
        additional_metadata: Dictionary of metadata to add/update
    """
    # Update our context variable
    current = _current_session_context.get() or {}
    merged = {**current, **additional_metadata}
    _current_session_context.set(merged)
    logger.debug(f"Trace metadata updated: {additional_metadata}")
