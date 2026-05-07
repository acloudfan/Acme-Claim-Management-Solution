"""
Anthropic Claude LLM client implementation.
"""
import logging
import base64
from typing import List, Iterator
from anthropic import Anthropic, Stream
from anthropic.types import Message as AnthropicMessage, ContentBlock

from ..base import (
    BaseLLMClient,
    Message,
    ToolDefinition,
    ToolCall,
    ChatResponse
)

logger = logging.getLogger(__name__)


class AnthropicClient(BaseLLMClient):
    """Anthropic Claude LLM client"""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4.5-20250929",
        base_url: str = "https://api.anthropic.com",
        timeout: int = 60
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        self.client = Anthropic(api_key=api_key, base_url=base_url, timeout=timeout)

    def chat(
        self,
        system: str,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> ChatResponse:
        """Basic chat completion using Anthropic API"""
        try:
            response = self.client.messages.create(
                model=self.model,
                system=system,
                messages=[
                    {"role": msg.role, "content": msg.content}
                    for msg in messages
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Extract text content from response
            content_text = ""
            for block in response.content:
                if block.type == "text":
                    content_text += block.text

            return ChatResponse(
                content=content_text,
                role="assistant",
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                stop_reason=response.stop_reason
            )

        except Exception as e:
            logger.error(f"Anthropic chat error: {e}")
            raise

    def chat_stream(
        self,
        system: str,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> Iterator[str]:
        """Streaming chat completion"""
        try:
            with self.client.messages.stream(
                model=self.model,
                system=system,
                messages=[
                    {"role": msg.role, "content": msg.content}
                    for msg in messages
                ],
                temperature=temperature,
                max_tokens=max_tokens
            ) as stream:
                for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Anthropic stream error: {e}")
            raise

    def chat_with_tools(
        self,
        system: str,
        messages: List[Message],
        tools: List[ToolDefinition],
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> ChatResponse:
        """Chat with tool calling support"""
        try:
            response = self.client.messages.create(
                model=self.model,
                system=system,
                messages=[
                    {"role": msg.role, "content": msg.content}
                    for msg in messages
                ],
                tools=[
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.parameters
                    }
                    for tool in tools
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Extract content and tool calls
            content_text = ""
            tool_calls = []

            for block in response.content:
                if block.type == "text":
                    content_text += block.text
                elif block.type == "tool_use":
                    tool_calls.append(ToolCall(
                        id=block.id,
                        name=block.name,
                        arguments=block.input
                    ))

            return ChatResponse(
                content=content_text,
                role="assistant",
                tool_calls=tool_calls if tool_calls else None,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                stop_reason=response.stop_reason
            )

        except Exception as e:
            logger.error(f"Anthropic tool chat error: {e}")
            raise

    def chat_with_image(
        self,
        system: str,
        messages: List[Message],
        image_data: bytes,
        image_format: str = 'image/jpeg',
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> ChatResponse:
        """Chat with vision support"""
        try:
            # Encode image to base64
            image_base64 = base64.standard_b64encode(image_data).decode('utf-8')

            # Build messages with image
            anthropic_messages = []
            for msg in messages:
                if msg.role == "user":
                    # Add image to the first user message
                    anthropic_messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": image_format,
                                    "data": image_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": msg.content
                            }
                        ]
                    })
                    break
                else:
                    anthropic_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })

            # Add remaining messages
            for msg in messages[1:]:
                anthropic_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

            response = self.client.messages.create(
                model=self.model,
                system=system,
                messages=anthropic_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Extract text content
            content_text = ""
            for block in response.content:
                if block.type == "text":
                    content_text += block.text

            return ChatResponse(
                content=content_text,
                role="assistant",
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                stop_reason=response.stop_reason
            )

        except Exception as e:
            logger.error(f"Anthropic vision chat error: {e}")
            raise

    def supports_vision(self) -> bool:
        """Check if model supports vision"""
        # All Claude 3 and later models support vision
        return "claude-3" in self.model.lower() or "claude-sonnet-4" in self.model.lower() or "claude-opus-4" in self.model.lower()
