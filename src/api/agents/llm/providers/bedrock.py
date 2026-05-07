"""
AWS Bedrock LLM client implementation.
"""
import json
import logging
import base64
from typing import List, Iterator
import boto3
from botocore.exceptions import ClientError

from ..base import (
    BaseLLMClient,
    Message,
    ToolDefinition,
    ToolCall,
    ChatResponse
)

logger = logging.getLogger(__name__)


class BedrockClient(BaseLLMClient):
    """AWS Bedrock LLM client"""

    def __init__(
        self,
        region: str = "us-east-1",
        model: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    ):
        self.region = region
        self.model = model
        # boto3 uses default credential chain (env vars, IAM role, config file)
        self.client = boto3.client('bedrock-runtime', region_name=region)

    def chat(
        self,
        system: str,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> ChatResponse:
        """Basic chat completion using AWS Bedrock"""
        try:
            # For Claude models on Bedrock
            if 'anthropic.claude' in self.model:
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "system": system,
                    "messages": [
                        {"role": msg.role, "content": msg.content}
                        for msg in messages
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }

                response = self.client.invoke_model(
                    modelId=self.model,
                    body=json.dumps(body)
                )

                response_body = json.loads(response['body'].read())

                # Extract text content
                content_text = ""
                for block in response_body['content']:
                    if block['type'] == 'text':
                        content_text += block['text']

                return ChatResponse(
                    content=content_text,
                    role='assistant',
                    input_tokens=response_body['usage']['input_tokens'],
                    output_tokens=response_body['usage']['output_tokens'],
                    stop_reason=response_body.get('stop_reason', 'end_turn')
                )

            # For other Bedrock models (Titan, Llama), implement separately
            raise NotImplementedError(f"Model {self.model} not yet supported")

        except ClientError as e:
            logger.error(f"Bedrock chat error: {e}")
            raise
        except Exception as e:
            logger.error(f"Bedrock chat error: {e}")
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
            if 'anthropic.claude' in self.model:
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "system": system,
                    "messages": [
                        {"role": msg.role, "content": msg.content}
                        for msg in messages
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }

                response = self.client.invoke_model_with_response_stream(
                    modelId=self.model,
                    body=json.dumps(body)
                )

                for event in response['body']:
                    chunk = json.loads(event['chunk']['bytes'])
                    if chunk['type'] == 'content_block_delta':
                        if 'delta' in chunk and 'text' in chunk['delta']:
                            yield chunk['delta']['text']

            else:
                raise NotImplementedError(f"Streaming not supported for {self.model}")

        except Exception as e:
            logger.error(f"Bedrock stream error: {e}")
            raise

    def chat_with_tools(
        self,
        system: str,
        messages: List[Message],
        tools: List[ToolDefinition],
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> ChatResponse:
        """Chat with tool calling support (Claude models only)"""
        try:
            if 'anthropic.claude' not in self.model:
                raise NotImplementedError("Tool use only supported for Claude models")

            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "system": system,
                "messages": [
                    {"role": msg.role, "content": msg.content}
                    for msg in messages
                ],
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.parameters
                    }
                    for tool in tools
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            response = self.client.invoke_model(
                modelId=self.model,
                body=json.dumps(body)
            )

            response_body = json.loads(response['body'].read())

            # Parse tool calls and content
            tool_calls = []
            content_text = ""

            for content_block in response_body['content']:
                if content_block['type'] == 'text':
                    content_text += content_block['text']
                elif content_block['type'] == 'tool_use':
                    tool_calls.append(ToolCall(
                        id=content_block['id'],
                        name=content_block['name'],
                        arguments=content_block['input']
                    ))

            return ChatResponse(
                content=content_text,
                role='assistant',
                tool_calls=tool_calls if tool_calls else None,
                input_tokens=response_body['usage']['input_tokens'],
                output_tokens=response_body['usage']['output_tokens'],
                stop_reason=response_body.get('stop_reason', 'end_turn')
            )

        except Exception as e:
            logger.error(f"Bedrock tool chat error: {e}")
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
        """Chat with vision support (Claude 3 models on Bedrock)"""
        try:
            if 'anthropic.claude-3' not in self.model:
                raise NotImplementedError("Vision only supported for Claude 3 models")

            # Encode image to base64
            image_base64 = base64.standard_b64encode(image_data).decode('utf-8')

            # Build messages with image
            bedrock_messages = []
            for msg in messages:
                if msg.role == 'user':
                    bedrock_messages.append({
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
                    bedrock_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })

            # Add remaining messages
            for msg in messages[1:]:
                bedrock_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "system": system,
                "messages": bedrock_messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            response = self.client.invoke_model(
                modelId=self.model,
                body=json.dumps(body)
            )

            response_body = json.loads(response['body'].read())

            # Extract text content
            content_text = ""
            for block in response_body['content']:
                if block['type'] == 'text':
                    content_text += block['text']

            return ChatResponse(
                content=content_text,
                role='assistant',
                input_tokens=response_body['usage']['input_tokens'],
                output_tokens=response_body['usage']['output_tokens'],
                stop_reason=response_body.get('stop_reason', 'end_turn')
            )

        except Exception as e:
            logger.error(f"Bedrock vision chat error: {e}")
            raise

    def supports_vision(self) -> bool:
        """Check if model supports vision"""
        return 'anthropic.claude-3' in self.model
