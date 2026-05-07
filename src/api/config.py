"""
Configuration loader for YAML-based settings.
Reads from api-config.yaml file.
"""
from pathlib import Path
from functools import lru_cache
from typing import List
import yaml
import logging

logger = logging.getLogger(__name__)

class Settings:
    """Application settings loaded from YAML configuration"""

    def __init__(self, config_path: str = "api-config.yaml"):
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}. "
                f"Please create api-config.yaml in the project root."
            )

        # Load YAML configuration
        with open(self.config_path, 'r') as f:
            self._config = yaml.safe_load(f)

        logger.info(f"Configuration loaded from {config_path}")

    # API Configuration
    @property
    def API_TITLE(self) -> str:
        return self._config['api']['title']

    @property
    def API_VERSION(self) -> str:
        return self._config['api']['version']

    @property
    def DEBUG(self) -> bool:
        return self._config['api']['debug']

    @property
    def HOST(self) -> str:
        return self._config['api']['host']

    @property
    def PORT(self) -> int:
        return self._config['api']['port']

    # Database Configuration
    @property
    def DATABASE_URL(self) -> str:
        return self._config['database']['url']

    @property
    def DATABASE_POOL_SIZE(self) -> int:
        return self._config['database']['pool_size']

    @property
    def DATABASE_MAX_OVERFLOW(self) -> int:
        return self._config['database']['max_overflow']

    @property
    def DATABASE_ECHO(self) -> bool:
        return self._config['database']['echo']

    # Storage Configuration
    @property
    def IMAGES_ROOT_FOLDER(self) -> str:
        return self._config['storage']['images_root_folder']

    @property
    def MAX_UPLOAD_SIZE_MB(self) -> int:
        return self._config['storage']['max_upload_size_mb']

    @property
    def ALLOWED_IMAGE_TYPES(self) -> List[str]:
        return self._config['storage']['allowed_image_types']

    @property
    def MAX_IMAGES_PER_CLAIM(self) -> int:
        return self._config['storage']['max_images_per_claim']

    # AI Configuration
    # YOLO Configuration
    @property
    def YOLO_MODEL_SOURCE(self) -> str:
        """Model source: huggingface or local"""
        return self._config['ai']['yolo']['model_source']

    @property
    def YOLO_MODEL_PATH(self) -> str:
        """HuggingFace repo ID or local file path"""
        return self._config['ai']['yolo']['model_path']

    @property
    def YOLO_CONFIDENCE_THRESHOLD(self) -> float:
        """Minimum confidence threshold for YOLO detections"""
        return self._config['ai']['yolo']['confidence_threshold']

    @property
    def YOLO_DEVICE(self) -> str:
        """Device for YOLO inference: cpu, cuda, or mps"""
        return self._config['ai']['yolo']['device']

    @property
    def YOLO_SAVE_ANNOTATED_IMAGES(self) -> bool:
        """Whether to save annotated images with bounding boxes"""
        return self._config['ai']['yolo']['save_annotated_images']

    @property
    def YOLO_ANNOTATED_IMAGE_PREFIX(self) -> str:
        """Prefix for annotated image filenames"""
        return self._config['ai']['yolo']['annotated_image_prefix']

    @property
    def SOP_CLAIMS_DOCUMENT(self) -> str:
        """Path to SOP document for AI agent instructions"""
        return self._config['ai']['sop_claims_document']

    @property
    def CLAIMS_RULES_YAML(self) -> str:
        """Path to claims rules YAML file"""
        return self._config['ai']['claims_rules_yaml']

    @property
    def AI_CONFIDENCE_HIGH_THRESHOLD(self) -> float:
        return self._config['ai']['confidence']['high_threshold']

    @property
    def AI_CONFIDENCE_LOW_THRESHOLD(self) -> float:
        return self._config['ai']['confidence']['low_threshold']

    @property
    def FRAUD_RISK_THRESHOLD(self) -> float:
        return self._config['ai']['fraud']['risk_threshold']

    @property
    def LOSS_ESTIMATE_HUMAN_REVIEW_THRESHOLD(self) -> float:
        return self._config['ai']['estimate']['human_review_threshold']

    # Logging Configuration
    @property
    def LOG_LEVEL(self) -> str:
        return self._config['logging']['level']

    @property
    def LOG_FILE(self) -> str:
        return self._config['logging']['file']

    @property
    def LOG_MAX_BYTES(self) -> int:
        return self._config['logging']['max_bytes']

    @property
    def LOG_BACKUP_COUNT(self) -> int:
        return self._config['logging']['backup_count']

    @property
    def LOG_FORMAT(self) -> str:
        return self._config['logging']['format']

    # CORS Configuration
    @property
    def CORS_ALLOW_ORIGINS(self) -> List[str]:
        return self._config['cors']['allow_origins']

    @property
    def CORS_ALLOW_CREDENTIALS(self) -> bool:
        return self._config['cors']['allow_credentials']

    @property
    def CORS_ALLOW_METHODS(self) -> List[str]:
        return self._config['cors']['allow_methods']

    @property
    def CORS_ALLOW_HEADERS(self) -> List[str]:
        return self._config['cors']['allow_headers']

    # LLM Configuration
    @property
    def DEFAULT_LLM_PROVIDER(self) -> str:
        """Default LLM provider"""
        return self._config['llm']['default_provider']

    @property
    def DEFAULT_VISION_MODEL(self) -> str:
        """Default vision model provider for image analysis"""
        return self._config['llm']['default_vision_model']

    # Agent Configuration
    @property
    def FRAUD_DETECTOR_ENABLED(self) -> bool:
        """Whether fraud detection is enabled"""
        return self._config['agents']['fraud_detector']['enabled']

    @property
    def FRAUD_HIGH_RISK_THRESHOLD(self) -> float:
        """Final risk >= this threshold = HIGH RISK"""
        return self._config['agents']['fraud_detector']['high_risk_threshold']

    @property
    def FRAUD_MEDIUM_RISK_THRESHOLD(self) -> float:
        """Final risk >= this threshold = MEDIUM RISK"""
        return self._config['agents']['fraud_detector']['medium_risk_threshold']

    def get_fraud_phase1_config(self) -> dict:
        """Get Phase 1 vision detection configuration (with enabled flags and weights)"""
        return self._config['agents']['fraud_detector']['phase1_vision']

    def get_fraud_phase2_config(self) -> dict:
        """Get Phase 2 static check configuration (with enabled flags and weights)"""
        return self._config['agents']['fraud_detector']['phase2_static']

    def get_fraud_phase3_config(self) -> dict:
        """Get Phase 3 behavioral analysis configuration"""
        return self._config['agents']['fraud_detector']['phase3_behavioral']

    # Agent Enable/Disable Flags
    @property
    def AGENTS_CHATBOT_ENABLED(self) -> bool:
        """Check if customer chatbot is enabled"""
        return self._config.get('agents', {}).get('chatbot', {}).get('enabled', True)

    @property
    def AGENTS_FRAUD_DETECTOR_ENABLED(self) -> bool:
        """Check if fraud detector is enabled"""
        return self._config.get('agents', {}).get('fraud_detector', {}).get('enabled', True)

    # Expose full config dictionary for advanced use cases
    @property
    def config(self) -> dict:
        """Get the full configuration dictionary"""
        return self._config

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Settings are loaded once and cached.
    """
    return Settings()

def reload_settings() -> Settings:
    """
    Reload configuration from file by clearing the cache.
    Use this after updating api-config.yaml to load new settings.

    Returns:
        Newly loaded Settings instance
    """
    get_settings.cache_clear()
    logger.info("Configuration cache cleared, reloading settings")
    new_settings = get_settings()

    # Update the global settings reference
    global settings
    settings = new_settings

    return new_settings

# Global settings instance
settings = get_settings()
