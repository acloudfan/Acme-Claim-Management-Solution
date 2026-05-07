"""
Admin Portal API Schemas

Pydantic models for admin configuration management endpoints.
Based on API-BACKEND-DESIGN.md Section 17.4
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime


class ConfigUpdateRequest(BaseModel):
    """Request body for updating configuration"""
    config: Dict[str, Any] = Field(
        ...,
        description="Full configuration object to save"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "config": {
                    "api": {
                        "debug": True,
                        "host": "0.0.0.0",
                        "port": 8000
                    },
                    "ai": {
                        "confidence": {
                            "high_threshold": 0.55,
                            "low_threshold": 0.35
                        }
                    }
                }
            }
        }


class ConfigResponse(BaseModel):
    """Response for GET /admin/config"""
    config: Dict[str, Any]
    file_path: str
    last_modified: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "config": {"api": {}, "database": {}},
                "file_path": "/path/to/api-config.yaml",
                "last_modified": "2026-05-07T14:30:45"
            }
        }


class ConfigSaveResponse(BaseModel):
    """Response for successful config save"""
    success: bool = True
    message: str
    backup_file: str
    config_path: str
    restart_required: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Configuration saved successfully",
                "backup_file": "api-config.2026-05-07-14-30-45.bak",
                "config_path": "/path/to/api-config.yaml",
                "restart_required": True
            }
        }


class ConfigValidationErrorResponse(BaseModel):
    """Response when config validation fails"""
    success: bool = False
    message: str
    errors: Dict[str, str]

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Configuration validation failed",
                "errors": {
                    "ai.confidence.high_threshold": "Must be between 0 and 1",
                    "database.pool_size": "Must be a positive integer"
                }
            }
        }


class BackupInfo(BaseModel):
    """Information about a single backup file"""
    filename: str
    timestamp: datetime
    size_bytes: int
    size_formatted: str

    class Config:
        json_schema_extra = {
            "example": {
                "filename": "api-config.2026-05-07-14-30-45.bak",
                "timestamp": "2026-05-07T14:30:45",
                "size_bytes": 12345,
                "size_formatted": "12.1 KB"
            }
        }


class BackupListResponse(BaseModel):
    """Response for GET /admin/config/backups"""
    backups: List[BackupInfo]
    total_count: int
    total_size_bytes: int

    class Config:
        json_schema_extra = {
            "example": {
                "backups": [
                    {
                        "filename": "api-config.2026-05-07-14-30-45.bak",
                        "timestamp": "2026-05-07T14:30:45",
                        "size_bytes": 12345,
                        "size_formatted": "12.1 KB"
                    }
                ],
                "total_count": 1,
                "total_size_bytes": 12345
            }
        }


class RestoreRequest(BaseModel):
    """Request body for restoring from backup"""
    backup_filename: str = Field(
        ...,
        pattern=r"^api-config\.\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}\.bak$",
        description="Backup filename to restore from (security: validates filename pattern)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "backup_filename": "api-config.2026-05-07-14-30-45.bak"
            }
        }


class RestoreResponse(BaseModel):
    """Response for successful config restore"""
    success: bool = True
    message: str
    backup_of_current: str
    restart_required: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Configuration restored from api-config.2026-05-07-14-30-45.bak",
                "backup_of_current": "api-config.2026-05-07-15-45-12.bak",
                "restart_required": True
            }
        }
