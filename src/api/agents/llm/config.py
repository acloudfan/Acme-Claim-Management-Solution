"""
LLM configuration and factory for creating provider clients.
"""
import os
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any

from .base import BaseLLMClient
from .providers import AnthropicClient, OpenAIClient, BedrockClient
from .langfuse_wrapper import LangfuseWrapper, is_langfuse_enabled

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """LLM configuration"""
    provider: str  # 'anthropic', 'openai', 'bedrock'
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    aws_region: Optional[str] = None  # For Bedrock
    timeout_s: int = 60
    max_tokens: int = 4096
    temperature: float = 0.2


def load_llm_config(provider_name: str, config_dict: Dict[str, Any]) -> LLMConfig:
    """
    Load LLM configuration from api-config.yaml structure.

    Args:
        provider_name: Name of the provider ('anthropic', 'openai', 'bedrock')
        config_dict: Full configuration dictionary from api-config.yaml

    Returns:
        LLMConfig object

    Raises:
        ValueError: If provider not found or not enabled
    """
    if 'llm' not in config_dict:
        raise ValueError("LLM configuration not found in config")

    if 'providers' not in config_dict['llm']:
        raise ValueError("LLM providers configuration not found")

    if provider_name not in config_dict['llm']['providers']:
        raise ValueError(f"Provider '{provider_name}' not found in configuration")

    provider_config = config_dict['llm']['providers'][provider_name]

    # Check if provider is enabled
    if not provider_config.get('enabled', False):
        raise ValueError(f"Provider '{provider_name}' is not enabled in configuration")

    # Get API key from environment variable (not needed for Bedrock)
    api_key = None
    api_key_env = provider_config.get('api_key_env')
    if api_key_env:
        api_key = os.getenv(api_key_env)
        if not api_key:
            logger.warning(f"API key environment variable '{api_key_env}' not set for provider '{provider_name}'")

    # Get AWS region for Bedrock
    aws_region = provider_config.get('aws_region')

    return LLMConfig(
        provider=provider_name,
        model=provider_config['default_model'],
        api_key=api_key,
        base_url=provider_config.get('base_url'),
        aws_region=aws_region,
        timeout_s=provider_config.get('timeout_s', 60),
        max_tokens=provider_config.get('max_tokens', 4096),
        temperature=provider_config.get('temperature', 0.2)
    )


def get_llm_client(config: LLMConfig) -> BaseLLMClient:
    """
    Factory method to create LLM client based on provider configuration.

    If Langfuse tracing is enabled, the client will be wrapped with LangfuseWrapper
    to automatically trace all LLM calls.

    Args:
        config: LLMConfig object

    Returns:
        BaseLLMClient implementation for the specified provider (optionally wrapped)

    Raises:
        ValueError: If provider is not supported
    """
    provider = config.provider.lower()

    # Create the base provider client
    if provider == "anthropic":
        if not config.api_key:
            raise ValueError("Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable.")
        client = AnthropicClient(
            api_key=config.api_key,
            model=config.model,
            base_url=config.base_url or "https://api.anthropic.com",
            timeout=config.timeout_s
        )

    elif provider == "openai":
        if not config.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        client = OpenAIClient(
            api_key=config.api_key,
            model=config.model,
            base_url=config.base_url or "https://api.openai.com/v1",
            timeout=config.timeout_s
        )

    elif provider == "bedrock":
        if not config.aws_region:
            raise ValueError("AWS region not specified for Bedrock provider")
        client = BedrockClient(
            region=config.aws_region,
            model=config.model
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

    # Wrap with Langfuse if tracing is enabled
    if is_langfuse_enabled():
        logger.debug(f"Wrapping {provider} client with Langfuse tracing")
        return LangfuseWrapper(client)

    return client


def get_default_llm_client(config_dict: Dict[str, Any]) -> BaseLLMClient:
    """
    Get LLM client using the default provider from configuration.

    Args:
        config_dict: Full configuration dictionary from api-config.yaml

    Returns:
        BaseLLMClient implementation for the default provider
    """
    if 'llm' not in config_dict:
        raise ValueError("LLM configuration not found")

    default_provider = config_dict['llm'].get('default_provider', 'anthropic')
    llm_config = load_llm_config(default_provider, config_dict)
    return get_llm_client(llm_config)
