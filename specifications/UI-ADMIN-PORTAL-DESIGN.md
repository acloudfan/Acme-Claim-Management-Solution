# Admin Portal - Design Specification

**Last Updated:** 2026-05-07  
**Status:** Design Phase  
**Purpose:** Configuration management portal for insurance claims API system

---

## 1. Overview

**ACME Claims : Admin Portal** provides a centralized interface for managing the Insurance Claims API configuration. It allows administrators to:
- **(a)** Manage Business rules applied to the AI Agents
- **(b)** Configure Technical parameters such as Vision models, Model providers, etc.

This eliminates the need to directly edit YAML files or manually restart services.

### 1.1 Key Features

- **Configuration Management**: Edit API configuration (api-config.yaml) with validation
- **Section-based UI**: Organized into "Claim Processing Rules" and "Technical Parameters"
- **Backup & Restore**: Automatic timestamped backups (.datetime.bak) before changes
- **Portal Quick Access**: Convenience panel with buttons to launch Customer, Adjustor, and Executive portals in separate windows
- **No Authentication**: Open access for prototype/demo environments only

### 1.2 Out of Scope (Future Enhancements)

- Live system monitoring/dashboards (kept simple per user preference)
- Config change history viewer (file backups only)
- Role-based access control (no auth for prototype)
- Preview/test mode for configuration changes

---

## 2. Architecture

### 2.1 Technology Stack

```
Frontend:
- Vite + React 18
- React Router v7
- Tailwind CSS v3
- Axios for API calls
- Lucide React for icons

Backend Integration:
- REST API: /api/v1/admin/*
- Config file: api-config.yaml (loaded and saved via API)
- Backup strategy: YAML + .datetime.bak files
```

### 2.2 Project Structure

The Admin Portal is an **independent React application** (not a monorepo) following the same pattern as Customer and Adjustor portals:

```
src/ui/admin/
├── public/
│   ├── admin-portal-config.yaml     # Portal-specific configuration
│   └── index.html
├── src/
│   ├── main.jsx                      # Entry point with config loader
│   ├── App.jsx                       # Router + Routes
│   ├── context/
│   │   └── AuthContext.jsx           # Authentication (no-auth mode)
│   ├── pages/
│   │   ├── LoginPage.jsx             # Minimal login (no password required)
│   │   ├── DashboardPage.jsx         # Main config editor
│   │   └── NotFoundPage.jsx
│   ├── components/
│   │   ├── common/                   # Reused from customer/adjustor
│   │   │   ├── Button.jsx
│   │   │   ├── Card.jsx
│   │   │   ├── Input.jsx
│   │   │   ├── Textarea.jsx
│   │   │   ├── Badge.jsx
│   │   │   ├── Modal.jsx
│   │   │   └── Spinner.jsx
│   │   └── config/                   # Admin-specific
│   │       ├── ConfigSection.jsx     # Collapsible section wrapper
│   │       ├── ConfigField.jsx       # Editable field with description
│   │       └── PortalLauncher.jsx    # Quick access panel
│   ├── api/
│   │   ├── client.js                 # Axios client with X-Admin-ID header
│   │   ├── config.js                 # Load admin-portal-config.yaml
│   │   └── admin.js                  # Admin API endpoints
│   └── utils/
│       ├── formatters.js
│       └── constants.js
├── package.json
├── vite.config.js
└── tailwind.config.js
```

---

## 3. User Interface Design

### 3.1 Layout Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Admin Portal Header]                                  [Admin Name] │
├───────────────────────────────────────┬─────────────────────────────┤
│                                       │  ┌──────────────────────┐   │
│  CONFIGURATION EDITOR (80%)           │  │  Quick Access Panel  │   │
│                                       │  │  (20%)               │   │
│  ┌─────────────────────────────────┐ │  │                      │   │
│  │ [Save] [Reset] [Backup History] │ │  │  [Customer Portal]   │   │
│  └─────────────────────────────────┘ │  │                      │   │
│                                       │  │  [Adjustor Portal]   │   │
│  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │  │                      │   │
│  ┃ Section 1: Claim Processing    ┃ │  │  [Executive Portal]  │   │
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ │  │    (Disabled)        │   │
│    ┌─ Subsection: Thresholds ───┐   │  └──────────────────────┘   │
│    │ • Confidence Thresholds     │   │                             │
│    │   - High Threshold  [0.55]  │   │  Portal URLs loaded from    │
│    │   - Low Threshold   [0.35]  │   │  admin-portal-config.yaml   │
│    │ • Fraud Detection           │   │                             │
│    │   - Risk Threshold  [0.1]   │   │  ┌──────────────────────┐   │
│    │ • Auto-Approval             │   │  │  🎬 Demo Scenarios   │   │
│    │   - Amount Threshold [$5000]│   │  ├──────────────────────┤   │
│    └─────────────────────────────┘   │  │ 1️⃣ Happy Path       │   │
│                                       │  │   Cx accepts AI est  │   │
│    ┌─ Subsection: Agent Settings ─┐  │  │   John Doe/Corolla   │   │
│    │ • Fraud Detector            │  │  │                      │   │
│    │   ☑ Enabled                 │  │  │ 2️⃣ Customer Appeal  │   │
│    │ • Risk Estimator            │  │  │   Human Review - Cx  │   │
│    │   ☑ Enabled                 │  │  │   Appeals            │   │
│    │ • Damage Analyzer           │  │  │   Jane Smith/BMW     │   │
│    │   ☑ Enabled                 │  │  │                      │   │
│    │   ☑ Enhance All Damages     │  │  │ 3️⃣ Fraud Detection  │   │
│    └─────────────────────────────┘  │  │   Bob Johnson/Chevy  │   │
│                                       │  │   (Config toggle)    │   │
│                                       │  └──────────────────────┘   │
│                                       │                             │
│  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │                             │
│  ┃ Section 2: Technical Parameters┃ │                             │
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ │                             │
│    ┌─ Subsection: LLM Config ────┐  │                             │
│    │ • Default Provider          │  │                             │
│    │   ○ Anthropic               │  │                             │
│    │   ○ OpenAI                  │  │                             │
│    │   ⦿ AWS Bedrock             │  │                             │
│    │ • Model Settings            │  │                             │
│    │   - Timeout (s)     [60]    │  │                             │
│    │   - Max Tokens      [4096]  │  │                             │
│    │   - Temperature     [0.2]   │  │                             │
│    └─────────────────────────────┘  │                             │
│                                       │                             │
│    ┌─ Subsection: Database ──────┐  │                             │
│    │ • Connection Pool           │  │                             │
│    │   - Pool Size       [5]     │  │                             │
│    │   - Max Overflow    [10]    │  │                             │
│    └─────────────────────────────┘  │                             │
└───────────────────────────────────────┴─────────────────────────────┘
```

**Note:** The Demo Scenarios card appears in the right sidebar (20% column) below the Quick Access panel. It displays three color-coded scenarios:
- 1️⃣ Happy Path (green background) - John Doe/Toyota Corolla flow
- 2️⃣ Customer Appeal (amber background) - Jane Smith/BMW with radiator damage and human review
- 3️⃣ Fraud Detection (red background) - Bob Johnson/Chevy with config toggle demonstration showing make mismatch detection

### 3.2 Page Descriptions

#### 3.2.1 Login Page (`/login`)

**Purpose:** Minimal entry point (no authentication required for prototype)

**UI Elements:**
- Admin Portal logo/title
- "Admin ID" text input (optional, defaults to "admin_001")
- "Enter Portal" button (no password field)
- Auto-login if localStorage has `admin_id`

**Behavior:**
- On submit: Store `admin_id` in localStorage → redirect to `/dashboard`
- No API validation (prototype mode)

---

#### 3.2.2 Dashboard Page (`/dashboard`)

**Purpose:** Main configuration editor

**Layout:** 80/20 split (config editor / portal launcher)

##### Left Section (80%): Configuration Editor

**Header Actions:**
- **[Save]** button (primary): Validates → Saves to YAML → Creates backup → Shows restart prompt
- **[Reset]** button (secondary): Reverts unsaved changes
- **[Backup History]** button (ghost): Shows list of .bak files with restore option

**Section 1: Claim Processing Rules**

*Subsection: Confidence & Thresholds*
| Field | Type | Default | Description | Example |
|-------|------|---------|-------------|---------|
| High Confidence Threshold | Number (0-1) | 0.55 | Minimum confidence to auto-present estimate to customer | 0.55 means 55% confidence |
| Low Confidence Threshold | Number (0-1) | 0.35 | Below this, route to traditional claim process | 0.35 means 35% confidence |
| Fraud Risk Threshold | Number (0-1) | 0.1 | Above this, flag claim for human review | 0.1 means 10% risk |
| Human Review Amount | Currency ($) | 5000.00 | Dollar threshold for mandatory human review | Claims over $5,000 require review |

*Subsection: Agent Toggles*
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| Enable Fraud Detector | Checkbox | ✓ | Run fraud detection on all claims |
| Enable Risk Estimator | Checkbox | ✓ | Analyze claims for actuarial risk |
| Enable AI Image Detector | Checkbox | ✓ | Detect AI-generated/manipulated images |
| Enable Damage Analyzer | Checkbox | ✓ | Enhance damage assessments with LLM |
| Enhance All Damages | Checkbox | ✓ | Apply analyzer to all damage reports (vs. low-confidence only) |
| Enable Chatbot | Checkbox | ✓ | Customer-facing chatbot in portal |

*Subsection: Fraud Detection Settings*
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| High Risk Threshold | Number (0-1) | 0.7 | ≥0.7 = HIGH RISK (recommend reject) |
| Medium Risk Threshold | Number (0-1) | 0.4 | 0.4-0.7 = MEDIUM RISK (human review) |
| Enable Color Verification | Checkbox | ✓ | Check if image color matches vehicle record |
| Enable Make/Model Verification | Checkbox | ✓ | Verify vehicle make/model in images |
| Enable AI Image Detection | Checkbox | ✓ | Detect AI-generated images |
| Enable Manipulation Detection | Checkbox | ✓ | Detect photo editing/manipulation |

**Section 2: Technical Parameters**

*Subsection: LLM Configuration*
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| Default Provider | Radio | bedrock | anthropic, openai, or bedrock |
| Default Vision Model | Radio | bedrock | Model used for image analysis |
| Timeout (seconds) | Number | 60 | LLM API request timeout |
| Max Tokens | Number | 4096 | Maximum response tokens |
| Temperature | Number (0-2) | 0.2 | Sampling temperature (lower = more deterministic) |

*Subsection: Bedrock Settings (if selected)*
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| AWS Region | Text | us-east-1 | AWS region for Bedrock |
| Default Model | Select | claude-3-5-sonnet-v2 | Model ID (dropdown of available models) |

*Subsection: Database*
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| Pool Size | Number | 5 | Connection pool size |
| Max Overflow | Number | 10 | Additional connections beyond pool |
| Echo SQL | Checkbox | ☐ | Log all SQL queries (debug mode) |

*Subsection: Storage*
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| Images Root Folder | Text | uploads | Directory for claim images |
| Max Upload Size (MB) | Number | 10 | Per-image size limit |
| Max Images Per Claim | Number | 20 | Maximum images allowed per claim |

*Subsection: API*
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| Debug Mode | Checkbox | ✓ | Enable debug logging and CORS |
| Host | Text | 0.0.0.0 | API server host (0.0.0.0 for all interfaces) |
| Port | Number | 8000 | API server port |

##### Right Section (20%): Portal Launcher & Demo Scenarios

**Component:** Fixed sidebar with quick access buttons and demo scenarios

**Buttons:**
1. **[🌐 Customer Portal]** 
   - Opens `http://localhost:5173` (from config) in new window
   - Opens in standard browser window (not tab)

