"""
Logging configuration for the API.
"""
import logging
import logging.handlers
from pathlib import Path
from src.api.config import settings

def setup_logging():
    """Configure structured logging"""

    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Get log level from settings
    log_level = getattr(logging, settings.LOG_LEVEL.upper())

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=settings.LOG_FORMAT,
        handlers=[
            # Console handler
            logging.StreamHandler(),
            # Rotating file handler
            logging.handlers.RotatingFileHandler(
                settings.LOG_FILE,
                maxBytes=settings.LOG_MAX_BYTES,
                backupCount=settings.LOG_BACKUP_COUNT
            )
        ]
    )

    # Set log levels for third-party libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured: level={settings.LOG_LEVEL}, file={settings.LOG_FILE}")
