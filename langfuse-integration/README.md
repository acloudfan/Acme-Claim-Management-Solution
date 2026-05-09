# Langfuse Integration for Acme Claims Management System

This directory contains the Langfuse setup for LLM observability and AI agent tracing in the Acme Claims Management Solution.

## What is Langfuse?

Langfuse is an open-source LLM engineering platform that provides:
- **Trace visualization** - See every LLM call with prompts, completions, tokens, and costs
- **Human annotations** - Adjustors can rate AI decisions and create evaluation datasets
- **Performance monitoring** - Track latency, error rates, and token usage across agents
- **Dataset creation** - Export production traces for model evaluation and fine-tuning

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git (for cloning Langfuse repository)
- API server configured with environment variables

### 1. Clone Langfuse Repository

```bash
# From the project root directory
cd langfuse-integration
git clone https://github.com/langfuse/langfuse.git
cd langfuse
```

### 2. Start Langfuse Server

```bash
docker compose up -d
```

**Verify containers are running:**
```bash
docker compose ps
```

Expected output:
```
NAME                     STATUS    PORTS
langfuse-langfuse-1      Up        0.0.0.0:3000->3000/tcp
langfuse-db-1            Up        5432/tcp
```

### 3. Access Langfuse UI

Open your browser and navigate to:
```
http://localhost:3000
```

### 4. Initial Setup in UI

1. **Sign up** with email and password (first-time setup)
2. **Create organization:**
   - Name: `acme-org`
   - Click "Create Organization"
3. **Create project:**
   - Name: `claims-project`
   - Click "Create Project"
4. **Generate API keys:**
   - Navigate to **Settings → API Keys**
   - Click **"Create New API Key"**
   - Copy the generated keys:
     - **Public Key:** `pk-lf-...`
     - **Secret Key:** `sk-lf-...`

### 5. Configure Environment Variables

Create or update `.env` file in the project root:

```bash
# Navigate back to project root
cd ../..

# Add to .env file
cat >> .env << EOF

# Langfuse Configuration
LANGFUSE_PUBLIC_KEY="pk-lf-your-public-key-here"
LANGFUSE_SECRET_KEY="sk-lf-your-secret-key-here"
LANGFUSE_HOST="http://localhost:3000"
EOF
```

⚠️ **Important:** Ensure `.env` is in `.gitignore` to avoid committing secrets.

### 6. Enable Langfuse in API Config

Edit `api-config.yaml`:

```yaml
tracking:
  usage_logging_enabled: true
  log_to_database: true
  langfuse:
    enabled: true  # Change from false to true
```

> **Note:** Langfuse reads credentials directly from environment variables (`LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`). No need to duplicate them in the config file.

### 7. Install Python Package

```bash
uv add langfuse
```

### 8. Restart API Server

```bash
# Start the API server
./scripts/start-api-server.sh

# The server will pick up the new configuration
```

### 9. Verify Integration

**Test with a chatbot message:**

```bash
curl -X POST http://localhost:8000/api/v1/chatbot/customer/message \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 100,
    "message": "What is my claim status?",
    "session_id": "test_session_001"
  }'
```

**Check Langfuse UI:**
1. Open http://localhost:3000
2. Navigate to **Traces** page
3. You should see a new trace named **"ChatbotAgent"**
4. Click to expand and see:
   - Full prompt and completion
   - Token counts (input/output)
   - Cost estimate
   - Latency
   - Metadata (customer_id, session_id)

## Architecture

The Langfuse integration wraps all LLM calls at the client layer:

```
API Endpoint
    ↓
Agent Layer (FraudSupervisor, ChatbotAgent, etc.)
    ↓
LangfuseWrapper → LLM Client (Anthropic/OpenAI/Bedrock)
    ↓
Langfuse Server (traces, annotations, datasets)
```

**Key Components:**
- `src/api/agents/llm/langfuse_wrapper.py` - Wraps BaseLLMClient
- `src/api/agents/tracking/langfuse_context.py` - Trace context management
- `src/api/agents/llm/config.py` - Factory integration

## Usage

### For Developers