2. **[👤 Adjustor Portal]**
   - Opens `http://localhost:5174` (from config) in new window

3. **[📊 Executive Portal]** (Disabled)
   - Grayed out with "Coming Soon" badge
   - Tooltip: "Business dashboards will be available in future release"

**Config Source:** URLs loaded from `admin-portal-config.yaml`:
```yaml
portal_links:
  customer_portal_url: "http://localhost:5173"
  adjustor_portal_url: "http://localhost:5174"
  executive_portal_url: null  # Future
```

**Demo Scenarios Card:**

Below the Quick Access panel, a Demo Scenarios card displays three test scenarios for demonstrating the claims system:

**Card Layout:**
```
┌────────────────────────────────────┐
│ 🎬 Demo Scenarios                  │
├────────────────────────────────────┤
│ ┌────────────────────────────────┐ │
│ │ 1️⃣ Happy Path                  │ │
│ │ Happy Path - Cx accepts AI     │ │
│ │ estimate                       │ │
│ │ • Customer: John Doe (#100)    │ │
│ │ • Vehicle: 2015 Toyota Corolla │ │
│ │ • Flow: Submit → AI estimate   │ │
│ │   → Customer accepts           │ │
│ └────────────────────────────────┘ │
│                                    │
│ ┌────────────────────────────────┐ │
│ │ 2️⃣ Customer Appeal             │ │
│ │ Human Review - Cx Appeals      │ │
│ │ • Customer: Jane Smith (#101)  │ │
│ │ • Vehicle: 2006 BMW 1 Series   │ │
│ │ • Damage: Radiator damaged     │ │
│ │ • Flow: Submit → Low AI conf   │ │
│ │   → Cx appeals → Adj review    │ │
│ └────────────────────────────────┘ │
│                                    │
│ ┌────────────────────────────────┐ │
│ │ 3️⃣ Fraud - Make Mismatch       │ │
│ │ • Customer: Bob Johnson (#102) │ │
│ │ • Vehicle: 2012 Chevy truck    │ │
│ │ • Detection: Make mismatch     │ │
│ └────────────────────────────────┘ │
│                                    │
│ ┌────────────────────────────────┐ │
│ │ 4️⃣ Fraud - AI Generated Image │ │
│ │ • Customer: Alice Williams     │ │
│ │ • Vehicle: 2022 Honda Accord   │ │
│ │ • Detection: VLM analyzes for  │ │
│ │   AI generation signals        │ │
│ │ • Note: Production systems use │ │
│ │   VLM + static analysis tools  │ │
│ └────────────────────────────────┘ │
└────────────────────────────────────┘
```

**Visual Design:**
- Scenario 1 (Happy Path): Light green background (`bg-green-50`)
- Scenario 2 (Customer Appeal): Light amber background (`bg-amber-50`)
- Scenario 3 (Fraud Detection): Light red background (`bg-red-50`)
- Each scenario displays emoji indicator (1️⃣, 2️⃣, 3️⃣)
- Bullet points with customer details, vehicle info, and flow steps
- Card has subtle border and shadow for visual separation

**Purpose:**
Provides quick reference for demo users to understand the three main claim processing paths:
1. **Happy Path**: Standard approval flow with AI estimate acceptance
2. **Customer Appeal**: Human review triggered by customer disagreement
3. **Fraud Detection**: Configurable fraud detection with make/model verification

---

### 3.3 Component Design

#### 3.3.1 ConfigSection Component

**Purpose:** Collapsible section wrapper for organizing related settings

**Props:**
```jsx
<ConfigSection
  title="Claim Processing Rules"
  description="Business rules and thresholds for automated claim processing"
  defaultExpanded={true}
  icon={<Settings />}  // Lucide icon
>
  {children}
</ConfigSection>
```

**UI:**
- Clickable header with expand/collapse icon
- Title + description (gray text)
- Animated expand/collapse transition
- Border + subtle shadow (card-like)

---

#### 3.3.2 ConfigField Component

**Purpose:** Reusable field editor with label, input, description, and validation

**Props:**
```jsx
<ConfigField
  label="High Confidence Threshold"
  description="Minimum confidence to auto-present estimate to customer"
  example="0.55 means 55% confidence"
  type="number"  // text, number, checkbox, select, radio
  value={config.ai.confidence.high_threshold}
  onChange={(value) => handleChange('ai.confidence.high_threshold', value)}
  validation={{ min: 0, max: 1, step: 0.05 }}
  error={errors['ai.confidence.high_threshold']}
  required={true}
/>
```

**UI:**
- Label (bold) with optional "(required)" indicator
- Input field (styled based on type)
- Description text (gray, small font)
- Example text (italic, lighter gray)
- Error message (red text below field)

**Validation:**
- Real-time validation on change
- Error display without blocking
- Submit-time validation before save

---

#### 3.3.3 PortalLauncher Component

**Purpose:** Quick access panel for launching other portals

