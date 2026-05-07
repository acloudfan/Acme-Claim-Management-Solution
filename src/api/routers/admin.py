"""
Admin Portal API Router

Endpoints for managing API configuration.
Based on API-BACKEND-DESIGN.md Section 17
"""
from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from datetime import datetime
import yaml
import shutil
import re
import logging

from src.api.schemas.admin import (
    ConfigUpdateRequest,
    ConfigResponse,
    ConfigSaveResponse,
    ConfigValidationErrorResponse,
    BackupListResponse,
    BackupInfo,
    RestoreRequest,
    RestoreResponse
)
from src.api.utils.config_validator import (
    validate_config,
    mask_sensitive_fields,
    format_bytes
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Configuration file path (relative to project root)
CONFIG_FILE = Path("api-config.yaml")


@router.get(
    "/config",
    response_model=ConfigResponse,
    summary="Get current API configuration",
    description="Retrieve current API configuration from api-config.yaml with sensitive fields masked"
)
def get_config(x_admin_id: str = Header(..., alias="X-Admin-ID")):
    """
    Load and return current API configuration.

    - **X-Admin-ID**: Admin identifier (header, for tracking only)

    Returns configuration with:
    - Masked database credentials
    - Full configuration structure
    - File path and last modified timestamp
    """
    logger.info(f"Admin {x_admin_id} requested configuration")

    if not CONFIG_FILE.exists():
        logger.error(f"Configuration file not found: {CONFIG_FILE}")
        raise HTTPException(
            status_code=500,
            detail=f"Configuration file not found: {CONFIG_FILE}"
        )

    try:
        with open(CONFIG_FILE, 'r') as f:
            config = yaml.safe_load(f)

        # Mask sensitive fields
        masked_config = mask_sensitive_fields(config)

        # Get file metadata
        last_modified = datetime.fromtimestamp(CONFIG_FILE.stat().st_mtime)

        logger.info(f"Configuration loaded successfully for admin {x_admin_id}")

        return ConfigResponse(
            config=masked_config,
            file_path=str(CONFIG_FILE.absolute()),
            last_modified=last_modified
        )

    except yaml.YAMLError as e:
        logger.error(f"Failed to parse YAML configuration: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse configuration file: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load configuration: {str(e)}"
        )


@router.post(
    "/config",
    response_model=ConfigSaveResponse,
    responses={
        400: {"model": ConfigValidationErrorResponse, "description": "Validation failed"}
    },
    summary="Save API configuration",
    description="Save updated configuration with automatic backup and validation"
)
def save_config(
    request: ConfigUpdateRequest,
    x_admin_id: str = Header(..., alias="X-Admin-ID")
):
    """
    Save updated API configuration with validation and automatic backup.

    - **X-Admin-ID**: Admin identifier (header, for tracking only)
    - **config**: Full configuration object to save

    Workflow:
    1. Validate configuration (types, ranges, consistency)
    2. Create timestamped backup of current config
    3. Write new configuration to api-config.yaml
    4. Return success with backup filename

    Note: API server must be restarted for changes to take effect.
    """
    logger.info(f"Admin {x_admin_id} attempting to save configuration")

    # Step 1: Validate configuration
    errors = validate_config(request.config)

    if errors:
        logger.warning(f"Configuration validation failed with {len(errors)} errors")
        return JSONResponse(
            status_code=400,
            content=ConfigValidationErrorResponse(
                success=False,
                message="Configuration validation failed",
                errors=errors
            ).model_dump()
        )

    # Step 2: Create backup of current configuration
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    backup_filename = f"api-config.{timestamp}.bak"
    backup_path = CONFIG_FILE.parent / backup_filename

    try:
        if CONFIG_FILE.exists():
            shutil.copy2(CONFIG_FILE, backup_path)
            logger.info(f"Created backup: {backup_filename}")
        else:
            logger.warning("No existing config file to backup")

    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create backup: {str(e)}"
        )

    # Step 3: Write new configuration
    try:
        with open(CONFIG_FILE, 'w') as f:
            yaml.safe_dump(
                request.config,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True
            )

        logger.info(f"Configuration saved successfully by admin {x_admin_id}")

        return ConfigSaveResponse(
            success=True,
            message="Configuration saved successfully",
            backup_file=backup_filename,
            config_path=str(CONFIG_FILE.absolute()),
            restart_required=True
        )

    except Exception as e:
        logger.error(f"Failed to save configuration: {e}")
        # Try to restore from backup if save failed
        if backup_path.exists():
            try:
                shutil.copy2(backup_path, CONFIG_FILE)
                logger.info("Restored configuration from backup after failed save")
            except Exception as restore_error:
                logger.error(f"Failed to restore backup: {restore_error}")

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save configuration: {str(e)}"
        )


