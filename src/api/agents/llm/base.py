"""
Base LLM client interface for provider-agnostic LLM integration.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Iterator
from dataclasses import dataclass
from enum import Enum


class MessageRole(str, Enum):
    """Message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Message:
    """Chat message"""
    role: str  # 'user' or 'assistant'
    content: str


@dataclass
class ToolDefinition:
    """Tool definition for LLM function calling"""
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON schema


@dataclass
class ToolCall:
    """Tool call made by LLM"""
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class ChatResponse:
    """LLM chat response"""
    content: str
    role: str
    tool_calls: Optional[List[ToolCall]] = None
    input_tokens: int = 0
    output_tokens: int = 0
    stop_reason: Optional[str] = None

    @property
    def total_tokens(self) -> int:
        """Total tokens used"""
        return self.input_tokens + self.output_tokens


class BaseLLMClient(ABC):
    """
    Abstract base class for LLM clients.

    All provider implementations (Anthropic, OpenAI, Bedrock) must extend this class.
    """

    @abstractmethod
    def chat(
        self,
        system: str,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> ChatResponse:
        """
        Basic chat completion.

        Args:
            system: System prompt
            messages: List of conversation messages
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            ChatResponse with generated content and token usage
        """
        pass

    @abstractmethod
    def chat_stream(
        self,
        system: str,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> Iterator[str]:
        """
        Streaming chat completion.

        Args:
            system: System prompt
            messages: List of conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Yields:
            Content chunks as they are generated
        """
        pass

    @abstractmethod
    def chat_with_tools(
        self,
        system: str,
        messages: List[Message],
        tools: List[ToolDefinition],
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> ChatResponse:
        """
        Chat completion with tool/function calling.

        Args:
            system: System prompt
            messages: List of conversation messages
            tools: List of available tools
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            ChatResponse with tool calls (if any)
        """
        pass

    @abstractmethod
    def chat_with_image(
        self,
        system: str,
        messages: List[Message],
        image_data: bytes,
        image_format: str = 'image/jpeg',
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> ChatResponse:
        """
        Chat completion with vision/image input.

        Args:
            system: System prompt
            messages: List of conversation messages
            image_data: Raw image bytes
            image_format: MIME type (e.g., 'image/jpeg', 'image/png')
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            ChatResponse with vision analysis

        Raises:
            NotImplementedError: If provider doesn't support vision
        """
        pass

    @abstractmethod
    def supports_vision(self) -> bool:
        """
        Check if the current model supports vision/image input.

        Returns:
            True if vision is supported, False otherwise
        """
        pass
