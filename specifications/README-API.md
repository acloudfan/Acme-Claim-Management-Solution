# Insurance Claims API

AI-Powered Auto Insurance Claims API (Prototype)

## Quick Start

### 1. Install uv (if not already installed)

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Setup Project

```bash
# Run the setup script (handles everything)
./scripts/setup_uv.sh

# Or manually:
uv sync                              # Install dependencies
cp api-config.example.yaml api-config.yaml
mkdir -p uploads logs
```

### 3. Run the API

```bash
# Quick start (recommended)
./scripts/start_api.sh

# Start with clean database (deletes existing data)
./scripts/start_api.sh --clean

# Or manually with uv
uv run uvicorn src.api.main:app --reload

# Or run as module
uv run python -m src.api.main
```

### 4. Access API Documentation

Once running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Project Structure

```
src/api/
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration loader
├── database.py             # Database connection
├── constants.py            # Enums and state machine
├── exceptions.py           # Custom exceptions
│
├── models/                 # SQLAlchemy ORM models
├── schemas/                # Pydantic request/response schemas
├── routers/                # API endpoint routers
├── services/               # Business logic layer
├── ai/                     # AI integration (YOLO)
└── utils/                  # Utility functions
```

## API Endpoints

### Customer Endpoints

- `POST /api/v1/customers/{customer_id}/claims` - Create new claim (draft)
- `POST /api/v1/customers/{customer_id}/claims/{claim_id}/submit` - Submit claim for processing
- `GET /api/v1/customers/{customer_id}/claims` - Get customer claims
- `GET /api/v1/customers/{customer_id}/claims/{claim_id}` - Get specific claim
- `POST /api/v1/customers/{customer_id}/claims/{claim_id}/images` - Upload damage photo
- `DELETE /api/v1/customers/{customer_id}/claims/{claim_id}/images/{image_id}` - Delete photo
- `GET /api/v1/customers/{customer_id}/claims/{claim_id}/images` - Get claim images

### Claims Endpoints

- `POST /api/v1/claims/{claim_id}/estimate` - Generate AI damage estimate
- `GET /api/v1/claims/{claim_id}/estimates/{estimate_id}` - Get estimate damages
- `GET /api/v1/claims/{claim_id}/estimates` - Get all estimate IDs

### Cost Estimation Endpoints

- `POST /api/v1/cost/estimate` - Calculate repair cost estimate

## Example Usage

### Create a Claim (FNOL)

```bash
curl -X POST "http://localhost:8000/api/v1/customers/100/claims" \
  -H "Content-Type: application/json" \
  -d '{
    "vin": "1ABC23456789DEFGH",
    "policy_number": "PA-992384-01",
    "fnol_date": "2026-05-03",
    "fnol_time": "10:30:00",
    "date_of_damage": "2026-05-02",
    "is_drivable": true
  }'
```

### Upload Damage Photo

```bash
curl -X POST "http://localhost:8000/api/v1/customers/100/claims/1000/images" \
  -F "file=@front_bumper_damage.jpg"
```

### Generate AI Estimate

```bash
curl -X POST "http://localhost:8000/api/v1/claims/1000/estimate" \
  -H "Content-Type: application/json" \
  -d '{
    "claim_id": 1000,
    "image_ids": ["front_bumper_damage.jpg"],
    "state": "CA"
  }'
```

### Calculate Cost

```bash
curl -X POST "http://localhost:8000/api/v1/cost/estimate" \
  -H "Content-Type: application/json" \
  -d '{
    "damage_report": {
      "id": 1,
      "class": 5,
      "confidence": 0.82,
      "part": "front-bumper-dent"
    },
    "assessment": {
      "internal_damage_probability": 0.3,
      "severity": 0.6,
      "recommended_action": "repair",
      "reasoning": "Moderate front bumper damage",
      "car_side": "front",
      "confidence": 0.82
    },
    "state": "CA"
  }'
```

## Configuration

