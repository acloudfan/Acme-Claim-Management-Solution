"""
Factory module for creating LLM clients (alias for easier imports).
"""
from .config import get_llm_client, load_llm_config, get_default_llm_client, LLMConfig

__all__ = ['get_llm_client', 'load_llm_config', 'get_default_llm_client', 'LLMConfig']
