"""
Langfuse integration for LLM observability using the observe decorator.

This module initializes the Langfuse client and provides a wrapper
for tracing LLM calls from Anthropic/OpenAI/Bedrock providers.
"""
import os
import logging
from typing import Dict, Any, List, Optional, Iterator

from ..llm.base import BaseLLMClient, Message, ToolDefinition, ChatResponse

logger = logging.getLogger(__name__)

# Global Langfuse client singleton
_langfuse_client = None
_langfuse_enabled = False


def initialize_langfuse(config: Dict[str, Any]) -> bool:
    """
    Initialize Langfuse client from configuration.

    This should be called once at application startup with the tracking
    configuration from api-config.yaml.

    Args:
        config: Configuration dict with structure:
            {
                "tracking": {
                    "langfuse": {
                        "enabled": true/false
                    }
                }
            }

    Returns:
        True if Langfuse was successfully initialized, False otherwise

    Environment Variables Required:
        - LANGFUSE_PUBLIC_KEY: Project public key from Langfuse UI
        - LANGFUSE_SECRET_KEY: Project secret key from Langfuse UI
        - LANGFUSE_HOST: Langfuse server URL (e.g., http://localhost:3000)
    """
    global _langfuse_client, _langfuse_enabled

    try:
        # Check if Langfuse is enabled in config
        langfuse_config = config.get("tracking", {}).get("langfuse", {})
        enabled = langfuse_config.get("enabled", False)

        if not enabled:
            logger.info("Langfuse tracing is disabled in configuration")
            _langfuse_enabled = False
            return False

        # Check environment variables
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        # Support both LANGFUSE_HOST and LANGFUSE_BASE_URL for flexibility
        host = os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL")

        if not all([public_key, secret_key, host]):
            logger.warning(
                "Langfuse enabled but missing environment variables. "
                "Required: LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST (or LANGFUSE_BASE_URL)"
            )
            _langfuse_enabled = False
            return False

        # Import and initialize Langfuse
        from langfuse import Langfuse

        _langfuse_client = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host
        )

        _langfuse_enabled = True
        logger.info(f"Langfuse tracing initialized successfully (host: {host})")
        return True

    except ImportError:
        logger.warning("Langfuse package not installed. Run: uv add langfuse")
        _langfuse_enabled = False
        return False

    except Exception as e:
        logger.warning(f"Failed to initialize Langfuse: {e}")
        _langfuse_enabled = False
        return False


def get_langfuse_client():
    """
    Get the global Langfuse client instance.

    Returns:
        Langfuse client if initialized and enabled, None otherwise
    """
    return _langfuse_client if _langfuse_enabled else None


def is_langfuse_enabled() -> bool:
    """
    Check if Langfuse tracing is enabled.

    Returns:
        True if Langfuse is enabled and initialized, False otherwise
    """
    return _langfuse_enabled and _langfuse_client is not None


class LangfuseWrapper(BaseLLMClient):
    """
    Wrapper around BaseLLMClient that logs interactions to Langfuse.

    This is a transparent pass-through wrapper that sends trace data
    to Langfuse using the observe decorator pattern.
    """

    def __init__(self, wrapped_client: BaseLLMClient):
        """
        Initialize wrapper around an existing LLM client.

        Args:
            wrapped_client: The actual LLM client to wrap
        """
        self.wrapped_client = wrapped_client
        self.logger = logging.getLogger(f"{self.__class__.__name__}[{wrapped_client.__class__.__name__}]")

    def chat(
        self,
        system: str,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> ChatResponse:
        """Basic chat completion with Langfuse logging."""
        if is_langfuse_enabled():
            from langfuse import observe

            # Get session context
            from ..tracking.langfuse_context import get_current_trace_metadata
            trace_metadata = get_current_trace_metadata() or {}
            session_id = trace_metadata.get('session_id')

            # Wrap the actual call with observe decorator
            @observe(name="chat", as_type="generation")
            def _traced_chat():
                # Make the LLM call
                response = self.wrapped_client.chat(
                    system=system,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                return response

            return _traced_chat()
        else:
            return self.wrapped_client.chat(
                system=system,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

    def chat_stream(
        self,
        system: str,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> Iterator[str]:
        """Streaming chat completion (not traced in Phase 1)."""
        return self.wrapped_client.chat_stream(
            system=system,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

    def chat_with_tools(
        self,
        system: str,
        messages: List[Message],
        tools: List[ToolDefinition],
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> ChatResponse:
        """Chat with tool calling, with Langfuse logging."""
        if is_langfuse_enabled():
            from langfuse import observe

            # Get session context
            from ..tracking.langfuse_context import get_current_trace_metadata
            trace_metadata = get_current_trace_metadata() or {}
            session_id = trace_metadata.get('session_id')

            # Wrap the actual call with observe decorator
            @observe(name="tool_use", as_type="generation")
            def _traced_chat_with_tools():
                # Make the LLM call
                response = self.wrapped_client.chat_with_tools(
                    system=system,
                    messages=messages,
                    tools=tools,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                return response

            return _traced_chat_with_tools()
        else:
            return self.wrapped_client.chat_with_tools(
                system=system,
                messages=messages,
                tools=tools,
                temperature=temperature,
                max_tokens=max_tokens
            )

    def chat_with_image(
        self,
        system: str,
        messages: List[Message],
        image_data: bytes,
        image_format: str = 'image/jpeg',
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> ChatResponse:
        """Chat with image, with Langfuse logging."""
        if is_langfuse_enabled():
            from langfuse import observe

            # Get session context
            from ..tracking.langfuse_context import get_current_trace_metadata
            trace_metadata = get_current_trace_metadata() or {}
            session_id = trace_metadata.get('session_id')

            # Wrap the actual call with observe decorator
            @observe(name="vision", as_type="generation")
            def _traced_chat_with_image():
                # Make the LLM call
                response = self.wrapped_client.chat_with_image(
                    system=system,
                    messages=messages,
                    image_data=image_data,
                    image_format=image_format,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                return response

            return _traced_chat_with_image()
        else:
            return self.wrapped_client.chat_with_image(
                system=system,
                messages=messages,
                image_data=image_data,
                image_format=image_format,
                temperature=temperature,
                max_tokens=max_tokens
            )

    def supports_vision(self) -> bool:
        """Check if the wrapped client supports vision."""
        return self.wrapped_client.supports_vision()