The API is configured via `api-config.yaml`. Key settings:

- **Database**: SQLAnywhere connection string
- **Storage**: Image upload directory and limits
- **AI**: Model paths and thresholds
- **Logging**: Log level and file location
- **CORS**: Cross-origin settings (permissive for prototype)

See `api-config.example.yaml` for full configuration options.

## State Machine

Claims follow a state machine with the following transitions:

```
FNOL → IMAGE_UPLOADED → LOSS_ESTIMATED_AI →
  CUSTOMER_DECISION_PENDING → LOSS_APPROVED →
  SENT_FOR_PAYMENT → CLAIM_PAID → CLAIM_CLOSED
```

Alternative paths include human review and traditional processing routes.

## Development

### Installing Dev Dependencies

```bash
# Install dev dependencies (pytest, black, ruff, etc.)
uv sync --extra dev

# Install AI dependencies (YOLO, numpy, pillow)
uv sync --extra ai

# Install all extras
uv sync --all-extras
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/api --cov-report=html

# Run specific test file
uv run pytest src/api/tests/test_claims.py
```

### Code Formatting

```bash
# Format with Black
uv run black src/api

# Lint with Ruff
uv run ruff check src/api

# Fix linting issues
uv run ruff check --fix src/api
```

### Database Setup

The API will auto-create tables on startup if they don't exist. For production:

1. Review the database schema in `specifications/API-BACKEND-DESIGN.md`
2. Run migrations using Alembic (optional)
3. Seed test data using provided scripts

## Architecture

The API follows a **layered architecture**:

1. **API Layer** (Routers) - FastAPI endpoints, request/response handling
2. **Business Logic Layer** (Services) - State management, business rules
3. **Database Layer** (Models) - SQLAlchemy ORM, database operations

Key design principles:
- Separation of concerns
- Event sourcing (all state changes logged)
- State machine validation
- Decorator-based event logging

## AI Integration

The API includes YOLOv11 damage detection in `src/api/ai/damage_detector.py`.

Current implementation:
- Uses `vineetsarpal/yolov11n-car-damage` model from HuggingFace
- Detects 14 types of car damage with bounding boxes
- Generates annotated images with bounding boxes (BB- prefix)
- Provides heuristic-based severity and repair recommendations

Configuration:
- Model source and path configurable in `api-config.yaml`
- Supports both HuggingFace and local models
- Adjustable confidence threshold and device (CPU/CUDA/MPS)

## Security Warning

⚠️ **This is a PROTOTYPE with NO AUTHENTICATION**

- All endpoints are publicly accessible
- No user authentication or authorization
- CORS is fully permissive
- Use ONLY in isolated development environments
- DO NOT deploy to production without adding:
  - Authentication (JWT, OAuth2)
  - Authorization/permissions
  - Input sanitization
  - Rate limiting
  - HTTPS/TLS
  - Proper CORS configuration

## Troubleshooting

### Database Connection Errors

Check `api-config.yaml` database URL is correct:
```yaml
database:
  url: "sqlanywhere://user:password@localhost:2638/insurance_db"
```

### Image Upload Errors

Ensure uploads directory exists and is writable:
```bash
mkdir -p uploads
chmod 755 uploads
```

### Import Errors

Ensure Python path includes project root:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Configuration Not Found

Ensure `api-config.yaml` exists in project root:
```bash
ls -la api-config.yaml
```

## Next Steps

1. **Database Integration**: Connect to real SQLAnywhere database
2. **YOLO Integration**: Add trained car damage detection model
3. **Testing**: Add comprehensive test coverage
4. **Authentication**: Implement user authentication
5. **Deployment**: Containerize with Docker
6. **Monitoring**: Add observability and metrics

## Support

For issues and questions:
- Review the design document: `specifications/API-BACKEND-DESIGN.md`
- Check API documentation: http://localhost:8000/docs
- Review CLAUDE.md for project context

## License

Prototype implementation for demonstration purposes.
