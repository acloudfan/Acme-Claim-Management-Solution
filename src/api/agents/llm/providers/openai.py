"""
OpenAI LLM client implementation.
"""
import logging
import base64
from typing import List, Iterator
from openai import OpenAI

from ..base import (
    BaseLLMClient,
    Message,
    ToolDefinition,
    ToolCall,
    ChatResponse
)

logger = logging.getLogger(__name__)


class OpenAIClient(BaseLLMClient):
    """OpenAI GPT LLM client"""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4-turbo",
        base_url: str = "https://api.openai.com/v1",
        timeout: int = 60
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)

    def chat(
        self,
        system: str,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> ChatResponse:
        """Basic chat completion using OpenAI API"""
        try:
            openai_messages = [{"role": "system", "content": system}]
            openai_messages.extend([
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ])

            response = self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            return ChatResponse(
                content=response.choices[0].message.content or "",
                role="assistant",
                input_tokens=response.usage.prompt_tokens if response.usage else 0,
                output_tokens=response.usage.completion_tokens if response.usage else 0,
                stop_reason=response.choices[0].finish_reason
            )

        except Exception as e:
            logger.error(f"OpenAI chat error: {e}")
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
            openai_messages = [{"role": "system", "content": system}]
            openai_messages.extend([
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ])

            stream = self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"OpenAI stream error: {e}")
            raise

    def chat_with_tools(
        self,
        system: str,
        messages: List[Message],
        tools: List[ToolDefinition],
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> ChatResponse:
        """Chat with function calling support"""
        try:
            openai_messages = [{"role": "system", "content": system}]
            openai_messages.extend([
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ])

            # Convert tool definitions to OpenAI format
            openai_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters
                    }
                }
                for tool in tools
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                tools=openai_tools,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Extract tool calls if present
            tool_calls = None
            if response.choices[0].message.tool_calls:
                tool_calls = [
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=eval(tc.function.arguments)  # OpenAI returns JSON string
                    )
                    for tc in response.choices[0].message.tool_calls
                ]

            return ChatResponse(
                content=response.choices[0].message.content or "",
                role="assistant",
                tool_calls=tool_calls,
                input_tokens=response.usage.prompt_tokens if response.usage else 0,
                output_tokens=response.usage.completion_tokens if response.usage else 0,
                stop_reason=response.choices[0].finish_reason
            )

        except Exception as e:
            logger.error(f"OpenAI tool chat error: {e}")
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
            data_url = f"data:{image_format};base64,{image_base64}"

            openai_messages = [{"role": "system", "content": system}]

            # Add image to first user message
            for msg in messages:
                if msg.role == "user":
                    openai_messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": data_url}
                            },
                            {
                                "type": "text",
                                "text": msg.content
                            }
                        ]
                    })
                    break
                else:
                    openai_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })

            # Add remaining messages
            for msg in messages[1:]:
                openai_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

            response = self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            return ChatResponse(
                content=response.choices[0].message.content or "",
                role="assistant",
                input_tokens=response.usage.prompt_tokens if response.usage else 0,
                output_tokens=response.usage.completion_tokens if response.usage else 0,
                stop_reason=response.choices[0].finish_reason
            )

        except Exception as e:
            logger.error(f"OpenAI vision chat error: {e}")
            raise

    def supports_vision(self) -> bool:
        """Check if model supports vision"""
        # GPT-4 Vision and GPT-4 Turbo support vision
        return "gpt-4" in self.model.lower() and ("vision" in self.model.lower() or "turbo" in self.model.lower() or "o" in self.model.lower())