@router.get(
    "/config/backups",
    response_model=BackupListResponse,
    summary="List configuration backups",
    description="List all available backup files with metadata (sorted newest first)"
)
def list_backups(x_admin_id: str = Header(..., alias="X-Admin-ID")):
    """
    List all configuration backup files.

    - **X-Admin-ID**: Admin identifier (header, for tracking only)

    Returns:
    - List of backups (newest first)
    - Each backup includes filename, timestamp, size
    - Total count and total size
    """
    logger.info(f"Admin {x_admin_id} requested backup list")

    config_dir = CONFIG_FILE.parent
    backup_pattern = re.compile(r"api-config\.(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})\.bak")

    backups = []

    try:
        for file in config_dir.glob("api-config.*.bak"):
            match = backup_pattern.match(file.name)
            if match:
                timestamp_str = match.group(1)
                try:
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d-%H-%M-%S")
                    size_bytes = file.stat().st_size

                    backups.append(
                        BackupInfo(
                            filename=file.name,
                            timestamp=timestamp,
                            size_bytes=size_bytes,
                            size_formatted=format_bytes(size_bytes)
                        )
                    )
                except ValueError as e:
                    logger.warning(f"Skipping backup with invalid timestamp: {file.name}")
                    continue

        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x.timestamp, reverse=True)

        total_size = sum(b.size_bytes for b in backups)

        logger.info(f"Found {len(backups)} backup files (total {format_bytes(total_size)})")

        return BackupListResponse(
            backups=backups,
            total_count=len(backups),
            total_size_bytes=total_size
        )

    except Exception as e:
        logger.error(f"Failed to list backups: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list backups: {str(e)}"
        )


@router.post(
    "/config/restore",
    response_model=RestoreResponse,
    summary="Restore configuration from backup",
    description="Restore API configuration from a backup file (creates backup of current config first)"
)
def restore_config(
    request: RestoreRequest,
    x_admin_id: str = Header(..., alias="X-Admin-ID")
):
    """
    Restore configuration from a backup file.

    - **X-Admin-ID**: Admin identifier (header, for tracking only)
    - **backup_filename**: Backup filename to restore from

    Workflow:
    1. Validate backup filename (security: prevent path traversal)
    2. Check backup file exists
    3. Create backup of current config (before overwriting)
    4. Copy backup file to api-config.yaml
    5. Return success with backup-of-current filename

    Note: API server must be restarted for changes to take effect.
    """
    logger.info(f"Admin {x_admin_id} attempting to restore from {request.backup_filename}")

    # Step 1: Validate filename (already validated by Pydantic pattern)
    # Additional security check: ensure no path traversal
    if "/" in request.backup_filename or "\\" in request.backup_filename:
        logger.error(f"Invalid backup filename (path traversal attempt): {request.backup_filename}")
        raise HTTPException(
            status_code=400,
            detail="Invalid backup filename format"
        )

    # Step 2: Check backup exists
    backup_path = CONFIG_FILE.parent / request.backup_filename

    if not backup_path.exists():
        logger.error(f"Backup file not found: {request.backup_filename}")
        raise HTTPException(
            status_code=404,
            detail=f"Backup file not found: {request.backup_filename}"
        )

    # Step 3: Create backup of current config
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    current_backup = f"api-config.{timestamp}.bak"
    current_backup_path = CONFIG_FILE.parent / current_backup

    try:
        if CONFIG_FILE.exists():
            shutil.copy2(CONFIG_FILE, current_backup_path)
            logger.info(f"Created backup of current config: {current_backup}")
        else:
            logger.warning("No current config file to backup")
            current_backup = "(none - no current config)"

    except Exception as e:
        logger.error(f"Failed to create backup of current config: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create backup of current config: {str(e)}"
        )

    # Step 4: Restore from backup
    try:
        shutil.copy2(backup_path, CONFIG_FILE)
        logger.info(f"Configuration restored from {request.backup_filename} by admin {x_admin_id}")

        return RestoreResponse(
            success=True,
            message=f"Configuration restored from {request.backup_filename}",
            backup_of_current=current_backup,
            restart_required=True
        )

    except Exception as e:
        logger.error(f"Failed to restore configuration: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to restore configuration: {str(e)}"
        )


@router.post(
    "/config/reload",
    status_code=200,
    summary="Reload API configuration without restarting server"
)
def reload_config(
    x_admin_id: str = Header(..., alias="X-Admin-ID")
):
    """
    Reload API configuration from api-config.yaml without restarting the server.

    This clears the configuration cache and reloads settings from disk.
    Use this after saving configuration changes to apply them immediately.

    - **x_admin_id**: Admin identifier (required header)

    Returns:
        Success message with timestamp
    """
    try:
        from src.api.config import reload_settings

        # Reload configuration
        new_settings = reload_settings()

        logger.info(f"Configuration reloaded by admin {x_admin_id}")

        return {
            "success": True,
            "message": "Configuration reloaded successfully",
            "timestamp": datetime.now().isoformat(),
            "config_loaded": {
                "api_title": new_settings.API_TITLE,
                "api_version": new_settings.API_VERSION,
                "debug": new_settings.DEBUG
            }
        }

    except Exception as e:
        logger.error(f"Failed to reload configuration: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reload configuration: {str(e)}"
        )


@router.get(
    "/features",
    status_code=200,
    summary="Get public feature flags (no auth required)"
)
def get_feature_flags():
    """
    Get public feature flags for client applications.
    No authentication required - this is public information.

    Returns:
        Feature flags object with enabled/disabled features
    """
    from src.api.config import settings

    return {
        "chatbot_enabled": settings.AGENTS_CHATBOT_ENABLED,
        "fraud_detector_enabled": settings.AGENTS_FRAUD_DETECTOR_ENABLED,
        "timestamp": datetime.now().isoformat()
    }
