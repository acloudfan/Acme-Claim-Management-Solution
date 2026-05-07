"""
Utility for loading and caching claims rules from YAML file.
"""
from pathlib import Path
from functools import lru_cache
from typing import Dict, Any
import yaml
import logging

logger = logging.getLogger(__name__)

class ClaimsRules:
    """Claims rules loaded from YAML file"""

    def __init__(self, rules_path: str):
        """
        Load claims rules from YAML file.

        Args:
            rules_path: Path to rules YAML file
        """
        self.rules_path = Path(rules_path)
        if not self.rules_path.exists():
            raise FileNotFoundError(
                f"Claims rules file not found: {rules_path}"
            )

        with open(self.rules_path, 'r') as f:
            self._rules = yaml.safe_load(f)

        logger.info(f"Claims rules loaded from {rules_path}")
        logger.info(f"Rules version: {self._rules.get('version', 'unknown')}")

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get rule value using dot notation.

        Args:
            key_path: Dot-separated path (e.g., "confidence.high_threshold")
            default: Default value if not found

        Returns:
            Rule value or default

        Example:
            rules.get("confidence.high_threshold")  # Returns 0.55
            rules.get("fraud.risk_threshold")       # Returns 0.1
        """
        keys = key_path.split('.')
        value = self._rules

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default

            if value is None:
                return default

        return value

    @property
    def version(self) -> str:
        """Get rules version"""
        return self._rules.get('version', 'unknown')

    @property
    def all_rules(self) -> Dict:
        """Get all rules as dictionary"""
        return self._rules.copy()

@lru_cache()
def get_claims_rules(rules_path: str = None) -> ClaimsRules:
    """
    Get cached claims rules instance.

    Args:
        rules_path: Path to rules file (defaults to config value)

    Returns:
        ClaimsRules instance
    """
    if rules_path is None:
        from src.api.config import settings
        rules_path = settings.CLAIMS_RULES_YAML

    return ClaimsRules(rules_path)

# Global rules instance
def load_rules():
    """Load claims rules from config"""
    from src.api.config import settings
    return get_claims_rules(settings.CLAIMS_RULES_YAML)
