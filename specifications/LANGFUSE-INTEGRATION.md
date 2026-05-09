# Langfuse Integration Specification

**Version:** 1.0  
**Last Updated:** 2026-05-09  
**Status:** Design Complete, Implementation Pending

## Table of Contents
1. [Overview](#overview)
2. [Objectives](#objectives)
3. [Architecture](#architecture)
4. [Setup Instructions](#setup-instructions)
5. [Integration Design](#integration-design)
6. [Trace Structure](#trace-structure)
7. [Human Annotation Workflow](#human-annotation-workflow)
8. [Error Handling & Monitoring](#error-handling--monitoring)
9. [Verification Guide](#verification-guide)
10. [Future Enhancements](#future-enhancements)

---

## Overview

### Purpose

Langfuse provides comprehensive observability for the Acme Claims Management Solution's AI agents and LLM integrations. While the existing `usage_tracker.py` system handles basic billing metrics, Langfuse adds:

- **Rich distributed tracing** for debugging multi-agent workflows
- **Human-in-the-loop annotation** for quality improvement
- **Dataset creation** from production traces for evaluation
- **Prompt versioning** and A/B testing (future)

### Benefits

| Benefit | Description |
|---------|-------------|
| **Debugging** | Trace complex multi-agent flows (fraud detection supervisor with 4 parallel vision agents) |
| **Quality Assurance** | Adjustors annotate AI decisions directly, building feedback datasets |
| **Cost Visibility** | See per-agent, per-claim LLM costs in real-time |
| **Performance Monitoring** | Track latency, token usage, error rates across all agents |
| **Evaluation** | Export annotated traces to build regression test suites |

### Design Principles

1. **Non-invasive:** Minimal changes to existing agent code
2. **Graceful degradation:** Langfuse failures don't break API functionality
3. **Parallel systems:** Runs alongside `usage_tracker.py` for billing continuity
4. **Per-agent isolation:** Each agent execution gets its own trace
5. **Configuration-driven:** Enable/disable via `api-config.yaml`

---

## Objectives

### Primary Goals

✅ **Comprehensive LLM Call Tracing**  
Automatically capture all `chat()`, `chat_with_tools()`, and `chat_with_image()` calls across:
- Fraud Detection Supervisor (Phase 1 vision agents + Phase 3 behavioral agent)
- Customer Chatbot Agent
- Future agents (damage analyzer, estimate explainer, etc.)

✅ **Per-Agent Trace Isolation**  
Each agent execution creates a separate trace:
- Fraud detection run → 1 trace with 4-5 generation spans
- Chatbot message → 1 trace with 1-2 generation spans
- Enables targeted debugging and performance analysis

✅ **Human Annotation Workflow**  
Adjustors can:
- View AI trace from claim review page
- Add scores (fraud_accuracy, estimate_quality, overall_confidence)
- Leave comments for team learning
- Tag traces for evaluation dataset export

✅ **Dataset Creation Pipeline**  
- Mark production traces with `export_for_evaluation` tag
- Export to evaluation datasets for regression testing
- Feed model fine-tuning and prompt engineering efforts

### Non-Goals (Future Work)

- ❌ **Prompt management migration** - Prompts stay in code initially (Python files)
- ❌ **Replacing usage_tracker.py** - Both systems run in parallel
- ❌ **External monitoring integration** - No Datadog, New Relic, Prometheus connectors

---

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         API Endpoint                             │
│         POST /api/v1/customers/{id}/claims                       │
│         POST /api/v1/chatbot/customer/message                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Agent Layer                                 │
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │ FraudSupervisor  │  │  ChatbotAgent    │  │  Future Agents│ │
│  │                  │  │                  │  │               │ │
│  │ • Trace context  │  │ • Trace context  │  │ • Trace ctx   │ │
│  │ • claim_id meta  │  │ • customer_id    │  │ • metadata    │ │
│  └──────────────────┘  └──────────────────┘  └───────────────┘ │
│                                                                   │
│  Instrumentation: start_agent_trace() at execute() entry        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│            LLM Client Layer (INTEGRATION POINT)                  │
│                                                                   │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────┐│
│  │ AnthropicClient    │  │   OpenAIClient     │  │  Bedrock   ││
│  │   (wrapped)        │  │    (wrapped)       │  │ (wrapped)  ││
│  └────────────────────┘  └────────────────────┘  └────────────┘│
│            ▲                       ▲                      ▲      │
│            └───────────────────────┴──────────────────────┘      │
│                      LangfuseWrapper                             │
│                                                                   │
│  • Intercepts: chat(), chat_with_image(), chat_with_tools()     │
│  • Creates: Langfuse generation spans                            │
│  • Captures: tokens, latency, cost, prompt, completion          │
│  • Handles: errors gracefully (no API breakage)                 │
└───────────┬───────────────────────────────────────┬─────────────┘
            │                                       │
            ▼                                       ▼
┌───────────────────────┐             ┌───────────────────────────┐
│  Langfuse Server      │             │  Local Database           │
│  (Docker/Cloud)       │             │  (agent_usage_logs)       │
│                       │             │                           │
│  • Traces             │             │  • Billing records        │
│  • Generations        │             │  • Cost aggregation       │
│  • Scores             │             │  • Historical trends      │
│  • Annotations        │             │  • Uptime tracking        │
│  • Datasets           │             │                           │
└───────────────────────┘             └───────────────────────────┘
         ▲
         │
         │ (Annotation UI)
         │
┌────────┴──────────┐
│ Adjustor Portal   │
│ "View AI Trace"   │
└───────────────────┘
```

### Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| **LangfuseWrapper** | Wraps BaseLLMClient methods, creates generation spans, handles errors |
| **langfuse_context.py** | Manages trace lifecycle (start_agent_trace, get_current_trace_id) |
| **BaseAgent** | Initializes trace context at execute() entry |
| **LLM Clients** | Unchanged - wrapper is transparent proxy |
| **usage_tracker.py** | Unchanged - continues database logging in parallel |
| **Langfuse Server** | Stores traces, provides annotation UI, exports datasets |

---

## Setup Instructions

### Option 1: Local Docker Deployment (Recommended for Development)

#### Prerequisites
- Docker and Docker Compose installed
- Git (for cloning Langfuse repository)

#### Step 1: Clone Langfuse Repository

```bash
cd /home/raj/workspace2026/Acme-Claim-Management-Solution/langfuse-integration
git clone https://github.com/langfuse/langfuse.git
cd langfuse
```

#### Step 2: Start Langfuse Server

```bash
docker compose up -d
```

This starts:
- Langfuse web app on `http://localhost:3000`
- PostgreSQL database (persistent volume)

Check status:
```bash
docker compose ps
```

#### Step 3: Initial Setup

1. Navigate to `http://localhost:3000` in browser
2. Click "Sign Up" and create an account:
   - Email: your-email@example.com
   - Password: (choose secure password)
3. Create organization: **acme-org**
4. Create project: **claims-project**
5. Navigate to Settings → API Keys
6. Click "Create New API Key"
7. Copy the generated keys:
   - **Public Key:** `pk-lf-...`
   - **Secret Key:** `sk-lf-...`

#### Step 4: Configure Environment Variables

Create or update `.env` file in project root:

```bash
# Langfuse Configuration
LANGFUSE_PUBLIC_KEY="pk-lf-a8121427..."
LANGFUSE_SECRET_KEY="sk-lf-af095a7..."
LANGFUSE_HOST="http://localhost:3000"
```

⚠️ **Security:** Never commit `.env` to version control. Ensure `.env` is in `.gitignore`.

#### Step 5: Enable in api-config.yaml

```yaml
tracking:
  usage_logging_enabled: true
  log_to_database: true
  langfuse:
    enabled: true  # Toggle to enable
    public_key_env: LANGFUSE_PUBLIC_KEY
    secret_key_env: LANGFUSE_SECRET_KEY
    host: http://localhost:3000
```

### Option 2: Cloud Langfuse (Alternative)

#### Step 1: Sign Up for Langfuse Cloud

1. Navigate to https://cloud.langfuse.com
2. Create account
3. Create organization and project
4. Get API keys from Settings

#### Step 2: Configure Environment

```bash
# .env file
LANGFUSE_PUBLIC_KEY="pk-lf-..."
LANGFUSE_SECRET_KEY="sk-lf-..."
LANGFUSE_HOST="https://cloud.langfuse.com"
```

#### Step 3: Update api-config.yaml

```yaml
tracking:
  langfuse:
    enabled: true
    host: https://cloud.langfuse.com  # Cloud endpoint
```

**Benefits:**
- No Docker management
- Managed scaling and backups
- Team collaboration features

**Considerations:**
- Data sent to cloud (review privacy/compliance)
- Requires internet connectivity
- May have usage limits on free tier

---

## Integration Design

### 1. LLM Client Layer Wrapping

**File:** `/src/api/agents/llm/langfuse_wrapper.py` (new)

The `LangfuseWrapper` class acts as a transparent proxy for `BaseLLMClient`:

**Responsibilities:**
- Intercept all LLM method calls (chat, chat_with_image, chat_with_tools, chat_stream)
- Create Langfuse generation spans with full context
- Extract token counts and latency from responses
- Calculate costs using existing `usage_tracker.calculate_cost()` logic
- Handle errors gracefully (don't break LLM calls if Langfuse fails)

**Key Methods:**

```python
class LangfuseWrapper(BaseLLMClient):
    def __init__(self, client: BaseLLMClient, langfuse_client: Langfuse):
        """Wraps an existing LLM client with Langfuse tracing"""
        
    async def chat(self, messages, **kwargs) -> ChatResponse:
        """Wraps chat() with generation span creation"""
        
    async def chat_with_image(self, messages, image_data, **kwargs) -> ChatResponse:
        """Wraps vision calls, attaches image metadata to span"""
        
    async def chat_with_tools(self, messages, tools, **kwargs) -> ChatResponse:
        """Wraps tool-calling, logs tool executions as sub-spans"""
        
    def _create_generation(self, method_name, input_data) -> Generation:
        """Helper to create Langfuse generation with standard metadata"""
        
    def _update_generation_with_response(self, generation, response):
        """Extracts tokens/latency, calculates cost, updates span"""
```

**Error Handling:**
- If Langfuse client initialization fails → log warning, return unwrapped client
- If generation creation fails → log error, proceed with LLM call
- If span update fails → log error, don't raise exception
- Principle: **Observability is optional, LLM functionality is critical**

### 2. Factory Integration

**File:** `/src/api/agents/llm/config.py` (modified)

Update `get_llm_client()` to conditionally wrap clients:

```python
def get_llm_client(provider: str = None) -> BaseLLMClient:
    """Get LLM client, optionally wrapped with Langfuse"""
    
    # Get base provider client (existing logic)
    client = _create_provider_client(provider)
    
    # Check if Langfuse is enabled in config
    if settings.LANGFUSE_ENABLED:
        try:
            langfuse_client = _get_langfuse_singleton()
            return LangfuseWrapper(client, langfuse_client)
        except Exception as e:
            logger.warning(f"Langfuse initialization failed: {e}")
            return client  # Fall back to unwrapped client
    
    return client
```

**Singleton Pattern:**
- Langfuse client initialized once per application lifecycle
- Reused across all LLM client instances
- Thread-safe for async operations

### 3. Trace Context Management

**File:** `/src/api/agents/tracking/langfuse_context.py` (new)

Manages trace lifecycle using Python's `contextvars` for async-safe propagation:

**Key Functions:**

```python
# Context variable for trace ID
_trace_context: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)

def start_agent_trace(
    agent_name: str, 
    claim_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    **metadata
) -> str:
    """
    Creates a new Langfuse trace for agent execution.
    
    Returns trace_id (stored in context for child spans)
    """

def get_current_trace_id() -> Optional[str]:
    """Returns trace ID for current async context"""

def add_trace_metadata(key: str, value: Any):
    """Adds metadata to current trace (if exists)"""

def end_agent_trace(success: bool = True, error: Optional[str] = None):
    """Finalizes trace with outcome"""
```

**Why contextvars?**
- Thread-safe for async/await operations
- Automatically propagates through `asyncio.gather()` (parallel agents)
- No need for explicit trace ID passing through function signatures

### 4. Agent Layer Instrumentation

**File:** `/src/api/agents/base_agent.py` (modified)

Minimal changes to `BaseAgent.execute()`:

```python
class BaseAgent(ABC):
    async def execute(self, **kwargs) -> AgentResult:
        """Execute agent with automatic Langfuse trace creation"""
        
        # Start trace (if Langfuse enabled)
        claim_id = kwargs.get('claim_id')
        customer_id = kwargs.get('customer_id')
        
        if settings.LANGFUSE_ENABLED:
            start_agent_trace(
                agent_name=self.__class__.__name__,
                claim_id=claim_id,
                customer_id=customer_id
            )
        
        # Existing execution logic (unchanged)
        try:
            result = await self._execute_impl(**kwargs)
            
            if settings.LANGFUSE_ENABLED:
                end_agent_trace(success=result.success)
            
            return result
        except Exception as e:
            if settings.LANGFUSE_ENABLED:
                end_agent_trace(success=False, error=str(e))
            raise
```

**No changes required in:**
- Individual agent implementations (fraud agents, chatbot)
- Service layer
- API routers

### 5. Configuration Loading

**File:** `/src/api/config.py` (modified)

Add properties to `Settings` class:

```python
class Settings:
    @property
    def LANGFUSE_ENABLED(self) -> bool:
        return self._config['tracking']['langfuse']['enabled']
    
    @property
    def LANGFUSE_PUBLIC_KEY(self) -> str:
        env_var = self._config['tracking']['langfuse']['public_key_env']
        return os.getenv(env_var)
    
    @property
    def LANGFUSE_SECRET_KEY(self) -> str:
        env_var = self._config['tracking']['langfuse']['secret_key_env']
        return os.getenv(env_var)
    
    @property
    def LANGFUSE_HOST(self) -> str:
        return self._config['tracking']['langfuse']['host']
```

---

## Trace Structure

### Per-Agent Trace Isolation

Each agent execution creates **one trace** with **one or more generation spans**:

```
Trace: "FraudDetectionSupervisor"
├── Generation: "color_verification" (Phase 1)
├── Generation: "make_model_verification" (Phase 1)
├── Generation: "ai_generated_detection" (Phase 1)
├── Generation: "image_manipulation_detection" (Phase 1)
└── Generation: "behavior_pattern_analysis" (Phase 3, conditional)

Trace: "ChatbotAgent"
├── Generation: "chatbot_initial_call" (with tools)
└── Generation: "chatbot_final_response" (tool results processed)
```

### Generation Span Metadata Schema

Each generation span includes:

```json
{
  "name": "color_verification",
  "model": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
  "prompt": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "Analyze vehicle color..."}
  ],
  "completion": "{\n  \"color_match\": true,\n  \"confidence\": 0.85,\n  ...\n}",
  "usage": {
    "input": 1250,
    "output": 180,
    "total": 1430,
    "unit": "TOKENS"
  },
  "usage_metadata": {
    "cost_usd": 0.0045,
    "latency_ms": 2340
  },
  "metadata": {
    "claim_id": 5001,
    "customer_id": 123,
    "agent_name": "ColorVerificationAgent",
    "provider": "bedrock",
    "phase": "phase1_vision"
  }
}
```

**Key Fields:**
- `name`: Human-readable identifier for this LLM call
- `model`: Exact model ID used
- `prompt`: Full input (system prompt + user message)
- `completion`: Full output from LLM
- `usage`: Token counts (input/output/total)
- `usage_metadata.cost_usd`: Calculated using `usage_tracker.calculate_cost()`
- `usage_metadata.latency_ms`: End-to-end call duration
- `metadata.*`: Business context (claim_id, customer_id, agent_name)

### Trace Metadata Schema

Trace-level metadata (applies to entire agent execution):

```json
{
  "trace_id": "abc-def-123",
  "name": "FraudDetectionSupervisor",
  "timestamp": "2026-05-09T14:23:45Z",
  "metadata": {
    "claim_id": 5001,
    "customer_id": 123,
    "vehicle_vin": "1ABC23456789DEFG",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "session_type": "fraud_detection",
    "total_images": 3,
    "phase1_score": 0.45,
    "phase3_enabled": true,
    "final_risk_level": "medium"
  },
  "tags": ["fraud_detection", "phase1", "phase3"],
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "customer_123"
}
```

**Usage:**
- Filter traces by `claim_id` to see all agent runs for a claim
- Filter by `customer_id` to see all AI interactions for a customer
- Filter by `session_id` to see all traces in a specific user session
- Filter by `session_type` to see all traces of a specific type (chatbot, fraud_detection, etc.)
- `tags` enable querying by workflow type or feature flag

---

## Session Tracking & Request Correlation

### Overview

Session tracking unifies related LLM interactions under a single session identifier, enabling complete user journey visibility and session-level analytics in Langfuse.

### Session Types

The system tracks four distinct session types:

| Session Type | Description | Duration | Example Use Case |
|-------------|-------------|----------|------------------|
| `chatbot` | Multi-turn conversational interactions with customer chatbot | 30 minutes (timeout) | Customer asks 3 questions about their claim status |
| `fraud_detection` | Claim submission and fraud analysis workflow | Single execution | Claim submitted → fraud detection runs → risk assessment complete |
| `claims_submission` | Complete claim filing process from start to finish | Hours to days | Customer starts claim → uploads images → submits → receives confirmation |
| `adjustor_review` | Adjustor portal interactions and annotations | Per-review session | Adjustor opens claim → reviews AI decision → adds annotations |

### Session ID Generation

**Chatbot Sessions:**
- Generated by frontend when conversation starts
- Maintained in `SessionManager` for 30-minute window
- Included in every chatbot message request

**Fraud Detection Sessions:**
- Generated when claim is submitted (`uuid.uuid4()`)
- Passed through router → service → agent
- Links claim submission to fraud analysis

**Claims Submission Sessions:**
- Generated at FNOL (First Notice of Loss)
- Spans multiple steps: customer info → vehicle info → damage images → submission
- Future enhancement

**Adjustor Review Sessions:**
- Generated when adjustor opens claim for review
- Groups all adjustor actions (view, annotate, approve)
- Future enhancement

### Session Metadata

All traces include session context in metadata:

```python
metadata = {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "session_type": "fraud_detection",
    "customer_id": 123,
    "claim_id": 5001,
    # ... other context fields
}
```

### Session-Level Analytics

**Query Examples:**

1. **Session duration:**
   ```python
   # Get all traces for a session, calculate time span
   traces = langfuse.get_traces(session_id="550e...")
   duration = traces[-1].timestamp - traces[0].timestamp
   ```

2. **Session cost:**
   ```python
   # Sum LLM costs across all traces in session
   total_cost = sum(trace.total_cost for trace in traces)
   ```

3. **Trace count per session:**
   ```python
   # Count LLM calls made during session
   trace_count = len(langfuse.get_traces(session_id="550e..."))
   ```

### Benefits

1. **Debugging:** "Show me everything that happened during session X"
2. **User Journey Visibility:** See complete customer interaction flow
3. **Performance Monitoring:** Track session-level latency and costs
4. **A/B Testing:** Compare session outcomes between model versions
5. **Adjustor Workflow:** Link related traces for holistic review

---

## Human Annotation Workflow

### Overview

Adjustors can annotate AI decisions to:
1. Provide feedback on fraud detection accuracy
2. Rate cost estimate quality
3. Build evaluation datasets from production data
4. Drive continuous improvement

### Integration Points

#### 1. Adjustor Portal UI

**Location:** `/src/ui/adjustor/src/pages/ClaimReviewPage.jsx`

**New Component:** "View AI Trace" button next to claim details

```jsx
<div className="ai-insights-section">
  <h3>AI Decision Trace</h3>
  <p>Trace ID: {claim.fraud_trace_id}</p>
  <a 
    href={`http://localhost:3000/trace/${claim.fraud_trace_id}`}
    target="_blank"
    className="btn-view-trace"
  >
    View AI Trace in Langfuse →
  </a>
</div>
```

**Data Flow:**
1. When fraud detection runs, store trace_id in `claim_events` table
2. Frontend fetches trace_id from API
3. Button opens Langfuse UI in new tab

#### 2. Storing Trace IDs

**Database:** Add field to `claim_events` table

```sql
ALTER TABLE claim_events 
ADD COLUMN langfuse_trace_id VARCHAR(255);
```

**Service Layer:** Update `FraudService.run_fraud_detection()`

```python
async def run_fraud_detection(claim_id: int) -> FraudResult:
    # Start trace
    trace_id = start_agent_trace("fraud_supervisor", claim_id=claim_id)
    
    # Run supervisor
    result = await supervisor.execute(claim_id=claim_id)
    
    # Store trace_id in database
    await event_service.log_event(
        claim_id=claim_id,
        event_type="fraud_analysis_completed",
        metadata={"langfuse_trace_id": trace_id}
    )
    
    return result
```

### Annotation Schema

#### Score Dimensions

Adjustors rate AI decisions on 1-5 scale:

| Score Name | Description | Good (4-5) | Poor (1-2) |
|------------|-------------|------------|------------|
| `fraud_accuracy` | Was fraud detection accurate? | Correctly identified all signals | Missed obvious fraud OR false positive |
| `estimate_quality` | Was cost estimate reasonable? | Within 10% of actual repair cost | >20% deviation |
| `overall_confidence` | Trust in AI decision | Would auto-approve | Requires full human review |

#### Comment Field

Free-text feedback for:
- Explaining low scores
- Highlighting edge cases
- Documenting disagreement with AI reasoning
- Suggesting prompt improvements

**Example:**
> "Color verification failed because car was in shadow. Need to add lighting condition context to prompt."

#### Tags for Dataset Export

Special tags trigger evaluation dataset export:

- `export_for_evaluation` - Include in regression test suite
- `edge_case` - Rare scenario worth manual review
- `model_upgrade_test` - Use for A/B testing new model versions
- `prompt_engineering` - Example for prompt improvement experiments

### Annotation Workflow (Step-by-Step)

1. **Adjustor reviews claim in portal**
   - Sees AI-generated fraud score and cost estimate
   - Clicks "View AI Trace" button

2. **Langfuse UI opens in new tab**
   - Shows trace with all generation spans
   - Displays prompts, completions, tokens, costs

3. **Adjustor clicks "Add Score" button**
   - Modal opens with score dimensions
   - Adjustor selects ratings (1-5) for each dimension
   - Adds free-text comment (optional)
   - Adds tags (e.g., `export_for_evaluation`)

4. **Score saved to Langfuse database**
   - Associated with trace_id
   - Visible in Langfuse analytics dashboard
   - Available for export via API

5. **Dataset export (manual/automated)**
   - Nightly job queries Langfuse API for tagged traces
   - Exports to JSONL format for model evaluation
   - Archives in `/data/evaluation_datasets/`

---

## Error Handling & Monitoring

### Graceful Degradation

**Principle:** Langfuse failures never break API functionality.

#### Error Scenarios & Handling

| Error | Cause | Response |
|-------|-------|----------|
| **Langfuse server unreachable** | Docker container down, network issue | Log warning, skip trace creation, LLM call proceeds normally |
| **Invalid API keys** | Misconfigured environment variables | Log error on startup, disable Langfuse wrapper, use unwrapped client |
| **Trace creation timeout** | Langfuse overloaded or slow network | Log timeout, continue with LLM call (trace incomplete but doesn't block) |
| **Generation update failure** | Langfuse API bug or data format issue | Log error, LLM response still returned to caller |

#### Implementation Pattern

```python
async def chat_with_image(self, messages, image_data, **kwargs):
    """Wraps vision call with Langfuse generation span"""
    generation = None
    
    try:
        # Attempt to create generation span
        generation = self._create_generation("chat_with_image", {...})
    except Exception as e:
        logger.warning(f"Langfuse generation creation failed: {e}")
        # Continue without tracing
    
    # Always call underlying LLM client
    response = await self.client.chat_with_image(messages, image_data, **kwargs)
    
    if generation:
        try:
            # Update span with response data
            self._update_generation_with_response(generation, response)
        except Exception as e:
            logger.warning(f"Langfuse generation update failed: {e}")
            # Response already obtained, safe to continue
    
    return response  # Always returns valid response
```

### Health Monitoring

#### Langfuse Integration Status

**Endpoint:** `GET /api/v1/admin/health`

Add Langfuse health check:

```json
{
  "status": "healthy",
  "components": {
    "database": "ok",
    "langfuse": {
      "status": "ok",
      "enabled": true,
      "host": "http://localhost:3000",
      "last_successful_trace": "2026-05-09T14:30:12Z",
      "error_count_24h": 3
    }
  }
}
```

**Metrics Tracked:**
- `langfuse_enabled`: Boolean from config
- `last_successful_trace`: Timestamp of most recent successful trace creation
- `error_count_24h`: Number of Langfuse errors in last 24 hours
- `average_latency_ms`: Overhead added by Langfuse instrumentation

#### Logging Strategy

**Log Levels:**
- `INFO`: Langfuse enabled/disabled on startup
- `WARNING`: Non-critical errors (trace creation failed, timeout)
- `ERROR`: Critical errors (invalid API keys, client initialization failure)

**Example Logs:**

```
2026-05-09 14:25:10 | INFO     | langfuse_wrapper | Langfuse integration enabled (host=http://localhost:3000)
2026-05-09 14:30:45 | WARNING  | langfuse_wrapper | Failed to create generation span: connection timeout (LLM call proceeded)
2026-05-09 15:02:33 | ERROR    | langfuse_context | Langfuse client initialization failed: invalid secret key (disabling wrapper)
```

#### Admin Dashboard Integration

**Location:** `/src/ui/admin/src/pages/DashboardPage.jsx`

Add "Langfuse Status" card:

```jsx
<Card title="Langfuse Observability">
  <StatusBadge status={langfuse.status} />
  <Metric label="Traces Today" value={langfuse.traces_today} />
  <Metric label="Error Rate" value={`${langfuse.error_rate}%`} />
  <Metric label="Avg Overhead" value={`${langfuse.avg_latency_ms}ms`} />
  <Link href={langfuse.host}>Open Langfuse Dashboard →</Link>
</Card>
```

---

## Verification Guide

### Prerequisites

1. ✅ Langfuse server running (Docker or cloud)
2. ✅ API keys configured in `.env`
3. ✅ `tracking.langfuse.enabled: true` in `api-config.yaml`
4. ✅ API server running: `uvicorn src.api.main:app --reload`

### Test 1: Chatbot Agent (Simplest Case)

**Objective:** Verify basic LLM tracing with single generation span

#### Step 1: Send Chatbot Message

```bash
curl -X POST http://localhost:8000/api/v1/chatbot/customer/message \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 100,
    "message": "What is my claim status?",
    "session_id": "test_session_001"
  }'
```

**Expected Response:**
```json
{
  "response": "Your most recent claim (Claim ID: 1000) was submitted on...",
  "session_id": "test_session_001"
}
```

#### Step 2: Verify in Langfuse UI

1. Open http://localhost:3000
2. Navigate to **Traces** page
3. Look for trace named **ChatbotAgent**
4. Click to expand trace details

**Expected Trace Structure:**
```
Trace: "ChatbotAgent"
├── metadata:
│   ├── customer_id: 100
│   ├── session_id: "test_session_001"
│   └── timestamp: "2026-05-09T..."
└── Generation: "chatbot_initial_call"
    ├── model: "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    ├── input_tokens: 450
    ├── output_tokens: 120
    ├── latency_ms: 1800
    └── cost_usd: 0.0032
```

**Verification Checklist:**
- ✅ Trace appears in UI within 5 seconds
- ✅ Customer ID visible in metadata
- ✅ Full prompt and completion visible
- ✅ Token counts match response headers
- ✅ Cost calculated correctly

### Test 2: Fraud Detection (Multi-Agent Complex Workflow)

**Objective:** Verify parallel agent tracing with multiple generation spans

#### Step 1: Submit Claim with Image

```bash
# Prepare test image
cp test_images/rear_bumper_dent.jpg /tmp/test_damage.jpg

# Submit claim
curl -X POST http://localhost:8000/api/v1/customers/100/claims \
  -F "loss_description=Rear-end collision at parking lot" \
  -F "loss_date=2026-05-08" \
  -F "vehicle_drivable=true" \
  -F "vehicle_vin=1ABC23456789DEFG" \
  -F "images=@/tmp/test_damage.jpg"
```

**Expected Response:**
```json
{
  "claim_id": 5001,
  "status": "FNOL",
  "fraud_risk_level": "low",
  "estimated_cost": 2450.00
}
```

#### Step 2: Verify in Langfuse UI

1. Navigate to **Traces**
2. Look for trace named **FraudDetectionSupervisor**
3. Expand to see generation spans

**Expected Trace Structure:**
```
Trace: "FraudDetectionSupervisor"
├── metadata:
│   ├── claim_id: 5001
│   ├── customer_id: 100
│   ├── vehicle_vin: "1ABC23456789DEFG"
│   ├── total_images: 1
│   └── phase3_enabled: true
├── Generation: "color_verification" (Phase 1)
│   ├── input_tokens: 1250
│   ├── output_tokens: 150
│   ├── latency_ms: 2340
│   └── cost_usd: 0.0045
├── Generation: "make_model_verification" (Phase 1)
│   ├── input_tokens: 1280
│   ├── output_tokens: 160
│   └── latency_ms: 2280
├── Generation: "ai_generated_detection" (Phase 1)
│   ├── input_tokens: 1200
│   ├── output_tokens: 140
│   └── latency_ms: 2100
├── Generation: "image_manipulation_detection" (Phase 1)
│   ├── input_tokens: 1220
│   ├── output_tokens: 145
│   └── latency_ms: 2190
└── Generation: "behavior_pattern_analysis" (Phase 3)
    ├── input_tokens: 980
    ├── output_tokens: 180
    └── latency_ms: 1950
```

**Verification Checklist:**
- ✅ Single trace with 5 generation spans (4 Phase 1 + 1 Phase 3)
- ✅ All generations have unique names matching agent names
- ✅ Total cost aggregated at trace level
- ✅ Timestamps show Phase 1 agents ran in parallel (<3s total, not 4x2.3s=9.2s)
- ✅ Claim ID and VIN visible in trace metadata

### Test 3: Human Annotation Workflow

**Objective:** Verify adjustor can annotate traces from UI

#### Step 1: Get Trace ID from API

```bash
curl http://localhost:8000/api/v1/claims/5001/events | jq '.events[] | select(.event_type=="fraud_analysis_completed") | .metadata.langfuse_trace_id'
```

**Expected Output:**
```
"abc-def-123-456"
```

#### Step 2: Open Trace in Langfuse

Navigate to:
```
http://localhost:3000/trace/abc-def-123-456
```

#### Step 3: Add Annotation

1. Click **"Add Score"** button (top right)
2. Fill in custom score:
   - **Name:** `fraud_accuracy`
   - **Value:** `4` (1-5 scale)
   - **Comment:** "Correctly identified color match and vehicle make/model"
3. Click **"Save"**

#### Step 4: Add Tag for Dataset Export

1. Click **"Add Tag"** button
2. Enter tag: `export_for_evaluation`
3. Press Enter to save

#### Step 5: Verify Annotation Saved

1. Refresh page
2. Check "Scores" section shows `fraud_accuracy: 4`
3. Check "Tags" section shows `export_for_evaluation`
4. Verify comment appears in annotation history

**Verification Checklist:**
- ✅ Score saved and visible
- ✅ Comment associated with score
- ✅ Tag applied to trace
- ✅ Annotation timestamp recorded

### Test 4: Error Handling (Graceful Degradation)

**Objective:** Verify API continues working when Langfuse is unavailable

#### Step 1: Stop Langfuse Server

```bash
cd langfuse-integration/langfuse
docker compose down
```

#### Step 2: Send Chatbot Message

```bash
curl -X POST http://localhost:8000/api/v1/chatbot/customer/message \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 100, "message": "Test message"}'
```

**Expected Behavior:**
- ✅ API responds normally (200 OK)
- ✅ Response contains valid chatbot answer
- ✅ No error exposed to user
- ✅ Logs show warning: `"Langfuse unavailable, skipping trace"`

#### Step 3: Check API Logs

```bash
tail -f logs/api.log | grep -i langfuse
```

**Expected Log Entry:**
```
2026-05-09 15:45:23 | WARNING | langfuse_wrapper | Failed to create trace: connection refused (host=http://localhost:3000)
2026-05-09 15:45:23 | INFO    | chatbot_agent | Chatbot message processed successfully (Langfuse disabled)
```

#### Step 4: Restart Langfuse

```bash
docker compose up -d
```

#### Step 5: Send Another Message

Verify tracing resumes automatically without API restart.

**Verification Checklist:**
- ✅ API functional during Langfuse outage
- ✅ Error logged but not propagated to user
- ✅ Tracing resumes when Langfuse recovers
- ✅ No data loss in `usage_tracker.py` database logs

### Test 5: Performance Overhead

**Objective:** Measure latency added by Langfuse instrumentation

#### Benchmark Script

```python
# scripts/benchmark_langfuse.py
import asyncio
import time
from src.api.agents.llm.config import get_llm_client

async def benchmark():
    client = get_llm_client("bedrock")
    
    iterations = 10
    start = time.time()
    
    for i in range(iterations):
        await client.chat([
            {"role": "user", "content": "What is the capital of France?"}
        ])
    
    elapsed = (time.time() - start) * 1000  # ms
    avg_per_call = elapsed / iterations
    
    print(f"Average per call: {avg_per_call:.2f}ms")

asyncio.run(benchmark())
```

#### Run Benchmark

**With Langfuse Disabled:**
```bash
# Set tracking.langfuse.enabled: false in api-config.yaml
python scripts/benchmark_langfuse.py
```

**With Langfuse Enabled:**
```bash
# Set tracking.langfuse.enabled: true in api-config.yaml
python scripts/benchmark_langfuse.py
```

**Expected Results:**
- Langfuse disabled: ~1800ms per call
- Langfuse enabled: ~1850ms per call
- **Overhead: <50ms (<3% increase)**

**Verification Checklist:**
- ✅ Overhead within acceptable range (<50ms)
- ✅ No timeout errors at scale
- ✅ Memory usage stable (no leaks)

---

## Future Enhancements

### Phase 5: Prompt Management Migration

**Objective:** Move prompts from Python code to Langfuse dashboard

**Benefits:**
- Version control for prompts (compare v1 vs v2)
- A/B testing without code deployment
- Non-technical stakeholders can edit prompts
- Rollback to previous prompt versions instantly

**Implementation:**
- Replace hardcoded prompts in `/src/api/agents/llm/prompts.py` with Langfuse prompt API calls
- Create prompt templates in Langfuse UI
- Use prompt versioning for gradual rollout

**Example:**
```python
# Before (hardcoded)
system_prompt = "You are a fraud detection agent..."

# After (Langfuse-managed)
prompt = langfuse.get_prompt("fraud_color_verification", version=2)
system_prompt = prompt.compile(vehicle_color="red", policy_color="blue")
```

### Phase 6: Streaming Support

**Objective:** Trace streaming LLM calls (e.g., chatbot with real-time responses)

**Challenge:**
- Current implementation requires full completion before creating generation span
- Streaming returns chunks incrementally

**Solution:**
- Accumulate chunks in buffer
- Create generation span when stream completes
- Attach full completion and token counts

**Implementation:**
```python
async def chat_stream(self, messages, **kwargs):
    generation = self._create_generation("chat_stream", {...})
    chunks = []
    
    async for chunk in self.client.chat_stream(messages, **kwargs):
        chunks.append(chunk)
        yield chunk  # Stream to caller
    
    # After stream completes, update generation
    full_completion = "".join(chunks)
    generation.update(completion=full_completion, ...)
```

### Phase 7: Automated Dataset Export

**Objective:** Nightly job to export annotated traces to evaluation datasets

**Architecture:**
```
┌─────────────────────┐
│  Cron Job (Nightly) │
│  02:00 AM           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  scripts/export_langfuse_datasets.py    │
│                                          │
│  1. Query Langfuse API for tagged traces│
│  2. Filter by date range (last 24h)     │
│  3. Export to JSONL format              │
│  4. Upload to evaluation framework      │
└──────────┬──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│  /data/evaluation_datasets/             │
│  ├── fraud_detection_2026-05-09.jsonl   │
│  ├── chatbot_responses_2026-05-09.jsonl │
│  └── cost_estimates_2026-05-09.jsonl    │
└─────────────────────────────────────────┘
```

**Dataset Format (JSONL):**
```json
{"trace_id": "abc-123", "agent": "fraud_supervisor", "input": {...}, "output": {...}, "score": 4, "comment": "..."}
{"trace_id": "def-456", "agent": "fraud_supervisor", "input": {...}, "output": {...}, "score": 5, "comment": "..."}
```

**Usage:**
- Regression testing (ensure new model versions don't degrade)
- Fine-tuning datasets (annotated examples for model training)
- Evaluation benchmarks (compare model A vs model B)

### Phase 8: Evaluation Pipeline Integration

**Objective:** Automated evaluation of AI agent performance

**Components:**
1. **Evaluation Framework:** LangSmith, Braintrust, or custom harness
2. **Metrics:**
   - Fraud detection accuracy (precision, recall)
   - Cost estimate MAE (mean absolute error)
   - Chatbot response quality (BLEU score, human ratings)
3. **Automated Runs:** Triggered on:
   - Model version change
   - Prompt template update
   - Weekly regression suite

**Architecture:**
```
Langfuse Dataset Export
         ↓
Evaluation Framework (LangSmith)
         ↓
Run agents on test cases
         ↓
Compare outputs to ground truth
         ↓
Generate scorecard
         ↓
Alert if metrics degrade
```

**Alerts:**
- Slack notification if fraud detection recall drops <90%
- Email if cost estimate MAE increases >15%
- Dashboard shows evaluation trends over time

---

## Implementation Phases & TODOs

This section breaks down the Langfuse integration into four sequential phases, each with specific objectives, actionable TODO items, verification steps, and rollback strategies. Complete each phase fully before proceeding to the next.

### Phase 0: Environment Setup

**Goal:** Set up Langfuse infrastructure and install dependencies

**Duration:** 1-2 hours

**Prerequisites:** None (starting point)

#### TODOs

> ✅ **PHASE 0 COMPLETED** - Environment setup is complete.

- [x] **Clone Langfuse repository**
  ```bash
  cd langfuse-integration
  git clone https://github.com/langfuse/langfuse.git
  cd langfuse
  ```

- [x] **Start Langfuse Docker containers**
  ```bash
  docker compose up -d
  # Verify containers running
  docker compose ps
  ```

- [x] **Access Langfuse UI**
  - Navigate to http://localhost:3000
  - Verify landing page loads

- [x] **Create organization and project**
  - Sign up with email/password
  - Create organization: `acme-org`
  - Create project: `claims-project`

- [x] **Generate API keys**
  - Navigate to Settings → API Keys
  - Click "Create New API Key"
  - Copy public key (pk-lf-...) and secret key (sk-lf-...)

- [x] **Configure environment variables**
  - Create or update `.env` file in project root:
    ```bash
    LANGFUSE_PUBLIC_KEY="pk-lf-..."
    LANGFUSE_SECRET_KEY="sk-lf-..."
    LANGFUSE_HOST="http://localhost:3000"
    ```
  - Verify `.env` is in `.gitignore`

- [x] **Install langfuse Python package**
  ```bash
  uv add langfuse
  ```

- [x] **Verify installation**
  ```bash
  uv pip list | grep langfuse
  ```

#### Verification Steps

1. ✅ Langfuse UI accessible at http://localhost:3000
2. ✅ Can log in with credentials
3. ✅ See "acme-org / claims-project" in dashboard
4. ✅ API keys generated and stored in `.env`
5. ✅ `langfuse` package installed (verify with `uv pip list | grep langfuse`)
6. ✅ Navigate to "Traces" page (should be empty)

#### Rollback Strategy

If setup fails or you need to start over:

```bash
# Stop and remove Langfuse containers
cd langfuse-integration/langfuse
docker compose down -v  # -v removes volumes (fresh start)

# Remove Python package
uv remove langfuse

# Remove environment variables
# Delete LANGFUSE_* lines from .env
```

---

### Phase 1: Core Integration

**Goal:** Implement basic LLM call tracing without breaking existing functionality

**Duration:** 1-2 days

**Prerequisites:** Phase 0 complete, Langfuse server running

#### TODOs

**Step 1: Create trace context management module**

- [ ] **Create `langfuse_context.py`**
  - File: `/src/api/agents/tracking/langfuse_context.py`
  - Implement functions:
    - `get_langfuse_client()` - Singleton Langfuse client
    - `start_agent_trace(agent_name, claim_id, customer_id, **metadata)` - Creates trace
    - `get_current_trace()` - Returns current trace from context
    - `end_agent_trace(success, error)` - Finalizes trace
  - Use Python `contextvars` for async-safe trace propagation
  - Handle initialization errors gracefully (return None if Langfuse unavailable)

**Step 2: Create LLM wrapper class**

- [ ] **Create `langfuse_wrapper.py`**
  - File: `/src/api/agents/llm/langfuse_wrapper.py`
  - Class: `LangfuseWrapper(BaseLLMClient)`
  - Implement `__init__(self, client: BaseLLMClient, langfuse_client: Langfuse)`

- [ ] **Implement `chat()` wrapper**
  - Get current trace from context
  - Create generation span before LLM call
  - Call wrapped `client.chat()`
  - Extract tokens from response
  - Calculate cost using `usage_tracker.calculate_cost()`
  - Update generation with completion, tokens, cost, latency
  - Return original response

- [ ] **Implement `chat_with_image()` wrapper**
  - Similar to `chat()` but:
  - Add image metadata to generation (image count, sizes)
  - Mark generation as vision call

- [ ] **Implement `chat_with_tools()` wrapper**
  - Create generation for initial LLM call
  - Log tool executions as child spans (if tools invoked)
  - Create second generation for final response (after tool results)

- [ ] **Add error handling**
  - Wrap all Langfuse calls in try-except
  - Log warnings on Langfuse errors
  - Always return LLM response (even if tracing fails)

**Step 3: Integrate with LLM factory**

- [ ] **Update `config.py`**
  - Add properties for Langfuse config:
    - `LANGFUSE_ENABLED`
    - `LANGFUSE_PUBLIC_KEY`
    - `LANGFUSE_SECRET_KEY`
    - `LANGFUSE_HOST`

- [ ] **Modify `get_llm_client()` in `config.py`**
  ```python
  def get_llm_client(provider: str = None) -> BaseLLMClient:
      client = _create_provider_client(provider)
      
      if settings.LANGFUSE_ENABLED:
          try:
              langfuse_client = get_langfuse_client()
              return LangfuseWrapper(client, langfuse_client)
          except Exception as e:
              logger.warning(f"Langfuse init failed: {e}")
      
      return client
  ```

**Step 4: Instrument base agent**

- [ ] **Update `BaseAgent.execute()` in `base_agent.py`**
  - Call `start_agent_trace()` at method entry
  - Extract `claim_id`, `customer_id` from kwargs
  - Pass agent class name as trace name
  - Call `end_agent_trace()` in finally block

- [ ] **Keep langfuse.enabled=false initially**
  - Complete implementation before enabling
  - Allows testing without affecting existing behavior

**Step 5: Testing**

- [ ] **Enable Langfuse in config**
  ```yaml
  tracking:
    langfuse:
      enabled: true
  ```

- [ ] **Test chatbot agent (simple case)**
  ```bash
  # Start API server
  uvicorn src.api.main:app --reload
  
  # Send chatbot message
  curl -X POST http://localhost:8000/api/v1/chatbot/customer/message \
    -H "Content-Type: application/json" \
    -d '{"customer_id": 100, "message": "What is my claim status?"}'
  ```
  - Verify trace appears in Langfuse UI
  - Check tokens, cost, latency are recorded
  - Verify prompt and completion visible

- [ ] **Test fraud detection agent (complex multi-agent)**
  ```bash
  # Submit claim with image
  curl -X POST http://localhost:8000/api/v1/customers/100/claims \
    -F "loss_description=Rear-end collision" \
    -F "vehicle_drivable=true" \
    -F "images=@test_images/damage1.jpg"
  ```
  - Verify single trace with 4-5 generation spans
  - Check all Phase 1 agents appear (color, make/model, AI-gen, manipulation)
  - Verify Phase 3 agent appears if triggered
  - Confirm metadata includes claim_id

- [ ] **Verify usage_tracker still works**
  - Query `agent_usage_logs` table
  - Confirm records still being created
  - Validate parallel system operation

#### Verification Steps

1. ✅ All LLM calls traced automatically (no manual instrumentation in agents)
2. ✅ Traces visible in Langfuse UI within 5 seconds
3. ✅ Token counts match LLM provider responses
4. ✅ Costs calculated correctly (compare to usage_tracker)
5. ✅ Parallel agents (fraud Phase 1) show in single trace
6. ✅ Business context (claim_id, customer_id) attached to traces
7. ✅ Prompts and completions fully visible in UI
8. ✅ No errors in API logs related to Langfuse
9. ✅ usage_tracker.py continues logging to database

#### Rollback Strategy

**Immediate rollback (no code changes):**
```yaml
# In api-config.yaml
tracking:
  langfuse:
    enabled: false
```

**Full rollback (remove code):**
```bash
# Remove new files
rm src/api/agents/llm/langfuse_wrapper.py
rm src/api/agents/tracking/langfuse_context.py

# Revert changes to config.py and base_agent.py
git checkout src/api/agents/llm/config.py
git checkout src/api/agents/base_agent.py

# Remove package
uv remove langfuse
```

---

### Phase 2: Session Tracking & Request Correlation

**Goal:** Unify all agent interactions under session IDs for complete user journey tracking

**Duration:** 1 day

**Prerequisites:** Phase 1 complete (basic tracing working)

#### TODOs

**Session Tracking Design:**

- [ ] **Define session types**
  - `chatbot`: Conversational interactions (already exists)
  - `fraud_detection`: Claim submission and analysis workflow
  - `claims_submission`: Complete claim filing session
  - `adjustor_review`: Adjustor portal interactions (future)

- [ ] **Extend Langfuse metadata schema**
  - Add `session_id` field (UUID) to all traces
  - Add `session_type` field (enum: chatbot, fraud_detection, claims_submission, adjustor_review)
  - Add `parent_session_id` for related sessions (optional)
  - Add `session_start_time` for duration calculation

**Implementation:**

- [ ] **Update fraud detection flow to generate session IDs**
  - File: `src/api/routers/claims.py`
  - Generate `session_id` when claim submitted
  - Pass through to `FraudService.run_fraud_detection()`
  - Example:
    ```python
    import uuid
    session_id = str(uuid.uuid4())
    fraud_result = await fraud_service.run_fraud_detection(
        claim_id=claim.id,
        session_id=session_id
    )
    ```

- [ ] **Update FraudService to accept and propagate session_id**
  - File: `src/api/services/fraud_service.py`
  - Add `session_id` parameter to `run_fraud_detection()`
  - Pass to supervisor's `execute()` method

- [ ] **Update fraud_supervisor.py to include session in trace**
  - File: `src/api/agents/fraud/fraud_supervisor.py`
  - Modify metadata in `start_agent_trace()`:
    ```python
    trace_id = start_agent_trace(
        agent_name="FraudDetectionSupervisor",
        metadata={
            "claim_id": claim_id,
            "customer_id": input_data.get("customer_id"),
            "vin": input_data.get("vin"),
            "session_id": input_data.get("session_id"),  # NEW
            "session_type": "fraud_detection"  # NEW
        }
    )
    ```

- [ ] **Enhance langfuse_wrapper.py to log session context**
  - File: `src/api/agents/llm/langfuse_wrapper.py`
  - Add session fields to all generation events
  - Include `session_id` and `session_type` in `create_event()` metadata

- [ ] **Update chatbot to explicitly set session_type**
  - File: `src/api/agents/chatbot/chatbot_agent.py`
  - Add `session_type: "chatbot"` to metadata alongside existing session_id

**Database Schema (Optional):**

- [ ] **Create langfuse_sessions table (optional)**
  - Purpose: Persist session metadata for historical lookup without querying Langfuse API
  - Schema:
    ```sql
    CREATE TABLE langfuse_sessions (
        session_id VARCHAR(255) PRIMARY KEY,
        customer_id INTEGER,
        session_type VARCHAR(50),
        created_at TIMESTAMP,
        closed_at TIMESTAMP,
        trace_count INTEGER DEFAULT 0,
        last_activity TIMESTAMP
    );
    ```
  - Note: This is optional - sessions can be queried directly from Langfuse API

**Documentation:**

- [ ] **Update trace structure examples in spec**
  - Show `session_id` and `session_type` in all metadata examples
  - Add session filtering examples for Langfuse UI
  
- [ ] **Document session types**
  - Add table describing each session type
  - Explain when each type is used
  - Provide use case examples
  
- [ ] **Add session querying guide**
  - How to filter by session in Langfuse UI
  - API examples for session-based queries
  - Session-level analytics examples (duration, cost, trace count)

**Testing:**

- [ ] **Test chatbot session tracking**
  - Start new conversation with specific session_id
  - Send 3 messages in same session
  - Verify all 3 traces have same `session_id` in Langfuse
  - Check `session_type: "chatbot"` appears in metadata

- [ ] **Test fraud detection session tracking**
  - Submit new claim (generates session_id)
  - Trigger fraud detection automatically
  - Verify trace includes `session_id` in metadata
  - Check `session_type: "fraud_detection"` appears
  - Confirm all Phase 1 sub-agents inherit session ID

- [ ] **Test session filtering**
  - In Langfuse UI, filter traces by specific session_id
  - Verify all related traces appear grouped together
  - Test filtering by session_type (show all chatbot sessions)

- [ ] **Test session-level metrics**
  - Query session duration (timestamp of first trace to last trace)
  - Calculate total LLM cost per session
  - Count number of traces per session

#### Verification Steps

1. ✅ All traces include `session_id` in metadata
2. ✅ Session types correctly set (`chatbot`, `fraud_detection`)
3. ✅ Can filter traces by session in Langfuse UI
4. ✅ Chatbot conversations grouped under one session
5. ✅ Fraud detection runs include session context
6. ✅ Session-level analytics queries work (duration, cost, trace count)
7. ✅ Documentation updated with session examples

#### Rollback Strategy

**Configuration rollback** (if issues occur):
- Session tracking is additive (metadata fields only)
- No breaking changes to existing code
- Can be disabled by removing session_id from metadata without code changes

**Code rollback** (if needed):
```bash
# Revert changes to specific files
git checkout src/api/routers/claims.py
git checkout src/api/services/fraud_service.py
git checkout src/api/agents/fraud/fraud_supervisor.py
git checkout src/api/agents/chatbot/chatbot_agent.py
```

---

### Phase 3: Production Readiness

**Goal:** Add error handling, monitoring, and performance safeguards

**Duration:** 1 day

**Prerequisites:** Phase 2 complete (session tracking implemented), traces visible in Langfuse

#### TODOs

**Step 1: Error handling enhancements**

- [ ] **Add timeout handling to Langfuse calls**
  - Set timeout on Langfuse client initialization (e.g., 5s)
  - Add timeout to generation span creation
  - Log timeout events with WARNING level

- [ ] **Improve exception handling in wrapper**
  - Catch specific exceptions (ConnectionError, Timeout, APIError)
  - Log different error types with appropriate context
  - Never raise exceptions to caller (graceful degradation)

- [ ] **Add circuit breaker pattern (optional)**
  - If Langfuse fails N times in a row, temporarily disable
  - Re-enable after cooldown period
  - Prevents log spam during outages

**Step 2: Health monitoring**

- [ ] **Add Langfuse health check**
  - Update `/api/v1/admin/health` endpoint
  - Add `langfuse` component to health response:
    ```json
    {
      "langfuse": {
        "status": "ok",
        "enabled": true,
        "host": "http://localhost:3000",
        "last_successful_trace": "2026-05-09T14:30:12Z",
        "error_count_24h": 3
      }
    }
    ```

- [ ] **Implement error counter**
  - Track Langfuse errors in memory (last 24 hours)
  - Expose count via health endpoint
  - Reset counter daily

- [ ] **Add Langfuse status to admin dashboard**
  - File: `/src/ui/admin/src/pages/DashboardPage.jsx`
  - Create "Langfuse Status" card:
    - Status badge (green/yellow/red)
    - Traces today counter
    - Error rate percentage
    - Average latency overhead
    - Link to Langfuse dashboard

**Step 3: Performance optimization**

- [ ] **Run performance benchmarks**
  - Create benchmark script: `scripts/benchmark_langfuse.py`
  - Measure latency with Langfuse disabled vs enabled
  - Run 20 iterations, calculate average
  - Target: <50ms overhead per LLM call
  - Document results in `/tmp/langfuse_benchmark_results.txt`

- [ ] **Profile trace creation overhead**
  - Use `cProfile` or `py-spy` to identify bottlenecks
  - Optimize JSON serialization if needed
  - Consider async trace creation (non-blocking)

- [ ] **Add trace sampling (if needed)**
  - If overhead too high, implement sampling
  - Trace 100% in development, sample in production (e.g., 10%)
  - Configurable via `tracking.langfuse.sample_rate`

**Step 4: Testing**

- [ ] **Test graceful degradation**
  ```bash
  # Stop Langfuse server
  cd langfuse-integration/langfuse
  docker compose down
  
  # Submit claim
  curl -X POST http://localhost:8000/api/v1/customers/100/claims \
    -F "loss_description=Test" \
    -F "images=@test_images/damage1.jpg"
  
  # Verify:
  # - API returns 200 OK
  # - Claim processed successfully
  # - Logs show "Langfuse unavailable" warning
  # - usage_tracker database still populated
  
  # Restart Langfuse
  docker compose up -d
  
  # Submit another claim
  # Verify tracing resumes automatically
  ```

- [ ] **Test invalid API keys**
  - Set invalid `LANGFUSE_SECRET_KEY` in `.env`
  - Restart API server
  - Verify API still functional
  - Check logs show initialization error

- [ ] **Load test (optional)**
  - Use `locust` or `k6` to generate load
  - Submit 100 claims concurrently
  - Monitor API latency, error rates
  - Verify no memory leaks

#### Verification Steps

1. ✅ API remains functional when Langfuse server is down
2. ✅ Errors logged with WARNING level (not ERROR)
3. ✅ Health endpoint shows Langfuse status
4. ✅ Admin dashboard displays Langfuse metrics
5. ✅ <50ms average latency overhead per LLM call
6. ✅ No exceptions propagated to API callers
7. ✅ Tracing resumes automatically after Langfuse recovers
8. ✅ Error counter tracks failures accurately

#### Rollback Strategy

No code rollback needed - error handling is defensive and doesn't break existing functionality. If issues arise:

```yaml
# Disable Langfuse temporarily
tracking:
  langfuse:
    enabled: false
```

---

### Phase 4: Human-in-the-Loop

**Goal:** Enable adjustor annotations and dataset creation workflow

**Duration:** 1 day

**Prerequisites:** Phase 3 complete, production-ready tracing working

#### TODOs

**Step 1: Database schema update**

> ✅ **COMPLETED** - Since we're in dev mode, the schema has been updated directly without migration.

- [x] **Updated ClaimEvent model**
  - File: `/src/api/models/claim_event.py`
  - Added `langfuse_trace_id = Column(String(255), nullable=True)`
  - Column will be created automatically on next database initialization

- [x] **Updated ERD diagram**
  - File: `/specifications/diagrams/claim-database-erd.mmd`
  - Added `langfuse_trace_id` field to `claims_events` entity

> **Note:** In dev mode, SQLAlchemy will automatically create the new column when the database is reinitialized. No manual migration needed.

**Step 2: Store trace IDs during fraud detection**

- [ ] **Modify FraudService**
  - File: `/src/api/services/fraud_service.py`
  - In `run_fraud_detection()`:
    ```python
    trace_id = start_agent_trace("fraud_supervisor", claim_id=claim_id)
    result = await supervisor.execute(claim_id=claim_id)
    
    # Store trace ID in claim event
    await event_service.log_event(
        claim_id=claim_id,
        event_type="fraud_analysis_completed",
        metadata={"langfuse_trace_id": trace_id}
    )
    ```

- [ ] **Test trace ID storage**
  - Submit claim via API
  - Query claim_events table
  - Verify `langfuse_trace_id` populated

**Step 3: Adjustor portal UI integration**

- [ ] **Add "View AI Trace" button**
  - File: `/src/ui/adjustor/src/pages/ClaimReviewPage.jsx`
  - Find section displaying claim details
  - Add new component:
    ```jsx
    {claim.langfuse_trace_id && (
      <div className="ai-trace-section">
        <h4>AI Decision Trace</h4>
        <a 
          href={`http://localhost:3000/trace/${claim.langfuse_trace_id}`}
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-secondary"
        >
          View AI Trace in Langfuse →
        </a>
      </div>
    )}
    ```

- [ ] **Update API to return trace ID**
  - File: `/src/api/routers/adjustors.py`
  - In claim detail response, include `langfuse_trace_id`
  - Fetch from latest fraud analysis event

**Step 4: Annotation workflow documentation**

- [ ] **Create annotation guide for adjustors**
  - File: `/docs/adjustor_annotation_guide.md`
  - Document:
    - How to access traces from claim review page
    - How to add scores (fraud_accuracy, estimate_quality, overall_confidence)
    - Score meaning (1-5 scale with examples)
    - How to add comments
    - How to tag traces for dataset export (`export_for_evaluation`)

- [ ] **Update adjustor training materials**
  - Add Langfuse annotation to onboarding checklist
  - Create video walkthrough (optional)

**Step 5: Dataset creation workflow**

- [ ] **Create manual export script**
  - File: `/scripts/export_langfuse_dataset.py`
  - Script functionality:
    - Query Langfuse API for traces with tag `export_for_evaluation`
    - Filter by date range (command line arg)
    - Export to JSONL format
    - Include: trace_id, agent_name, input, output, scores, comments
    - Save to `/data/evaluation_datasets/`
  - Usage:
    ```bash
    python scripts/export_langfuse_dataset.py --start-date 2026-05-01 --end-date 2026-05-09
    ```

- [ ] **Document dataset export process**
  - Add instructions to `docs/dataset_export.md`
  - Include manual process (for Phase 3)
  - Note: automated nightly job is future enhancement

**Step 6: Testing end-to-end workflow**

- [ ] **Test complete annotation workflow**
  1. Submit claim via customer portal
  2. Fraud detection runs automatically
  3. Log in to adjustor portal
  4. Open claim for review
  5. Click "View AI Trace" button
  6. Langfuse UI opens in new tab
  7. Add score: `fraud_accuracy = 4`
  8. Add comment: "Correctly identified vehicle color mismatch"
  9. Add tag: `export_for_evaluation`
  10. Verify score/comment/tag appear in Langfuse

- [ ] **Test dataset export**
  ```bash
  # Run export script
  python scripts/export_langfuse_dataset.py --start-date 2026-05-09 --end-date 2026-05-09
  
  # Verify JSONL file created
  ls -lh data/evaluation_datasets/
  
  # Check file contents
  head -n 1 data/evaluation_datasets/fraud_detection_2026-05-09.jsonl | jq .
  ```

- [ ] **Train one adjustor on workflow**
  - Walk through end-to-end process
  - Get feedback on usability
  - Iterate on UI/documentation as needed

#### Verification Steps

1. ✅ Trace IDs stored in `claim_events` table
2. ✅ "View AI Trace" button visible in adjustor portal
3. ✅ Button opens correct Langfuse trace in new tab
4. ✅ Adjustor can add scores in Langfuse UI
5. ✅ Scores and comments persist in Langfuse
6. ✅ Tags applied successfully
7. ✅ Export script retrieves tagged traces
8. ✅ JSONL format includes all required fields
9. ✅ Adjustor trained and can use workflow independently

#### Rollback Strategy

**UI rollback:**
```jsx
// Comment out "View AI Trace" button in ClaimReviewPage.jsx
// Trace IDs remain in DB but unused
```

**Database rollback (optional):**
```sql
ALTER TABLE claim_events DROP COLUMN langfuse_trace_id;
```

---

## Phase Completion Timeline

### Gantt Chart (Estimated)

```
Phase 0: Environment Setup
├─ Day 0 (1-2 hours): Docker setup, API keys, package install
└─ ✅ Milestone: Langfuse UI accessible with empty traces

Phase 1: Core Integration
├─ Day 1: langfuse_context.py + langfuse_wrapper.py implementation
├─ Day 2: Factory integration + base agent instrumentation
├─ Day 2-3: Testing (chatbot + fraud detection)
└─ ✅ Milestone: Traces visible in Langfuse with full metadata

Phase 2: Session Tracking & Request Correlation
├─ Day 3: Define session types + extend metadata schema
├─ Day 3: Update fraud detection and chatbot to include session context
├─ Day 3: Testing (session grouping, filtering, analytics)
└─ ✅ Milestone: All traces grouped by session, session-level metrics available

Phase 3: Production Readiness
├─ Day 4: Error handling + timeout logic
├─ Day 4-5: Health monitoring + admin dashboard
├─ Day 5: Performance benchmarks
└─ ✅ Milestone: API functional during Langfuse outages

Phase 4: Human-in-the-Loop
├─ Day 5-6: FraudService updates (database schema already updated)
├─ Day 6: Adjustor portal UI button
├─ Day 6: Export script + documentation
├─ Day 6: End-to-end testing + training
└─ ✅ Milestone: Adjustors can annotate traces

Total: 4-6 days (depending on testing thoroughness)
```

## Success Criteria

Upon completing all five phases, validate:

### Functional Requirements
- ✅ All LLM calls automatically traced (fraud, chatbot, future agents)
- ✅ Traces visible in Langfuse UI within 5 seconds of LLM call
- ✅ Each agent execution creates separate trace (no mixing)
- ✅ Token counts, latency, cost accurately recorded
- ✅ Business context (claim_id, customer_id, VIN) attached to traces
- ✅ Prompts and completions fully visible in Langfuse
- ✅ All traces include session_id and session_type in metadata
- ✅ Can filter and group traces by session in Langfuse UI
- ✅ Session-level metrics calculable (duration, cost, trace count)

### Reliability Requirements
- ✅ API remains functional if Langfuse server is down
- ✅ No exceptions propagated to API callers due to Langfuse errors
- ✅ Tracing resumes automatically when Langfuse recovers
- ✅ usage_tracker.py continues logging to database (parallel system)
- ✅ Zero production incidents caused by Langfuse integration

### Performance Requirements
- ✅ <50ms average latency overhead per LLM call
- ✅ No memory leaks during extended operation
- ✅ Concurrent claims (100+) processed without Langfuse bottlenecks

### Usability Requirements
- ✅ Adjustors can find AI trace from claim review page in <2 clicks
- ✅ Adjustors can add scores and comments in Langfuse UI
- ✅ Scores follow consistent schema (fraud_accuracy, estimate_quality, overall_confidence)
- ✅ Tagged traces exported to JSONL for evaluation

### Configuration Requirements
- ✅ Can enable/disable Langfuse via api-config.yaml without code changes
- ✅ Can switch between local Docker and cloud Langfuse without code changes
- ✅ Environment variables properly secured (not committed to git)

## Post-Implementation Checklist

After completing all phases:

- [ ] **Documentation review**
  - [ ] Update main README.md with Langfuse section
  - [ ] Add runbook entry for Langfuse troubleshooting
  - [ ] Document cost implications (Langfuse hosting, API overhead)

- [ ] **Team enablement**
  - [ ] Present Langfuse capabilities to engineering team
  - [ ] Train adjustors on annotation workflow
  - [ ] Share example traces that highlight value

- [ ] **Monitoring setup**
  - [ ] Add Langfuse health to alerting (if critical)
  - [ ] Set up weekly review of annotated traces
  - [ ] Establish metrics: traces/day, annotation rate, error rate

- [ ] **Future planning**
  - [ ] Prioritize Phase 5+ enhancements (prompt management, streaming)
  - [ ] Evaluate automated dataset export (Phase 7)
  - [ ] Consider evaluation pipeline integration (Phase 8)

---

## Appendix

### Dependencies

**Python Package:**
```toml
[project.dependencies]
langfuse = ">=2.50.0"
```

**Install:**
```bash
uv add langfuse
```

### Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `LANGFUSE_PUBLIC_KEY` | Langfuse project public key | `pk-lf-a8121427...` |
| `LANGFUSE_SECRET_KEY` | Langfuse project secret key | `sk-lf-af095a7...` |
| `LANGFUSE_HOST` | Langfuse server URL | `http://localhost:3000` or `https://cloud.langfuse.com` |

### Configuration Reference

**api-config.yaml:**
```yaml
tracking:
  usage_logging_enabled: true  # Keep existing usage_tracker.py enabled
  log_to_database: true
  langfuse:
    enabled: false  # Toggle to enable Langfuse
```

> **Note:** Credentials are read from environment variables (`LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`), not from the config file.

### API Endpoints Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/admin/health` | GET | Langfuse integration health check |
| `/api/v1/claims/{id}/events` | GET | Retrieve trace IDs for claim |

### Langfuse API Reference

**Get Trace by ID:**
```bash
curl https://cloud.langfuse.com/api/public/traces/{trace_id} \
  -H "Authorization: Bearer sk-lf-..."
```

**Export Tagged Traces:**
```python
from langfuse import Langfuse

langfuse = Langfuse()
traces = langfuse.get_traces(tags=["export_for_evaluation"], limit=100)

for trace in traces:
    print(f"Trace: {trace.id}, Score: {trace.scores}")
```

### Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Traces not appearing | Langfuse disabled in config | Set `tracking.langfuse.enabled: true` |
| "Invalid API key" error | Wrong env var value | Check `.env` file, regenerate keys in Langfuse UI |
| "Connection refused" | Docker container not running | Run `docker compose up -d` in langfuse directory |
| Slow API responses | Langfuse timeout | Increase `langfuse_client.timeout` or disable temporarily |
| Trace ID not in database | Service layer not updated | Run database migration, check event logging |

### Support Resources

- **Langfuse Documentation:** https://langfuse.com/docs
- **Langfuse GitHub:** https://github.com/langfuse/langfuse
- **Docker Compose Setup:** https://langfuse.com/docs/deployment/self-host
- **API Reference:** https://api.reference.langfuse.com

---

**Document Version:** 1.0  
**Last Updated:** 2026-05-09  
**Next Review:** After Phase 1 implementation complete