**Automatic tracing:** All LLM calls are automatically traced. No code changes needed in agents.

**View traces:**
1. Open http://localhost:3000
2. Navigate to **Traces**
3. Filter by agent name, date, or claim_id

**Debug errors:**
- Click on failed traces (red status)
- Inspect full prompt and error message
- Check token usage and latency

### For Adjustors

**Annotate AI decisions:**

1. Open claim in adjustor portal
2. Click **"View AI Trace"** button
3. Langfuse opens in new tab
4. Click **"Add Score"** button
5. Rate the AI decision:
   - `fraud_accuracy` (1-5): Was fraud detection accurate?
   - `estimate_quality` (1-5): Was cost estimate reasonable?
   - `overall_confidence` (1-5): Trust in AI decision
6. Add comments explaining rating
7. Add tags for dataset export: `export_for_evaluation`

### For Administrators

**Monitor health:**
- Check admin dashboard for Langfuse status
- View error rates and latency metrics
- Endpoint: `GET /api/v1/admin/health`

**Export datasets:**

```bash
# Manual export of annotated traces
python scripts/export_langfuse_dataset.py \
  --start-date 2026-05-01 \
  --end-date 2026-05-09

# Output: data/evaluation_datasets/fraud_detection_2026-05-09.jsonl
```

## Configuration Reference

### api-config.yaml

```yaml
tracking:
  langfuse:
    enabled: true  # Toggle Langfuse on/off (false to disable)
```

> Credentials are read from environment variables, not from the config file.

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `LANGFUSE_PUBLIC_KEY` | Project public key from Langfuse UI | `pk-lf-a8121427...` |
| `LANGFUSE_SECRET_KEY` | Project secret key from Langfuse UI | `sk-lf-af095a7...` |
| `LANGFUSE_HOST` | Langfuse server URL | `http://localhost:3000` or `https://cloud.langfuse.com` |

## Agents Being Traced

The following agents are automatically traced:

### Fraud Detection Agents
- **FraudDetectionSupervisor** - Main orchestrator
- **ColorVerificationAgent** - Vision-based color matching
- **MakeModelVerificationAgent** - Vision-based vehicle identification
- **AIGeneratedDetectorAgent** - Synthetic image detection
- **ImageManipulationDetectorAgent** - Photoshop detection
- **BehaviorPatternAgent** - Behavioral analysis

### Customer Interaction Agents
- **ChatbotAgent** - Customer-facing Q&A assistant

### Future Agents
- **DamageAnalyzerAgent** - Damage severity assessment
- **EstimateExplainerAgent** - Cost estimate explanation
- **ShopRecommenderAgent** - Repair shop recommendations

## Trace Structure

**Example Fraud Detection Trace:**

```
Trace: "FraudDetectionSupervisor"
├── Metadata: {claim_id: 5001, customer_id: 123, vin: "1ABC..."}
├── Generation: "color_verification"
│   ├── Model: us.anthropic.claude-sonnet-4-5-20250929-v1:0
│   ├── Tokens: 1200 input, 150 output
│   ├── Cost: $0.0045
│   └── Latency: 2.3s
├── Generation: "make_model_verification"
│   ├── Tokens: 1280 input, 160 output
│   ├── Cost: $0.0048
│   └── Latency: 2.2s
├── Generation: "ai_generated_detection"
│   └── ... (similar structure)
├── Generation: "image_manipulation_detection"
│   └── ... (similar structure)
└── Generation: "behavior_pattern_analysis" (Phase 3, conditional)
    └── ... (similar structure)
```

**Total trace:** 5 LLM calls, aggregated tokens/cost/latency

## Troubleshooting

### Langfuse UI not accessible

**Check containers:**
```bash
cd langfuse-integration/langfuse
docker compose ps
```

**Restart if needed:**
```bash
docker compose down
docker compose up -d
```

### Traces not appearing

**1. Verify Langfuse enabled:**
```bash
grep -A 5 "langfuse:" api-config.yaml
```
Should show `enabled: true`

**2. Check environment variables:**
```bash
cat .env | grep LANGFUSE
```
Should show public key, secret key, and host

