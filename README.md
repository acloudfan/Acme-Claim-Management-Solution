# ACME Insurance - AI Claims Management System

**Purpose**: Demonstration of AI-based auto claim adjudication

This project showcases how AI can streamline insurance claims processing through automated damage detection, fraud analysis, cost estimation, and intelligent routing - reducing claim processing time from days to minutes while maintaining accuracy and fraud prevention.

**Key Technologies**: YOLO damage detection, Vision Language Models for fraud detection, multi-portal architecture for different user roles.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Dependency Management](#dependency-management)
- [Configuration](#configuration)
  - [Minimum Setup - Environment Variables](#minimum-setup---environment-variables)
  - [Supported LLM Providers](#supported-llm-providers)
  - [How to Switch LLM Providers](#how-to-switch-llm-providers)
- [Quick Start](#quick-start)
- [What's Built](#whats-built)
- [Demo Scenarios](#demo-scenarios)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Key Features](#key-features)
- [Configuration Management](#configuration-management)
  - [Key Configuration Parameters](#key-configuration-parameters)
  - [How to Configure](#how-to-configure)
- [Documentation](#documentation)
- [How This Prototype Was Built](#how-this-prototype-was-built)
- [References](#references)
  - [External Resources](#external-resources)
  - [Technical Diagrams](#technical-diagrams)
- [FAQ](#faq)
- [License](#license)

---

## Prerequisites

This project requires **uv** (fast Python package installer):

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or run the setup script (one-time setup)
./scripts/setup_uv.sh
```

---

## Dependency Management

This project uses **locked dependencies** for reproducible builds:
- **NPM**: `package-lock.json` files ensure exact frontend dependency versions
- **Python**: `uv.lock` file ensures exact backend dependency versions

📖 **See [DEPENDENCY-MANAGEMENT.md](DEPENDENCY-MANAGEMENT.md) for complete guide on:**
- Locking dependencies with `./scripts/lock-dependencies.sh`
- Updating dependencies safely
- CI/CD best practices
- Troubleshooting lock file issues

---

## Configuration

⚠️ **REQUIRED**: Before starting the system, you MUST configure at least one LLM provider.

### Minimum Setup - Environment Variables

Create a `.env` file in the project root with API keys for at least one provider:

**Option 1: AWS Bedrock**
```bash
# AWS Bedrock uses AWS CLI credentials
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_DEFAULT_REGION=us-east-1
```
*Default Model: `us.anthropic.claude-sonnet-4-5-20250929-v1:0`*

**Note**: If you already have AWS credentials configured in `~/.aws/credentials`, you can skip adding AWS variables to `.env`. The system will automatically use your AWS CLI credentials.

**Option 2: Anthropic Claude**
```bash
ANTHROPIC_API_KEY=sk-ant-api03-your_key_here
```
*Default Model: `claude-sonnet-4.5-20250929`*

**Option 3: OpenAI**
```bash
OPENAI_API_KEY=sk-your_key_here
```
*Default Model: `gpt-4o`*

### Quick Setup Steps

1. **Create `.env` file** in project root:
   ```bash
   touch .env
   ```

2. **Add your API key** for one of the supported providers (see options above)

3. **Verify configuration** (optional):
   ```bash
   # Check that .env file exists and has content
   cat .env
   ```

### Supported LLM Providers

| Provider | Default | Default Model | Required Variables | How to Get Keys |
|----------|---------|---------------|-------------------|-----------------|
| **AWS Bedrock** | ✅ Yes | Claude Sonnet 4.5 | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | [AWS Console](https://aws.amazon.com/) → IAM → Access Keys |
| **Anthropic** | No | Claude Sonnet 4.5 | `ANTHROPIC_API_KEY` | [Anthropic Console](https://console.anthropic.com/) → API Keys |
| **OpenAI** | No | GPT-4o | `OPENAI_API_KEY` | [OpenAI Platform](https://platform.openai.com/) → API Keys |

### How to Switch LLM Providers

The system uses **AWS Bedrock** by default. To switch to a different provider:

**Method 1: Edit Configuration File (Recommended)**

1. Open `api-config.yaml` in the project root
2. Find the `llm` section
3. Change `default_provider` to your preferred provider:

```yaml
llm:
  default_provider: "anthropic"  # Options: "bedrock" | "anthropic" | "openai"
  default_vision_model: "anthropic"  # Should match default_provider
```

4. Save the file
5. Restart API server: `./scripts/start-api-server.sh`

**Method 2: Use Admin Portal (No Restart Required)**

1. Open Admin Portal: http://localhost:5170
2. Navigate to **Technical Parameters** section
3. Find **Default LLM Provider**
4. Select from dropdown: `bedrock`, `anthropic`, or `openai`
5. Click **Save Configuration**
6. Changes take effect immediately (automatic reload)

**Important**: Ensure you have the API key configured in `.env` for the provider you're switching to.

### Important Notes

- **Security**: Never commit `.env` file to version control (already in `.gitignore`)
- **Default Provider**: The system is configured to use AWS Bedrock by default
- **AWS Credentials**: If you have `~/.aws/credentials` configured, you don't need to add AWS variables to `.env`
- **Multiple Providers**: You can configure all three providers and switch between them anytime

### Example `.env` File

```env
# ==============================================================================
# LLM PROVIDER SELECTION
# ==============================================================================
# To switch providers, set one of these values in api-config.yaml:
# - llm.default_provider: "bedrock" | "anthropic" | "openai"
# 
# OR use Admin Portal (http://localhost:5170) → Technical Parameters → LLM Provider
# ==============================================================================

# Choose ONE or MORE providers below:

# ------------------------------------------------------------------------------
# AWS Bedrock (Default Provider)
# ------------------------------------------------------------------------------
# If you have AWS CLI configured (~/.aws/credentials), you can skip these:
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_DEFAULT_REGION=us-east-1

# ------------------------------------------------------------------------------
# Anthropic (Optional - to use, set llm.default_provider: "anthropic")
# ------------------------------------------------------------------------------
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ------------------------------------------------------------------------------
# OpenAI (Optional - to use, set llm.default_provider: "openai")
# ------------------------------------------------------------------------------
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Without proper LLM configuration, the following features will not work:**
- AI fraud detection (VLM analysis)
- Customer chatbot
- Damage analysis enhancement
- Estimate explanations

---

## Quick Start

### 1. Install UI Dependencies (First Time Only)

```bash
# From project root - install dependencies for all portals with automatic fixes
./scripts/install-ui-dependencies.sh --clean
```

This script:
- Installs npm packages for all 4 UI portals (customer, adjustor, admin, executive)
- **Automatically detects and fixes version compatibility issues**:
  - Downgrades unstable Vite versions (6.x/7.x/8.x → 5.4.21)
  - Fixes React plugin compatibility (@vitejs/plugin-react 6.x → 5.2.0)
  - Converts Tailwind v4 to v3 (package.json, postcss.config.js, tailwind.config.js, CSS files)

**Why --clean?** It ensures a fresh installation by removing existing `node_modules` and `package-lock.json` files.

📖 **For detailed portal setup information, see [PORTAL-SETUP-GUIDE.md](PORTAL-SETUP-GUIDE.md)**

### 2. Start API Server

```bash
# From project root - create database and seed demo data
./scripts/start-api-server.sh --clean

# To continue with existing data (skip --clean flag)
./scripts/start-api-server.sh
```

The API server will start on port 8000. Access API docs at: http://localhost:8000/docs

### 3. Start All Portals

```bash
# From project root - starts all 4 portals
./scripts/start-portals.sh
```

This starts:
- Customer Portal: http://localhost:5173
- Adjustor Portal: http://localhost:5174
- Admin Portal: http://localhost:5170
- Executive Portal: http://localhost:5175

### 3. Open Admin Portal

Navigate to **http://localhost:5170** in your browser:

![Admin Portal](docs/images/admin-portal.png)

From the Admin Portal, you can launch the Customer, Adjustor, and Executive portals using the **Quick Access** panel on the right side.

## What's Built

### Backend API (FastAPI)
- YOLO-based damage detection (real-time during upload)
- AI fraud detection (VLM + multi-signal analysis)
- Cost estimation engine
- Customer chatbot (Claude + RAG)
- Complete claim lifecycle management

### Customer Portal
- File claims with photo upload
- Real-time AI damage analysis
- Instant repair estimates
- Appeal decisions
- Mobile QR code support

### Adjustor Portal
- Review flagged claims
- Manual damage assessment
- Fraud signal analysis
- Cost estimate adjustments
- SOP reference viewer

### Admin Portal
- Configure AI thresholds
- Toggle fraud detection features
- Manage business rules
- View demo scenarios

### Executive Portal
- 6-month historical analytics
- KPI dashboards
- Fraud detection metrics
- Cost savings analysis

## How This Prototype Was Built

This prototype was developed using a structured, research-driven approach combining domain expertise with AI-assisted implementation:

### Development Process

**(a) Research Phase**  
Author conducted extensive research on how auto insurance claims are processed by insurance companies, studying traditional workflows, pain points, and inefficiencies.

**(b) Performance Metrics**  
Gathered key metrics that measure auto insurance claim performance, including cycle time, auto-adjudication rate, fraud detection rate, cost per claim, and customer satisfaction scores.

**(c) Stakeholder Identification**  
Identified key stakeholders and their needs:
- **Customers**: Fast, transparent claim processing
- **Adjustors**: Efficient review tools with AI assistance
- **Executives**: Business insights and KPI tracking
- **Operations Managers**: Configuration and policy management

**(d) Conceptual Design**  
Created a high-level conceptual design providing a comprehensive view of "AI-Adjudicated Claim Processing" from multiple stakeholder perspectives, ensuring each role had appropriate tools and insights.

**(e) Design Documentation**  
Captured initial thoughts and requirements in [specifications/Thoughts.md](specifications/Thoughts.md), establishing the foundation for detailed specification development.

**(f) Specification Development**  
Used Claude Code in plan mode to brainstorm and generate detailed specifications for each capability from a business perspective, including:
- User workflows and journeys
- Business rules and decision logic
- UI/UX requirements
- Integration points

**(g) Technical Implementation**  
Provided Claude with technical guidance for implementing each component:
- Database schema design
- API route definitions
- AI agent architecture
- Frontend component structure

**(h) Validation & Review**  
Validated all designs, specifications, and diagrams generated by Claude, ensuring alignment with insurance industry practices and technical feasibility.

**(i) Iterative Build-Out**  
Rolled forward with implementation of each component, testing and refining through multiple iterations to achieve a cohesive, working demonstration.

### Key Documents

- **[specifications/Thoughts.md](specifications/Thoughts.md)** - Original design document used for initiating design discussions
- **[specifications/diagrams/](specifications/diagrams/)** - Technical workflow diagrams
- **[specifications/policies/sop_damage_triage.md](specifications/policies/sop_damage_triage.md)** - Standard operating procedures

This collaborative approach leveraged human domain expertise and strategic thinking with AI-powered implementation speed, resulting in a comprehensive demonstration system built in an accelerated timeframe.

---

## Demo Scenarios

Test images are provided in the `images/` directory. Use these images when filing claims through the Customer Portal.

### 1. Happy Path - Auto-Approved
- **Customer**: John Doe (#100)
- **Vehicle**: 2015 Toyota Corolla (Silver)
- **Image**: `images/toyota-rear-end-damage.png`
- **Expected**: Auto-approved with AI estimate
- **Outcome**: Customer accepts estimate

### 2. Customer Appeal - Human Review
- **Customer**: Jane Smith (#101)
- **Vehicle**: 2006 BMW 1 Series E87 (Silver)
- **Image**: `images/bmw-silver-2006-front-damaged.png`
- **Expected**: AI estimate presented, customer appeals
- **Appeal Reason**: "Radiator seems to be damaged beyond repair"
- **Outcome**: Adjustor adds manual damage and revises estimate

### 3. Fraud Detection - Make Mismatch
- **Customer**: Bob Johnson (#102)
- **Vehicle**: 2012 Chevy Silverado (Red)
- **Images**: 
  - Upload: `images/red-ford-f150-ai-generated-damage.jpg` (Ford F-150)
  - Note: Vehicle mismatch (Chevy ≠ Ford)
- **Expected**: Fraud signals detected
- **Outcome**: Routed to adjustor for fraud review

### 4. Fraud Detection - AI Generated Image
- **Customer**: Alice Williams (#103)
- **Vehicle**: 2022 Honda Accord (Black)
- **Image**: `images/honda-acord-ex-2022-ai-generated-damage.jpg`
- **Expected**: AI-generated damage detected by VLM
- **Outcome**: Routed to fraud review with AI generation analysis

**Default password for all portals**: `password`

**Additional Test Images**:
- `images/damaged-car-1.jpg` - General damage
- `images/damaged-car-dent-2.jpg` - Dent damage
- `images/damaged-car-front-bumper-3.jpg` - Front bumper
- `images/damaged-car-back-bumper-4.jpg` - Back bumper
- `images/damaged-car-door-5.jpg` - Door damage
- `images/red-ford-f150-no-damage.jpg` - Undamaged Ford F-150

## Project Structure

```
├── src/
│   ├── api/              # FastAPI backend
│   ├── ui/
│   │   ├── customer/     # Customer portal (React)
│   │   ├── adjustor/     # Adjustor portal (React)
│   │   ├── admin/        # Admin portal (React)
│   │   └── executive/    # Executive portal (React)
│   └── data/             # Warehouse data, FAQs
├── scripts/              # Setup and seed scripts
├── specifications/       # Design docs and SOPs
└── simulation/           # Data generation scripts
```

## Technology Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite
- **AI/ML**: YOLO v8, Claude (Anthropic), AWS Bedrock
- **Frontend**: React 18, Vite, Tailwind CSS, Recharts
- **Data**: DuckDB (warehouse), SQLite (operational)

## Key Features

✅ Real-time damage detection (YOLO)  
✅ AI fraud detection (make/model mismatch, AI-generated images)  
✅ Instant cost estimation  
✅ Customer chatbot with RAG  
✅ Human review workflow  
✅ Executive analytics dashboards  
✅ Configurable business rules  
✅ Complete audit trail

## Configuration Management

Configuration is managed through `api-config.yaml`, environment variables (`.env` file), and the **Admin Portal** (http://localhost:5170).

See the **[Configuration](#configuration)** section above for setting up environment variables and LLM provider API keys.

### Key Configuration Parameters

#### AI Confidence Thresholds
Controls automatic claim routing based on AI confidence levels.

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `ai.confidence.high_threshold` | Auto-present estimate to customer | **0.55** | `0.55` (55% confidence) |
| `ai.confidence.low_threshold` | Below this routes to traditional process | **0.35** | `0.35` (35% confidence) |

#### Fraud Detection
Controls fraud detection sensitivity and features.

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `ai.fraud.risk_threshold` | Flag claims above this risk score | **0.1** | `0.1` (10% risk) |
| `agents.fraud_detector.enabled` | Enable/disable fraud detection | **true** | `true` or `false` |
| `agents.fraud_detector.high_risk_threshold` | High fraud risk threshold | **0.7** | `0.7` (70% risk) |
| `agents.fraud_detector.medium_risk_threshold` | Medium fraud risk threshold | **0.4** | `0.4` (40% risk) |
| `agents.fraud_detector.phase1_vision.color_verification.enabled` | Verify vehicle color | **true** | `true` or `false` |
| `agents.fraud_detector.phase1_vision.make_model_verification.enabled` | Verify vehicle make/model | **true** | `true` or `false` |
| `agents.fraud_detector.phase1_vision.ai_generated_detection.enabled` | Detect AI-generated images | **true** | `true` or `false` |

#### Cost Estimation
Controls when human review is required.

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `ai.estimate.human_review_threshold` | Dollar amount requiring manual review | **5000** | `5000` ($5,000+) |

#### YOLO Damage Detection
Controls the YOLO model for damage detection.

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `ai.yolo.model_path` | HuggingFace model identifier | **vineetsarpal/yolov11n-car-damage** | `username/model-name` |
| `ai.yolo.confidence_threshold` | Minimum confidence for detection | **0.25** | `0.25` (25%) |
| `ai.yolo.device` | Processing device | **cpu** | `cpu` or `cuda` |

#### LLM Provider Configuration
Configure which AI provider to use.

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `llm.default_provider` | Default LLM provider | **bedrock** | `bedrock`, `anthropic`, or `openai` |
| `llm.default_vision_model` | Default Vision Language Model | **bedrock** | `bedrock`, `anthropic`, or `openai` |
| `llm.providers.bedrock.default_model` | AWS Bedrock model ID | **us.anthropic.claude-sonnet-4-5...** | See AWS Bedrock docs |
| `llm.providers.bedrock.temperature` | LLM temperature (creativity) | **0.2** | `0.0` (deterministic) to `1.0` (creative) |

#### AI Agents
Enable or disable specific AI agents.

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `agents.chatbot.enabled` | Customer chatbot | **true** | `true` or `false` |
| `agents.fraud_detector.enabled` | Fraud detection agent | **true** | `true` or `false` |
| `agents.damage_analyzer.enabled` | Enhanced damage analysis | **true** | `true` or `false` |
| `agents.risk_estimator.enabled` | Actuarial risk analysis | **false** | `true` or `false` |

#### Database
Database connection settings.

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `database.url` | Database connection string | **sqlite:///./test_insurance.db** | `sqlite:///./database.db` |
| `database.pool_size` | Connection pool size | **5** | `5` connections |

#### Storage
File upload and storage settings.

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `storage.images_root_folder` | Image upload directory | **uploads** | `uploads/` |
| `storage.max_upload_size_mb` | Max image size per file | **10** | `10` MB |
| `storage.max_images_per_claim` | Max images per claim | **20** | `20` images |

### How to Configure

**Option 1: Admin Portal (Recommended)**
1. Open http://localhost:5170
2. Navigate to Business Rules or Technical Parameters
3. Adjust values using the UI
4. Click "Save Configuration"
5. Changes take effect immediately (automatic reload)

**Option 2: Edit Configuration File**
1. Edit `api-config.yaml` in project root
2. Save changes
3. Restart API server: `./scripts/start-api-server.sh`

### Configuration Backup

The system automatically creates timestamped backups when you save configuration through the Admin Portal:
- Format: `api-config.YYYY-MM-DD-HH-MM-SS.bak`
- Location: Project root directory
- Restore: Use Admin Portal → Backup History (coming soon)

---

## Documentation

- [Quick Start Guide](specifications/QUICK-START-UV.md)
- [API Design](specifications/API-BACKEND-DESIGN.md)
- [Customer Portal](specifications/UI-CUSTOMER-PORTAL-DESIGN.md)
- [Adjustor Portal](specifications/UI-ADJUSTOR-PORTAL-DESIGN.md)
- [Admin Portal](specifications/UI-ADMIN-PORTAL-DESIGN.md)
- [Executive Portal](specifications/UI-EXECUTIVES-PORTAL-DESIGN.md)
- [SOP - Damage Triage](specifications/policies/sop_damage_triage.md)

## References

### External Resources

- [Car Damage Assessment AI](https://github.com/artemxdata/Car-Damage-Assessment-AI)
- [AAA Mechanic Labor Rates](https://www.aaa.com/autorepair/articles/average-mechanic-labor-rate-repair-costs-in-your-state-2026)
- [COCO Car Damage Dataset](https://www.kaggle.com/datasets/lplenka/coco-car-damage-detection-dataset)
- [Mitchell International](https://www.mitchell.com/) - Industry standard repair time database
- [CCC Intelligent Solutions](https://cccis.com/) - Claims and collision repair platform

### Standard Operating Procedures

- [Damage Triage SOP](specifications/policies/sop_damage_triage.md) - Comprehensive guide for AI agents and adjustors on claim triage, fraud detection, confidence thresholds, and damage assessment guidelines

### Technical Diagrams

Mermaid diagrams illustrating system architecture and workflows:

- [AI-Powered Claim Flow](specifications/diagrams/claim-flow-with-ai.mmd) - End-to-end claim processing with AI
- [Traditional Claims Process](specifications/diagrams/traditional-claims.mmd) - Comparison: traditional vs AI workflow
- [Claim State Machine](specifications/diagrams/claims-state-machine.mmd) - Claim lifecycle states and transitions
- [Image Upload Flow](specifications/diagrams/claim_image_upload.mmd) - YOLO damage detection during upload
- [Fraud Detection Agent](specifications/diagrams/customer-fraud-ai-agent.mmd) - AI fraud detection workflow
- [Database ERD](specifications/diagrams/claim-database-erd.mmd) - Data model and relationships

---

## FAQ

### Common Setup Issues

**Q: I get "Can't load plugin: sqlalchemy.dialects:sqlanywhere" error**

A: This means your `api-config.yaml` has the wrong database URL. Edit the file and change:
```yaml
database:
  url: "sqlite:///./test_insurance.db"
```

**Q: Portal fails to start with "Cannot find module 'vite/dist/node/cli.js'" error**

A: Dependencies are missing or corrupted. Run:
```bash
./scripts/install-ui-dependencies.sh --clean
```

**Q: How do I completely reset and start fresh?**

A: Run these commands:
```bash
# Clean UI dependencies
./scripts/install-ui-dependencies.sh --clean

# Clean API and database
./scripts/start-api-server.sh --clean
```

### Can I try my own images?

Yes! You can upload your own vehicle damage images through the Customer Portal when filing a claim. The system will analyze any clear photos of vehicle damage.

### How can I use my own LLM provider?

The system supports multiple LLM providers (Anthropic, OpenAI, AWS Bedrock). You can configure your preferred provider and API keys in the `api-config.yaml` file or through the Admin Portal.

### Where can I set the LLM or VLM to use?

Configure LLM and Vision Language Model (VLM) settings in two ways:
1. **Admin Portal**: Open JSON to adjust technical parameters
2. **Configuration File**: Edit `api-config.yaml` in the project root

You can set the default provider, model selection, temperature, tokens, and other parameters.

### Which version of YOLO are you using?

The system uses **YOLO v8** for real-time vehicle damage detection.

### Did you fine-tune the YOLO model?

No, we are using an open-source fine-tuned version of YOLO v8 from HuggingFace that has been pre-trained on vehicle damage detection datasets.

### Are you showing real data in the Executive Portal?

No, we are using **synthetically generated data** driven by multiple auto industry averages for realistic data generation. 

We simulate a **Data Warehouse** for ACME claims data. This warehouse holds the data in a **flattened structure** optimized for analytics queries. The Executive dashboard runs off this warehouse structure, demonstrating how business intelligence and reporting would work in a production system.

The 6-month historical analytics, KPIs, and metrics are simulated to demonstrate the types of insights an executive dashboard would provide.

### Is this system ready for production?

No, this is a **demonstration and starting point** for anyone interested in AI-based auto claim adjudication. For production use, you would need:
- Enhanced security and authentication
- Scalable infrastructure
- Compliance with insurance regulations
- Additional fraud prevention measures
- Comprehensive testing and validation
- Integration with existing insurance systems

### How long did it take for you to build this prototype?

It took me **~2 days** and most of that time was spent waiting for Claude to finish thinking :-)

---

## License

MIT License

Copyright (c) 2026 ACME Insurance - AI Claims Management System

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.