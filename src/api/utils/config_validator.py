"""
Configuration Validator Utility

Validates API configuration structure, types, ranges, and consistency.
Based on API-BACKEND-DESIGN.md Section 17.3.3
"""
from typing import Dict, Any, List, Optional, Union
import logging

logger = logging.getLogger(__name__)


def get_nested(config: Dict[str, Any], path: str) -> Optional[Any]:
    """
    Get nested value from config using dot notation path.

    Args:
        config: Configuration dictionary
        path: Dot-separated path (e.g., "ai.confidence.high_threshold")

    Returns:
        Value at path, or None if not found
    """
    keys = path.split('.')
    value = config

    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]

    return value


def set_nested(config: Dict[str, Any], path: str, value: Any) -> None:
    """
    Set nested value in config using dot notation path.

    Args:
        config: Configuration dictionary (modified in place)
        path: Dot-separated path
        value: Value to set
    """
    keys = path.split('.')
    current = config

    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]

    current[keys[-1]] = value


def validate_range(
    config: Dict[str, Any],
    path: str,
    min_val: Union[int, float],
    max_val: Union[int, float]
) -> bool:
    """
    Validate that a numeric value is within range.

    Args:
        config: Configuration dictionary
        path: Dot-separated path to value
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)

    Returns:
        True if valid, False otherwise
    """
    value = get_nested(config, path)

    if value is None:
        return False

    if not isinstance(value, (int, float)):
        return False

    return min_val <= value <= max_val


def validate_type(config: Dict[str, Any], path: str, expected_type: type) -> bool:
    """
    Validate that a value has the expected type.

    Args:
        config: Configuration dictionary
        path: Dot-separated path to value
        expected_type: Expected Python type

    Returns:
        True if valid, False otherwise
    """
    value = get_nested(config, path)

    if value is None:
        return False

    return isinstance(value, expected_type)


def validate_enum(config: Dict[str, Any], path: str, allowed_values: List[str]) -> bool:
    """
    Validate that a string value is one of the allowed values.

    Args:
        config: Configuration dictionary
        path: Dot-separated path to value
        allowed_values: List of allowed string values

    Returns:
        True if valid, False otherwise
    """
    value = get_nested(config, path)

    if value is None:
        return False

    return value in allowed_values


