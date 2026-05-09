# API Backend Design Document
## AI-Powered Auto Insurance Claims System - Implementation Guide

**Version:** 1.1 (Prototype)  
**Last Updated:** 2026-05-07  
**Status:** Design Document  
**Security:** ⚠️ **NO AUTHENTICATION - PROTOTYPE ONLY**

**Changes in v1.1:**
- Added Section 17: Admin Portal API Endpoints
- Configuration management endpoints (GET/POST /admin/config)
- Backup list and restore endpoints
- Complete validation rules and schemas
- Security considerations for admin operations

---

## Table of Contents

1. [Design Overview](#1-design-overview)
2. [Technology Stack](#2-technology-stack)
3. [Project Structure](#3-project-structure)
4. [Core Components](#4-core-components)
5. [Database Layer](#5-database-layer)
6. [Business Logic Layer](#6-business-logic-layer)
7. [API Layer](#7-api-layer)
8. [State Machine Implementation](#8-state-machine-implementation)
9. [Event Logging System](#9-event-logging-system)
10. [Image Storage & Management](#10-image-storage--management)
11. [AI Integration](#11-ai-integration)
12. [Error Handling](#12-error-handling)
13. [Logging & Monitoring](#13-logging--monitoring)
14. [Testing Strategy](#14-testing-strategy)
15. [Database Seeding](#15-database-seeding)
16. [Deployment Considerations](#16-deployment-considerations)

---

## 1. Design Overview

### 1.1 Architecture Style

This API backend follows a **layered architecture** pattern:

```
┌─────────────────────────────────────────────────┐
│           API Layer (FastAPI Routers)           │
│  - Request validation (Pydantic)                │
│  - Response formatting                          │
│  - HTTP error handling                          │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│      Business Logic Layer (Services)            │
│  - State machine validation                     │
│  - Business rules enforcement                   │
│  - Event logging (via decorators)               │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│       Database Layer (SQLAlchemy ORM)           │
│  - Database models                              │
│  - Session management                           │
│  - Transaction handling                         │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│           SQLAnywhere Database                  │
└─────────────────────────────────────────────────┘
```

### 1.2 Design Principles

1. **Separation of Concerns**: Clear boundaries between API, business logic, and data layers
2. **Single Responsibility**: Each service handles one domain (claims, estimates, payments)
3. **DRY (Don't Repeat Yourself)**: Reusable decorators for event logging, validation
4. **Fail-Fast**: Validate state transitions and business rules early
5. **Synchronous Simplicity**: No async/await for prototype simplicity
6. **Event Sourcing**: All state changes logged in `claims_events` table

### 1.3 Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Image Storage** | Local Filesystem | Simple for prototype, easy debugging |
| **State Machine** | Dictionary-based validation | Lightweight, testable, easily modified |
| **AI Integration** | YOLOv11 from HuggingFace | Real damage detection with annotated image output |
| **Database Access** | SQLAlchemy ORM | Type-safe, well-documented, FastAPI friendly |
| **Async Pattern** | Synchronous code | Simpler debugging for prototype |
| **Event Logging** | Decorator-based | DRY principle, automatic audit trail |
| **Validation** | Pydantic + Service layer | Structure validation vs business rules |
| **Transactions** | Dependency injection | FastAPI standard, auto-rollback on error |
| **Test Coverage** | Core functionality (~50-60%) | Pragmatic for prototype |

---

## 2. Technology Stack

### 2.1 Core Dependencies

```toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
sqlalchemy = "^2.0.0"
sqlanydb = "^1.0.0"  # SQLAnywhere Python driver
pydantic = "^2.0.0"
python-multipart = "^0.0.6"  # For file uploads
pyyaml = "^6.0.0"  # For YAML configuration

# AI/CV Dependencies (YOLO Integration)
ultralytics = "^8.3.0"  # YOLOv11 for damage detection
huggingface-hub = "^0.20.0"  # HuggingFace model downloads
pillow = "^10.2.0"  # Image processing
opencv-python = "^4.9.0"  # Computer vision operations
numpy = "^1.26.0"  # Numerical operations

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-cov = "^4.1.0"
httpx = "^0.25.0"  # For FastAPI test client
faker = "^19.0.0"  # For test data generation
black = "^23.0.0"
ruff = "^0.1.0"
```

**Note:** For users with `uv` package manager:
```bash
uv add ultralytics huggingface-hub pillow opencv-python numpy
```

---

## 3. Project Structure

```
src/api/
├── main.py                      # FastAPI application entry point
├── config.py                    # Environment configuration
├── database.py                  # Database connection and session
├── dependencies.py              # Dependency injection functions
├── constants.py                 # Constants, enums, state machine definitions
├── exceptions.py                # Custom exception classes
│
├── models/                      # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── customer.py              # Customer, CustomerPolicy models
│   ├── policy.py                # Policy, PolicyVehicle models
│   ├── vehicle.py               # Vehicle model
│   ├── claim.py                 # Claim, ClaimImage models
│   ├── damage.py                # Damage model
│   └── claim_event.py           # ClaimEvent model
│
├── schemas/                     # Pydantic models (request/response)
│   ├── __init__.py
│   ├── customer.py              # CustomerResponse, CustomerCreate
│   ├── policy.py                # PolicyResponse, PolicyWithVehicles
│   ├── vehicle.py               # VehicleResponse
│   ├── claim.py                 # ClaimResponse, ClaimCreate, ClaimUpdate
│   ├── damage.py                # DamageResponse, EstimateResponse
│   ├── claim_event.py           # ClaimEventResponse
│   └── common.py                # PaginationParams, ErrorResponse, SuccessResponse
│
├── routers/                     # API route handlers
│   ├── __init__.py
│   ├── customers.py             # Customer endpoints (/customers/*)
│   ├── claims.py                # Claims endpoints (/claims/*)
│   └── cost.py                  # Cost estimation endpoints (/cost/*)
│
├── services/                    # Business logic layer
│   ├── __init__.py
│   ├── claim_service.py         # Claim CRUD and state management
│   ├── estimate_service.py      # AI/human estimate generation
│   ├── cost_service.py          # Cost calculation service
│   ├── image_service.py         # Image upload/delete operations
│   ├── payment_service.py       # Payment initiation/confirmation
│   ├── state_machine.py         # State transition validation
│   └── event_logger.py          # Event logging decorator and logic
│
├── ai/                          # AI integration layer
│   ├── __init__.py
│   ├── damage_detector.py       # YOLOv11 damage detection integration
│   └── damage_estimator.py      # Cost estimation logic
│
├── utils/                       # Utility functions
│   ├── __init__.py
│   ├── logging_config.py        # Structured logging setup
│   ├── file_utils.py            # File validation, path management
│   └── rules_loader.py          # Claims rules YAML loader
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py              # pytest fixtures
│   ├── test_customers.py        # Customer API tests
│   ├── test_claims.py           # Claims API tests
│   ├── test_state_machine.py   # State transition tests
│   ├── test_estimate.py         # Estimate generation tests
│   └── test_events.py           # Event logging tests
│
└── migrations/                  # Database migrations (optional)
    └── versions/

# Root directory files
├── api-config.yaml              # Main configuration file
├── api-config.example.yaml      # Template for configuration
├── pyproject.toml               # Poetry dependencies
├── pytest.ini                   # pytest configuration
├── alembic.ini                  # Alembic migrations config (if used)
├── seed.sql                     # Database seed script
└── README.md                    # Developer documentation

# Policies directory (business rules and SOPs)
policies/
├── rules.yaml                   # Claims processing rules and thresholds
├── damage_triage.md             # SOP for damage triage (AI instructions)
└── README.md                    # Policy documentation

# Data directories (created at runtime)
uploads/                         # Image storage
├── {claim_id}/                  # Per-claim subdirectories
│   └── *.jpg, *.png, etc.
logs/                            # Application logs
└── api.log
```

---

## 4. Core Components

### 4.1 Application Entry Point (`main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import customers, claims, cost
from src.api.database import engine, Base
from src.api.config import settings
from src.api.exceptions import register_exception_handlers
from src.api.utils.logging_config import setup_logging
import logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="AI-Powered Auto Insurance Claims API (Prototype)",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (permissive for prototype)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for prototype
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
register_exception_handlers(app)

# Include routers
app.include_router(
    customers.router,
    prefix="/api/v1/customers",
    tags=["Customers"]
)
app.include_router(
    claims.router,
    prefix="/api/v1/claims",
    tags=["Claims"]
)
app.include_router(
    cost.router,
    prefix="/api/v1/cost",
    tags=["Cost Estimation"]
)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting Insurance Claims API...")
    # Create database tables if they don't exist
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Insurance Claims API...")

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Insurance Claims API",
        "version": settings.API_VERSION
    }

@app.get("/health")
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "version": settings.API_VERSION
    }
```

### 4.2 Configuration (`api-config.yaml`)

**Configuration file location**: `api-config.yaml` (root directory)

```yaml
# API Configuration
api:
  title: "Insurance Claims API"
  version: "v1"
  debug: true
  host: "0.0.0.0"
  port: 8000

# Database Configuration
database:
  url: "sqlanywhere://user:password@localhost:2638/insurance_db"
  pool_size: 5
  max_overflow: 10
  echo: false  # Set to true to log SQL queries

# Image Storage Configuration
storage:
  images_root_folder: "uploads"  # Root directory for claim images
  max_upload_size_mb: 10
  allowed_image_types:
    - "jpg"
    - "jpeg"
    - "png"
    - "heic"
  max_images_per_claim: 20
  # Storage structure: {images_root_folder}/{claim_id}/{filename}
  # Example: uploads/1000/front_bumper_damage.jpg

# AI/State Machine Configuration
ai:
  # YOLO Model Configuration
  yolo:
    model_source: "huggingface"  # Options: huggingface, local
    model_path: "vineetsarpal/yolov11n-car-damage"  # HF repo or local path
    confidence_threshold: 0.5  # Minimum confidence for detections
    device: "cpu"  # Options: cpu, cuda, mps
    save_annotated_images: true  # Save images with bounding boxes
    annotated_image_prefix: "BB-"  # Prefix for annotated images
  
  # Path to SOP document for AI agent instructions
  sop_claims_document: "policies/damage_triage.md"
  
  # Path to claims rules YAML file (contains all thresholds)
  claims_rules_yaml: "policies/rules.yaml"
  
  # Inline thresholds (can be overridden by claims_rules_yaml)
  confidence:
    high_threshold: 0.55      # Above this: auto-approve to customer
    low_threshold: 0.35       # Below this: route to traditional
  fraud:
    risk_threshold: 0.1       # Above this: flag for human review
  estimate:
    human_review_threshold: 5000.00  # Amount threshold for human review

# Logging Configuration
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  file: "logs/api.log"
  max_bytes: 10485760  # 10MB
  backup_count: 5
  format: "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

# CORS Configuration (for prototype - permissive)
cors:
  allow_origins:
    - "*"
  allow_credentials: true
  allow_methods:
    - "*"
  allow_headers:
    - "*"

# Tracking Configuration
tracking:
  usage_logging_enabled: true
  log_to_database: true
  langfuse:
    enabled: false  # Set to true to enable Langfuse tracing (credentials in .env)
```

**Note:** Langfuse credentials are read from environment variables:
- `LANGFUSE_PUBLIC_KEY` - Public API key from Langfuse project
- `LANGFUSE_SECRET_KEY` - Secret API key from Langfuse project  
- `LANGFUSE_HOST` - Langfuse server URL (http://localhost:3000 or https://cloud.langfuse.com)

### 4.3 Configuration Loader (`config.py`)

```python
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

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Settings are loaded once and cached.
    """
    return Settings()

# Global settings instance
settings = get_settings()
```

**Dependencies Update** (`pyproject.toml`):
```toml
[tool.poetry.dependencies]
# ... existing dependencies ...
pyyaml = "^6.0.0"  # For YAML configuration parsing
```

### 4.4 Claims Rules Configuration (`policies/rules.yaml`)

**External rules file** for business logic thresholds (referenced in main config):

```yaml
# ============================================================================
# Claims Processing Rules and Thresholds
# ============================================================================
# This file contains all business rules for claim processing
# Referenced from api-config.yaml via ai.claims_rules_yaml

# Version and metadata
version: "1.0"
last_updated: "2026-05-03"
description: "Business rules for AI-powered claims processing"

# Confidence Score Thresholds
confidence:
  high_threshold: 0.55        # Auto-approve to customer decision
  medium_lower: 0.35          # Lower bound for human review
  medium_upper: 0.55          # Upper bound for human review
  low_threshold: 0.35         # Below this: route to traditional

# Fraud Detection Thresholds
fraud:
  risk_threshold: 0.1         # Above this: flag for human review
  high_risk: 0.5              # Above this: automatic rejection
  suspicious_patterns:
    multiple_claims_days: 30  # Multiple claims within X days
    high_value_threshold: 10000  # High value claims need extra scrutiny

# Claim Amount Thresholds
estimate:
  human_review_threshold: 5000.00      # Amount requiring human review
  auto_approve_max: 2500.00            # Max auto-approve amount
  executive_approval_threshold: 25000.00  # Requires executive approval

# Damage Severity Thresholds
severity:
  light: 0.3                  # Light damage (0.0 - 0.3)
  moderate: 0.6               # Moderate damage (0.3 - 0.6)
  severe: 1.0                 # Severe damage (0.6 - 1.0)

# Area Coverage Thresholds (percentage of vehicle)
area_coverage:
  minor: 0.05                 # Less than 5% of vehicle
  moderate: 0.15              # 5-15% of vehicle
  extensive: 0.25             # 15-25% of vehicle
  total_loss_threshold: 0.75  # Above 75%: consider total loss

# State-specific Rules
state_rules:
  CA:  # California
    max_auto_approve: 3000.00
    requires_photos: true
  TX:  # Texas
    max_auto_approve: 2500.00
    requires_photos: true
  NY:  # New York
    max_auto_approve: 2000.00
    requires_photos: true
    requires_police_report: true

# Time-based Rules
time_limits:
  fnol_reporting_days: 30     # Must report within 30 days
  image_upload_hours: 48      # Upload images within 48 hours
  customer_decision_hours: 72 # Customer must decide within 72 hours
  payment_processing_days: 5  # Process payment within 5 business days

# Business Rules Flags
flags:
  enable_auto_approval: true
  enable_fraud_detection: true
  require_human_review_for_new_customers: false
  enable_weekend_processing: true
```

### 4.5 Rules Loader Utility (`utils/rules_loader.py`)

```python
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
```

### 4.6 Using Rules in Services

**Example usage in `services/estimate_service.py`:**

```python
from src.api.utils.rules_loader import load_rules

class EstimateService(BaseService):
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.rules = load_rules()  # Load claims rules
    
    def should_flag_for_human_review(
        self, 
        confidence: float, 
        fraud_risk: float,
        estimated_amount: float
    ) -> bool:
        """
        Determine if claim should be flagged for human review.
        Uses rules from claims_rules_yaml.
        """
        # Get thresholds from rules
        high_confidence = self.rules.get("confidence.high_threshold")
        medium_lower = self.rules.get("confidence.medium_lower")
        fraud_threshold = self.rules.get("fraud.risk_threshold")
        amount_threshold = self.rules.get("estimate.human_review_threshold")
        
        # Apply business rules
        if fraud_risk > fraud_threshold:
            return True  # High fraud risk
        
        if estimated_amount > amount_threshold:
            return True  # High claim amount
        
        if medium_lower <= confidence < high_confidence:
            return True  # Medium confidence
        
        return False
```

**Example usage with SOP document:**

```python
from pathlib import Path
from src.api.config import settings

class AIAgentService(BaseService):
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.sop_document = self._load_sop()
    
    def _load_sop(self) -> str:
        """Load SOP document for AI agent instructions"""
        sop_path = Path(settings.SOP_CLAIMS_DOCUMENT)
        if sop_path.exists():
            with open(sop_path, 'r') as f:
                return f.read()
        else:
            logger.warning(f"SOP document not found: {sop_path}")
            return ""
    
    def get_agent_instructions(self) -> str:
        """Get instructions for AI agent from SOP"""
        return self.sop_document
```

### 4.3 Constants (`constants.py`)

```python
from enum import Enum

# Claim States
class ClaimState(str, Enum):
    FNOL = "FNOL"
    IMAGE_UPLOADED = "image_uploaded"
    LOSS_ESTIMATED_AI = "loss_estimated_ai"
    CUSTOMER_DECISION_PENDING = "customer_decision_pending"
    LOSS_APPROVED = "loss_approved"
    LOSS_APPEALED = "loss_appealed"
    HUMAN_REVIEW_PENDING = "human_review_pending"
    HUMAN_REVIEW_COMPLETED = "human_review_completed"
    SENT_FOR_PAYMENT = "sent_for_payment"
    CLAIM_PAID = "claim_paid"
    ROUTED_TO_TRADITIONAL = "routed_to_traditional"
    TRADITIONAL_PROCESSING_ACTIVE = "traditional_processing_active"
    CLAIM_CLOSED = "claim_closed"

# Actions
class ClaimAction(str, Enum):
    # Customer actions
    CREATE_CLAIM = "create_claim"
    UPLOAD_DAMAGE_PHOTOS = "upload_damage_photos"
    DELETE_IMAGE = "delete_image"
    ACCEPT_ESTIMATE = "accept_estimate"
    APPEAL_ESTIMATE = "appeal_estimate"
    
    # AI agent actions
    GENERATE_ESTIMATE = "generate_estimate"
    ASSESS_FRAUD_RISK = "assess_fraud_risk"
    CALCULATE_CONFIDENCE_SCORE = "calculate_confidence_score"
    FLAG_FOR_HUMAN_REVIEW = "flag_for_human_review"
    
    # Adjustor actions
    APPROVE_CLAIM = "approve_claim"
    DENIED_APPEAL = "denied_appeal"
    APPROVED_APPEAL = "approved_appeal"
    REVISED_ESTIMATE = "revised_estimate"
    ROUTE_TO_TRADITIONAL = "route_to_traditional"
    
    # Admin actions
    INITIATE_PAYMENT = "initiate_payment"
    PAYMENT_SENT = "payment_sent"
    CLOSE_CLAIM = "close_claim"

# Actor Types
class ActorType(str, Enum):
    CUSTOMER = "customer"
    AI_AGENT = "AI agent"
    ADJUSTOR = "adjustor"
    ADMIN = "admin"

# Estimate Types
class EstimateType(str, Enum):
    AI = "ai"
    HUMAN = "human"

# Valid State Transitions
VALID_TRANSITIONS = {
    ClaimState.FNOL: [ClaimState.IMAGE_UPLOADED],
    ClaimState.IMAGE_UPLOADED: [ClaimState.LOSS_ESTIMATED_AI],
    ClaimState.LOSS_ESTIMATED_AI: [
        ClaimState.CUSTOMER_DECISION_PENDING,
        ClaimState.HUMAN_REVIEW_PENDING
    ],
    ClaimState.CUSTOMER_DECISION_PENDING: [
        ClaimState.LOSS_APPROVED,
        ClaimState.LOSS_APPEALED
    ],
    ClaimState.LOSS_APPROVED: [ClaimState.SENT_FOR_PAYMENT],
    ClaimState.LOSS_APPEALED: [ClaimState.HUMAN_REVIEW_PENDING],
    ClaimState.HUMAN_REVIEW_PENDING: [ClaimState.HUMAN_REVIEW_COMPLETED],
    ClaimState.HUMAN_REVIEW_COMPLETED: [
        ClaimState.CUSTOMER_DECISION_PENDING,
        ClaimState.ROUTED_TO_TRADITIONAL
    ],
    ClaimState.SENT_FOR_PAYMENT: [ClaimState.CLAIM_PAID],
    ClaimState.CLAIM_PAID: [ClaimState.CLAIM_CLOSED],
    ClaimState.ROUTED_TO_TRADITIONAL: [ClaimState.TRADITIONAL_PROCESSING_ACTIVE],
    ClaimState.TRADITIONAL_PROCESSING_ACTIVE: [ClaimState.CLAIM_CLOSED],
    ClaimState.CLAIM_CLOSED: []  # Terminal state
}
```

---

## 5. Database Layer

### 5.1 Database Connection (`database.py`)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.api.config import settings
import logging

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verify connection before using
    echo=settings.DEBUG  # Log SQL in debug mode
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for ORM models
Base = declarative_base()

def get_db():
    """
    Dependency for database session.
    Yields session and ensures cleanup.
    Auto-rollback on exception.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()  # Commit if no exception
    except Exception as e:
        db.rollback()  # Rollback on exception
        logger.error(f"Database transaction rolled back: {e}")
        raise
    finally:
        db.close()
```

### 5.2 Example ORM Model (`models/claim.py`)

```python
from sqlalchemy import Column, Integer, String, Date, Time, Boolean, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.api.database import Base
from datetime import date, time, datetime

class Claim(Base):
    __tablename__ = "claims"
    
    # Primary Key
    claim_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    vin = Column(String(17), ForeignKey("vehicles.vin"), nullable=False)
    policy_number = Column(String(50), ForeignKey("policies.policy_number"), nullable=False)
    
    # FNOL Information
    fnol_date = Column(Date, nullable=False, default=date.today)
    fnol_time = Column(Time, nullable=False, default=datetime.now().time)
    date_of_damage = Column(Date, nullable=False)
    is_drivable = Column(Boolean, nullable=False)
    incident_description = Column(Text, nullable=True)  # Customer's description of what happened
    
    # Status Tracking
    current_status = Column(String(50), nullable=False, default="draft")
    claim_closed = Column(Boolean, default=False)
    claim_closed_date = Column(Date, nullable=True)
    
    # AI/Human Review Flags
    ai_estimate_accepted = Column(Boolean, default=False)
    routed_to_traditional = Column(Boolean, default=False)
    reason_routing_to_traditional = Column(String(255), nullable=True)
    
    # Appeal Tracking (NEW - 2026-05-06)
    appeal_count = Column(Integer, default=0)  # Number of appeals (0, 1, or 2)
    first_appeal_reason = Column(Text, nullable=True)  # Customer's reason for first appeal
    first_appeal_date = Column(Date, nullable=True)  # Date of first appeal
    second_appeal_reason = Column(Text, nullable=True)  # Customer's reason for second appeal
    second_appeal_date = Column(Date, nullable=True)  # Date of second appeal
    
    # Estimate Reference
    active_estimate_id = Column(String(100), nullable=True)
    
    # Financial Information
    claim_amount = Column(Numeric(10, 2), nullable=True)
    actual_claim_amount = Column(Numeric(10, 2), nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="claims")
    vehicle = relationship("Vehicle", back_populates="claims")
    policy = relationship("Policy", back_populates="claims")
    images = relationship("ClaimImage", back_populates="claim", cascade="all, delete-orphan")
    damages = relationship("Damage", back_populates="claim", cascade="all, delete-orphan")
    events = relationship("ClaimEvent", back_populates="claim", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Claim(claim_id={self.claim_id}, status={self.current_status})>"

class ClaimImage(Base):
    __tablename__ = "claim_images"
    
    # Primary Key (filename)
    image_id = Column(String(255), primary_key=True)
    
    # Foreign Key
    claim_id = Column(Integer, ForeignKey("claims.claim_id"), nullable=False)
    
    # Metadata
    uploaded_at = Column(DateTime, nullable=False, default=datetime.now)
    uploaded_by = Column(String(100), nullable=False)
    
    # Relationships
    claim = relationship("Claim", back_populates="images")
    damages = relationship("Damage", back_populates="image", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ClaimImage(image_id={self.image_id}, claim_id={self.claim_id})>"

class Damage(Base):
    __tablename__ = "damages"
    
    # Primary Key
    damage_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    claim_id = Column(Integer, ForeignKey("claims.claim_id"), nullable=False)
    estimate_id = Column(String(100), nullable=False)
    image_id = Column(String(255), ForeignKey("claim_images.image_id"), nullable=False)
    
    # Estimate Type
    estimate_type = Column(String(20), nullable=False)  # 'ai' or 'human'
    
    # YOLO Detection Fields
    damage_class = Column(Integer, nullable=True)  # YOLO class ID (0-13)
    damage_confidence = Column(Numeric(5, 2), nullable=True)  # YOLO confidence (0.0-1.0)
    damage_part = Column(String(100), nullable=False)
    
    # Bounding Box Coordinates
    bounding_box_x = Column(Integer, nullable=True)
    bounding_box_y = Column(Integer, nullable=True)
    bounding_box_width = Column(Integer, nullable=True)
    bounding_box_height = Column(Integer, nullable=True)
    
    # VLM Assessment Fields
    internal_damage_probability = Column(Numeric(5, 2), nullable=True)
    severity = Column(Numeric(5, 2), nullable=False)
    recommended_action = Column(String(50), nullable=True)
    reasoning = Column(Text, nullable=True)
    car_side = Column(String(20), nullable=True)
    assessment_confidence = Column(Numeric(5, 2), nullable=True)
    
    # Annotated Image Reference
    annotated_image_id = Column(String(255), nullable=True)
    
    # ============================================================================
    # COST FIELDS - DUAL-COLUMN APPROACH (OPTION 1)
    # ============================================================================
    # Purpose: Preserve original AI estimates while allowing adjustor modifications
    # Design: AI estimates are immutable; adjustor estimates are nullable overlays
    #
    # Background:
    # - AI generates initial estimates (labor_hours, parts_cost)
    # - Adjustor reviews and may modify these values
    # - PROBLEM: Direct modification overwrites AI data, losing audit trail
    # - SOLUTION: Separate columns for AI vs adjustor estimates
    #
    # Implementation:
    # 1. AI Estimate Fields (IMMUTABLE - set once during AI estimation):
    ai_labor_hours = Column(Numeric(5, 2), nullable=False)
    ai_parts_cost = Column(Numeric(10, 2), nullable=False)
    ai_total_cost = Column(Numeric(10, 2), nullable=False)
    
    # 2. Adjustor Estimate Fields (NULLABLE - set during human review):
    adjustor_labor_hours = Column(Numeric(5, 2), nullable=True)
    adjustor_parts_cost = Column(Numeric(10, 2), nullable=True)
    adjustor_total_cost = Column(Numeric(10, 2), nullable=True)
    adjustor_note = Column(Text, nullable=True)
    reviewed_by_adjustor = Column(Boolean, default=False)
    reviewed_at = Column(DateTime, nullable=True)
    
    # 3. Display Logic (application layer):
    # - IF adjustor_labor_hours IS NOT NULL: use adjustor estimates
    # - ELSE: use AI estimates
    #
    # Benefits:
    # - Original AI estimates preserved for audit/analysis
    # - Can show customers: "AI: $1,200 → Adjustor: $1,450"
    # - Enables AI accuracy tracking over time
    # - Supports second appeal with full history
    #
    # Implementation Note:
    # - System under development - no data migration needed
    # - Database will be reseeded with new schema
    # - Old fields removed completely (not deprecated)
    # ============================================================================
    
    avg_labor_cost = Column(Numeric(10, 2), nullable=True)  # DEPRECATED: Use claim.state_avg_labor_cost
    
    # Timestamp Fields
    generated_on_date = Column(Date, nullable=True)
    generated_on_time = Column(Time, nullable=True)
    
    # Relationships
    claim = relationship("Claim", back_populates="damages")
    image = relationship("ClaimImage", back_populates="damages")
    
    def __repr__(self):
        return f"<Damage(damage_id={self.damage_id}, part={self.damage_part})>"
```

---

## 6. Business Logic Layer

### 6.1 Service Base Pattern

All services follow a consistent pattern:

```python
# services/base_service.py
from sqlalchemy.orm import Session
from typing import Optional
import logging

class BaseService:
    """Base class for all services"""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def commit(self):
        """Commit database transaction"""
        try:
            self.db.commit()
        except Exception as e:
            self.logger.error(f"Commit failed: {e}")
            self.db.rollback()
            raise
    
    def refresh(self, instance):
        """Refresh instance from database"""
        self.db.refresh(instance)
```

### 6.2 Claim Service (`services/claim_service.py`)

```python
from sqlalchemy.orm import Session
from src.api.models.claim import Claim, ClaimImage
from src.api.schemas.claim import ClaimCreate, ClaimUpdate
from src.api.services.base_service import BaseService
from src.api.services.event_logger import log_event
from src.api.constants import ClaimState, ClaimAction, ActorType
from src.api.exceptions import ResourceNotFoundError, StateTransitionError
from typing import Optional, List
from datetime import date, datetime

class ClaimService(BaseService):
    """Service for claim operations"""
    
    @log_event(action=ClaimAction.CREATE_CLAIM, actor_type=ActorType.CUSTOMER)
    def create_claim(self, customer_id: int, claim_data: ClaimCreate) -> Claim:
        """
        Create new claim (FNOL).
        
        Args:
            customer_id: Customer ID
            claim_data: Claim creation data
            
        Returns:
            Created Claim instance
            
        Raises:
            ValidationError: If policy/vehicle validation fails
        """
        # Validate policy is active
        # Validate vehicle is covered by policy
        # (Business logic validation here)
        
        claim = Claim(
            customer_id=customer_id,
            vin=claim_data.vin,
            policy_number=claim_data.policy_number,
            fnol_date=claim_data.fnol_date,
            fnol_time=claim_data.fnol_time,
            is_drivable=claim_data.is_drivable,
            current_status=ClaimState.FNOL
        )
        
        self.db.add(claim)
        self.commit()
        self.refresh(claim)
        
        self.logger.info(f"Created claim {claim.claim_id} for customer {customer_id}")
        return claim
    
    def get_claim(self, claim_id: int) -> Claim:
        """Get claim by ID"""
        claim = self.db.query(Claim).filter(Claim.claim_id == claim_id).first()
        if not claim:
            raise ResourceNotFoundError("Claim", claim_id)
        return claim
    
    def get_customer_claims(
        self, 
        customer_id: int, 
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Claim]:
        """Get claims for customer with optional filtering"""
        query = self.db.query(Claim).filter(Claim.customer_id == customer_id)
        
        if status:
            query = query.filter(Claim.current_status == status)
        
        return query.offset(offset).limit(limit).all()
    
    def update_claim_status(
        self,
        claim_id: int,
        new_status: ClaimState,
        actor_type: ActorType,
        actor_identity: str,
        comments: str = ""
    ) -> Claim:
        """
        Update claim status with state machine validation.
        
        Args:
            claim_id: Claim ID
            new_status: Target state
            actor_type: Who is making the change
            actor_identity: Actor identifier
            comments: Optional comments
            
        Returns:
            Updated Claim instance
            
        Raises:
            StateTransitionError: If transition is invalid
        """
        from src.api.services.state_machine import validate_transition
        
        claim = self.get_claim(claim_id)
        current_status = ClaimState(claim.current_status)
        
        # Validate state transition
        if not validate_transition(current_status, new_status):
            raise StateTransitionError(
                current_status,
                new_status,
                get_valid_transitions(current_status)
            )
        
        # Update status
        claim.current_status = new_status.value
        self.commit()
        
        self.logger.info(
            f"Claim {claim_id} transitioned: {current_status} → {new_status}"
        )
        
        return claim
```

### 6.3 Policy Service (`services/policy_service.py`)

```python
from sqlalchemy.orm import Session, joinedload
from src.api.models.policy import Policy
from src.api.models.customer import Customer
from src.api.models.vehicle import Vehicle
from src.api.models.policy_vehicle import PolicyVehicle
from src.api.services.base_service import BaseService
from src.api.exceptions import ResourceNotFoundError
from typing import List

class PolicyService(BaseService):
    """Service for policy operations (read-only)"""
    
    def get_customer_policies(self, customer_id: int) -> List[Policy]:
        """
        Get all policies for a customer with associated vehicles.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            List of Policy instances with vehicles eagerly loaded
            
        Raises:
            ResourceNotFoundError: If customer doesn't exist
        """
        # Verify customer exists
        customer = self.db.query(Customer).filter(
            Customer.customer_id == customer_id
        ).first()
        
        if not customer:
            raise ResourceNotFoundError("Customer", customer_id)
        
        # Get policies with vehicles using JOIN
        policies = (
            self.db.query(Policy)
            .filter(Policy.customer_id == customer_id)
            .all()
        )
        
        # Eagerly load vehicles for each policy
        for policy in policies:
            policy_vehicles = (
                self.db.query(Vehicle)
                .join(PolicyVehicle)
                .filter(PolicyVehicle.policy_number == policy.policy_number)
                .all()
            )
            # Add vehicles list to policy object (for response serialization)
            policy.vehicles = policy_vehicles
        
        self.logger.info(f"Retrieved {len(policies)} policies for customer {customer_id}")
        return policies
    
    def get_policy(self, customer_id: int, policy_number: str) -> Policy:
        """
        Get single policy with vehicles.
        
        Args:
            customer_id: Customer ID
            policy_number: Policy number
            
        Returns:
            Policy instance with vehicles
            
        Raises:
            ResourceNotFoundError: If policy doesn't exist or doesn't belong to customer
        """
        policy = (
            self.db.query(Policy)
            .filter(
                Policy.policy_number == policy_number,
                Policy.customer_id == customer_id
            )
            .first()
        )
        
        if not policy:
            raise ResourceNotFoundError(
                "Policy", 
                policy_number,
                f"Policy not found for customer {customer_id}"
            )
        
        # Load vehicles
        policy_vehicles = (
            self.db.query(Vehicle)
            .join(PolicyVehicle)
            .filter(PolicyVehicle.policy_number == policy.policy_number)
            .all()
        )
        policy.vehicles = policy_vehicles
        
        self.logger.info(f"Retrieved policy {policy_number} with {len(policy_vehicles)} vehicles")
        return policy
```

**Key Points:**
- **Read-only**: No create/update/delete operations yet
- **Customer validation**: Ensures customer exists before querying policies
- **Eager loading**: Loads vehicles with policies to avoid N+1 queries
- **Policy ownership**: Validates policy belongs to specified customer

---

## 7. API Layer

### 7.1 API Endpoint Overview

The API is organized into the following router modules:

| Router | Base Path | Description |
|--------|-----------|-------------|
| **customers.py** | `/customers` | Customer CRUD, claims, images, events |
| **claims.py** | `/claims` | Claim estimates and damage details |
| **cost.py** | `/cost` | Cost estimation utilities |

---

### 7.2 Customer Router (`routers/customers.py`)

#### 7.2.1 Customer CRUD Operations

**Get Customer**
```python
@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Get customer details"
)
def get_customer(
    customer_id: int,
    include_policies: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get customer by ID.
    
    - **customer_id**: Customer identifier
    - **include_policies**: Include related policies and vehicles (default: false)
    
    Returns customer details with optional policy/vehicle relationships.
    """
    service = CustomerService(db)
    customer = service.get_customer(customer_id, include_policies)
    return customer
```

**Create Customer**
```python
@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new customer"
)
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db)
):
    """
    Create new customer account.
    
    Required fields:
    - **first_name**: Customer first name
    - **last_name**: Customer last name
    - **email**: Valid email address (unique)
    - **phone**: Contact phone number
    - **date_of_birth**: Date of birth (must be 18+)
    - **license_number**: Driver's license number
    
    Optional fields:
    - **address**: Street address
    - **city**: City
    - **state**: State code (2 letters)
    - **zip_code**: ZIP code
    """
    service = CustomerService(db)
    customer = service.create_customer(customer_data)
    return customer
```

**Update Customer**
```python
@router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Update customer (full update)"
)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db)
):
    """
    Update customer details (full update - all fields required).
    
    - **customer_id**: Customer identifier
    - **customer_data**: Complete customer data
    
    All fields must be provided. Use PATCH for partial updates.
    """
    service = CustomerService(db)
    customer = service.update_customer(customer_id, customer_data)
    return customer

@router.patch(
    "/{customer_id}",
    response_model=CustomerResponse,
    summary="Update customer (partial update)"
)
def patch_customer(
    customer_id: int,
    customer_data: CustomerPatch,
    db: Session = Depends(get_db)
):
    """
    Partially update customer details.
    
    - **customer_id**: Customer identifier
    - **customer_data**: Fields to update (all optional)
    
    Only provided fields will be updated. Omitted fields remain unchanged.
    """
    service = CustomerService(db)
    customer = service.patch_customer(customer_id, customer_data)
    return customer
```

#### 7.2.2 Policy Operations

**List Customer Policies**
```python
@router.get(
    "/{customer_id}/policies",
    response_model=List[PolicyResponse],
    summary="List customer policies"
)
def list_customer_policies(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all policies for a customer.
    
    - **customer_id**: Customer identifier
    
    Returns all policies associated with the customer, including:
    - Policy details (number, dates, coverage, premium)
    - Associated vehicles for each policy
    
    **Read-only operation** - Policies cannot be created/modified via API yet.
    """
    service = PolicyService(db)
    policies = service.get_customer_policies(customer_id)
    return policies
```

**Get Single Policy**
```python
@router.get(
    "/{customer_id}/policies/{policy_number}",
    response_model=PolicyResponse,
    summary="Get policy details"
)
def get_customer_policy(
    customer_id: int,
    policy_number: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information for a specific policy.
    
    - **customer_id**: Customer identifier
    - **policy_number**: Policy number (e.g., "POL-2026-001")
    
    Returns:
    - Complete policy information
    - All vehicles covered under the policy
    - Coverage details (liability, collision, comprehensive)
    - Premium and deductible information
    
    **Read-only operation**
    """
    service = PolicyService(db)
    policy = service.get_policy(customer_id, policy_number)
    return policy
```

**Response Schema**

```python
# PolicyResponse schema (Pydantic)
class VehicleInfo(BaseModel):
    vin: str
    year: int
    make: str
    model: str
    color: Optional[str] = None

class PolicyResponse(BaseModel):
    policy_number: str
    customer_id: int
    policyholder_name: str
    insured_name: str
    
    # Dates
    effective_date: date
    expiration_date: date
    
    # Drivers (flattened from JSON structure)
    driver_1: Optional[str] = None
    driver_2: Optional[str] = None
    driver_3: Optional[str] = None
    driver_4: Optional[str] = None
    
    # Coverage details
    bodily_injury_limit: Decimal
    property_damage_limit: Decimal
    collision_deductible: Optional[Decimal] = None
    comprehensive_deductible: Optional[Decimal] = None
    
    # Financial
    premium: Decimal
    deductible: Decimal
    
    # Associated vehicles
    vehicles: List[VehicleInfo] = []
    
    class Config:
        from_attributes = True
```

**Example Response**

```json
GET /api/v1/customers/100/policies

[
  {
    "policy_number": "POL-2026-001",
    "customer_id": 100,
    "policyholder_name": "John Doe",
    "insured_name": "John Doe",
    "effective_date": "2024-05-01",
    "expiration_date": "2025-05-01",
    "driver_1": "John Doe",
    "driver_2": "Jane Doe",
    "driver_3": null,
    "driver_4": null,
    "bodily_injury_limit": 100000.00,
    "property_damage_limit": 50000.00,
    "collision_deductible": 500.00,
    "comprehensive_deductible": 250.00,
    "premium": 1200.00,
    "deductible": 500.00,
    "vehicles": [
      {
        "vin": "1ABC23456789DEFG",
        "year": 2022,
        "make": "Toyota",
        "model": "Camry",
        "color": "Silver"
      }
    ]
  }
]
```

**Business Rules**

| Rule | Description |
|------|-------------|
| **Read-only** | Policies cannot be created or modified via API (future enhancement) |
| **Customer validation** | Customer must exist |
| **Policy ownership** | Policy must belong to the specified customer |
| **Vehicles included** | Response includes all vehicles covered by the policy |
| **No filtering** | Returns all policies (active, expired, cancelled) |

**Error Responses**

| Status Code | Scenario |
|-------------|----------|
| `404 Not Found` | Customer does not exist |
| `404 Not Found` | Policy does not exist for this customer |
| `200 OK` | Success with empty array if customer has no policies |

#### 7.2.3 Claim Operations

**Create Claim (Draft State)**
```python
@router.post(
    "/{customer_id}/claims",
    response_model=ClaimResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new claim in draft state"
)
def create_claim(
    customer_id: int,
    claim_data: ClaimCreate,
    db: Session = Depends(get_db)
):
    """
    Create new claim in draft state.
    
    - **customer_id**: Customer identifier
    - **claim_data**: Claim details (VIN, policy, dates)
    
    Claim is created in 'draft' state. Use submit endpoint to move to FNOL.
    """
    service = ClaimService(db)
    claim = service.create_claim(customer_id, claim_data)
    return claim
```

**Submit Claim for Processing**
```python
@router.post(
    "/{customer_id}/claims/{claim_id}/submit",
    response_model=ClaimResponse,
    summary="Submit claim for processing"
)
def submit_claim(
    customer_id: int,
    claim_id: int,
    db: Session = Depends(get_db)
):
    """
    Submit claim for processing (DRAFT → FNOL transition).
    
    - **customer_id**: Customer identifier
    - **claim_id**: Claim identifier
    
    Transitions claim from 'draft' to 'FNOL' (First Notice of Loss).
    """
    service = ClaimService(db)
    claim = service.submit_claim(claim_id, customer_id)
    return claim
```

**Accept Estimate**
```python
@router.post(
    "/{customer_id}/claims/{claim_id}/accept-estimate",
    response_model=ClaimResponse,
    status_code=status.HTTP_200_OK,
    summary="Accept AI estimate and process for payment"
)
def accept_estimate(
    customer_id: int,
    claim_id: int,
    db: Session = Depends(get_db)
):
    """
    Accept AI estimate and transition to payment processing.
    
    - **customer_id**: Customer identifier
    - **claim_id**: Claim identifier
    
    State transitions:
    1. customer_decision_pending → loss_approved (customer accepts)
       - Sets ai_estimate_accepted = True
       - Logs ACCEPT_ESTIMATE event
    2. loss_approved → sent_for_payment (initiate payment)
       - Logs INITIATE_PAYMENT event
    
    Customer must be in customer_decision_pending state to accept.
    
    After acceptance:
    - Payment processing initiated
    - Customer receives confirmation email (future)
    - Payment issued within 24 hours
    - Customer can appeal for additional funds if actual repair cost exceeds estimate
    """
    service = ClaimService(db)
    claim = service.accept_estimate(claim_id=claim_id, customer_id=customer_id)
    return claim
```

**Get Customer Claims**
```python
@router.get(
    "/{customer_id}/claims",
    response_model=List[ClaimResponse],
    summary="Get customer claims"
)
def get_customer_claims(
    customer_id: int,
    status: str = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get all claims for customer with optional filtering.
    
    - **customer_id**: Customer identifier
    - **status**: Optional filter by claim status
    - **limit**: Maximum results (default: 20, max: 100)
    - **offset**: Pagination offset (default: 0)
    """
    service = ClaimService(db)
    claims = service.get_customer_claims(customer_id, status, limit, offset)
    return claims
```

**Get Specific Claim**
```python
@router.get(
    "/{customer_id}/claims/{claim_id}",
    response_model=ClaimResponse,
    summary="Get specific claim"
)
def get_claim(
    customer_id: int,
    claim_id: int,
    db: Session = Depends(get_db)
):
    """
    Get specific claim by ID with damage assessment.
    
    - **customer_id**: Customer identifier (for authorization)
    - **claim_id**: Claim identifier
    
    Returns claim with nested damage_assessment containing:
    - total_estimated_cost: Sum of all damage costs
    - damage_count: Number of damages detected
    - damages: Array of damage details (all fields from damages table)
    
    Verifies claim belongs to customer before returning.
    """
    service = ClaimService(db)
    claim_dict = service.get_claim_with_damages(claim_id)
    
    # Verify ownership
    if claim_dict['customer_id'] != customer_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return claim_dict
```

**Response Example:**
```json
{
  "claim_id": 1000,
  "customer_id": 100,
  "vin": "1ABC23456789DEFG",
  "policy_number": "POL-2026-001",
  "fnol_date": "2026-05-01",
  "fnol_time": "10:30:00",
  "date_of_damage": "2026-04-30",
  "is_drivable": true,
  "incident_description": "I was rear-ended at a red light by another driver",
  "current_status": "draft",
  "claim_closed": false,
  "claim_closed_date": null,
  "ai_estimate_accepted": false,
  "routed_to_traditional": false,
  "reason_routing_to_traditional": null,
  "active_estimate_id": null,
  "claim_amount": null,
  "actual_claim_amount": null,
  "damage_assessment": {
    "total_estimated_cost": 2734.00,
    "damage_count": 2,
    "damages": [
      {
        "damage_id": 1,
        "estimate_id": "1000_20260503103000",
        "image_id": "front_bumper.jpg",
        "estimate_type": "ai",
        "damage_part": "front-bumper-dent",
        "severity": 0.60,
        "estimated_total_cost": 1484.00,
        "labor_hours": 1.90,
        "avg_labor_cost": 156.00,
        "estimated_parts_cost": 1188.00
      },
      {
        "damage_id": 2,
        "estimate_id": "1000_20260503103000",
        "image_id": "door_scratch.jpg",
        "estimate_type": "ai",
        "damage_part": "door-scratch",
        "severity": 0.40,
        "estimated_total_cost": 1250.00,
        "labor_hours": 1.20,
        "avg_labor_cost": 156.00,
        "estimated_parts_cost": 1062.80
      }
    ]
  }
}
```

**Notes:**
- `damage_assessment` is `null` if no damages have been detected yet
- All damages for the claim are included (may span multiple estimates)
- Each damage includes reference to the `image_id` that generated it
```

#### 7.2.4 Image Operations

**Upload Damage Photo**
```python
@router.post(
    "/{customer_id}/claims/{claim_id}/images",
    status_code=status.HTTP_201_CREATED,
    summary="Upload damage photo"
)
def upload_claim_image(
    customer_id: int,
    claim_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload damage photo to claim.
    
    - **file**: Image file (jpg, png, heic)
    - Maximum size: 10MB (configurable)
    - Maximum images per claim: 20 (configurable)
    
    Transitions claim from FNOL → IMAGE_UPLOADED on first upload.
    """
    image_service = ImageService(db)
    image = image_service.upload_image(claim_id, file, f"customer_{customer_id}")
    return {"image_id": image.image_id, "claim_id": claim_id}
```

**Delete Damage Photo**
```python
@router.delete(
    "/{customer_id}/claims/{claim_id}/images/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete damage photo"
)
def delete_claim_image(
    customer_id: int,
    claim_id: int,
    image_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete uploaded damage photo.
    
    - **customer_id**: Customer identifier
    - **claim_id**: Claim identifier
    - **image_id**: Image filename
    
    Cascade deletes associated damage detections.
    """
    image_service = ImageService(db)
    image_service.delete_image(claim_id, image_id, f"customer_{customer_id}")
    return None
```

**Get Claim Images (List)**
```python
@router.get(
    "/{customer_id}/claims/{claim_id}/images",
    response_model=List[ClaimImageResponse],
    summary="Get claim images list"
)
def get_claim_images(
    customer_id: int,
    claim_id: int,
    db: Session = Depends(get_db)
):
    """
    Get metadata for all images in a claim.
    
    - **customer_id**: Customer identifier
    - **claim_id**: Claim identifier
    
    Returns list of image metadata (not the actual image files).
    """
    service = ClaimService(db)
    images = service.get_claim_images(claim_id)
    return images
```

**Get Claim Image (Serve File)**
```python
from fastapi.responses import FileResponse
import os
from pathlib import Path

@router.get(
    "/{customer_id}/claims/{claim_id}/images/{image_id}",
    response_class=FileResponse,
    summary="Get claim image file"
)
def get_claim_image(
    customer_id: int,
    claim_id: int,
    image_id: str,
    annotated: Optional[str] = Query(None, description="Set to 'yes' for annotated image"),
    db: Session = Depends(get_db)
):
    """
    Serve a damage photo (original or annotated).
    
    - **customer_id**: Customer identifier
    - **claim_id**: Claim identifier
    - **image_id**: Image filename (e.g., 'front_bumper.jpg')
    - **annotated**: Query param - set to 'yes' to get YOLO-annotated version
    
    Query examples:
    - Original: GET /customers/100/claims/1000/images/front.jpg
    - Annotated: GET /customers/100/claims/1000/images/front.jpg?annotated=yes
    
    Returns FileResponse with appropriate Content-Type header.
    Annotated images are stored as 'BB-{original_filename}'.
    """
    # Validate image_id to prevent path traversal
    if ".." in image_id or "/" in image_id or "\\" in image_id:
        raise HTTPException(
            status_code=400,
            detail="Invalid image_id: path traversal not allowed"
        )
    
    # Verify customer owns the claim
    claim_service = ClaimService(db)
    claim = claim_service.get_claim_by_id(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    # For prototype: skip customer ownership check
    # Production: verify claim.customer_id == customer_id
    
    # Determine file path
    config = get_config()
    images_root = config.storage.images_root_folder
    
    if annotated == "yes":
        # Serve annotated image with bounding boxes
        filename = f"BB-{image_id}"
    else:
        # Serve original image
        filename = image_id
    
    file_path = Path(images_root) / str(claim_id) / filename
    
    # Check file exists
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Image not found: {filename}"
        )
    
    # Determine media type from extension
    ext = file_path.suffix.lower()
    media_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".heic": "image/heic"
    }
    media_type = media_type_map.get(ext, "application/octet-stream")
    
    # Return file with appropriate headers
    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        headers={
            "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
            "Content-Disposition": f'inline; filename="{filename}"'
        }
    )
```

#### 7.2.5 Claim Events (Audit Trail)

**Get Claim Events**
```python
@router.get(
    "/{customer_id}/claims/{claim_id}/events",
    response_model=List[ClaimEventResponse],
    summary="Get claim event history"
)
def get_claim_events(
    customer_id: int,
    claim_id: int,
    actor_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get event history for a claim (audit trail).
    
    - **customer_id**: Customer identifier (for authorization)
    - **claim_id**: Claim identifier
    - **actor_type**: Filter by actor (customer, AI agent, adjustor, admin)
    - **limit**: Maximum results (default: 100, max: 500)
    - **offset**: Pagination offset (default: 0)
    
    Returns events in chronological order (oldest first).
    Events provide complete audit trail of all claim actions.
    
    **Event Fields:**
    - event_id: Sequential event ID within claim
    - event_date: Date of action
    - event_time: Time of action
    - status: Claim status after action
    - action: Action taken (e.g., "create_claim", "upload_damage_photos")
    - action_by: Actor type (customer, AI agent, adjustor, admin)
    - action_by_identity: Specific actor identifier (e.g., "customer_100")
    - comments: Optional notes/context
    
    **Use Cases:**
    - Customer viewing claim timeline
    - Adjustor auditing claim history
    - Compliance/regulatory reporting
    - Debugging state transition issues
    """
    service = EventService(db)
    
    # Verify claim belongs to customer
    claim_service = ClaimService(db)
    claim = claim_service.get_claim(claim_id)
    if claim.customer_id != customer_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    events = service.get_claim_events(
        claim_id=claim_id,
        actor_type=actor_type,
        limit=limit,
        offset=offset
    )
    return events
```

---

### 7.3 Pydantic Request/Response Schemas

#### 7.3.1 Customer Schemas (`schemas/customer.py`)

```python
from pydantic import BaseModel, Field, field_validator, EmailStr
from datetime import date
from typing import Optional, List

class CustomerCreate(BaseModel):
    """Request schema for creating customer"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr  # Validates email format
    phone: str = Field(..., pattern=r'^\+?1?\d{9,15}$')  # Basic phone validation
    date_of_birth: date
    license_number: str = Field(..., min_length=5, max_length=50)
    
    # Optional fields
    address: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, pattern=r'^[A-Z]{2}$')  # 2-letter state code
    zip_code: Optional[str] = Field(None, pattern=r'^\d{5}(-\d{4})?$')  # US ZIP code
    
    @field_validator("date_of_birth")
    @classmethod
    def validate_age(cls, v):
        """Ensure customer is at least 18 years old"""
        from datetime import date
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError("Customer must be at least 18 years old")
        if age > 120:
            raise ValueError("Invalid date of birth")
        return v

class CustomerUpdate(BaseModel):
    """Request schema for full customer update (all fields required)"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(..., pattern=r'^\+?1?\d{9,15}$')
    date_of_birth: date
    license_number: str = Field(..., min_length=5, max_length=50)
    address: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, pattern=r'^[A-Z]{2}$')
    zip_code: Optional[str] = Field(None, pattern=r'^\d{5}(-\d{4})?$')

class CustomerPatch(BaseModel):
    """Request schema for partial customer update (all fields optional)"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    date_of_birth: Optional[date] = None
    license_number: Optional[str] = Field(None, min_length=5, max_length=50)
    address: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, pattern=r'^[A-Z]{2}$')
    zip_code: Optional[str] = Field(None, pattern=r'^\d{5}(-\d{4})?$')

class CustomerResponse(BaseModel):
    """Response schema for customer"""
    customer_id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    date_of_birth: date
    license_number: str
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    created_at: date
    
    # Optional: included if include_policies=true
    policies: Optional[List["PolicyResponse"]] = None
    
    class Config:
        from_attributes = True
```

#### 7.3.2 Policy Schemas (`schemas/policy.py`)

```python
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List
from decimal import Decimal

class VehicleInfo(BaseModel):
    """Vehicle information in policy response"""
    vin: str
    year: int
    make: str
    model: str
    color: Optional[str] = None
    
    class Config:
        from_attributes = True

class PolicyResponse(BaseModel):
    """Response schema for policy"""
    policy_number: str
    customer_id: int
    policyholder_name: str
    insured_name: str
    
    # Dates
    effective_date: date
    expiration_date: date
    
    # Drivers (flattened structure)
    driver_1: Optional[str] = None
    driver_2: Optional[str] = None
    driver_3: Optional[str] = None
    driver_4: Optional[str] = None
    
    # Coverage limits
    bodily_injury_limit: Decimal
    property_damage_limit: Decimal
    collision_deductible: Optional[Decimal] = None
    comprehensive_deductible: Optional[Decimal] = None
    
    # Financial
    premium: Decimal
    deductible: Decimal
    
    # Associated vehicles
    vehicles: List[VehicleInfo] = []
    
    class Config:
        from_attributes = True
```

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `policy_number` | string | Unique policy identifier (PK) |
| `customer_id` | integer | Foreign key to customer |
| `policyholder_name` | string | Name of policyholder |
| `insured_name` | string | Name of insured party |
| `effective_date` | date | Policy start date |
| `expiration_date` | date | Policy end date |
| `driver_1` - `driver_4` | string | Named drivers on policy (nullable) |
| `bodily_injury_limit` | decimal | Liability coverage limit |
| `property_damage_limit` | decimal | Property damage coverage limit |
| `collision_deductible` | decimal | Collision coverage deductible |
| `comprehensive_deductible` | decimal | Comprehensive coverage deductible |
| `premium` | decimal | Total annual premium |
| `deductible` | decimal | Default deductible amount |
| `vehicles` | list | Vehicles covered by this policy |

#### 7.3.3 Claim Schemas (`schemas/claim.py`)

```python
from pydantic import BaseModel, Field, field_validator
from datetime import date, time
from typing import Optional, List

class ClaimCreate(BaseModel):
    """Request schema for creating claim"""
    vin: str = Field(..., min_length=17, max_length=17)
    policy_number: str = Field(..., max_length=50)
    fnol_date: date
    fnol_time: time
    date_of_damage: date
    is_drivable: bool
    incident_description: Optional[str] = Field(None, max_length=1000)
    
    @field_validator("fnol_date")
    @classmethod
    def validate_fnol_date(cls, v):
        """Ensure FNOL date is not in the future"""
        if v > date.today():
            raise ValueError("FNOL date cannot be in the future")
        return v
    
    @field_validator("date_of_damage")
    @classmethod
    def validate_date_of_damage(cls, v, info):
        """Ensure damage date is not in the future"""
        if v > date.today():
            raise ValueError("Date of damage cannot be in the future")
        # Validate against FNOL date if available
        if info.data.get("fnol_date") and v > info.data["fnol_date"]:
            raise ValueError("Date of damage cannot be after FNOL date")
        return v

class DamageDetail(BaseModel):
    """Individual damage detail from damages table"""
    damage_id: int
    estimate_id: str
    image_id: str
    estimate_type: str  # 'ai' or 'human'
    damage_part: str
    severity: Decimal
    estimated_total_cost: Decimal
    labor_hours: Decimal
    avg_labor_cost: Decimal  # Labor rate ($/hour) applied
    labor_rate_state: str  # State code used for labor rate (e.g., "CA", "TX", "NY")
    estimated_parts_cost: Decimal
    
    class Config:
        from_attributes = True

class DamageAssessment(BaseModel):
    """Damage assessment summary with all damages"""
    total_estimated_cost: Decimal
    damage_count: int
    damages: List[DamageDetail]

class ClaimResponse(BaseModel):
    """Response schema for claim"""
    claim_id: int
    customer_id: int
    vin: str
    policy_number: str
    fnol_date: date
    fnol_time: time
    date_of_damage: date
    is_drivable: bool
    current_status: str
    claim_closed: bool
    claim_closed_date: Optional[date]
    ai_estimate_accepted: bool
    routed_to_traditional: bool
    reason_routing_to_traditional: Optional[str]
    active_estimate_id: Optional[str]
    claim_amount: Optional[float]
    actual_claim_amount: Optional[float]
    
    # Labor Rate Fields
    state_avg_labor_cost: Optional[Decimal] = None
    labor_rate_state: Optional[str] = None
    labor_rate_source: Optional[str] = None
    
    # Appeal Tracking Fields (NEW - 2026-05-06)
    appeal_count: int = 0
    first_appeal_reason: Optional[str] = None
    first_appeal_date: Optional[date] = None
    second_appeal_reason: Optional[str] = None
    second_appeal_date: Optional[date] = None
    
    damage_assessment: Optional[DamageAssessment] = None
    
    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)
```

**Key Schema Features:**

| Schema | Purpose |
|--------|---------|
| `DamageDetail` | Individual damage with all fields from damages table |
| `DamageAssessment` | Container for damages array plus summary (total cost, count) |
| `ClaimResponse` | Claim data with nested `damage_assessment` (null if no damages) |

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `damage_assessment` | DamageAssessment | Null if no damages; otherwise contains summary and damages array |
| `total_estimated_cost` | Decimal | Sum of all estimated_total_cost values |
| `damage_count` | int | Number of damages detected |
| `damages` | List[DamageDetail] | Array of all damages (may span multiple estimates) |
| `image_id` | string | Reference to the image that generated this damage |
| `avg_labor_cost` | Decimal | Labor rate in $/hour (e.g., 156.00 for CA, 125.00 for TX) |
| `labor_rate_state` | string | State code used to determine labor rate (sourced from customer's state of residence) |
```

#### 7.3.4 Claim Event Schemas (`schemas/claim_event.py`)

```python
from pydantic import BaseModel, Field
from datetime import date, time
from typing import Optional

class ClaimEventResponse(BaseModel):
    """Response schema for claim event"""
    claim_id: int
    event_id: int
    event_date: date
    event_time: time
    status: str  # Claim status after this action
    action: str  # Action taken (e.g., "create_claim", "submit_claim")
    action_by: str  # Actor type (customer, AI agent, adjustor, admin)
    action_by_identity: str  # Specific actor (e.g., "customer_100", "adjustor_42")
    comments: Optional[str]  # Optional notes/context
    
    class Config:
        from_attributes = True

class ClaimEventSummary(BaseModel):
    """Summary response for event listing"""
    total_events: int
    events: List[ClaimEventResponse]
    
    # Optional: event statistics
    customer_actions: Optional[int] = 0
    ai_actions: Optional[int] = 0
    adjustor_actions: Optional[int] = 0
    admin_actions: Optional[int] = 0
```

---

## 8. State Machine Implementation

### 8.0 Action-to-Event Mapping

**Every action taken on a claim generates an event** that is logged in the `claims_events` table for audit trail purposes. Events are emitted regardless of whether a state transition occurs. This ensures a complete audit trail of all claim activities.

**Key Principle:** Events capture what happened, not just state changes. An action may update claim data without changing state, but an event is still logged.

The tables below show the complete mapping of actions to events. The "State Transition" column indicates typical transitions, but **the event is logged even if no transition occurs**.

#### 8.0.1 Customer Actions

| Action | Event Logged | Typical State Transition | Actor | Description |
|--------|-------------|--------------------------|-------|-------------|
| **Create Claim** | `create_claim` | → `draft` | Customer | Customer initiates a new claim in draft state |
| **Submit Claim** | `submit_claim` | `draft` → `FNOL` | Customer | Customer submits draft claim for processing |
| **Upload Damage Photo** | `upload_damage_photos` | _(none)_ | Customer | Customer uploads photos of vehicle damage (event per upload) |
| **Delete Image** | `image_deleted` | _(none)_ | Customer | Customer removes an uploaded image (no state change, event logged) |
| **Accept Estimate** | `accept_estimate` | `customer_decision_pending` → `loss_approved` | Customer | Customer accepts AI or human-reviewed estimate |
| **Appeal Estimate** | `appeal_estimate` | `customer_decision_pending` → `loss_appealed` | Customer | Customer disputes the estimate (first appeal → human review, second appeal → traditional) |

#### 8.0.2 AI Agent Actions

| Action | Event Logged | Typical State Transition | Actor | Description |
|--------|-------------|--------------------------|-------|-------------|
| **Generate Estimate** | `generate_estimate` | `FNOL` → `loss_estimated_ai` → `customer_decision_pending` (if conf >= 0.55) OR `FNOL` → `loss_estimated_ai` → `human_review_pending` (if conf < 0.55) | AI Agent | AI analyzes damage photos and generates estimate. High confidence estimates (>= 0.55) automatically proceed to customer decision; low confidence estimates route to human review |
| **Assess Fraud Risk** | `assess_fraud_risk` | _(none)_ | AI Agent | AI calculates fraud probability score (updates claim data, event logged) |
| **Calculate Confidence** | `calculate_confidence_score` | _(none)_ | AI Agent | AI determines confidence in damage assessment (updates claim data, event logged) |
| **Flag for Review** | `flag_for_human_review` | `loss_appealed` → `human_review_pending` | AI Agent | AI flags claim for manual review after first customer appeal |
| **Present Estimate to Customer** | `present_estimate_to_customer` | `loss_estimated_ai` → `customer_decision_pending` | AI Agent | System automatically presents high-confidence AI estimate to customer for accept/appeal decision |

#### 8.0.3 Adjustor Actions

| Action | Event Logged | Typical State Transition | Actor | Description |
|--------|-------------|--------------------------|-------|-------------|
| **Deny Appeal** | `denied_appeal` | `human_review_completed` → `customer_decision_pending` | Adjustor | Adjustor denies customer's appeal (claim data updated, event logged) |
| **Approve Appeal** | `approved_appeal` | `human_review_pending` → `customer_decision_pending` | Adjustor | Adjustor accepts customer's appeal for review |
| **Revise Estimate** | `revised_estimate` | `human_review_pending` → `human_review_completed` | Adjustor | Adjustor completes manual review with revised estimate |
| **Route to Traditional** | `route_to_traditional` | `human_review_completed` → `route_to_traditional` OR `loss_appealed` → `route_to_traditional` | Adjustor / System | Adjustor manually routes claim OR system automatically routes after second customer appeal |

#### 8.0.4 Admin Actions

| Action | Event Logged | Typical State Transition | Actor | Description |
|--------|-------------|--------------------------|-------|-------------|
| **Initiate Payment** | `initiate_payment` | `loss_approved` → `sent_for_payment` | Admin | Payment processing initiated |
| **Payment Sent** | `payment_sent` | `sent_for_payment` → `claim_paid` | Admin | Payment successfully issued to customer |
| **Close Claim** | `close_claim` | `claim_paid` → `claim_closed` OR `traditional_processing_active` → `claim_closed` | Admin | Claim is closed and finalized |

#### 8.0.5 Event Logging Principles

**Important Implementation Notes:**

1. **Events Always Logged:** Every claim update generates an event, regardless of state transition
2. **State in Event Record:** The `status` field captures the claim state **after** the action
3. **Multiple Events Per Claim:** A claim may have many events in sequence (one per action)
4. **No Transition = Still Logged:** Actions that only update claim data (no state change) still generate events
5. **Sequential Event IDs:** Events are numbered sequentially per claim for audit trail ordering

**Example Scenario:**

```
Claim 1000 Event Timeline:
- Event 1: create_claim → status: "draft"
- Event 2: submit_claim → status: "FNOL" (state changed)
- Event 3: upload_damage_photos → status: "IMAGE_UPLOADED" (state changed)
- Event 4: upload_damage_photos → status: "IMAGE_UPLOADED" (NO state change, still logged)
- Event 5: image_deleted → status: "IMAGE_UPLOADED" (NO state change, still logged)
- Event 6: generate_estimate → status: "loss_estimated_ai" (state changed)
```

Each event provides:
- What action occurred
- Who performed it
- When it happened
- What the claim status was afterward
- Optional comments/context

#### 8.0.6 Event Record Structure

Every event logged contains:

```python
{
    "claim_id": 1000,              # Reference to claim
    "event_id": 1,                 # Sequential event ID within claim
    "event_date": "2026-05-03",    # Date of action
    "event_time": "14:30:00",      # Time of action
    "status": "FNOL",              # Claim status after action
    "action": "submit_claim",       # Action taken (from ClaimAction enum)
    "action_by": "customer",       # Actor type (customer/AI agent/adjustor/admin)
    "action_by_identity": "customer_100",  # Specific actor identifier
    "comments": "Claim submitted for processing"  # Optional notes
}
```

#### 8.0.7 Event Logging Implementation

Events are logged automatically using the `@log_event` decorator:

```python
@log_event(action=ClaimAction.SUBMIT_CLAIM, actor_type=ActorType.CUSTOMER)
def submit_claim(self, claim_id: int, customer_id: int) -> Claim:
    # Method implementation
    return claim
```

The decorator:
1. Executes the method
2. Extracts `claim_id` from result
3. Creates event record in `claims_events` table
4. Logs action, actor, and timestamp

#### 8.0.8 Appeal Workflow Business Rules

**Customer Appeal Process:**

When a customer receives an estimate (AI or human-reviewed), they can either accept or appeal:

1. **First Appeal (AI Estimate)**
   - Customer in `customer_decision_pending` state appeals estimate
   - State transitions: `customer_decision_pending` → `loss_appealed` → `human_review_pending`
   - Human adjustor reviews the claim
   - Adjustor completes review: `human_review_pending` → `human_review_completed`
   - Results sent back to customer: `human_review_completed` → `customer_decision_pending`

2. **Second Appeal (After Human Review)**
   - If customer appeals again from `customer_decision_pending` (after human review)
   - State transitions: `customer_decision_pending` → `loss_appealed` → `routed_to_traditional`
   - Claim automatically routed to traditional processing workflow
   - No further AI or human-reviewed estimates

**Implementation Logic:**

The system tracks appeal information in the claim record:
- **Database fields** (NEW - 2026-05-06):
  - `appeal_count`: Number of appeals (0, 1, or 2)
  - `first_appeal_reason`: Customer's reason for first appeal (Text field)
  - `first_appeal_date`: Date when first appeal was submitted
  - `second_appeal_reason`: Customer's reason for second appeal (Text field)
  - `second_appeal_date`: Date when second appeal was submitted
- **First appeal** (appeal_count = 1): Route to `human_review_pending`
- **Second appeal** (appeal_count = 2): Route directly to `routed_to_traditional`
- Appeal reasons are also stored in ClaimEvent.comments field for audit trail

**Event Sequence Example:**

```
First Appeal Workflow:
- Event N: appeal_estimate → status: "loss_appealed" (first appeal)
- Event N+1: flag_for_human_review → status: "human_review_pending"
- Event N+2: revised_estimate → status: "human_review_completed"
- Event N+3: (system) → status: "customer_decision_pending"
- Event N+4: accept_estimate → status: "loss_approved" (customer accepts)

Second Appeal Workflow (Escalation):
- Event N: appeal_estimate → status: "loss_appealed" (first appeal)
- Event N+1: flag_for_human_review → status: "human_review_pending"
- Event N+2: revised_estimate → status: "human_review_completed"
- Event N+3: (system) → status: "customer_decision_pending"
- Event N+4: appeal_estimate → status: "loss_appealed" (second appeal)
- Event N+5: route_to_traditional → status: "routed_to_traditional" (automatic)
```

**Business Justification:**
- Gives customer fair opportunity for human review
- Prevents infinite appeal loops
- Escalates persistent disputes to traditional process with physical inspection

---

### 8.1 State Machine Service (`services/state_machine.py`)

```python
from src.api.constants import ClaimState, VALID_TRANSITIONS
from typing import List

def validate_transition(current_state: ClaimState, new_state: ClaimState) -> bool:
    """
    Validate if state transition is allowed.
    
    Args:
        current_state: Current claim state
        new_state: Target state
        
    Returns:
        True if transition is valid, False otherwise
    """
    valid_next_states = VALID_TRANSITIONS.get(current_state, [])
    return new_state in valid_next_states

def get_valid_transitions(current_state: ClaimState) -> List[ClaimState]:
    """Get list of valid next states"""
    return VALID_TRANSITIONS.get(current_state, [])

def is_terminal_state(state: ClaimState) -> bool:
    """Check if state is terminal (no valid transitions)"""
    return len(VALID_TRANSITIONS.get(state, [])) == 0
```

---

## 9. Event Logging System

### 9.1 Event Logger Decorator (`services/event_logger.py`)

```python
from functools import wraps
from sqlalchemy.orm import Session
from src.api.models.claim_event import ClaimEvent
from src.api.constants import ClaimAction, ActorType
from datetime import date, datetime
import logging

logger = logging.getLogger(__name__)

def log_event(action: ClaimAction, actor_type: ActorType):
    """
    Decorator to automatically log claim events.
    
    Usage:
        @log_event(action=ClaimAction.CREATE_CLAIM, actor_type=ActorType.CUSTOMER)
        def create_claim(self, customer_id, claim_data):
            # ... method implementation
            return claim
    
    The decorator expects the method to return a Claim instance.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Execute the function
            result = func(self, *args, **kwargs)
            
            # Extract claim_id from result
            claim_id = getattr(result, 'claim_id', None)
            
            if claim_id:
                try:
                    # Create event record
                    event = ClaimEvent(
                        claim_id=claim_id,
                        event_date=date.today(),
                        event_time=datetime.now().time(),
                        status=result.current_status,
                        action=action.value,
                        action_by=actor_type.value,
                        action_by_identity=_extract_actor_identity(*args, **kwargs),
                        comments=kwargs.get('comments', '')
                    )
                    
                    self.db.add(event)
                    self.db.commit()
                    
                    logger.info(
                        f"Logged event: claim_id={claim_id}, "
                        f"action={action.value}, actor={actor_type.value}"
                    )
                except Exception as e:
                    logger.error(f"Failed to log event: {e}")
                    # Don't fail the operation if logging fails
            
            return result
        return wrapper
    return decorator

def _extract_actor_identity(*args, **kwargs) -> str:
    """Extract actor identity from method arguments"""
    # Try to get from kwargs
    if 'actor_identity' in kwargs:
        return kwargs['actor_identity']
    
    # Try to infer from customer_id or adjustor_id
    if 'customer_id' in kwargs:
        return f"customer_{kwargs['customer_id']}"
    
    # Default
    return "system"
```

---

## 10. Image Storage & Management

### 10.1 Image Upload Flow

> **Sequence Diagram:** See [`diagrams/claim_image_upload.mmd`](./diagrams/claim_image_upload.mmd) for complete flow visualization

**Business Rule - Critical:** Images can **ONLY** be uploaded when claim is in `draft` state. Any attempt to upload to a claim not in draft state will result in an error.

**Upload Flow (7 steps):**

1. **Customer uploads image**
   - `POST /api/v1/customers/{customer_id}/claims/{claim_id}/images`
   - Multipart form data with image file

2. **Verify claim is in 'draft' state**
   - Query claim record and check `current_status`
   - **If NOT draft:** Return 400 Bad Request error
   - **If draft:** Proceed to next step

3. **Store image file**
   - Save to filesystem: `uploads/{claim_id}/{filename}`
   - Create database record in `claim_images` table

4. **YOLO analyzes image** (AI damage detection)
   - Image processed by YOLO model
   - Returns damage detections (part, severity, confidence, etc.)

5. **Add damage report to claim**
   - Insert damage report into `damages` table
   - Links damage to claim and image
   - Includes: damage_part, severity, confidence, cost estimates

6. **Log event**
   - Insert event into `claims_events` table
   - Action: `upload_damage_photos`
   - Records who uploaded and when

7. **NO status change**
   - ⚠️ **Important:** Claim status remains `draft`
   - Multiple images can be uploaded while claim stays in draft
   - Status only changes during claim submission (separate process)

**Key Points:**
- ✅ Only draft claims can receive image uploads
- ✅ YOLO analyzes every uploaded image automatically
- ✅ Damage reports created and stored in database
- ✅ Events logged for complete audit trail
- ❌ Claim status does NOT change (remains `draft`)

**When Does Status Change?**
Status change happens during **Claim Submission** (not image upload):
- `draft` → `FNOL` when customer submits claim for processing
- Claim submission is a separate API endpoint and process

### 10.1.1 Image Upload Business Rules

**Critical Validation:**
| Rule | Requirement | Error if Violated |
|------|-------------|-------------------|
| **Claim State** | Claim MUST be in `draft` state | 400 Bad Request: "Cannot add image to claim not in draft state" |
| **Claim Exists** | Claim must exist in database | 404 Not Found: "Claim not found" |

**What Happens During Upload:**
- ✅ Image stored in filesystem
- ✅ YOLO analyzes image for damage
- ✅ Damage report added to `damages` table
- ✅ Event logged in `claims_events` table
- ❌ Claim status does NOT change (stays `draft`)

**Multiple Image Uploads:**
- Customer can upload multiple images to same claim
- Each upload triggers independent YOLO analysis
- Each upload logs separate event
- Claim remains in `draft` state throughout

**Database Changes:**

```sql
-- 1. Store image reference
INSERT INTO claim_images (image_id, claim_id, uploaded_at, uploaded_by)
VALUES ('{filename}', {claim_id}, NOW(), 'customer_{id}');

-- 2. Add YOLO damage detection results
INSERT INTO damages (
    claim_id,
    estimate_id,
    image_id,
    damage_part,      -- e.g., "boot-dent"
    severity,         -- e.g., 0.8
    confidence,       -- e.g., 0.86
    -- ... other YOLO outputs
) VALUES (...);

-- 3. Log upload event
INSERT INTO claims_events (
    claim_id,
    event_date,
    event_time,
    status,           -- Still 'draft' (NO CHANGE)
    action,           -- 'upload_damage_photos'
    action_by,        -- 'customer'
    action_by_identity,
    comments
) VALUES (...);

-- 4. NO UPDATE to claims table status
-- Claim remains in 'draft' state
```

**Error Scenarios:**

| Error Condition | HTTP Status | Error Message |
|----------------|-------------|---------------|
| Claim NOT in 'draft' state | 400 Bad Request | "Cannot add image to claim not in draft state" |
| Claim not found | 404 Not Found | "Claim not found" |

### 10.1.2 Example Upload Requests

**Example Upload Request (curl):**
```bash
curl -X POST \
  http://localhost:8000/api/v1/customers/100/claims/1000/images \
  -F "file=@front_bumper_damage.jpg" \
  -H "Content-Type: multipart/form-data"
```

**Example Upload Request (Python requests):**
```python
import requests

url = "http://localhost:8000/api/v1/customers/100/claims/1000/images"
files = {"file": open("front_bumper_damage.jpg", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

**Example Upload Request (JavaScript/Fetch):**
```javascript
const formData = new FormData();
formData.append("file", fileInput.files[0]);

fetch("/api/v1/customers/100/claims/1000/images", {
  method: "POST",
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

### 10.1.3 Storage Structure

**Filesystem Storage:**
```
{IMAGES_ROOT_FOLDER}/              # Configurable root (default: "uploads")
├── {claim_id}/                    # Per-claim subdirectory
│   └── {filename}                 # Original filename preserved
│
Example:
uploads/                           # Root folder
├── 1000/                          # Claim 1000
│   ├── front_bumper_damage.jpg
│   ├── rear_damage.jpg
│   └── side_panel.jpg
├── 1001/                          # Claim 1001
│   └── trunk_dent.jpg
└── 1002/                          # Claim 1002
    ├── door_scratch.jpg
    └── hood_damage.jpg
```

**Path Format**: `{IMAGES_ROOT_FOLDER}/{claim_id}/{filename}`  
**Example Full Path**: `uploads/1000/front_bumper_damage.jpg`

---

### 10.2 Image Service Implementation

**Status:** ✅ Implementation aligned with specification (2026-05-03)

**Implementation:** `services/image_service.py`

```python
from fastapi import UploadFile
from sqlalchemy.orm import Session
from src.api.models.claim import ClaimImage
from src.api.services.base_service import BaseService
from src.api.config import settings
from src.api.exceptions import ValidationError, ResourceNotFoundError
from src.api.constants import ClaimAction, ActorType
from src.api.services.event_logger import log_event
import os
import shutil
from pathlib import Path
from datetime import datetime

class ImageService(BaseService):
    """Service for image upload/delete operations"""
    
    def __init__(self, db: Session):
        super().__init__(db)
        # Root directory for all claim images
        self.images_root = Path(settings.IMAGES_ROOT_FOLDER)
        self.images_root.mkdir(exist_ok=True)
    
    def _validate_image_file(self, file: UploadFile):
        """Validate image file type and size"""
        # Check filename exists
        if not file.filename:
            raise ValidationError("Filename is required")
        
        # Check file extension
        ext = file.filename.split('.')[-1].lower()
        if ext not in settings.ALLOWED_IMAGE_TYPES:
            raise ValidationError(
                f"Invalid file type. Allowed: {settings.ALLOWED_IMAGE_TYPES}"
            )
        
        # Check file size (read in chunks to avoid memory issues)
        file.file.seek(0, 2)  # Seek to end
        size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if size > max_size:
            raise ValidationError(
                f"File too large. Maximum: {settings.MAX_UPLOAD_SIZE_MB}MB"
            )
    
    def _check_duplicate_filename(self, claim_id: int, filename: str) -> bool:
        """Check if filename already exists for this claim"""
        existing = self.db.query(ClaimImage).filter(
            ClaimImage.claim_id == claim_id,
            ClaimImage.image_id == filename
        ).first()
        return existing is not None
    
    def _get_claim_upload_dir(self, claim_id: int) -> Path:
        """
        Get upload directory for specific claim.
        Creates subdirectory structure: {IMAGES_ROOT_FOLDER}/{claim_id}/
        
        Args:
            claim_id: Claim ID
            
        Returns:
            Path object for claim's image directory
        """
        claim_dir = self.images_root / str(claim_id)
        claim_dir.mkdir(parents=True, exist_ok=True)
        return claim_dir
    
    @log_event(action=ClaimAction.UPLOAD_DAMAGE_PHOTOS, actor_type=ActorType.CUSTOMER)
    def upload_image(
        self, 
        claim_id: int, 
        file: UploadFile,
        uploaded_by: str
    ) -> ClaimImage:
        """
        Upload image to filesystem and create database record.
        
        Args:
            claim_id: Claim ID
            file: Uploaded file
            uploaded_by: Actor identifier (e.g., "customer_100")
            
        Returns:
            ClaimImage instance
            
        Raises:
            ValidationError: If file validation fails
        """
        # Validate file
        self._validate_image_file(file)
        
        # Check for duplicate filename
        if self._check_duplicate_filename(claim_id, file.filename):
            raise ValidationError(
                f"Image '{file.filename}' already exists for this claim. "
                f"Please rename the file or delete the existing image first."
            )
        
        # Check max images per claim
        image_count = self.db.query(ClaimImage).filter(
            ClaimImage.claim_id == claim_id
        ).count()
        
        if image_count >= settings.MAX_IMAGES_PER_CLAIM:
            raise ValidationError(
                f"Maximum {settings.MAX_IMAGES_PER_CLAIM} images per claim"
            )
        
        # Save file to filesystem
        claim_dir = self._get_claim_upload_dir(claim_id)
        file_path = claim_dir / file.filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create database record
        image = ClaimImage(
            image_id=file.filename,
            claim_id=claim_id,
            uploaded_at=datetime.now(),
            uploaded_by=uploaded_by
        )
        
        self.db.add(image)
        self.commit()
        
        self.logger.info(f"Uploaded image {file.filename} for claim {claim_id}")
        return image
    
    @log_event(action=ClaimAction.DELETE_IMAGE, actor_type=ActorType.CUSTOMER)
    def delete_image(
        self, 
        claim_id: int, 
        image_id: str,
        deleted_by: str
    ) -> None:
        """
        Delete image from filesystem and database.
        Cascade deletes associated damages (ON DELETE CASCADE).
        
        Args:
            claim_id: Claim ID
            image_id: Image filename
            deleted_by: Actor identifier
            
        Raises:
            ResourceNotFoundError: If image doesn't exist
        """
        # Get image record
        image = self.db.query(ClaimImage).filter(
            ClaimImage.claim_id == claim_id,
            ClaimImage.image_id == image_id
        ).first()
        
        if not image:
            raise ResourceNotFoundError("Image", image_id)
        
        # Delete from filesystem
        claim_dir = self._get_claim_upload_dir(claim_id)
        file_path = claim_dir / image_id
        
        if file_path.exists():
            file_path.unlink()
        
        # Delete from database (cascade deletes damages)
        self.db.delete(image)
        self.commit()
        
        self.logger.info(f"Deleted image {image_id} from claim {claim_id}")
```

---

## 11. AI Integration

### 11.1 Damage Detector with YOLO Integration (`ai/damage_detector.py`)

**Model:** `vineetsarpal/yolov11n-car-damage` (HuggingFace)  
**Classes:** 14 car damage types (0-13)  
**Output:** Bounding boxes, confidence scores, damage classifications

```python
"""
Damage Detector - YOLO Integration

Integrates YOLOv11 model for car damage detection.
Model: vineetsarpal/yolov11n-car-damage (HuggingFace)
"""

from typing import List, Dict, Optional
from pathlib import Path
import logging

from ultralytics import YOLO
from huggingface_hub import hf_hub_download
from PIL import Image
import cv2
import numpy as np

from src.api.config import settings

logger = logging.getLogger(__name__)

# YOLO class names (14 damage types)
YOLO_CLASS_NAMES = {
    0: 'Front-windscreen-damage',
    1: 'Headlight-damage',
    2: 'Rear-windscreen-Damage',
    3: 'Runningboard-Damage',
    4: 'Sidemirror-Damage',
    5: 'Taillight-Damage',
    6: 'bonnet-dent',
    7: 'boot-dent',
    8: 'doorouter-dent',
    9: 'fender-dent',
    10: 'front-bumper-dent',
    11: 'quaterpanel-dent',
    12: 'rear-bumper-dent',
    13: 'roof-dent'
}

class DamageDetector:
    """Damage detection using YOLO model"""

    def __init__(self, model_path: Optional[str] = None, device: Optional[str] = None):
        """
        Initialize damage detector.

        Args:
            model_path: Path to YOLO model (HF repo or local path). If None, uses config.
            device: Device for inference (cpu, cuda, mps). If None, uses config.
        """
        # Load configuration
        self.model_source = settings.YOLO_MODEL_SOURCE
        self.model_path = model_path or settings.YOLO_MODEL_PATH
        self.device = device or settings.YOLO_DEVICE
        self.confidence_threshold = settings.YOLO_CONFIDENCE_THRESHOLD
        self.save_annotated = settings.YOLO_SAVE_ANNOTATED_IMAGES
        self.annotated_prefix = settings.YOLO_ANNOTATED_IMAGE_PREFIX
        
        # Load model
        self.model = self._load_model()
        
        logger.info(
            f"DamageDetector initialized: source={self.model_source}, "
            f"model={self.model_path}, device={self.device}"
        )

    def _load_model(self) -> YOLO:
        """Load YOLO model from HuggingFace or local path"""
        try:
            if self.model_source == "huggingface":
                logger.info(f"Downloading model from HuggingFace: {self.model_path}")
                model_file = hf_hub_download(
                    repo_id=self.model_path,
                    filename="best.pt"
                )
                model = YOLO(model_file)
            else:
                logger.info(f"Loading local model: {self.model_path}")
                model = YOLO(self.model_path)
            
            logger.info(f"Model loaded successfully: {model.names}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise RuntimeError(f"YOLO model initialization failed: {e}")
    
    def detect_damages(
        self, 
        image_path: Path,
        save_annotated_path: Optional[Path] = None
    ) -> List[Dict]:
        """
        Detect damages in image using YOLO.

        Args:
            image_path: Path to damage image
            save_annotated_path: Optional path to save annotated image

        Returns:
            List of damage detections with bounding boxes and assessments
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        logger.info(f"Running YOLO inference on: {image_path.name}")
        
        # Run YOLO inference
        results = self.model.predict(
            source=str(image_path),
            conf=self.confidence_threshold,
            device=self.device,
            verbose=False
        )
        
        # Parse results
        damages = []
        result = results[0]
        
        if len(result.boxes) == 0:
            logger.warning(f"No damages detected in {image_path.name}")
            return damages
        
        # Read image for size calculation
        image = cv2.imread(str(image_path))
        image_height, image_width = image.shape[:2]
        image_area = image_height * image_width
        
        for i, box in enumerate(result.boxes):
            class_id = int(box.cls)
            confidence = float(box.conf)
            damage_part = self.model.names[class_id]
            
            # Extract bounding box
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            bbox = {
                "x": int(x1),
                "y": int(y1),
                "width": int(x2 - x1),
                "height": int(y2 - y1)
            }
            
            # Calculate area and assess damage
            damage_area = bbox["width"] * bbox["height"]
            area_ratio = damage_area / image_area
            
            assessment = self._assess_damage(
                damage_part, confidence, bbox, area_ratio,
                image_width, image_height
            )
            
            damage = {
                "damage_class": class_id,
                "confidence": round(confidence, 2),
                "damage_part": damage_part,
                "bounding_box": bbox,
                **assessment
            }
            damages.append(damage)
        
        # Save annotated image if requested
        if save_annotated_path or self.save_annotated:
            path = save_annotated_path or self._get_annotated_path(image_path)
            self._save_annotated_image(result, path)
        
        logger.info(f"Detected {len(damages)} damage(s) in {image_path.name}")
        return damages
    
    def _assess_damage(
        self, damage_part: str, confidence: float, bbox: Dict,
        area_ratio: float, image_width: int, image_height: int
    ) -> Dict:
        """
        Assess damage severity (heuristic-based).
        Future: Replace with VLM assessment.
        """
        # Calculate severity from area ratio
        if area_ratio < 0.05:
            severity = 0.3
        elif area_ratio < 0.15:
            severity = 0.6
        else:
            severity = 0.9
        
        # Estimate internal damage probability
        if any(x in damage_part.lower() for x in ['windscreen', 'headlight', 'taillight']):
            internal_damage_prob = 0.8
        elif 'bumper' in damage_part.lower():
            internal_damage_prob = 0.6
        elif 'dent' in damage_part.lower():
            internal_damage_prob = 0.4 if severity > 0.6 else 0.2
        else:
            internal_damage_prob = 0.3
        
        # Determine recommended action
        if any(x in damage_part.lower() for x in ['windscreen', 'headlight', 'taillight', 'mirror']):
            action = "replace"
        elif 'dent' in damage_part.lower():
            action = "de-dent-and-paint" if severity > 0.5 else "de-dent"
        else:
            action = "repaint"
        
        # Determine car side from bbox position
        center_y = bbox["y"] + bbox["height"] / 2
        center_x = bbox["x"] + bbox["width"] / 2
        
        if center_y < image_height * 0.4:
            car_side = "front"
        elif center_y > image_height * 0.6:
            car_side = "back"
        elif center_x < image_width * 0.5:
            car_side = "driver_side"
        else:
            car_side = "passenger_side"
        
        reasoning = (
            f"{damage_part.replace('-', ' ').title()} detected with "
            f"{confidence:.0%} confidence. Damage covers {area_ratio:.1%} "
            f"of image area. Severity: {severity:.1f}. Action: {action}."
        )
        
        return {
            "severity": round(severity, 2),
            "internal_damage_probability": round(internal_damage_prob, 2),
            "recommended_action": action,
            "reasoning": reasoning,
            "car_side": car_side,
            "assessment_confidence": round(confidence * 0.95, 2)
        }

    def _get_annotated_path(self, original_path: Path) -> Path:
        """Generate path for annotated image"""
        return original_path.parent / f"{self.annotated_prefix}{original_path.name}"

    def _save_annotated_image(self, result, save_path: Path):
        """Save image with bounding boxes drawn"""
        try:
            annotated_img = result.plot()
            cv2.imwrite(str(save_path), annotated_img)
            logger.info(f"Annotated image saved: {save_path.name}")
        except Exception as e:
            logger.error(f"Failed to save annotated image: {e}")

# Singleton instance
_detector_instance = None

def get_damage_detector() -> DamageDetector:
    """Get singleton damage detector instance"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = DamageDetector()
    return _detector_instance
```

### 11.2 Cost Calculation Service (`services/cost_service.py`)

**Labor Rate Determination:**
- The cost estimator uses the **customer's state of residence** to determine the labor rate
- Customer state is stored in the `customers.state` field (2-letter state code)
- When damage is detected via image upload, the system automatically retrieves the customer's state from their profile
- The state is stored with each damage record in `damages.labor_rate_state` for audit purposes
- All damages for a single claim use the same labor rate based on customer's state

```python
"""
Cost calculation service for damage repair estimation.
Provides cost estimates based on damage part, severity, and customer state.
"""
from typing import Dict, Any
from src.api.services.base_service import BaseService
import logging

logger = logging.getLogger(__name__)

# State-specific labor rates ($/hour)
# These rates are applied based on the customer's state of residence
STATE_LABOR_RATES = {
    "CA": 156.00,
    "TX": 125.00,
    "NY": 175.00,
    "FL": 135.00,
    "DEFAULT": 140.00
}

# Damage part base estimates
DAMAGE_PART_ESTIMATES = {
    "boot-dent": {"labor_hours": (1.5, 3.0), "parts_cost": (500, 1200)},
    "front-bumper-dent": {"labor_hours": (1.0, 2.5), "parts_cost": (300, 800)},
    "door-scratch": {"labor_hours": (0.5, 1.5), "parts_cost": (200, 600)},
    "paint-damage": {"labor_hours": (1.0, 2.0), "parts_cost": (150, 400)},
    "rear-bumper": {"labor_hours": (1.5, 2.5), "parts_cost": (400, 900)},
    "hood-dent": {"labor_hours": (2.0, 3.5), "parts_cost": (600, 1500)},
    "side-panel": {"labor_hours": (2.5, 4.0), "parts_cost": (800, 2000)},
}

class CostService(BaseService):
    """Service for calculating repair cost estimates"""
    
    def calculate_cost(
        self,
        damage_report: Dict,
        assessment: Dict,
        state: str = "CA"
    ) -> Dict[str, Any]:
        """
        Calculate repair cost based on damage report and assessment.
        
        Args:
            damage_report: Damage detection info (part, class, confidence)
            assessment: Damage assessment (severity, internal_damage_probability)
            state: State code for labor rate (sourced from customer's state of residence)
            
        Returns:
            Cost breakdown with labor, parts, total, and state used
        """
        damage_part = damage_report.get("part", "unknown")
        severity = assessment.get("severity", 0.5)
        internal_damage_prob = assessment.get("internal_damage_probability", 0.0)
        confidence = damage_report.get("confidence", 0.7)
        
        # Get labor rate for customer's state of residence
        labor_rate = STATE_LABOR_RATES.get(state, STATE_LABOR_RATES["DEFAULT"])
        
        # Get base estimates for damage part
        if damage_part in DAMAGE_PART_ESTIMATES:
            base = DAMAGE_PART_ESTIMATES[damage_part]
        else:
            # Default estimates for unknown parts
            base = {"labor_hours": (1.0, 2.0), "parts_cost": (300, 600)}
            logger.warning(f"Unknown damage part: {damage_part}, using defaults")
        
        # Calculate labor hours based on severity
        labor_hours = self._interpolate_labor_hours(base["labor_hours"], severity)
        
        # Calculate parts cost based on severity
        parts_cost = self._interpolate_parts_cost(base["parts_cost"], severity)
        
        # Calculate base costs
        labor_cost = labor_hours * labor_rate
        
        # Apply internal damage adjustment
        if internal_damage_prob > 0.7:
            adjustment_factor = 1.5  # 50% increase
        elif internal_damage_prob > 0.5:
            adjustment_factor = 1.25  # 25% increase
        else:
            adjustment_factor = 1.0
        
        # Apply adjustment
        adjusted_labor_cost = labor_cost * adjustment_factor
        adjusted_parts_cost = parts_cost * adjustment_factor
        total_cost = adjusted_labor_cost + adjusted_parts_cost
        
        return {
            "damage_part": damage_part,
            "severity": severity,
            "labor_hours": round(labor_hours, 2),
            "avg_labor_cost": labor_rate,
            "estimated_parts_cost": round(adjusted_parts_cost, 2),
            "estimated_total_cost": round(total_cost, 2),
            "labor_rate_state": state,  # Store state used for labor rate calculation
            "breakdown": {
                "labor_cost": round(adjusted_labor_cost, 2),
                "parts_cost": round(adjusted_parts_cost, 2),
                "total": round(total_cost, 2)
            },
            "confidence": confidence,
            "notes": f"Estimate based on severity {severity} and internal damage probability {internal_damage_prob}"
        }
    
    def _interpolate_labor_hours(self, range_tuple: tuple, severity: float) -> float:
        """Interpolate labor hours based on severity"""
        min_hours, max_hours = range_tuple
        # Linear interpolation based on severity
        return min_hours + (max_hours - min_hours) * severity
    
    def _interpolate_parts_cost(self, range_tuple: tuple, severity: float) -> float:
        """Interpolate parts cost based on severity"""
        min_cost, max_cost = range_tuple
        # Linear interpolation based on severity
        return min_cost + (max_cost - min_cost) * severity
```

### 11.3 Cost Router (`routers/cost.py`)

```python
"""
Cost estimation API router.
Provides endpoint for calculating repair cost estimates.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.api.database import get_db
from src.api.schemas.cost import CostEstimateRequest, CostEstimateResponse
from src.api.services.cost_service import CostService
from pydantic import BaseModel, Field
from typing import Dict

router = APIRouter()

# Pydantic schemas
class DamageReportSchema(BaseModel):
    id: int
    class_: int = Field(..., alias="class")
    confidence: float = Field(..., ge=0.0, le=1.0)
    part: str

class AssessmentSchema(BaseModel):
    internal_damage_probability: float = Field(..., ge=0.0, le=1.0)
    severity: float = Field(..., ge=0.0, le=1.0)
    recommended_action: str
    reasoning: str
    car_side: str
    confidence: float = Field(..., ge=0.0, le=1.0)

class CostEstimateRequest(BaseModel):
    damage_report: DamageReportSchema
    assessment: AssessmentSchema
    state: str = "CA"

@router.post("/estimate", response_model=Dict)
def calculate_cost_estimate(
    request: CostEstimateRequest,
    db: Session = Depends(get_db)
):
    """
    Calculate repair cost estimate for damage report.
    
    - **damage_report**: Damage detection results
    - **assessment**: Damage assessment details
    - **state**: State code for labor rate (default: CA)
    """
    service = CostService(db)
    
    cost_info = service.calculate_cost(
        damage_report=request.damage_report.dict(by_alias=True),
        assessment=request.assessment.dict(),
        state=request.state
    )
    
    return {"data": cost_info}
```

**Important: State Parameter Flow for Labor Rates**

The `state` parameter used for labor rate calculation follows this flow:

1. **Image Upload** → When customer uploads damage images, the system retrieves the customer's state from `customers.state`
2. **Damage Detection** → YOLO analyzes images and generates damage reports
3. **Cost Calculation** → `CostService.calculate_cost()` is called with the customer's state
4. **Database Storage** → The resulting labor rate is stored in `damages.avg_labor_cost` and the state is stored in `damages.labor_rate_state`
5. **API Response** → When adjustor views claim, each damage includes both `avg_labor_cost` and `labor_rate_state` fields

This ensures:
- All damages on a claim use the customer's state of residence for labor rates
- Adjustors can see which state's rates were applied
- Audit trail is maintained for regulatory compliance

### 11.4 Estimate Service (Updated)

The estimate service now uses the cost service and automatically retrieves customer state:

```python
from src.api.services.cost_service import CostService

class EstimateService(BaseService):
    """Service for generating damage estimates"""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.cost_service = CostService(db)
    
    @log_event(action=ClaimAction.GENERATE_ESTIMATE, actor_type=ActorType.AI_AGENT)
    def generate_ai_estimate(
        self, 
        claim_id: int, 
        image_ids: List[str],
        state: str = "CA"
    ) -> Dict:
        """Generate AI damage estimate for claim"""
        detector = get_damage_detector()
        estimate_id = f"{claim_id}_{int(datetime.now().timestamp())}"
        
        damages = []
        total_cost = 0.0
        
        for image_id in image_ids:
            image_path = Path(settings.IMAGES_ROOT_FOLDER) / str(claim_id) / image_id
            detections = detector.detect_damages(image_path)
            
            for detection in detections:
                # Call cost service API
                cost_info = self.cost_service.calculate_cost(
                    damage_report={
                        "part": detection["damage_part"],
                        "class": detection["damage_class"],
                        "confidence": detection["confidence"]
                    },
                    assessment={
                        "severity": detection["severity"],
                        "internal_damage_probability": 0.5,  # From AI model
                        "confidence": detection["confidence"]
                    },
                    state=state
                )
                
                # Create damage record with cost info
                damage = Damage(
                    claim_id=claim_id,
                    estimate_id=estimate_id,
                    estimate_type=EstimateType.AI,
                    image_id=image_id,
                    damage_part=detection["damage_part"],
                    severity=detection["severity"],
                    estimated_total_cost=cost_info["estimated_total_cost"],
                    labor_hours=cost_info["labor_hours"],
                    avg_labor_cost=cost_info["avg_labor_cost"],
                    estimated_parts_cost=cost_info["estimated_parts_cost"]
                )
                
                self.db.add(damage)
                damages.append(damage)
                total_cost += cost_info["estimated_total_cost"]
        
        self.commit()
        
        return {
            "estimate_id": estimate_id,
            "total_cost": total_cost,
            "damages_count": len(damages)
        }
```

---

## 12. Error Handling

### 12.1 Custom Exceptions (`exceptions.py`)

```python
class AppException(Exception):
    """Base application exception"""
    pass

class ResourceNotFoundError(AppException):
    """Resource not found"""
    def __init__(self, resource_type: str, resource_id):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(f"{resource_type} {resource_id} not found")

class StateTransitionError(AppException):
    """Invalid state transition"""
    def __init__(self, current_state: str, new_state: str, valid_transitions: list):
        self.current_state = current_state
        self.new_state = new_state
        self.valid_transitions = valid_transitions
        super().__init__(
            f"Invalid transition from {current_state} to {new_state}"
        )

class ValidationError(AppException):
    """Validation error"""
    pass

def register_exception_handlers(app):
    """Register FastAPI exception handlers"""
    from fastapi import Request
    from fastapi.responses import JSONResponse
    
    @app.exception_handler(ResourceNotFoundError)
    async def not_found_handler(request: Request, exc: ResourceNotFoundError):
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "RESOURCE_NOT_FOUND",
                    "message": str(exc),
                    "details": {
                        "resource_type": exc.resource_type,
                        "resource_id": exc.resource_id
                    }
                }
            }
        )
    
    @app.exception_handler(StateTransitionError)
    async def state_transition_handler(request: Request, exc: StateTransitionError):
        return JSONResponse(
            status_code=409,
            content={
                "error": {
                    "code": "INVALID_STATE_TRANSITION",
                    "message": str(exc),
                    "details": {
                        "current_state": exc.current_state,
                        "requested_state": exc.new_state,
                        "valid_transitions": exc.valid_transitions
                    }
                }
            }
        )
```

---

## 13. Logging & Monitoring

### 13.1 Logging Configuration (`utils/logging_config.py`)

```python
import logging
import logging.handlers
from pathlib import Path
from src.api.config import settings

def setup_logging():
    """Configure structured logging"""
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        handlers=[
            # Console handler
            logging.StreamHandler(),
            # Rotating file handler
            logging.handlers.RotatingFileHandler(
                settings.LOG_FILE,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
        ]
    )
    
    # Set log levels for third-party libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
```

---

## 14. Testing Strategy

### 14.1 Test Configuration (`conftest.py`)

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.api.main import app
from src.api.database import Base, get_db
from src.api.models.customer import Customer
from src.api.models.claim import Claim

# Test database
TEST_DATABASE_URL = "sqlanywhere://test:test@localhost:2638/test_insurance_db"
engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    session = TestSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    """FastAPI test client"""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def sample_customer(db_session):
    """Create sample customer"""
    customer = Customer(
        customer_id=100,
        fname="Jane",
        lname="Doe",
        email="jane@example.com",
        phone="+1-555-0123"
    )
    db_session.add(customer)
    db_session.commit()
    return customer
```

### 14.2 Example Test (`tests/test_claims.py`)

```python
def test_create_claim_fnol(client, sample_customer):
    """Test FNOL creation"""
    response = client.post(
        f"/api/v1/customers/{sample_customer.customer_id}/claims",
        json={
            "vin": "1ABC23456789DEFG",
            "policy_number": "PA-992384-01",
            "fnol_date": "2026-05-03",
            "fnol_time": "10:30:00",
            "date_of_damage": "2026-05-02",
            "is_drivable": True
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["current_status"] == "FNOL"
    assert data["customer_id"] == sample_customer.customer_id
```

---

## 15. Database Seeding

### 15.1 Seed Script (`seed.sql`)

```sql
-- Seed sample data for testing

-- Customers
INSERT INTO customers VALUES 
    (100, 'Jane', 'Doe', 'jane@example.com', '+1-555-0123', '123 Main St, CA'),
    (101, 'John', 'Smith', 'john@example.com', '+1-555-0124', '456 Oak Ave, CA');

-- Policies
INSERT INTO policies VALUES
    ('PA-992384-01', 100, '2024-05-01', '2025-05-01', 'Jane Doe', 
     'Jane Doe', 'John Smith', NULL, NULL, 100000, 500, 250, 1200.50);

-- Vehicles
INSERT INTO vehicles VALUES
    ('1ABC23456789DEFG', 100, 2022, 'Toyota', 'Camry', 'Silver');

-- Link policy and vehicle
INSERT INTO policy_vehicle VALUES ('PA-992384-01', '1ABC23456789DEFG');
```

### 15.2 Python Seed Script (`scripts/seed_data.py`)

```python
"""Generate realistic test data using Faker"""
from faker import Faker
from src.api.database import SessionLocal
from src.api.models.customer import Customer
import random

fake = Faker()

def seed_customers(count=50):
    """Generate sample customers"""
    db = SessionLocal()
    
    for i in range(count):
        customer = Customer(
            customer_id=100 + i,
            fname=fake.first_name(),
            lname=fake.last_name(),
            email=fake.email(),
            phone=fake.phone_number(),
            address=fake.address().replace('\n', ', ')
        )
        db.add(customer)
    
    db.commit()
    db.close()
    print(f"Seeded {count} customers")

if __name__ == "__main__":
    seed_customers()
```

---

## 16. Deployment Considerations

### 16.0 Example Configuration File (`api-config.example.yaml`)

**Template configuration file** (copy to `api-config.yaml` and customize):

```yaml
# ============================================================================
# Insurance Claims API - Configuration File
# ============================================================================
# Copy this file to api-config.yaml and customize for your environment
# DO NOT commit api-config.yaml with sensitive data (database passwords, etc.)

# API Configuration
api:
  title: "Insurance Claims API"
  version: "v1"
  debug: true              # Set to false in production
  host: "0.0.0.0"         # Use "localhost" for local development only
  port: 8000

# Database Configuration
database:
  # SQLAnywhere connection string
  # Format: sqlanywhere://user:password@host:port/database
  url: "sqlanywhere://user:password@localhost:2638/insurance_db"
  pool_size: 5            # Connection pool size
  max_overflow: 10        # Max overflow connections
  echo: false             # Set to true to log all SQL queries (debug only)

# Image Storage Configuration
storage:
  # Root directory for storing claim images
  # Structure: {images_root_folder}/{claim_id}/{filename}
  images_root_folder: "uploads"
  
  # File upload limits
  max_upload_size_mb: 10
  allowed_image_types:
    - "jpg"
    - "jpeg"
    - "png"
    - "heic"
  max_images_per_claim: 20

# AI and State Machine Configuration
ai:
  # Path to Standard Operating Procedures (SOP) document
  # Contains instructions for AI agent decision-making
  sop_claims_document: "policies/damage_triage.md"
  
  # Path to claims rules YAML file
  # Contains all business rules and thresholds
  claims_rules_yaml: "policies/rules.yaml"
  
  # Inline thresholds (can be overridden by claims_rules_yaml)
  confidence:
    high_threshold: 0.55   # Above: auto-present to customer
    low_threshold: 0.35    # Below: route to traditional
  
  fraud:
    risk_threshold: 0.1    # Above: flag for human review
  
  estimate:
    human_review_threshold: 5000.00  # Dollar amount threshold

# Logging Configuration
logging:
  level: "INFO"           # DEBUG, INFO, WARNING, ERROR, CRITICAL
  file: "logs/api.log"
  max_bytes: 10485760     # 10MB per log file
  backup_count: 5         # Keep 5 backup files
  format: "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

# CORS Configuration (Cross-Origin Resource Sharing)
cors:
  allow_origins:
    - "*"                 # Allow all origins (prototype only!)
  allow_credentials: true
  allow_methods:
    - "*"
  allow_headers:
    - "*"

# ============================================================================
# Notes:
# - This is a PROTOTYPE configuration with NO SECURITY
# - Do NOT use in production
# - All endpoints are publicly accessible
# - Use only in isolated development/demo environments
# ============================================================================
```

### 16.1 Running the Application

```bash
# Development
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Production (with gunicorn)
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 16.2 Configuration Setup

**Step 1: Create configuration file**
```bash
# Copy example configuration
cp api-config.example.yaml api-config.yaml

# Edit configuration (update database URL, paths, etc.)
nano api-config.yaml
```

**Step 2: Install dependencies**
```bash
poetry install
```

**Step 3: Setup database**
```bash
python scripts/init_database.py
```

**Step 4: Seed test data**
```bash
python scripts/seed_data.py
```

**Step 5: Run tests**
```bash
pytest tests/ -v --cov=app
```

**Step 6: Start application**
```bash
# Development (uses api-config.yaml)
uvicorn src.api.main:app --reload

# Or use configured host/port from YAML
python -m src.api.main
```

**Configuration File Validation:**
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('api-config.yaml'))"
```

### 16.3 Docker Support (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

COPY src ./src

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 17. Data Integrity: Dual-Column Approach for AI vs Adjustor Estimates

### 17.1 Problem Statement

**Design Flaw Identified:** The initial implementation allowed adjustor modifications to directly overwrite AI-generated damage estimates, resulting in:

1. **Lost Audit Trail:** Original AI predictions permanently deleted when adjustor makes changes
2. **No Accuracy Tracking:** Cannot measure AI performance (how often/how much adjustors change estimates)
3. **Incomplete Customer Communication:** Cannot show "AI estimated $X, adjustor reviewed and adjusted to $Y"
4. **Second Appeal Issues:** If customer appeals adjustor's decision, no reference to original AI estimate
5. **Compliance Risk:** No immutable record of automated estimate for regulatory audit

**Example Scenario:**
```
1. AI estimates: labor_hours=2.5, parts_cost=$500 → total=$890
2. Customer appeals
3. Adjustor reviews, changes to: labor_hours=3.0, parts_cost=$650 → total=$1,118
4. Adjustor saves → OVERWRITES original AI values
5. Customer appeals again → Original AI estimate lost forever
```

### 17.2 Solution: Dual-Column Approach (Option 1)

**Design Pattern:** Preserve immutable AI estimates while allowing adjustor overlays

**Schema Changes to `damages` table:**

```python
class Damage(Base):
    # ... existing fields ...
    
    # ============================================================================
    # AI ESTIMATES (IMMUTABLE - Set once during AI estimation)
    # ============================================================================
    ai_labor_hours = Column(Numeric(5, 2), nullable=False)
    ai_parts_cost = Column(Numeric(10, 2), nullable=False)
    ai_total_cost = Column(Numeric(10, 2), nullable=False)
    
    # ============================================================================
    # ADJUSTOR ESTIMATES (NULLABLE - Set during human review)
    # ============================================================================
    adjustor_labor_hours = Column(Numeric(5, 2), nullable=True)
    adjustor_parts_cost = Column(Numeric(10, 2), nullable=True)
    adjustor_total_cost = Column(Numeric(10, 2), nullable=True)
    adjustor_note = Column(Text, nullable=True)
    reviewed_by_adjustor = Column(Boolean, default=False)
    reviewed_at = Column(DateTime, nullable=True)
    
    # ============================================================================
    # DEPRECATED FIELDS (Remove after migration)
    # ============================================================================
    # labor_hours = Column(Numeric(5, 2), nullable=False)
    # estimated_parts_cost = Column(Numeric(10, 2), nullable=False)
    # estimated_total_cost = Column(Numeric(10, 2), nullable=False)
```

### 17.3 Display Logic

**Application-layer logic for determining which estimate to show:**

```python
def get_effective_estimate(damage: Damage) -> dict:
    """
    Returns the estimate that should be displayed to the user.
    
    Rules:
    - If adjustor modified estimate: use adjustor values
    - Else: use AI values
    """
    if damage.adjustor_labor_hours is not None:
        # Adjustor has modified this damage
        return {
            "labor_hours": damage.adjustor_labor_hours,
            "parts_cost": damage.adjustor_parts_cost,
            "total_cost": damage.adjustor_total_cost,
            "estimate_source": "adjustor",
            "modified": True
        }
    else:
        # Use original AI estimate
        return {
            "labor_hours": damage.ai_labor_hours,
            "parts_cost": damage.ai_parts_cost,
            "total_cost": damage.ai_total_cost,
            "estimate_source": "ai",
            "modified": False
        }
```

### 17.4 API Response Schema Updates

**DamageResponse Schema Enhancement:**

```python
class DamageResponse(BaseModel):
    damage_id: int
    damage_part: str
    severity: float
    
    # Current effective estimate (what customer/adjustor sees)
    labor_hours: float
    parts_cost: float
    total_cost: float
    estimate_source: Literal["ai", "adjustor"]  # Which estimate is active
    
    # Optional: Original AI estimate (for comparison)
    ai_estimate: Optional[dict] = None  # {"labor_hours": X, "parts_cost": Y, "total": Z}
    
    # Adjustor review metadata
    reviewed_by_adjustor: bool = False
    adjustor_note: Optional[str] = None
    reviewed_at: Optional[datetime] = None
```

### 17.5 Service Layer Updates

**EstimateService - AI Estimation (CREATES immutable AI estimates):**

```python
def generate_ai_estimate(self, claim_id: int, image_ids: list, state: str):
    """Generate AI estimate and save to ai_* columns"""
    
    for damage_detection in yolo_results:
        damage = Damage(
            claim_id=claim_id,
            # ... detection fields ...
            
            # Set AI estimates (IMMUTABLE)
            ai_labor_hours=calculated_labor_hours,
            ai_parts_cost=calculated_parts_cost,
            ai_total_cost=calculated_total,
            
            # Adjustor fields remain NULL
            adjustor_labor_hours=None,
            adjustor_parts_cost=None,
            adjustor_total_cost=None,
            reviewed_by_adjustor=False
        )
        self.db.add(damage)
```

**ClaimService - Adjustor Review (OVERLAYS adjustor estimates):**

```python
def complete_review(self, claim_id: int, review_data: dict):
    """Complete adjustor review and save modifications"""
    
    if review_data.get('damages'):
        for damage_update in review_data['damages']:
            damage = self.db.query(Damage).filter(
                Damage.damage_id == damage_update['damage_id']
            ).first()
            
            if damage:
                # Update ADJUSTOR columns (AI columns untouched)
                damage.adjustor_labor_hours = damage_update['labor_hours']
                damage.adjustor_parts_cost = damage_update['parts_cost']
                damage.adjustor_total_cost = (
                    damage_update['labor_hours'] * claim.state_avg_labor_cost +
                    damage_update['parts_cost']
                )
                damage.adjustor_note = damage_update.get('adjustor_note')
                damage.reviewed_by_adjustor = True
                damage.reviewed_at = datetime.now()
                
                # AI estimates remain unchanged:
                # damage.ai_labor_hours (unchanged)
                # damage.ai_parts_cost (unchanged)
                # damage.ai_total_cost (unchanged)
```

### 17.6 Benefits

1. **Audit Trail Preserved**
   - Original AI estimate always available
   - Can see: "AI said $1,200 → Adjustor adjusted to $1,450"
   
2. **AI Accuracy Tracking**
   - Query: "How often do adjustors modify AI estimates?"
   - Analytics: Average deviation between AI and adjustor estimates
   
3. **Improved Customer Communication**
   - Show comparison: "Our AI estimated X, after human review we adjusted to Y"
   - Builds trust in process
   
4. **Second Appeal Support**
   - Full history available: AI → Adjustor → Second Appeal
   - Can reference original automated estimate
   
5. **Regulatory Compliance**
   - Immutable record of automated estimate
   - Clear distinction between machine and human judgment

### 17.7 Implementation Strategy

**Note:** System is under development - no data migration needed. Database will be reseeded with new schema.

**Implementation Steps:**

1. **Update Damage Model** (`src/api/models/damage.py`)
   - Replace old fields (`labor_hours`, `estimated_parts_cost`, `estimated_total_cost`)
   - Add new AI estimate fields (required, non-nullable)
   - Add new adjustor estimate fields (nullable)

2. **Update EstimateService** (`src/api/services/estimate_service.py`)
   - Modify `generate_ai_estimate()` to write to `ai_*` columns
   - Set `adjustor_*` columns to NULL

3. **Update ClaimService** (`src/api/services/claim_service.py`)
   - Modify `complete_review()` to write to `adjustor_*` columns
   - Never modify `ai_*` columns after initial creation
   - Set `reviewed_by_adjustor = True` and `reviewed_at` timestamp

4. **Update API Schemas** (`src/api/schemas/damage.py`)
   - Update `DamageResponse` to include `estimate_source` field
   - Add logic to determine which estimate to return
   - Optionally include both AI and adjustor estimates for comparison

5. **Update Frontend Display Logic**
   - Use `adjustor_*` values if present, otherwise `ai_*` values
   - Show comparison view if needed: "AI: $X → Adjustor: $Y"

6. **Reseed Database**
   - Drop existing database
   - Run fresh migrations with new schema
   - Reseed with test data using new structure

### 17.8 Testing Checklist

- [ ] AI estimation writes to `ai_*` columns only
- [ ] Adjustor review writes to `adjustor_*` columns only
- [ ] Display logic correctly picks adjustor estimate when available
- [ ] Display logic falls back to AI estimate when adjustor estimate is NULL
- [ ] API responses include `estimate_source` field
- [ ] Second appeal scenario preserves full history
- [ ] Migration script successfully migrates existing data
- [ ] No data loss during migration

---

**END OF DESIGN DOCUMENT**

---

---

## 17. Admin Portal API Endpoints

### 17.1 Overview

The Admin Portal requires API endpoints for managing the system configuration (`api-config.yaml`). These endpoints allow the admin UI to:
- Read current configuration
- Save configuration with automatic backup
- List available backups
- Restore from backup

**Router:** `src/api/routers/admin.py`  
**Base Path:** `/api/v1/admin`  
**Authentication:** None (prototype only - X-Admin-ID header for tracking)

### 17.2 Configuration Management Endpoints

#### 17.2.1 GET `/api/v1/admin/config`

**Description:** Retrieve current API configuration from `api-config.yaml`

**Request Headers:**
```
X-Admin-ID: admin_001
```

**Response (200 OK):**
```json
{
  "config": {
    "api": {
      "title": "Insurance Claims API",
      "version": "v1",
      "debug": true,
      "host": "0.0.0.0",
      "port": 8000
    },
    "database": {
      "url": "sqlanywhere://****@localhost:2638/insurance_db",
      "pool_size": 5,
      "max_overflow": 10,
      "echo": false
    },
    "ai": {
      "confidence": {
        "high_threshold": 0.55,
        "low_threshold": 0.35
      },
      "fraud": {
        "risk_threshold": 0.1
      },
      "estimate": {
        "human_review_threshold": 5000.00
      }
    },
    "llm": {
      "default_provider": "bedrock",
      "default_vision_model": "bedrock",
      "providers": {
        "bedrock": {
          "enabled": true,
          "aws_region": "us-east-1",
          "default_model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
          "timeout_s": 60,
          "max_tokens": 4096,
          "temperature": 0.2
        }
      }
    },
    "agents": {
      "fraud_detector": {
        "enabled": true,
        "high_risk_threshold": 0.7,
        "medium_risk_threshold": 0.4,
        "phase1_vision": {
          "color_verification": { "enabled": true },
          "make_model_verification": { "enabled": true },
          "ai_generated_detection": { "enabled": true },
          "manipulation_detection": { "enabled": true }
        }
      },
      "damage_analyzer": {
        "enabled": true,
        "enhance_all_damages": true
      },
      "chatbot": {
        "enabled": true
      }
    },
    "storage": {
      "images_root_folder": "uploads",
      "max_upload_size_mb": 10,
      "max_images_per_claim": 20
    }
  },
  "file_path": "/home/raj/workspace2026/Acme-Claim-Management-Solution/api-config.yaml",
  "last_modified": "2026-05-07T14:30:45Z"
}
```

**Response Notes:**
- `database.url` is masked (show `****` for credentials)
- `last_modified` is ISO 8601 timestamp of file modification time
- Full config structure returned (no filtering)

**Error Responses:**

```json
// 500 - File not found or read error
{
  "detail": "Failed to load configuration: [Errno 2] No such file or directory: 'api-config.yaml'"
}
```

**Implementation Notes:**
```python
import yaml
from pathlib import Path
from datetime import datetime

@router.get("/config")
def get_config(admin_id: str = Header(..., alias="X-Admin-ID")):
    config_path = Path("api-config.yaml")
    
    if not config_path.exists():
        raise HTTPException(status_code=500, detail="Configuration file not found")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Mask sensitive fields
    if 'database' in config and 'url' in config['database']:
        config['database']['url'] = mask_credentials(config['database']['url'])
    
    last_modified = datetime.fromtimestamp(config_path.stat().st_mtime)
    
    return {
        "config": config,
        "file_path": str(config_path.absolute()),
        "last_modified": last_modified.isoformat()
    }
```

---

#### 17.2.2 POST `/api/v1/admin/config`

**Description:** Save updated configuration with automatic backup

**Request Headers:**
```
X-Admin-ID: admin_001
Content-Type: application/json
```

**Request Body:**
```json
{
  "config": {
    "api": { ... },
    "database": { ... },
    "ai": { ... },
    "llm": { ... },
    "agents": { ... },
    "storage": { ... }
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Configuration saved successfully",
  "backup_file": "api-config.2026-05-07-14-30-45.bak",
  "config_path": "/home/raj/workspace2026/Acme-Claim-Management-Solution/api-config.yaml",
  "restart_required": true
}
```

**Error Response (400 - Validation Error):**
```json
{
  "success": false,
  "message": "Configuration validation failed",
  "errors": {
    "ai.confidence.high_threshold": "Must be between 0 and 1",
    "database.pool_size": "Must be a positive integer",
    "llm.providers.bedrock.timeout_s": "Must be between 1 and 600"
  }
}
```

**Error Response (500 - Write Error):**
```json
{
  "detail": "Failed to save configuration: [Errno 13] Permission denied: 'api-config.yaml'"
}
```

**Backend Logic:**
1. **Validate config** (types, ranges, required fields)
2. **Create backup** with timestamp: `api-config.2026-05-07-14-30-45.bak`
3. **Write new config** to `api-config.yaml`
4. **Return success** with backup filename

**Validation Rules:**

| Field | Type | Constraints | Error Message |
|-------|------|-------------|---------------|
| `ai.confidence.high_threshold` | float | 0.0 - 1.0 | "Must be between 0 and 1" |
| `ai.confidence.low_threshold` | float | 0.0 - 1.0 | "Must be between 0 and 1" |
| `ai.fraud.risk_threshold` | float | 0.0 - 1.0 | "Must be between 0 and 1" |
| `ai.estimate.human_review_threshold` | float | ≥ 0 | "Must be non-negative" |
| `agents.*.enabled` | boolean | true/false | "Must be boolean" |
| `database.pool_size` | int | 1 - 100 | "Must be between 1 and 100" |
| `database.max_overflow` | int | 0 - 100 | "Must be between 0 and 100" |
| `llm.default_provider` | string | anthropic, openai, bedrock | "Invalid provider" |
| `llm.providers.*.timeout_s` | int | 1 - 600 | "Must be between 1 and 600 seconds" |
| `llm.providers.*.max_tokens` | int | 1 - 100000 | "Must be between 1 and 100000" |
| `llm.providers.*.temperature` | float | 0.0 - 2.0 | "Must be between 0 and 2" |
| `storage.max_upload_size_mb` | int | 1 - 100 | "Must be between 1 and 100 MB" |
| `storage.max_images_per_claim` | int | 1 - 100 | "Must be between 1 and 100" |
| `api.port` | int | 1 - 65535 | "Must be valid port number" |

**Consistency Checks:**
- `low_threshold` < `high_threshold` (AI confidence)
- `medium_risk_threshold` < `high_risk_threshold` (fraud detection)

**Implementation Notes:**
```python
from datetime import datetime
import yaml
import shutil
from pathlib import Path

@router.post("/config")
def save_config(
    request: ConfigUpdateRequest,
    admin_id: str = Header(..., alias="X-Admin-ID")
):
    config_path = Path("api-config.yaml")
    
    # 1. Validate configuration
    errors = validate_config(request.config)
    if errors:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Configuration validation failed",
                "errors": errors
            }
        )
    
    # 2. Create backup
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    backup_filename = f"api-config.{timestamp}.bak"
    backup_path = config_path.parent / backup_filename
    
    if config_path.exists():
        shutil.copy2(config_path, backup_path)
    
    # 3. Write new configuration
    try:
        with open(config_path, 'w') as f:
            yaml.safe_dump(request.config, f, default_flow_style=False, sort_keys=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save configuration: {str(e)}")
    
    # 4. Return success
    return {
        "success": True,
        "message": "Configuration saved successfully",
        "backup_file": backup_filename,
        "config_path": str(config_path.absolute()),
        "restart_required": True
    }
```

---

#### 17.2.3 GET `/api/v1/admin/config/backups`

**Description:** List all available backup files in the config directory

**Request Headers:**
```
X-Admin-ID: admin_001
```

**Response (200 OK):**
```json
{
  "backups": [
    {
      "filename": "api-config.2026-05-07-14-30-45.bak",
      "timestamp": "2026-05-07T14:30:45Z",
      "size_bytes": 12345,
      "size_formatted": "12.1 KB"
    },
    {
      "filename": "api-config.2026-05-06-10-15-22.bak",
      "timestamp": "2026-05-06T10:15:22Z",
      "size_bytes": 12289,
      "size_formatted": "12.0 KB"
    }
  ],
  "total_count": 2,
  "total_size_bytes": 24634
}
```

**Response Notes:**
- Sorted by timestamp (newest first)
- `timestamp` parsed from filename (format: `YYYY-MM-DD-HH-MM-SS`)
- `size_bytes` from filesystem
- `size_formatted` human-readable (KB, MB)

**Implementation Notes:**
```python
import re
from pathlib import Path
from datetime import datetime

@router.get("/config/backups")
def list_backups(admin_id: str = Header(..., alias="X-Admin-ID")):
    config_dir = Path(".")
    backup_pattern = re.compile(r"api-config\.(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})\.bak")
    
    backups = []
    for file in config_dir.glob("api-config.*.bak"):
        match = backup_pattern.match(file.name)
        if match:
            timestamp_str = match.group(1)
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d-%H-%M-%S")
            size_bytes = file.stat().st_size
            
            backups.append({
                "filename": file.name,
                "timestamp": timestamp.isoformat(),
                "size_bytes": size_bytes,
                "size_formatted": format_bytes(size_bytes)
            })
    
    # Sort by timestamp (newest first)
    backups.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {
        "backups": backups,
        "total_count": len(backups),
        "total_size_bytes": sum(b["size_bytes"] for b in backups)
    }
```

---

#### 17.2.4 POST `/api/v1/admin/config/restore`

**Description:** Restore configuration from a backup file

**Request Headers:**
```
X-Admin-ID: admin_001
Content-Type: application/json
```

**Request Body:**
```json
{
  "backup_filename": "api-config.2026-05-07-14-30-45.bak"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Configuration restored from api-config.2026-05-07-14-30-45.bak",
  "backup_of_current": "api-config.2026-05-07-15-45-12.bak",
  "restart_required": true
}
```

**Error Response (404 - Backup Not Found):**
```json
{
  "detail": "Backup file not found: api-config.2026-05-07-14-30-45.bak"
}
```

**Error Response (400 - Invalid Filename):**
```json
{
  "detail": "Invalid backup filename format"
}
```

**Backend Logic:**
1. **Validate backup filename** (security: prevent path traversal)
2. **Check backup exists**
3. **Create backup of current config** (before overwriting)
4. **Copy backup file to `api-config.yaml`**
5. **Return success** with backup-of-current filename

**Security Notes:**
- **Path traversal prevention**: Only allow `api-config.*.bak` pattern
- **Reject**: `../api-config.bak`, `/etc/passwd`, etc.

**Implementation Notes:**
```python
import re
import shutil
from pathlib import Path
from datetime import datetime

@router.post("/config/restore")
def restore_config(
    request: RestoreRequest,
    admin_id: str = Header(..., alias="X-Admin-ID")
):
    # 1. Validate filename (prevent path traversal)
    backup_pattern = re.compile(r"^api-config\.\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}\.bak$")
    if not backup_pattern.match(request.backup_filename):
        raise HTTPException(status_code=400, detail="Invalid backup filename format")
    
    # 2. Check backup exists
    backup_path = Path(request.backup_filename)
    if not backup_path.exists():
        raise HTTPException(status_code=404, detail=f"Backup file not found: {request.backup_filename}")
    
    # 3. Create backup of current config
    config_path = Path("api-config.yaml")
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    current_backup = f"api-config.{timestamp}.bak"
    
    if config_path.exists():
        shutil.copy2(config_path, current_backup)
    
    # 4. Restore from backup
    shutil.copy2(backup_path, config_path)
    
    return {
        "success": True,
        "message": f"Configuration restored from {request.backup_filename}",
        "backup_of_current": current_backup,
        "restart_required": True
    }
```

---

### 17.3 Configuration Schema & Validation

#### 17.3.1 Editable Fields

The following fields from `api-config.yaml` are editable via the admin portal:

| YAML Path | Type | Default | Constraints | UI Section |
|-----------|------|---------|-------------|------------|
| `ai.confidence.high_threshold` | float | 0.55 | 0.0 - 1.0 | Claim Processing Rules |
| `ai.confidence.low_threshold` | float | 0.35 | 0.0 - 1.0 | Claim Processing Rules |
| `ai.fraud.risk_threshold` | float | 0.1 | 0.0 - 1.0 | Claim Processing Rules |
| `ai.estimate.human_review_threshold` | float | 5000.00 | ≥ 0 | Claim Processing Rules |
| `agents.fraud_detector.enabled` | boolean | true | - | Claim Processing Rules |
| `agents.fraud_detector.high_risk_threshold` | float | 0.7 | 0.0 - 1.0 | Claim Processing Rules |
| `agents.fraud_detector.medium_risk_threshold` | float | 0.4 | 0.0 - 1.0 | Claim Processing Rules |
| `agents.fraud_detector.phase1_vision.color_verification.enabled` | boolean | true | - | Claim Processing Rules |
| `agents.fraud_detector.phase1_vision.make_model_verification.enabled` | boolean | true | - | Claim Processing Rules |
| `agents.fraud_detector.phase1_vision.ai_generated_detection.enabled` | boolean | true | - | Claim Processing Rules |
| `agents.fraud_detector.phase1_vision.manipulation_detection.enabled` | boolean | true | - | Claim Processing Rules |
| `agents.risk_estimator.enabled` | boolean | true | - | Claim Processing Rules |
| `agents.ai_image_detector.enabled` | boolean | true | - | Claim Processing Rules |
| `agents.damage_analyzer.enabled` | boolean | true | - | Claim Processing Rules |
| `agents.damage_analyzer.enhance_all_damages` | boolean | true | - | Claim Processing Rules |
| `agents.chatbot.enabled` | boolean | true | - | Claim Processing Rules |
| `llm.default_provider` | string | "bedrock" | anthropic, openai, bedrock | Technical Parameters |
| `llm.default_vision_model` | string | "bedrock" | anthropic, openai, bedrock | Technical Parameters |
| `llm.providers.bedrock.aws_region` | string | "us-east-1" | - | Technical Parameters |
| `llm.providers.bedrock.default_model` | string | "claude-3-5-sonnet-v2" | - | Technical Parameters |
| `llm.providers.bedrock.timeout_s` | int | 60 | 1 - 600 | Technical Parameters |
| `llm.providers.bedrock.max_tokens` | int | 4096 | 1 - 100000 | Technical Parameters |
| `llm.providers.bedrock.temperature` | float | 0.2 | 0.0 - 2.0 | Technical Parameters |
| `database.pool_size` | int | 5 | 1 - 100 | Technical Parameters |
| `database.max_overflow` | int | 10 | 0 - 100 | Technical Parameters |
| `database.echo` | boolean | false | - | Technical Parameters |
| `storage.images_root_folder` | string | "uploads" | - | Technical Parameters |
| `storage.max_upload_size_mb` | int | 10 | 1 - 100 | Technical Parameters |
| `storage.max_images_per_claim` | int | 20 | 1 - 100 | Technical Parameters |
| `api.debug` | boolean | true | - | Technical Parameters |
| `api.host` | string | "0.0.0.0" | - | Technical Parameters |
| `api.port` | int | 8000 | 1 - 65535 | Technical Parameters |

#### 17.3.2 Read-Only Fields (Security)

The following fields are **NOT editable** via the admin portal:

- `database.url` - Contains credentials (show masked: `sqlanywhere://****@localhost:2638/insurance_db`)
- `llm.providers.*.api_key_env` - API key environment variable names
- `logging.*` - Logging configuration
- `cors.*` - CORS settings (security risk)
- `api.title`, `api.version` - API metadata

#### 17.3.3 Validation Utility

**File:** `src/api/utils/config_validator.py`

```python
from typing import Dict, Any, List

def validate_config(config: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate configuration dictionary.
    Returns dict of field_path -> error_message.
    Empty dict = valid.
    """
    errors = {}
    
    # Validate AI confidence thresholds
    if not validate_range(config, "ai.confidence.high_threshold", 0.0, 1.0):
        errors["ai.confidence.high_threshold"] = "Must be between 0 and 1"
    
    if not validate_range(config, "ai.confidence.low_threshold", 0.0, 1.0):
        errors["ai.confidence.low_threshold"] = "Must be between 0 and 1"
    
    # Consistency check: low < high
    low = get_nested(config, "ai.confidence.low_threshold")
    high = get_nested(config, "ai.confidence.high_threshold")
    if low is not None and high is not None and low >= high:
        errors["ai.confidence.low_threshold"] = "Must be less than high threshold"
    
    # Validate fraud thresholds
    if not validate_range(config, "ai.fraud.risk_threshold", 0.0, 1.0):
        errors["ai.fraud.risk_threshold"] = "Must be between 0 and 1"
    
    # Validate database settings
    if not validate_range(config, "database.pool_size", 1, 100):
        errors["database.pool_size"] = "Must be between 1 and 100"
    
    if not validate_range(config, "database.max_overflow", 0, 100):
        errors["database.max_overflow"] = "Must be between 0 and 100"
    
    # Validate LLM settings
    if not validate_enum(config, "llm.default_provider", ["anthropic", "openai", "bedrock"]):
        errors["llm.default_provider"] = "Must be anthropic, openai, or bedrock"
    
    if not validate_range(config, "llm.providers.bedrock.timeout_s", 1, 600):
        errors["llm.providers.bedrock.timeout_s"] = "Must be between 1 and 600 seconds"
    
    if not validate_range(config, "llm.providers.bedrock.max_tokens", 1, 100000):
        errors["llm.providers.bedrock.max_tokens"] = "Must be between 1 and 100000"
    
    if not validate_range(config, "llm.providers.bedrock.temperature", 0.0, 2.0):
        errors["llm.providers.bedrock.temperature"] = "Must be between 0 and 2"
    
    # Validate storage settings
    if not validate_range(config, "storage.max_upload_size_mb", 1, 100):
        errors["storage.max_upload_size_mb"] = "Must be between 1 and 100 MB"
    
    if not validate_range(config, "storage.max_images_per_claim", 1, 100):
        errors["storage.max_images_per_claim"] = "Must be between 1 and 100"
    
    # Validate API settings
    if not validate_range(config, "api.port", 1, 65535):
        errors["api.port"] = "Must be a valid port number (1-65535)"
    
    return errors
```

---

### 17.4 Request/Response Models

**File:** `src/api/schemas/admin.py`

```python
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class ConfigUpdateRequest(BaseModel):
    config: Dict[str, Any] = Field(..., description="Full configuration object")

class ConfigResponse(BaseModel):
    config: Dict[str, Any]
    file_path: str
    last_modified: datetime

class ConfigSaveResponse(BaseModel):
    success: bool
    message: str
    backup_file: str
    config_path: str
    restart_required: bool = True

class ConfigValidationErrorResponse(BaseModel):
    success: bool = False
    message: str
    errors: Dict[str, str]

class BackupInfo(BaseModel):
    filename: str
    timestamp: datetime
    size_bytes: int
    size_formatted: str

class BackupListResponse(BaseModel):
    backups: List[BackupInfo]
    total_count: int
    total_size_bytes: int

class RestoreRequest(BaseModel):
    backup_filename: str = Field(..., pattern=r"^api-config\.\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}\.bak$")

class RestoreResponse(BaseModel):
    success: bool
    message: str
    backup_of_current: str
    restart_required: bool = True
```

---

### 17.5 Integration with Main API

**File:** `src/api/main.py`

```python
from fastapi import FastAPI
from src.api.routers import admin

app = FastAPI(title="Insurance Claims API")

# Register admin router
app.include_router(
    admin.router,
    prefix="/api/v1/admin",
    tags=["Admin"]
)
```

---

### 17.6 Backup Retention Policy

**Decision:** Keep all backups indefinitely (no auto-cleanup)

- Every save creates a new `.bak` file with timestamp
- No automatic deletion
- Manual cleanup by admin if needed
- Rationale: Simple, safe, disk space not a concern for prototype

**Future Enhancement:** Add cleanup endpoint or cron job to delete backups older than N days

---

### 17.7 Security Considerations

**⚠️ Prototype Only - No Production Security**

- **No authentication**: Admin endpoints are open (X-Admin-ID header for tracking only)
- **No authorization**: Any user can modify configuration
- **No rate limiting**: Vulnerable to abuse
- **Credential masking**: `database.url` masked in GET response, but can be overwritten via POST
- **Path traversal protection**: Restore endpoint validates filename pattern

**Production Requirements:**
- Add JWT/OAuth authentication
- Role-based access control (admin, viewer)
- Audit log of all config changes
- Rate limiting on POST endpoints
- Encrypt sensitive config values at rest

---

## Summary

This design document provides a complete blueprint for implementing the FastAPI backend with:

✅ **Clear architecture** (layered pattern with separation of concerns)  
✅ **Synchronous implementation** (simpler debugging for prototype)  
✅ **Local filesystem storage** for images  
✅ **Dictionary-based state machine** with validation  
✅ **SQLAlchemy ORM** for database access  
✅ **Decorator-based event logging** (automatic audit trail)  
✅ **YOLOv11 integration** with HuggingFace model and annotated image generation  
✅ **Comprehensive error handling** with custom exceptions  
✅ **Structured logging** for debugging  
✅ **Core test coverage** (~50-60%) with pytest  
✅ **Database seeding** with SQL + Faker  
✅ **Admin configuration API** with backup/restore functionality  

The design follows FastAPI best practices while maintaining simplicity appropriate for a prototype system.