**Props:**
```jsx
<PortalLauncher
  customerPortalUrl="http://localhost:5173"
  adjustorPortalUrl="http://localhost:5174"
  executivePortalUrl={null}  // null = disabled
/>
```

**UI:**
- Fixed position sidebar (20% width)
- Title: "Quick Access"
- Three stacked buttons with icons
- Button states:
  - Enabled: Primary styling, opens in new window on click
  - Disabled: Gray styling, "Coming Soon" badge, tooltip

**Behavior:**
```javascript
const openPortal = (url) => {
  window.open(url, '_blank', 'width=1440,height=900');
};
```

---

#### 3.3.4 DemoScenarios Component

**Purpose:** Display three demo scenarios for testing the claims system

**Location:** Right sidebar (20% width), below Quick Access panel

**Component File:** `src/components/config/DemoScenarios.jsx`

**UI Structure:**
```jsx
<Card className="mt-4">
  <div className="space-y-4">
    <div className="flex items-center gap-2">
      <span className="text-2xl">🎬</span>
      <h3>Demo Scenarios</h3>
    </div>
    {/* Scenario cards */}
  </div>
</Card>
```

**Scenario Cards:**

**Scenario 1: Happy Path**
- Background: `bg-green-50 border-green-200`
- Emoji: 1️⃣
- Title: "Happy Path - Cx accepts AI estimate"
- Details:
  - Customer: John Doe (#100)
  - Vehicle: 2015 Toyota Corolla
  - Flow: Submit → AI estimate → Customer accepts

**Scenario 2: Customer Appeal**
- Background: `bg-amber-50 border-amber-200`
- Emoji: 2️⃣
- Title: "Human Review - Cx Appeals"
- Details:
  - Customer: Jane Smith (#101)
  - Vehicle: 2006 BMW 1 Series (E87)
  - Damage: Radiator damaged
  - Flow: Submit → Low AI confidence → Cx appeals → Adjustor review

**Scenario 3: Fraud Detection - Make Mismatch**
- Background: `bg-red-50 border-red-200`
- Emoji: 3️⃣
- Title: "Fraud Detection - Make Mismatch"
- Details:
  - Customer: Bob Johnson (#102)
  - Vehicle: 2012 Chevy Silverado (Red)
  - Test Variation: Use config toggle to disable/enable fraud detection
  - Images show Chevy vs Ford (make mismatch triggers fraud signal)

**Scenario 4: Fraud Detection - AI Generated Image**
- Background: `bg-red-50 border-red-200`
- Emoji: 4️⃣
- Title: "Fraud Detection - AI Generated Damage"
- Details:
  - Customer: Alice Williams (#103)
  - Vehicle: 2022 Honda Accord (Black)
  - Fraud Type: AI-generated damage image created using image manipulation model
  - Detection: Vision Language Model (VLM) analyzes images for AI generation artifacts and inconsistencies
  - Note: In production, static image analysis tools (forensic metadata analysis, pixel-level artifact detection) complement VLM analysis for comprehensive fraud detection

**Visual Design:**
- Each scenario in separate card with colored background
- Bullet points for details
- Compact layout to fit in sidebar
- Subtle border and shadow for card separation
- Responsive: stacks below Quick Access on mobile

---

### 3.4 Modals & Dialogs

#### 3.4.1 Save Confirmation Modal

**Trigger:** User clicks [Save] button

**Content:**
- **Title:** "Save Configuration Changes?"
- **Body:** "This will update `api-config.yaml` and create a backup. You'll need to restart the API server for changes to take effect."
- **Actions:**
  - [Cancel] (secondary)
  - [Save & Show Restart Instructions] (primary)

**On Confirm:**
1. POST `/api/v1/admin/config` with updated config
2. API creates backup: `api-config.2026-05-07-14-30-45.bak`
3. Show Restart Instructions modal

---

#### 3.4.2 Restart Instructions Modal

**Trigger:** After successful config save

**Content:**
- **Title:** "Configuration Saved"
- **Body:**
  ```
  ✓ Configuration saved to api-config.yaml
  ✓ Backup created: api-config.2026-05-07-14-30-45.bak
  
  To apply changes, restart the API server:
  
  Manual Restart:
    Ctrl+C in terminal, then: make run-api
  
  Automatic Restart (if supervisor enabled):
    Changes will apply in ~10 seconds
  ```
- **Actions:**
  - [Done] (primary)

**Future Enhancement:** Add [Restart Automatically] button that calls `/api/v1/admin/restart` endpoint

---

#### 3.4.3 Backup History Modal

**Trigger:** User clicks [Backup History] button

**Content:**
- **Title:** "Configuration Backups"
- **Body:** Table with columns:
  - Filename (e.g., `api-config.2026-05-07-14-30-45.bak`)
  - Timestamp (formatted as "May 7, 2026 at 2:30 PM")
  - Size (e.g., "12.3 KB")
  - Actions: [Restore] [Download]
- **Actions:**
  - [Close] (secondary)

**Restore Flow:**
1. User clicks [Restore]
2. Show confirmation dialog: "Restore `api-config.2026-05-07-14-30-45.bak`? This will overwrite current config."
3. On confirm: POST `/api/v1/admin/config/restore` with backup filename
4. Reload page to show restored config

---

## 4. API Endpoints

The Admin Portal integrates with backend API endpoints for configuration management.

**⚠️ IMPORTANT:** Complete API specifications, request/response schemas, validation rules, and implementation details are documented in:

**📄 [API-BACKEND-DESIGN.md - Section 17: Admin Portal API Endpoints](./API-BACKEND-DESIGN.md#17-admin-portal-api-endpoints)**

### 4.1 Endpoint Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/admin/config` | GET | Retrieve current API configuration from `api-config.yaml` |
| `/api/v1/admin/config` | POST | Save updated configuration with automatic backup |
| `/api/v1/admin/config/backups` | GET | List all available backup files with metadata |
| `/api/v1/admin/config/restore` | POST | Restore configuration from a specific backup file |

### 4.2 Key Features

- ✅ **Automatic Backups**: Every save creates timestamped backup (`api-config.YYYY-MM-DD-HH-MM-SS.bak`)
- ✅ **Validation**: Server-side validation with detailed error messages per field
- ✅ **Security**: Credential masking, path traversal protection
- ✅ **Backup Retention**: Keep all backups indefinitely (no auto-cleanup)

### 4.3 Frontend Integration

**API Client Configuration:**
```javascript
// src/ui/admin/src/api/admin.js
import { getApiClient } from './client';

export const loadConfig = async () => {
  const client = getApiClient();
  const response = await client.get('/admin/config');
  return response.data;
};

export const saveConfig = async (config) => {
  const client = getApiClient();
  const response = await client.post('/admin/config', { config });
  return response.data;
};

export const listBackups = async () => {
  const client = getApiClient();
  const response = await client.get('/admin/config/backups');
  return response.data;
};

export const restoreBackup = async (backupFilename) => {
  const client = getApiClient();
  const response = await client.post('/admin/config/restore', { backup_filename: backupFilename });
  return response.data;
};
```

**For complete details**, see [API-BACKEND-DESIGN.md Section 17](./API-BACKEND-DESIGN.md#17-admin-portal-api-endpoints).

---

## 5. Configuration Schema

### 5.1 Editable Fields Mapping

Map UI fields to `api-config.yaml` paths:

| Section | Subsection | Field | YAML Path | Type | Default | Constraints |
|---------|-----------|-------|-----------|------|---------|-------------|
| **Claim Processing** | Thresholds | High Confidence | `ai.confidence.high_threshold` | number | 0.55 | 0-1 |
| | | Low Confidence | `ai.confidence.low_threshold` | number | 0.35 | 0-1 |
| | | Fraud Risk | `ai.fraud.risk_threshold` | number | 0.1 | 0-1 |
| | | Human Review Amount | `ai.estimate.human_review_threshold` | number | 5000.00 | ≥0 |
| | Agent Toggles | Fraud Detector | `agents.fraud_detector.enabled` | boolean | true | - |
| | | Risk Estimator | `agents.risk_estimator.enabled` | boolean | true | - |
| | | AI Image Detector | `agents.ai_image_detector.enabled` | boolean | true | - |
| | | Damage Analyzer | `agents.damage_analyzer.enabled` | boolean | true | - |
| | | Enhance All | `agents.damage_analyzer.enhance_all_damages` | boolean | true | - |
| | | Chatbot | `agents.chatbot.enabled` | boolean | true | - |
| | Fraud Detection | High Risk Threshold | `agents.fraud_detector.high_risk_threshold` | number | 0.7 | 0-1 |
| | | Medium Risk Threshold | `agents.fraud_detector.medium_risk_threshold` | number | 0.4 | 0-1 |
| | | Color Verification | `agents.fraud_detector.phase1_vision.color_verification.enabled` | boolean | true | - |
| | | Make/Model Verification | `agents.fraud_detector.phase1_vision.make_model_verification.enabled` | boolean | true | - |
| | | AI Image Detection | `agents.fraud_detector.phase1_vision.ai_generated_detection.enabled` | boolean | true | - |
| | | Manipulation Detection | `agents.fraud_detector.phase1_vision.manipulation_detection.enabled` | boolean | true | - |
| **Technical Parameters** | LLM | Default Provider | `llm.default_provider` | select | bedrock | anthropic, openai, bedrock |
| | | Default Vision Model | `llm.default_vision_model` | select | bedrock | anthropic, openai, bedrock |
| | | Timeout (s) | `llm.providers.bedrock.timeout_s` | number | 60 | 1-600 |
| | | Max Tokens | `llm.providers.bedrock.max_tokens` | number | 4096 | 1-100000 |
| | | Temperature | `llm.providers.bedrock.temperature` | number | 0.2 | 0-2 |
| | Bedrock | AWS Region | `llm.providers.bedrock.aws_region` | text | us-east-1 | - |
| | | Default Model | `llm.providers.bedrock.default_model` | select | claude-3-5-sonnet-v2 | See available models |
| | Database | Pool Size | `database.pool_size` | number | 5 | 1-100 |
| | | Max Overflow | `database.max_overflow` | number | 10 | 0-100 |
| | | Echo SQL | `database.echo` | boolean | false | - |
| | Storage | Images Folder | `storage.images_root_folder` | text | uploads | - |
| | | Max Upload Size (MB) | `storage.max_upload_size_mb` | number | 10 | 1-100 |
| | | Max Images Per Claim | `storage.max_images_per_claim` | number | 20 | 1-100 |
| | API | Debug Mode | `api.debug` | boolean | true | - |
| | | Host | `api.host` | text | 0.0.0.0 | - |
| | | Port | `api.port` | number | 8000 | 1-65535 |

### 5.2 Non-Editable Fields

These fields are **read-only** in the UI (displayed but not editable):

- `api.title`, `api.version`
- `database.url` (sensitive - show masked version)
- All provider `api_key_env` fields (security)
- `logging.*` (managed separately)
- `cors.*` (security concern)

### 5.3 Validation Rules

**Client-Side Validation:**
- Number fields: Check min/max ranges, validate numeric input
- Threshold fields: Ensure `low_threshold < high_threshold`
- Required fields: Check presence before save
- Real-time feedback: Show error messages below fields

**Server-Side Validation:**
- Type checking: Enforce types from schema
- Range validation: Reject out-of-bounds values
- Consistency checks: Ensure logical relationships (e.g., pool_size ≤ pool_size + max_overflow)
- YAML validation: Ensure parseable YAML structure

---

## 6. State Management

### 6.1 Configuration State

```jsx
const [config, setConfig] = useState(null);        // Current config from API
const [editedConfig, setEditedConfig] = useState(null);  // User edits (unsaved)
const [errors, setErrors] = useState({});          // Validation errors
const [loading, setLoading] = useState(true);      // Loading state
const [saving, setSaving] = useState(false);       // Save in progress
const [isDirty, setIsDirty] = useState(false);     // Unsaved changes flag
```

### 6.2 State Flow

```
1. Page Load:
   - loadConfig() → GET /api/v1/admin/config
   - setConfig(response.config)
   - setEditedConfig(deepClone(response.config))
   - setLoading(false)

2. User Edits Field:
   - handleFieldChange(path, value)
   - updateNestedValue(editedConfig, path, value)
   - validateField(path, value) → update errors
   - setIsDirty(true)

3. User Clicks Save:
   - validateAll() → check all errors
   - if valid: saveConfig() → POST /api/v1/admin/config
   - Show success modal with restart instructions
   - setConfig(editedConfig)  // Sync state
   - setIsDirty(false)

4. User Clicks Reset:
   - setEditedConfig(deepClone(config))  // Discard edits
   - setErrors({})
   - setIsDirty(false)
```

---

## 7. Portal Configuration File

**File:** `src/ui/admin/public/admin-portal-config.yaml`

```yaml
# Admin Portal Configuration
# This file is loaded by the frontend (not the backend API)

api:
  base_url: "http://localhost:8000/api/v1"
  timeout: 30000  # 30 seconds

auth:
  # No authentication required for prototype
  require_login: false
  default_admin_id: "admin_001"

portal_links:
  customer_portal_url: "http://localhost:5173"
  adjustor_portal_url: "http://localhost:5174"
  executive_portal_url: null  # Not implemented yet

features:
  enable_backup_restore: true
  enable_validation_preview: false  # Future feature
  enable_auto_restart: false  # Future feature
```

---

## 8. User Workflows

### 8.1 Adjust Fraud Detection Threshold

**Scenario:** Admin wants to reduce false positives by increasing fraud risk threshold from 0.1 to 0.15

**Steps:**
1. Navigate to **Dashboard** (auto-redirect from login)
2. Expand **Section 1: Claim Processing Rules**
3. Find **Subsection: Confidence & Thresholds**
4. Change **Fraud Risk Threshold** from `0.1` to `0.15`
5. UI shows validation success (green checkmark)
6. Click **[Save]** button
7. Confirm in modal: **[Save & Show Restart Instructions]**
8. API saves config + creates backup
9. Modal shows restart instructions
10. Admin restarts API server manually: `Ctrl+C` → `make run-api`
11. Changes take effect

---

### 8.2 Enable/Disable Agent

**Scenario:** Admin wants to temporarily disable Damage Analyzer for testing

**Steps:**
1. Navigate to **Dashboard**
2. Expand **Section 1: Claim Processing Rules**
3. Find **Subsection: Agent Toggles**
4. Uncheck **☑ Enable Damage Analyzer**
5. Click **[Save]**
6. Confirm and restart API
7. Damage Analyzer no longer runs on new claims

---

### 8.3 Restore From Backup

**Scenario:** Admin made a mistake and wants to restore previous config

**Steps:**
1. Navigate to **Dashboard**
2. Click **[Backup History]** button
3. Modal shows list of backups:
   - `api-config.2026-05-07-14-30-45.bak` (Today at 2:30 PM)
   - `api-config.2026-05-06-10-15-22.bak` (Yesterday at 10:15 AM)
4. Click **[Restore]** on desired backup
5. Confirm: "Restore `api-config.2026-05-07-14-30-45.bak`?"
6. API restores config (current config is backed up first)
7. Page reloads to show restored config
8. Admin restarts API server

---

### 8.4 Launch Adjustor Portal

**Scenario:** Admin wants to quickly test adjustor workflow

**Steps:**
1. Navigate to **Dashboard**
2. In **Quick Access Panel** (right sidebar)
3. Click **[👤 Adjustor Portal]** button
4. New window opens: `http://localhost:5174`
5. Adjustor login page loads in separate window
6. Admin can test adjustor workflow while keeping config editor open

---

## 9. Error Handling

### 9.1 Configuration Load Failure

**Trigger:** GET `/api/v1/admin/config` fails (API down, network error)

**UI Response:**
- Show error card in place of config editor:
  ```
  ⚠️ Failed to Load Configuration
  
  Could not connect to API server. Please check:
  - API server is running (make run-api)
  - API URL is correct in admin-portal-config.yaml
  
  [Retry]
  ```
- Disable Quick Access Panel (grayed out)

---

### 9.2 Configuration Save Failure

**Trigger:** POST `/api/v1/admin/config` fails (validation error, permission denied, API error)

**UI Response:**
- Show error alert above config editor:
  ```
  ❌ Failed to Save Configuration
  
  <error message from API>
  ```
- Highlight fields with validation errors (red border + error text)
- Keep modal open so user can fix errors
- Do NOT close modal or reload page

---

### 9.3 Validation Errors

**Trigger:** User enters invalid value (e.g., threshold > 1.0)

**UI Response:**
- Real-time validation on field blur
- Show error message below field (red text):
  ```
  High Confidence Threshold [1.5]
  ❌ Must be between 0 and 1
  ```
- Disable [Save] button until all errors resolved
- On save attempt: Scroll to first error field

---

## 10. Styling & Design System

### 10.1 Color Palette (Tailwind)

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',  // Base blue
          600: '#2563eb',  // Primary button
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        // Reuse success, warning, error, info from customer portal
      }
    }
  }
}
```

### 10.2 Component Styles

**Buttons:**
- Primary: `bg-primary-600 hover:bg-primary-700 text-white`
- Secondary: `bg-gray-200 hover:bg-gray-300 text-gray-900`
- Ghost: `bg-transparent hover:bg-gray-100 text-gray-700`

**Cards:**
- ConfigSection: `bg-white rounded-lg shadow-sm border border-gray-200 p-6`
- Expanded state: Add `ring-2 ring-primary-200` for focus

**Form Fields:**
- Input: `border-gray-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200`
- Error state: `border-red-500 focus:border-red-500 focus:ring-red-200`

**Quick Access Panel:**
- Background: `bg-gray-50`
- Border: `border-l border-gray-200`
- Buttons: Full-width, stacked with 4px gap

### 10.3 Typography

- **Page Title:** `text-3xl font-bold text-gray-900`
- **Section Title:** `text-xl font-semibold text-gray-800`
- **Field Label:** `text-sm font-medium text-gray-700`
- **Description:** `text-sm text-gray-600`
- **Example:** `text-xs italic text-gray-500`
- **Error:** `text-sm text-red-600`

---

## 11. Responsive Design

### 11.1 Breakpoints

- **Desktop (1440px+):** Default 80/20 layout
- **Laptop (1024-1440px):** Same 80/20 layout, slightly narrower
- **Tablet (768-1024px):** Collapse Quick Access Panel below config editor (stacked)
- **Mobile (< 768px):** Single column, collapse all sections by default

### 11.2 Quick Access Panel Behavior

**Desktop:** Fixed right sidebar (20% width)

**Tablet/Mobile:** Move below config editor as full-width section:
```
┌─────────────────────────────────────┐
│  Configuration Editor (100%)        │
├─────────────────────────────────────┤
│  Quick Access (Horizontal Buttons)  │
│  [Customer] [Adjustor] [Executive]  │
└─────────────────────────────────────┘
```

---

## 12. Development Checklist

### Phase 1: Project Setup
- [ ] Create `src/ui/admin/` directory structure
- [ ] Copy `package.json` from customer portal, update name to `@acme/admin-portal`
- [ ] Copy `vite.config.js` and `tailwind.config.js`
- [ ] Install dependencies: `npm install`
- [ ] Create `admin-portal-config.yaml`
- [ ] Set up dev server: `npm run dev` (port 5170)

### Phase 2: Core Components
- [ ] Copy reusable components from customer portal:
  - Button, Card, Input, Textarea, Badge, Modal, Spinner
- [ ] Create `AuthContext.jsx` (no-auth mode)
- [ ] Create API client with `X-Admin-ID` header
- [ ] Create config loader (`api/config.js`)

### Phase 3: Pages
- [ ] LoginPage.jsx (minimal, no password)
- [ ] DashboardPage.jsx (main config editor)
- [ ] NotFoundPage.jsx

### Phase 4: Config Editor Components
- [ ] ConfigSection.jsx (collapsible section)
- [ ] ConfigField.jsx (editable field with validation)
- [ ] PortalLauncher.jsx (quick access panel)

### Phase 5: Backend API
- [ ] Create `/api/v1/admin/config` GET endpoint
- [ ] Create `/api/v1/admin/config` POST endpoint (with backup logic)
- [ ] Create `/api/v1/admin/config/backups` GET endpoint
- [ ] Create `/api/v1/admin/config/restore` POST endpoint
- [ ] Add validation layer for config schema

### Phase 6: State Management & Validation
- [ ] Implement config state management (useState hooks)
- [ ] Real-time field validation
- [ ] Dirty state tracking (unsaved changes)
- [ ] Deep clone utility for config objects

### Phase 7: Modals & Dialogs
- [ ] Save Confirmation Modal
- [ ] Restart Instructions Modal
- [ ] Backup History Modal

### Phase 8: Testing
- [ ] Test config load from API
- [ ] Test config save with validation
- [ ] Test backup creation and restore
- [ ] Test Quick Access Panel (open portals in new windows)
- [ ] Test error handling (API down, validation errors)
- [ ] Test responsive layout (desktop, tablet, mobile)

### Phase 9: Documentation
- [ ] Add README.md in `src/ui/admin/`
- [ ] Document API endpoints in main API docs
- [ ] Update `FILE-MANIFEST.md` with admin portal files

---

## 13. Future Enhancements (Out of Scope)

These features are **not included** in the initial implementation but may be added later:

### 13.1 Live System Monitoring
- Active claims count, API health, queue depth
- Real-time graphs (claims per hour, API response times)
- Log viewer with filtering

### 13.2 Config Change History
- Timeline view of all config changes
- "Who changed what and when" tracking
- Diff view between versions

### 13.3 Preview Mode
- Test config changes on a single claim before rollout
- Impact analysis: "This will affect 23 pending claims"
- Dry-run mode

### 13.4 Auto-Restart API
- [Restart Automatically] button in save modal
- POST `/api/v1/admin/restart` endpoint
- Supervisor/systemd integration for graceful restart

### 13.5 Role-Based Access Control
- Multiple admin roles (viewer, editor, super-admin)
- Permission-based field visibility
- Audit log of admin actions

### 13.6 SOP Document Editor
- Edit `policies/damage_triage.md` from UI
- Syntax highlighting for markdown
- Version control for policy documents

### 13.7 Rules Engine Editor
- Visual editor for `policies/rules.yaml`
- Drag-and-drop rule builder
- Rule testing/validation

---

## 14. Open Questions & Decisions

### Q1: Should we allow editing the database connection string?
**Decision:** No. Keep `database.url` read-only (security risk). Show masked version: `sqlanywhere://****@localhost:2638/insurance_db`

### Q2: How to handle concurrent edits (multiple admins)?
**Decision:** Not addressed in prototype. Future: Add optimistic locking or last-write-wins with warning.

### Q3: Should Quick Access Panel remember last opened portal?
**Decision:** No state persistence. Each click opens a fresh window.

### Q4: Validation strictness - should we allow "dangerous" values (e.g., threshold = 1.0)?
**Decision:** Allow with warnings. Show yellow warning icon + tooltip: "⚠️ This value may cause unexpected behavior."

### Q5: How to test config changes without affecting production?
**Decision:** Out of scope for prototype. Future: Add "test mode" that processes a single claim with new config.

---

## 15. Design Principles

1. **Simplicity First:** No authentication, no complex workflows, no bells and whistles
2. **Safety Nets:** Always create backups, validate before saving, clear restart instructions
3. **Consistency:** Follow customer/adjustor portal patterns (components, API client, routing)
4. **Separation of Concerns:** Admin portal is independent (not integrated into customer/adjustor)
5. **Prototype Mentality:** Built for demo purposes, not production-ready
6. **User Empowerment:** Make it easy for admins to tweak rules and see results quickly

---

## 16. Summary

The Admin Portal is a **configuration-first** UI that provides:
- ✅ Simple, no-auth access for demo environments
- ✅ Organized config editor with validation
- ✅ Automatic backups before changes
- ✅ Quick access to other portals (customer, adjustor)
- ✅ Clear instructions for restarting API
- ❌ No live monitoring, history viewer, or advanced features (kept simple per user preference)

**Tech Stack:** Vite + React 18, Tailwind CSS v3, Axios, React Router v7

**Key Files:**
- UI: `src/ui/admin/` (separate React app)
- Config: `admin-portal-config.yaml` (portal settings)
- API: `/api/v1/admin/*` (config management endpoints)
- Backend: `api-config.yaml` (system configuration)

**Next Steps:**
1. Create project structure (`src/ui/admin/`)
2. Implement backend API endpoints (`/api/v1/admin/config`)
3. Build config editor UI with validation
4. Test end-to-end workflow (edit → save → backup → restart)

---

## 18. Enhanced UI Design - Business Rules Configuration

### 18.1 Overview

Replace the JSON textarea editor with structured form components for better user experience. This section defines the UI components, layout, and interactions for editing business rules configuration.

**Design Goals:**
- Intuitive form fields for each configuration parameter
- Real-time validation with inline error messages
- Field descriptions and examples for guidance
- Responsive layout that works on desktop and tablet
- Preserve changes on navigation (dirty state)

---

### 18.2 Layout Structure - Enhanced Dashboard

```
┌──────────────────────────────────────────────────────────────────────┐
│  ACME Claims : Admin Portal                         Admin: admin_001  │
│  Manage the (a) Business rules applied to the AI Agents              │
│  (b) Technical parameters such as Vision models, Model providers etc. │
├───────────────────────────────────────┬──────────────────────────────┤
│                                       │  Quick Access                │
│  [Save] [Reset] [Backup History]     │                              │
│  ⚠ Unsaved changes                    │  🌐 [Customer Portal]        │
│                                       │  👤 [Adjustor Portal]        │
│  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │  📊 [Executive Portal]       │
│  ┃ Section 1: Business Rules     ┃ │      (Coming Soon)           │
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ │                              │
│  ┌─ Confidence Thresholds ──────┐   │  Opens portals in new window │
│  │                               │   │                              │
│  │ High Confidence Threshold     │   │                              │
│  │ ┌─────────────────────────┐   │   │                              │
│  │ │ 0.55  [━━━━━●━━━━━━] 1.0 │   │   │                              │
│  │ └─────────────────────────┘   │   │                              │
│  │ Minimum confidence to auto-   │   │                              │
│  │ present estimate to customer  │   │                              │
│  │ Example: 0.55 = 55%          │   │                              │
│  │                               │   │                              │
│  │ Low Confidence Threshold      │   │                              │
│  │ ┌─────────────────────────┐   │   │                              │
│  │ │ 0.35  [━━━●━━━━━━━━━] 1.0 │   │   │                              │
│  │ └─────────────────────────┘   │   │                              │
│  │ Below this, route to          │   │                              │
│  │ traditional claim process     │   │                              │
│  │                               │   │                              │
│  │ ✓ low_threshold < high_threshold │                              │
│  └───────────────────────────────┘   │                              │
│                                       │                              │
│  ┌─ Fraud Detection ────────────┐   │                              │
│  │                               │   │                              │
│  │ Fraud Risk Threshold          │   │                              │
│  │ ┌─────────────────────────┐   │   │                              │
│  │ │ 0.1   [●━━━━━━━━━━━━] 1.0 │   │   │                              │
│  │ └─────────────────────────┘   │   │                              │
│  │                               │   │                              │
│  │ ☑ Enable Fraud Detector       │   │                              │
│  │ ☑ Color Verification          │   │                              │
│  │ ☑ Make/Model Verification     │   │                              │
│  │ ☑ AI Image Detection          │   │                              │
│  └───────────────────────────────┘   │                              │
│                                       │                              │
│  ┌─ Agent Settings ─────────────┐   │                              │
│  │                               │   │                              │
│  │ ☑ Risk Estimator              │   │                              │
│  │ ☑ Damage Analyzer             │   │                              │
│  │ ☑ Chatbot                     │   │                              │
│  └───────────────────────────────┘   │                              │
└───────────────────────────────────────┴──────────────────────────────┘
```

---

### 18.3 Component Specifications

#### 18.3.1 ConfigSection Component (Enhanced)

**Purpose:** Collapsible section wrapper with expand/collapse functionality

**Component File:** `src/components/config/ConfigSection.jsx`

**Props:**
```jsx
<ConfigSection
  title="Business Rules"
  description="Configure thresholds and policies for automated claim processing"
  icon={<Settings className="h-5 w-5" />}
  defaultExpanded={true}
  collapsible={true}
>
  {children}
</ConfigSection>
```

**UI Features:**
- Clickable header to toggle expand/collapse
- Icon on left, title + description
- Chevron icon (down/up) on right
- Smooth animation (max-height transition)
- Card styling with border and shadow
- Expanded state persisted to localStorage

**Visual States:**
- **Collapsed:** Title + icon only, height ~60px
- **Expanded:** Full content visible, animated expansion
- **Hover:** Slight background color change on header

**Implementation Notes:**
```jsx
const [isExpanded, setIsExpanded] = useState(defaultExpanded);

// Persist state to localStorage
useEffect(() => {
  const key = `config-section-${title.toLowerCase().replace(/\s+/g, '-')}`;
  const saved = localStorage.getItem(key);
  if (saved !== null) {
    setIsExpanded(JSON.parse(saved));
  }
}, []);

const toggleExpanded = () => {
  const newState = !isExpanded;
  setIsExpanded(newState);
  localStorage.setItem(key, JSON.stringify(newState));
};
```

---

#### 18.3.2 ConfigField Component - Number Input with Slider

**Purpose:** Edit numeric fields with range validation and visual slider

**Component File:** `src/components/config/ConfigField.jsx`

**Props:**
```jsx
<ConfigField
  label="High Confidence Threshold"
  path="ai.confidence.high_threshold"
  value={0.55}
  type="number-slider"
  min={0}
  max={1}
  step={0.05}
  description="Minimum confidence to auto-present estimate to customer"
  example="0.55 means 55% confidence"
  onChange={handleChange}
  error={errors['ai.confidence.high_threshold']}
  required={true}
/>
```

**UI Layout:**
```
┌─────────────────────────────────────────────┐
│ High Confidence Threshold *                 │
│                                             │
│ 0.55  [━━━━━●━━━━━━━━━━] 1.0              │
│       Input   Slider      Max              │
│                                             │
│ Minimum confidence to auto-present          │
│ estimate to customer                        │
│ Example: 0.55 means 55% confidence          │
│                                             │
│ ✗ Must be between 0 and 1                   │ (if error)
└─────────────────────────────────────────────┘
```

**Features:**
- Number input on left (editable)
- Range slider in middle (draggable)
- Min/max labels on ends
- Synchronized input ↔ slider
- Real-time validation
- Red border + error message on invalid

**Validation Logic:**
```jsx
const validateValue = (val) => {
  if (val < min || val > max) {
    return `Must be between ${min} and ${max}`;
  }
  return null;
};

const handleInputChange = (e) => {
  const val = parseFloat(e.target.value);
  if (!isNaN(val)) {
    const error = validateValue(val);
    onChange(path, val, error);
  }
};
```

---

#### 18.3.3 ConfigField Component - Checkbox Toggle

**Purpose:** Enable/disable boolean options with toggle switch

**Component File:** `src/components/config/ConfigField.jsx`

**Props:**
```jsx
<ConfigField
  label="Enable Fraud Detector"
  path="agents.fraud_detector.enabled"
  value={true}
  type="checkbox"
  description="Run fraud detection on all claims"
  onChange={handleChange}
/>
```

**UI Layout:**
```
┌─────────────────────────────────────────────┐
│ ☑ Enable Fraud Detector                     │
│                                             │
│ Run fraud detection on all claims           │
└─────────────────────────────────────────────┘
```

**Features:**
- Checkbox styled as toggle switch (modern UI)
- Label clickable (toggles checkbox)
- Description below in gray text
- Green checkmark when enabled
- Smooth toggle animation

**Toggle Switch Styling:**
```css
/* Enabled: bg-primary-600 */
/* Disabled: bg-gray-300 */
/* Circle slides left/right with transition */
```

---

#### 18.3.4 ConfigField Component - Select Dropdown

**Purpose:** Choose from predefined options

**Component File:** `src/components/config/ConfigField.jsx`

**Props:**
```jsx
<ConfigField
  label="Default LLM Provider"
  path="llm.default_provider"
  value="bedrock"
  type="select"
  options={[
    { value: 'anthropic', label: 'Anthropic' },
    { value: 'openai', label: 'OpenAI' },
    { value: 'bedrock', label: 'AWS Bedrock' }
  ]}
  description="LLM provider for AI operations"
  onChange={handleChange}
  required={true}
/>
```

**UI Layout:**
```
┌─────────────────────────────────────────────┐
│ Default LLM Provider *                      │
│                                             │
│ ┌───────────────────────────────────┐ ▼    │
│ │ AWS Bedrock                       │      │
│ └───────────────────────────────────┘      │
│                                             │
│ LLM provider for AI operations              │
└─────────────────────────────────────────────┘
```

**Features:**
- Native `<select>` element (or custom dropdown)
- Styled with Tailwind
- Placeholder option if not required
- Validation on change

---

#### 18.3.5 Subsection Grouping

**Purpose:** Group related fields within a ConfigSection

**Component File:** `src/components/config/ConfigSubsection.jsx`

**Props:**
```jsx
<ConfigSubsection title="Confidence Thresholds">
  <ConfigField ... />
  <ConfigField ... />
</ConfigSubsection>
```

**UI Layout:**
```
┌─ Confidence Thresholds ─────────────────────┐
│                                             │
│ [Field 1]                                   │
│ [Field 2]                                   │
│ [Field 3]                                   │
│                                             │
└─────────────────────────────────────────────┘
```

**Features:**
- Subtle border + padding
- Title in bold, slightly larger font
- Light background color to distinguish from main section
- Spacing between fields

---

### 18.4 Business Rules Fields Layout

#### Section 1: Business Rules

**Subsection 1.1: Confidence Thresholds**

| Field | Type | Component | Validation |
|-------|------|-----------|------------|
| High Confidence Threshold | number-slider (0-1, step 0.05) | ConfigField | 0 ≤ value ≤ 1, value > low |
| Low Confidence Threshold | number-slider (0-1, step 0.05) | ConfigField | 0 ≤ value ≤ 1, value < high |
| Fraud Risk Threshold | number-slider (0-1, step 0.05) | ConfigField | 0 ≤ value ≤ 1 |
| Human Review Amount | number-input ($, step 100) | ConfigField | value ≥ 0 |

**Subsection 1.2: Agent Toggles**

| Field | Type | Component |
|-------|------|-----------|
| Enable Fraud Detector | checkbox | ConfigField |
| Enable Risk Estimator | checkbox | ConfigField |
| Enable AI Image Detector | checkbox | ConfigField |
| Enable Damage Analyzer | checkbox | ConfigField |
| Enhance All Damages | checkbox | ConfigField |
| Enable Chatbot | checkbox | ConfigField |

**Subsection 1.3: Fraud Detection Settings**

| Field | Type | Component | Validation |
|-------|------|-----------|------------|
| High Risk Threshold | number-slider (0-1, step 0.05) | ConfigField | 0 ≤ value ≤ 1, value > medium |
| Medium Risk Threshold | number-slider (0-1, step 0.05) | ConfigField | 0 ≤ value ≤ 1, value < high |
| Color Verification | checkbox | ConfigField | - |
| Make/Model Verification | checkbox | ConfigField | - |
| AI Image Detection | checkbox | ConfigField | - |
| Manipulation Detection | checkbox | ConfigField | - |

---

### 18.5 Validation and Error Handling

#### Real-Time Validation

**When to Validate:**
- On field blur (user leaves field)
- On slider drag end
- Before save (all fields)

**Validation Rules:**
```javascript
// Example: High Confidence Threshold
const validate = (value, config) => {
  // Range check
  if (value < 0 || value > 1) {
    return "Must be between 0 and 1";
  }
  
  // Consistency check
  const lowThreshold = getNestedValue(config, 'ai.confidence.low_threshold');
  if (lowThreshold && value <= lowThreshold) {
    return "Must be greater than low threshold";
  }
  
  return null; // Valid
};
```

**Error Display:**
- Red border on input/slider
- Red error icon (⚠️) next to label
- Error message below field in red text
- Save button disabled if any errors

#### Consistency Validation

**Cross-Field Validation:**
- `low_threshold < high_threshold` (AI confidence)
- `medium_risk < high_risk` (Fraud detection)
- Validate when either field changes

**UI Feedback:**
```
High Confidence Threshold
┌─────────────────────────┐
│ 0.30  [━━●━━━━━━━━━] 1.0 │
└─────────────────────────┘
⚠ Must be greater than low threshold (0.35)
```

---

### 18.6 Save Workflow with Enhanced UI

**Save Button States:**
1. **Disabled (gray):** No changes or validation errors
2. **Enabled (blue):** Changes present, no errors
3. **Loading (blue + spinner):** Saving in progress
4. **Success (green flash):** Save successful

**Save Flow:**
1. User clicks **[Save Configuration]**
2. Validate all fields
3. If errors: Scroll to first error, highlight field
4. If valid: Show confirmation modal (optional)
5. POST to API
6. On success: Show success message + backup filename
7. On error: Show error message (validation or network)

**Success Message:**
```
┌─────────────────────────────────────────────┐
│ ✓ Configuration Saved Successfully          │
│                                             │
│ Backup created: api-config.2026-05-07...bak│
│                                             │
│ ⚠ Restart API server for changes to apply   │
│   Command: make dev                         │
└─────────────────────────────────────────────┘
```

---

### 18.7 Responsive Design

**Desktop (1440px+):**
- 80/20 layout (config editor / portal launcher)
- Full slider widths
- 2-column layout for checkbox groups

**Tablet (768-1024px):**
- Portal launcher moves below config editor
- Single column layout
- Sliders stack vertically

**Mobile (< 768px):**
- All sections collapsed by default
- Single column
- Touch-friendly slider handles
- Larger tap targets (48px minimum)

---

### 18.8 Accessibility

**Keyboard Navigation:**
- Tab through fields in logical order
- Enter to toggle checkboxes
- Arrow keys to adjust sliders
- Esc to cancel edits (reset)

**Screen Readers:**
- ARIA labels on all inputs
- Error announcements (aria-live)
- Field descriptions read aloud
- Section expand/collapse announced

**Visual Aids:**
- Focus rings on interactive elements
- High contrast error states
- Clear labels and descriptions
- Consistent spacing

---

### 18.9 Implementation Approach

**Phase 1: Core Components**
1. Create ConfigField with number-slider variant
2. Create ConfigField with checkbox variant
3. Create ConfigField with select variant
4. Create ConfigSubsection wrapper

**Phase 2: Business Rules Section**
1. Replace JSON editor with ConfigSection
2. Add Confidence Thresholds subsection
3. Add Agent Toggles subsection
4. Add Fraud Detection subsection
5. Wire up onChange handlers

**Phase 3: Validation**
1. Implement real-time validation
2. Add consistency checks
3. Display inline errors
4. Disable save button on errors

**Phase 4: Polish**
1. Add smooth transitions
2. Implement responsive layout
3. Add keyboard navigation
4. Test accessibility

---

## 17. TODOs

### Immediate (Pre-Implementation)
1. [x] Review and approve design document with stakeholders ✅
2. [x] Confirm editable vs. read-only fields list ✅
3. [x] Verify API port assignments (5170 for admin portal) ✅
4. [x] Decide on backup retention policy (keep all backups indefinitely) ✅

### Backend Implementation

**📋 IMPORTANT - API DESIGN REFERENCE:**

All backend API design details, specifications, validation rules, request/response schemas, and implementation guidelines are documented in:

**👉 [API-BACKEND-DESIGN.md - Section 17: Admin Portal API Endpoints](./API-BACKEND-DESIGN.md#17-admin-portal-api-endpoints)**

**Implementation MUST follow the specifications in API-BACKEND-DESIGN.md, including:**
- Endpoint contracts (request/response formats)
- Validation rules and error messages
- Security considerations (path traversal protection, credential masking)
- Pydantic schemas and utility functions
- Backup file naming conventions

Do NOT implement based solely on this document - refer to API-BACKEND-DESIGN.md for authoritative specifications.

---

5. [x] Create `src/api/routers/admin.py` router (see API-BACKEND-DESIGN.md Section 17.2) ✅
6. [x] Implement `GET /api/v1/admin/config` endpoint (Section 17.2.1) ✅
7. [x] Implement `POST /api/v1/admin/config` endpoint with validation (Section 17.2.2) ✅
8. [x] Implement `GET /api/v1/admin/config/backups` endpoint (Section 17.2.3) ✅
9. [x] Implement `POST /api/v1/admin/config/restore` endpoint (Section 17.2.4) ✅
10. [x] Add config validation utility `src/api/utils/config_validator.py` (Section 17.3.3) ✅
11. [x] Add backup creation logic with timestamp format (Section 17.2.2) ✅
12. [x] Register admin router in `src/api/main.py` (Section 17.5) ✅
13. [x] Create Pydantic models in `src/api/schemas/admin.py` (Section 17.4) ✅
14. [x] Test all endpoints with curl/Postman (test script created: test_admin_api.py) ✅
15. [x] Add error handling for file I/O operations ✅

### Frontend Implementation
16. [x] Create `src/ui/admin/` directory structure ✅
17. [x] Set up package.json with dependencies ✅
18. [x] Configure Vite (port 5170) and Tailwind CSS ✅
19. [x] Create `public/admin-portal-config.yaml` ✅
20. [x] Copy reusable components from customer portal ✅
21. [x] Implement AuthContext (no-auth mode) ✅
22. [x] Implement API client with X-Admin-ID header ✅
23. [x] Implement config loader (`api/config.js`) ✅
24. [x] Create routing structure (App.jsx, routes) ✅
25. [x] Build LoginPage component ✅
26. [ ] Build ConfigSection component (collapsible) - MVP: JSON editor used instead
27. [ ] Build ConfigField component (all input types) - MVP: JSON editor used instead
28. [x] Build PortalLauncher component (sidebar) ✅
29. [x] Build DashboardPage with state management (MVP version with JSON editor) ✅
30. [ ] Implement Section 1: Claim Processing Rules UI - MVP: JSON editor
31. [ ] Implement Section 2: Technical Parameters UI - MVP: JSON editor
32. [ ] Build Save Confirmation Modal - Not needed in MVP
33. [ ] Build Restart Instructions Modal - Inline message used
34. [ ] Build Backup History Modal - Not implemented yet
35. [x] Implement client-side validation logic (JSON validation + server-side) ✅
36. [x] Implement error handling and display ✅
37. [x] Add loading states and spinners ✅
38. [x] Add dirty state indicator (unsaved changes) ✅
39. [x] Implement responsive layout (desktop/tablet/mobile) - Basic ✅
40. [x] Apply Tailwind styling and polish ✅

### Testing
41. [ ] Test config load from API
42. [ ] Test field editing and validation (all input types)
43. [ ] Test save workflow (validation → modal → backup → restart)
44. [ ] Test backup history modal (list, restore, download)
45. [ ] Test portal launcher (open in new windows)
46. [ ] Test error scenarios (API down, validation errors, network issues)
47. [ ] Test responsive layout on different screen sizes
48. [ ] Test cross-browser compatibility (Chrome, Firefox, Safari)
49. [ ] Test with invalid config data
50. [ ] Test backup restore workflow
51. [ ] Test unsaved changes warning
52. [ ] Verify all 50+ fields map correctly to YAML paths

### Documentation
53. [ ] Create `src/ui/admin/README.md` with setup instructions
54. [ ] Update `specifications/FILE-MANIFEST.md` with new files
55. [ ] Document admin API endpoints in main API documentation
56. [ ] Add admin portal section to main README
57. [ ] Document configuration field mappings
58. [ ] Add troubleshooting guide for common issues
59. [ ] Document backup/restore procedures

### Integration
60. [ ] Add admin portal to Makefile targets
61. [ ] Update `make run-ui` to include admin portal
62. [ ] Test integration with customer portal (port 5173)
63. [ ] Test integration with adjustor portal (port 5174)
64. [ ] Verify all three portals can run simultaneously
65. [ ] Test Quick Access panel links between portals

### Polish & Optimization
66. [ ] Optimize config loading performance
67. [ ] Add debouncing to real-time validation
68. [ ] Implement proper TypeScript types (if converting to TS)
69. [ ] Add accessibility features (ARIA labels, keyboard navigation)
70. [ ] Optimize bundle size
71. [ ] Add analytics/tracking (optional)
72. [ ] Implement undo/redo functionality (optional)

### Future Enhancements (Nice-to-Have)
73. [ ] Add config change history viewer
74. [ ] Implement preview/test mode for config changes
75. [ ] Add automatic API restart capability
76. [ ] Implement role-based access control
77. [ ] Add live system monitoring dashboard
78. [ ] Build visual rules engine editor
79. [ ] Add SOP document editor
80. [ ] Implement config diff viewer
81. [ ] Add export/import config functionality
82. [ ] Add configuration templates/presets

### Deployment
83. [ ] Create production build configuration
84. [ ] Set up environment variables for different environments
85. [ ] Add security headers and CORS configuration
86. [ ] Create deployment documentation
87. [ ] Add health check endpoint
88. [ ] Configure logging and monitoring
89. [ ] Set up CI/CD pipeline (optional)

---

## Enhanced UI Implementation (Business Rules Editor)

### Phase 1: Core Components (90-97)
90. [ ] Create ConfigField component base structure
91. [ ] Implement number-slider variant (with range input + slider)
92. [ ] Implement checkbox toggle variant (switch style)
93. [ ] Implement select dropdown variant
94. [ ] Implement text input variant
95. [ ] Create ConfigSubsection component for grouping
96. [ ] Add field validation logic (validateField function)
97. [ ] Add consistency validation (validateConsistency function)

### Phase 2: Business Rules Section UI (98-105)
98. [ ] Create "Business Rules" ConfigSection component
99. [ ] Add "Confidence Thresholds" subsection with 4 fields:
    - [ ] High Confidence Threshold (number-slider)
    - [ ] Low Confidence Threshold (number-slider)
    - [ ] Fraud Risk Threshold (number-slider)
    - [ ] Human Review Amount (number-input with currency)
100. [ ] Add "Agent Toggles" subsection with 6 checkboxes:
     - [ ] Enable Fraud Detector
     - [ ] Enable Risk Estimator
     - [ ] Enable AI Image Detector
     - [ ] Enable Damage Analyzer
     - [ ] Enhance All Damages
     - [ ] Enable Chatbot
101. [ ] Add "Fraud Detection Settings" subsection with 6 fields:
     - [ ] High Risk Threshold (number-slider)
     - [ ] Medium Risk Threshold (number-slider)
     - [ ] Color Verification (checkbox)
     - [ ] Make/Model Verification (checkbox)
     - [ ] AI Image Detection (checkbox)
     - [ ] Manipulation Detection (checkbox)
102. [ ] Wire up onChange handlers for all fields
103. [ ] Connect field values to editedConfig state
104. [ ] Implement real-time field validation
105. [ ] Add error display for each field

### Phase 3: State Management & Integration (106-111)
106. [ ] Replace JSON textarea with Business Rules section
107. [ ] Add "Show JSON" toggle (keep JSON view as option)
108. [ ] Implement dirty state tracking for form fields
109. [ ] Add unsaved changes warning on navigation
110. [ ] Update save workflow to collect form values
111. [ ] Test round-trip: Load → Edit Form → Save → Reload

### Phase 4: Validation & Error Handling (112-116)
112. [ ] Implement inline error messages (below each field)
113. [ ] Add field-level error icons (⚠️ next to label)
114. [ ] Implement consistency checks (low < high thresholds)
115. [ ] Disable save button when validation errors present
116. [ ] Scroll to first error field on save attempt

### Phase 5: Polish & UX (117-123)
117. [ ] Add smooth expand/collapse animations for sections
118. [ ] Add slider drag visual feedback
119. [ ] Implement responsive layout (desktop/tablet/mobile)
120. [ ] Add keyboard navigation (Tab, Arrow keys, Enter)
121. [ ] Add accessibility attributes (ARIA labels, live regions)
122. [ ] Add field descriptions and examples (hover tooltips)
123. [ ] Persist section expand/collapse state to localStorage

### Phase 6: Testing & Documentation (124-127)
124. [ ] Test all field types (slider, checkbox, select, text)
125. [ ] Test validation (range, consistency, required)
126. [ ] Test responsive layout on different screen sizes
127. [ ] Update ADMIN-FRONTEND-IMPLEMENTATION.md with enhanced UI docs

---

**Document Version:** 1.3  
**Last Updated:** 2026-05-07  
**Status:** ✅ MVP Complete with Demo Scenarios, Enhanced UI Design in Progress

**Changes in v1.3:**
- Added Demo Scenarios component to right sidebar (Section 3.1, 3.3.4)
- Documented three demo scenarios: Happy Path, Customer Appeal, Fraud Detection
- Updated layout diagram to show Demo Scenarios card below Quick Access
- Added scenario details: customer info, vehicles, and flow descriptions
- Updated Portal Launcher section (3.3.3) to reflect new sidebar content

**Changes in v1.2:**
- Added detailed Business Rules UI component specifications (Section 18)
- Added new TODOs for enhanced UI implementation (90-120)
- Defined ConfigField component variants for all field types
- Added form layout and validation specifications

**Changes in v1.1:**
- Moved API specifications to API-BACKEND-DESIGN.md Section 17
- Updated port number from 5175 to 5170
- Completed all Immediate (Pre-Implementation) TODOs
- Added cross-references to backend design document