**3. Check API logs:**
```bash
tail -f logs/api.log | grep -i langfuse
```
Look for initialization messages or errors

**4. Verify API keys are valid:**
- Open http://localhost:3000
- Go to Settings → API Keys
- Regenerate keys if needed
- Update `.env` file

### API still works but no traces

**This is expected behavior** - Langfuse integration uses graceful degradation:
- If Langfuse server is down, API continues normally
- Errors are logged but not raised to callers
- Check logs for warnings: `"Langfuse unavailable, skipping trace"`

**To fix:**
```bash
cd langfuse-integration/langfuse
docker compose up -d
```
Tracing will resume automatically without API restart.

### Traces visible but missing data

**Check wrapper implementation:**
- Ensure `langfuse_wrapper.py` is implemented (Phase 1)
- Verify `get_llm_client()` returns wrapped client
- Check logs for wrapper errors

### "Invalid API key" error

**Regenerate keys:**
1. Open http://localhost:3000
2. Settings → API Keys
3. Delete old key
4. Create new key
5. Update `.env` file
6. Restart API server

## Docker Commands

### Start Langfuse
```bash
cd langfuse-integration/langfuse
docker compose up -d
```

### Stop Langfuse
```bash
docker compose down
```

### View logs
```bash
docker compose logs -f langfuse
```

### Reset database (fresh start)
```bash
docker compose down -v  # -v removes volumes
docker compose up -d
```

### Check disk usage
```bash
docker system df
```

## Cloud Langfuse Alternative

Instead of local Docker, you can use Langfuse Cloud:

### Advantages
- No Docker management
- Managed scaling and backups
- Team collaboration features
- Always accessible

### Setup

1. **Sign up:** https://cloud.langfuse.com
2. **Create organization and project**
3. **Get API keys** from Settings
4. **Update configuration:**

```yaml
# api-config.yaml
tracking:
  langfuse:
    enabled: true
```

```bash
# .env
LANGFUSE_PUBLIC_KEY="pk-lf-..."
LANGFUSE_SECRET_KEY="sk-lf-..."
LANGFUSE_HOST="https://cloud.langfuse.com"  # Cloud URL instead of localhost
```

### Considerations
- Data sent to cloud (review privacy/compliance requirements)
- Requires internet connectivity
- May have usage limits on free tier

## Performance Impact

**Expected overhead:** <50ms per LLM call

**Benchmarking:**
```bash
# Run benchmark script
python scripts/benchmark_langfuse.py

# Compare with/without Langfuse enabled
```

**Optimization:**
- Trace creation is async (non-blocking)
- Graceful degradation prevents timeouts
- Sampling can be enabled if overhead too high

## Security Best Practices

1. **Never commit `.env` to git**
   - Ensure `.env` is in `.gitignore`
   - Use environment-specific secrets

2. **Rotate API keys regularly**
   - Regenerate keys monthly
   - Update in all environments

3. **Use separate projects per environment**
   - Development: `claims-dev`
   - Staging: `claims-staging`
   - Production: `claims-prod`

4. **Limit access to Langfuse UI**
   - Use authentication
   - Grant read-only access to developers
   - Admin access for team leads only

5. **Review trace data for PII**
   - Traces contain full prompts/completions
   - May include customer data (names, VINs, addresses)
   - Ensure compliance with privacy policies

## Support and Documentation

- **Langfuse Documentation:** https://langfuse.com/docs
- **Langfuse GitHub:** https://github.com/langfuse/langfuse
- **API Reference:** https://api.reference.langfuse.com
- **Integration Spec:** `/specifications/LANGFUSE-INTEGRATION.md`

## Next Steps

After setup is complete:

1. **Phase 1:** Implement core integration (langfuse_wrapper.py, context management)
2. **Phase 2:** Add production readiness (error handling, monitoring)
3. **Phase 3:** Enable human-in-the-loop (adjustor annotations, dataset export)

See `/specifications/LANGFUSE-INTEGRATION.md` for detailed implementation guide.

---

**Last Updated:** 2026-05-09  
**Version:** 1.0