def validate_config(config: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate complete configuration dictionary.

    Returns dict of field_path -> error_message.
    Empty dict means configuration is valid.

    Args:
        config: Configuration dictionary to validate

    Returns:
        Dictionary mapping field paths to error messages (empty if valid)
    """
    errors = {}

    # ========== AI Confidence Thresholds ==========
    if not validate_range(config, "ai.confidence.high_threshold", 0.0, 1.0):
        errors["ai.confidence.high_threshold"] = "Must be between 0 and 1"

    if not validate_range(config, "ai.confidence.low_threshold", 0.0, 1.0):
        errors["ai.confidence.low_threshold"] = "Must be between 0 and 1"

    # Consistency check: low < high
    low = get_nested(config, "ai.confidence.low_threshold")
    high = get_nested(config, "ai.confidence.high_threshold")
    if low is not None and high is not None and low >= high:
        errors["ai.confidence.low_threshold"] = "Must be less than high threshold"

    # ========== AI Fraud Threshold ==========
    if not validate_range(config, "ai.fraud.risk_threshold", 0.0, 1.0):
        errors["ai.fraud.risk_threshold"] = "Must be between 0 and 1"

    # ========== AI Estimate Threshold ==========
    human_review = get_nested(config, "ai.estimate.human_review_threshold")
    if human_review is not None:
        if not isinstance(human_review, (int, float)) or human_review < 0:
            errors["ai.estimate.human_review_threshold"] = "Must be non-negative"

    # ========== Agent Fraud Detector Settings ==========
    if not validate_range(config, "agents.fraud_detector.high_risk_threshold", 0.0, 1.0):
        errors["agents.fraud_detector.high_risk_threshold"] = "Must be between 0 and 1"

    if not validate_range(config, "agents.fraud_detector.medium_risk_threshold", 0.0, 1.0):
        errors["agents.fraud_detector.medium_risk_threshold"] = "Must be between 0 and 1"

    # Consistency check: medium < high for fraud thresholds
    medium_risk = get_nested(config, "agents.fraud_detector.medium_risk_threshold")
    high_risk = get_nested(config, "agents.fraud_detector.high_risk_threshold")
    if medium_risk is not None and high_risk is not None and medium_risk >= high_risk:
        errors["agents.fraud_detector.medium_risk_threshold"] = "Must be less than high risk threshold"

    # ========== LLM Provider ==========
    if not validate_enum(config, "llm.default_provider", ["anthropic", "openai", "bedrock"]):
        errors["llm.default_provider"] = "Must be anthropic, openai, or bedrock"

    if not validate_enum(config, "llm.default_vision_model", ["anthropic", "openai", "bedrock"]):
        errors["llm.default_vision_model"] = "Must be anthropic, openai, or bedrock"

    # ========== LLM Provider Settings (validate active provider) ==========
    provider = get_nested(config, "llm.default_provider")

    if provider == "bedrock":
        if not validate_range(config, "llm.providers.bedrock.timeout_s", 1, 600):
            errors["llm.providers.bedrock.timeout_s"] = "Must be between 1 and 600 seconds"

        if not validate_range(config, "llm.providers.bedrock.max_tokens", 1, 100000):
            errors["llm.providers.bedrock.max_tokens"] = "Must be between 1 and 100000"

        if not validate_range(config, "llm.providers.bedrock.temperature", 0.0, 2.0):
            errors["llm.providers.bedrock.temperature"] = "Must be between 0 and 2"

    elif provider == "anthropic":
        if not validate_range(config, "llm.providers.anthropic.timeout_s", 1, 600):
            errors["llm.providers.anthropic.timeout_s"] = "Must be between 1 and 600 seconds"

        if not validate_range(config, "llm.providers.anthropic.max_tokens", 1, 100000):
            errors["llm.providers.anthropic.max_tokens"] = "Must be between 1 and 100000"

        if not validate_range(config, "llm.providers.anthropic.temperature", 0.0, 2.0):
            errors["llm.providers.anthropic.temperature"] = "Must be between 0 and 2"

    elif provider == "openai":
        if not validate_range(config, "llm.providers.openai.timeout_s", 1, 600):
            errors["llm.providers.openai.timeout_s"] = "Must be between 1 and 600 seconds"

        if not validate_range(config, "llm.providers.openai.max_tokens", 1, 100000):
            errors["llm.providers.openai.max_tokens"] = "Must be between 1 and 100000"

        if not validate_range(config, "llm.providers.openai.temperature", 0.0, 2.0):
            errors["llm.providers.openai.temperature"] = "Must be between 0 and 2"

    # ========== Database Settings ==========
    if not validate_range(config, "database.pool_size", 1, 100):
        errors["database.pool_size"] = "Must be between 1 and 100"

    if not validate_range(config, "database.max_overflow", 0, 100):
        errors["database.max_overflow"] = "Must be between 0 and 100"

    # ========== Storage Settings ==========
    if not validate_range(config, "storage.max_upload_size_mb", 1, 100):
        errors["storage.max_upload_size_mb"] = "Must be between 1 and 100 MB"

    if not validate_range(config, "storage.max_images_per_claim", 1, 100):
        errors["storage.max_images_per_claim"] = "Must be between 1 and 100"

    # ========== API Settings ==========
    if not validate_range(config, "api.port", 1, 65535):
        errors["api.port"] = "Must be a valid port number (1-65535)"

    # Log validation results
    if errors:
        logger.warning(f"Configuration validation failed with {len(errors)} errors")
        for path, error in errors.items():
            logger.debug(f"  {path}: {error}")
    else:
        logger.info("Configuration validation passed")

    return errors


def mask_sensitive_fields(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mask sensitive fields in configuration for safe display.

    Args:
        config: Configuration dictionary (not modified)

    Returns:
        New dictionary with sensitive fields masked
    """
    import copy
    masked = copy.deepcopy(config)

    # Mask database URL credentials
    if "database" in masked and "url" in masked["database"]:
        url = masked["database"]["url"]
        if "://" in url and "@" in url:
            # Format: protocol://user:pass@host:port/db
            protocol = url.split("://")[0]
            rest = url.split("@", 1)[1]  # Everything after @
            masked["database"]["url"] = f"{protocol}://****@{rest}"

    # Mask API keys (shouldn't be in config, but just in case)
    for provider in ["anthropic", "openai", "bedrock"]:
        if "llm" in masked and "providers" in masked["llm"]:
            if provider in masked["llm"]["providers"]:
                provider_config = masked["llm"]["providers"][provider]
                if "api_key" in provider_config:
                    provider_config["api_key"] = "****"

    return masked


def format_bytes(size_bytes: int) -> str:
    """
    Format bytes as human-readable string.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "12.3 KB", "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
