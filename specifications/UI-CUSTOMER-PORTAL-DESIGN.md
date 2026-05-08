# Customer Portal UI Design Document
## AI-Powered Auto Insurance Claims Management - ACME Insurance

**Version:** 1.1  
**Date:** 2026-05-05  
**Status:** Design Document  
**Target Audience:** Customer Portal Users  
**Company:** ACME Insurance

---

## Table of Contents

1. [Overview](#1-overview)
2. [Implementation Strategy](#2-implementation-strategy)
3. [Design System](#3-design-system)
4. [Technology Stack](#4-technology-stack)
5. [Project Structure](#5-project-structure)
6. [User Flow](#6-user-flow)
7. [Page-by-Page Design](#7-page-by-page-design)
8. [Component Library](#8-component-library)
9. [API Integration](#9-api-integration)
10. [State Management](#10-state-management)
11. [Development Guidelines](#11-development-guidelines)

---

## 1. Overview

### 1.1 Purpose

The Customer Portal is a React-based web application that enables policyholders to:
- View their insurance policies and vehicles
- File new auto damage claims (FNOL - First Notice of Loss)
- Upload damage photos with real-time AI analysis
- Review AI-generated damage assessments with bounding box visualization
- Accept or appeal repair cost estimates
- Track claim status and history

### 1.2 Key Features

- ✅ **AI-Powered Claims**: Upload damage photos, get instant YOLO-based damage detection
- ✅ **Visual Damage Assessment**: View annotated images with bounding boxes and severity ratings
- ✅ **Transparent Pricing**: Detailed cost breakdown with reasoning for each damage
- ✅ **Real-Time Progress**: Progress indicators during image upload and processing
- ✅ **Claim History**: View past claims with full event timeline
- ✅ **Human Review Option**: Appeal AI decisions for human adjustor review

### 1.3 Design Philosophy

Inspired by GEICO's clean, approachable design (see `sample-home-page.png`):
- **Professional**: Insurance industry standards with ACME Insurance branding
- **Friendly**: Approachable mascot-style visuals
- **Transparent**: Clear explanations of AI decisions
- **Efficient**: Minimal clicks to complete tasks
- **Desktop-First**: Optimized for desktop use (mobile support future phase)

### 1.3.2 UX Design Decisions

**Image Upload Thumbnails:**
- Image thumbnails on the upload page (Step 2) should **NOT display damage details or cost information**
- **Rationale**: During the upload phase, customers are still gathering documentation. Showing individual damage costs per image can be confusing and create anxiety before the full assessment is complete
- Thumbnails should show:
  - ✅ Upload status (uploading, analyzing, complete)
  - ✅ Basic analysis completion indicator
  - ✅ Image filename
  - ❌ NO damage type/part names
  - ❌ NO cost estimates
- The complete damage assessment and cost breakdown is presented on the Claim Detail page (Step 3) after all images are analyzed and the estimate is generated
- This approach reduces cognitive load and prevents premature concern about individual damage costs

### 1.3.1 Branding

**Company Name:** ACME Insurance

**Logo:**
- **Source Location:** `src/common/assets/ACME-logo.png`
- **Public Location:** `src/ui/customer/public/ACME-logo.png` (copied for Vite access)
- **Usage:** Display in header navigation (similar to GEICO sample screenshots)
- **Placement:** Top-left corner of header on all pages
- **Size:** 48px height (h-12) in header, 80px height (h-20) on login page, auto width to maintain aspect ratio
- **Link:** Logo is clickable and navigates to home page (`/`) when clicked

### 1.4 Design Reference Screenshots

**IMPORTANT**: Use the screenshots in `specifications/ui-sample-images/` as visual design guides when building the customer portal pages. These screenshots show the actual look and feel to implement:

- **`sample-login-page.png`**: Reference for Login Page design (section 6.1)
  - Clean, centered login form
  - GEICO-style branding and color scheme
  - Professional but approachable aesthetic

- **`sample-home-page.png`**: Reference for Home Page layout (section 6.2)
  - Header navigation structure
  - Policy cards layout and styling
  - Welcome message presentation
  - Overall page composition and spacing

- **`policy-actions-screen.png`**: Reference for Policy Detail Page (section 6.3)
  - Policy information display
  - Action buttons and navigation
  - Card layouts for policy details
  - Claims history presentation

- **`report-claim.png`**: Reference for New Claim Page workflow (section 6.4)
  - Multi-step form design
  - Image upload interface
  - Progress indicators
  - Form field styling and layout

**How to use these screenshots:**
1. Open each screenshot and study the visual design, spacing, colors, and component styles
2. Match the color palette, typography, and component designs shown in the screenshots
3. Maintain consistency with GEICO's brand aesthetic throughout all pages
4. Use the screenshots as the primary visual reference; this document provides the technical implementation details

---

## 2. Implementation Strategy

### 2.1 Implementation Decisions

**Directory Structure:**
- Customer portal will be created in `src/ui/customer/` as specified in section 5

**Backend API:**
- API server is running at `http://localhost:8000/`
- All required endpoints are assumed to be ready and functional
- No backend verification needed before starting UI implementation

**Configuration Management:**
- API base URL will be configurable via `customer-portal-config.yaml`
- Configuration file location: `src/ui/customer/customer-portal-config.yaml`
- Allows easy switching between local, staging, and production environments

**Mock Data:**
- Customer data will be hardcoded for demo purposes
- Fake home insurance policy (POL-Home-1234) will be hardcoded in the UI
- Mock authentication using hardcoded customer ID (100)

**Image Serving:**
- Original images: `/api/v1/customers/{customer_id}/claims/{claim_id}/images/{image_id}`
- Annotated images: `/api/v1/customers/{customer_id}/claims/{claim_id}/images/{image_id}?annotated=yes`
- The backend will serve both original and YOLO-annotated images via the same endpoint using a query parameter

### 2.2 Phased Implementation Approach

**Phase 1: Authentication & Home Page**
- Login page with mock authentication
- Home page with policy overview
- Header and footer components
- Basic routing setup
- API client configuration
- Mock customer data

**Phase 2: Policy Details & Navigation**
- Policy detail page
- Vehicle cards
- Claims history list
- Navigation between pages
- Breadcrumb navigation

**Phase 3: New Claim Workflow (Critical Path)**
- New claim page (Step 1: Loss details form)
- Draft claim creation API integration
- Form validation and error handling
- Progress indicator component

**Phase 4: Image Upload & AI Analysis**
- Image uploader component with drag & drop
- Upload progress tracking
- Real-time damage detection display
- Image thumbnail grid
- Integration with image upload API

**Phase 5: Claim Review & Decision**
- Claim detail page
- Damage cards with bounding box viewer
- Cost breakdown display
- Accept estimate functionality
- Appeal estimate functionality
- Confirmation dialogs

**Phase 6: Polish & Refinement**
- Timeline component for claim history
- Status badges and indicators
- Error handling and loading states
- Responsive design adjustments
- Final UI polish based on screenshots

### 2.3 Configuration File Format

**customer-portal-config.yaml:**
```yaml
api:
  base_url: "http://localhost:8000/api/v1"
  timeout: 30000  # milliseconds
  
mock:
  customer_id: 100
  auth_password: "password123"
  
app:
  name: "Insurance Claims Portal"
  version: "1.0.0"
  
features:
  enable_appeal: true
  max_images_per_claim: 20
  max_image_size_mb: 10
```

---

## 3. Design System

### 2.1 Color Palette

Based on `sample-home-page.png` analysis:

```css
/* Primary Colors */
--primary-blue: #0046BE;           /* GEICO Blue - primary actions */
--primary-blue-hover: #003A9E;     /* Hover state */
--primary-blue-light: #4A7FC8;     /* Accents */

/* Secondary Colors */
--secondary-gray: #F5F5F5;         /* Background */
--secondary-white: #FFFFFF;        /* Cards, containers */
--secondary-light-blue: #E8F2FF;   /* Info backgrounds */

/* Status Colors */
--status-success: #10B981;         /* Approved, paid */
--status-warning: #F59E0B;         /* Pending review */
--status-error: #EF4444;           /* Rejected, appealed */
--status-info: #3B82F6;            /* Processing */

/* Claim Status Display Mapping */
Backend Status → UI Display Label:
- draft → "Draft"
- FNOL → "Submitted"
- image_uploaded → "Images Uploaded"
- loss_estimated_ai → "Loss Estimate Prepared"
- human_review_pending → "Review Pending"
- customer_decision_pending → "Customer decision pending"
- loss_approved → "Approved"
- loss_appealed → "Appealed"
- sent_for_payment → "Payment Processing"
- claim_paid → "Paid"
- routed_to_traditional → "Traditional Processing"
- claim_closed → "Closed"

/* Text Colors */
--text-primary: #1F2937;           /* Headings */
--text-secondary: #6B7280;         /* Body text */
--text-muted: #9CA3AF;             /* Labels, captions */

/* Borders */
--border-light: #E5E7EB;
--border-medium: #D1D5DB;
```

### 2.2 Typography

```css
/* Font Family - Clean Sans-Serif */
--font-primary: 'Inter', 'Avenir', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Font Sizes */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;

/* Line Heights */
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.75;
```

### 2.3 Spacing System

Tailwind-compatible spacing scale:

```
0 = 0
1 = 0.25rem (4px)
2 = 0.5rem (8px)
3 = 0.75rem (12px)
4 = 1rem (16px)
5 = 1.25rem (20px)
6 = 1.5rem (24px)
8 = 2rem (32px)
10 = 2.5rem (40px)
12 = 3rem (48px)
16 = 4rem (64px)
20 = 5rem (80px)
```

### 2.4 Component Styles

**Buttons:**
```css
/* Primary Button */
.btn-primary {
  background: var(--primary-blue);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: var(--primary-blue-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 70, 190, 0.3);
}

/* Secondary Button */
.btn-secondary {
  background: white;
  color: var(--primary-blue);
  border: 2px solid var(--primary-blue);
}
```

**Cards:**
```css
.card {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  border: 1px solid var(--border-light);
}
```

---

## 4. Technology Stack

### 4.1 Frontend Framework

```json
{
  "framework": "React 18.x",
  "language": "JavaScript (ES6+)",
  "styling": "Tailwind CSS 3.x",
  "buildTool": "Vite",
  "packageManager": "npm"
}
```

### 4.2 Core Dependencies

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.0",
    "tailwindcss": "^3.4.0",
    "lucide-react": "^0.300.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32"
  }
}
```

### 4.3 Key Libraries

- **react-router-dom**: Client-side routing
- **axios**: HTTP client for API calls
- **lucide-react**: Icon library (clean, modern icons)
- **tailwindcss**: Utility-first CSS framework

**NO Redux/Zustand** - Use React Context for simple state management

### 4.4 Additional Dependencies

```json
{
  "dependencies": {
    "js-yaml": "^4.1.0"
  }
}
```

- **js-yaml**: For loading and parsing `customer-portal-config.yaml`

---

## 5. Project Structure

```
src/ui/customer/
├── public/
│   ├── favicon.ico
│   └── index.html
├── customer-portal-config.yaml    # Configuration file
│
├── src/
│   ├── api/                      # API client layer
│   │   ├── config.js             # Load customer-portal-config.yaml
│   │   ├── client.js             # Axios instance config
│   │   ├── auth.js               # Mock authentication
│   │   ├── customers.js          # Customer API calls
│   │   ├── claims.js             # Claims API calls
│   │   └── images.js             # Image upload API calls
│   │
│   ├── components/               # Reusable components
│   │   ├── common/
│   │   │   ├── Button.jsx
│   │   │   ├── Card.jsx
│   │   │   ├── Input.jsx
│   │   │   ├── Badge.jsx
│   │   │   ├── ProgressBar.jsx
│   │   │   └── Spinner.jsx
│   │   │
│   │   ├── layout/
│   │   │   ├── Header.jsx
│   │   │   ├── Footer.jsx
│   │   │   └── Layout.jsx
│   │   │
│   │   ├── claims/
│   │   │   ├── ClaimCard.jsx
│   │   │   ├── ClaimTimeline.jsx
│   │   │   ├── DamageCard.jsx
│   │   │   ├── ImageUploader.jsx
│   │   │   └── BoundingBoxViewer.jsx
│   │   │
│   │   └── policies/
│   │       ├── PolicyCard.jsx
│   │       └── VehicleCard.jsx
│   │
│   ├── pages/                    # Page components
│   │   ├── LoginPage.jsx
│   │   ├── HomePage.jsx
│   │   ├── PolicyPage.jsx
│   │   ├── NewClaimPage.jsx
│   │   ├── ClaimAnalysisPage.jsx
│   │   ├── ClaimDetailPage.jsx
│   │   └── ClaimHistoryPage.jsx
│   │
│   ├── context/                  # React Context for state
│   │   ├── AuthContext.jsx
│   │   └── ClaimContext.jsx
│   │
│   ├── hooks/                    # Custom React hooks
│   │   ├── useAuth.js
│   │   ├── useClaims.js
│   │   └── useImageUpload.js
│   │
│   ├── utils/                    # Helper functions
│   │   ├── formatters.js         # Date, currency formatters
│   │   ├── validators.js         # Form validation
│   │   └── constants.js          # App constants
│   │
│   ├── App.jsx                   # Main app component
│   ├── main.jsx                  # Entry point
│   └── index.css                 # Global styles + Tailwind
│
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── README.md
```

---

## 6. User Flow

### 6.1 High-Level User Journey

```
┌─────────────┐
│  Login Page │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Home Page          │
│  - Welcome message  │
│  - Policy list      │
│    • Auto Policy    │
│    • Home Policy    │◀──┐
└──────┬──────────────┘   │
       │                   │
       ▼ (Click Auto)      │
┌─────────────────────┐   │
│  Policy Detail Page │   │
│  - Policy info      │   │
│  - Vehicle list     │   │
│  - Claim history    │   │
│  - [File Claim]     │   │
└──────┬──────────────┘   │
       │                   │
       ▼ (File Claim)      │
┌─────────────────────┐   │
│  New Claim Page     │   │
│  1. Loss details    │   │
│  2. Upload images   │   │
│  3. Review damages  │   │
│  4. Submit claim    │   │
└──────┬──────────────┘   │
       │                   │
       ▼ (Submit)          │
┌─────────────────────┐   │
│  Claim Detail Page  │   │
│  - AI estimate      │   │
│  - Damage reports   │   │
│  - [Accept/Appeal]  │───┘
└─────────────────────┘
```

### 6.2 Detailed Flow: New Claim Process

```
Step 1: Loss Details Form
  ├── Loss event description (textarea)
  ├── Loss event date (date picker)
  ├── Is vehicle drivable? (yes/no radio)
  ├── Do you have damage photos? (yes/no)
  └── [Continue] → Step 2

Step 2: Image Upload with Real-Time Analysis
  ├── Drop zone for images (drag & drop or click)
  ├── For EACH uploaded image:
  │   ├── Upload file with progress bar
  │   ├── Backend automatically runs YOLO detection
  │   ├── Backend creates damage records in database
  │   ├── Frontend waits ~1.5 seconds for analysis
  │   ├── Frontend refetches claim via GET /claims/{id}
  │   ├── Frontend extracts damages from damage_assessment.damages
  │   ├── Filter by image_filename to get this image's damages
  │   └── Display damages under thumbnail (damage_part + cost)
  ├── Show thumbnail grid with:
  │   ├── ✅ Analyzed (with damage list)
  │   ├── 🔄 Analyzing...
  │   └── ⏳ Pending upload
  └── [Continue] → Step 3 (when all images analyzed)

Step 3: Claim Submission & Estimate Aggregation
  ├── Page loads, fetch claim details to check for damages
  ├── Extract unique image_id values from damage_assessment.damages array
  ├── CHECK: Are there any damages detected?
  │   │
  │   ├── NO DAMAGES DETECTED (damages array is empty):
  │   │   ├── DO NOT submit claim to FNOL (keep in draft state)
  │   │   ├── DO NOT call estimate API
  │   │   ├── Show error message: "No damage detected in uploaded images"
  │   │   ├── Explain: AI could not detect damage, may need better photos or human review
  │   │   └── Show two options:
  │   │       ├── [Try New Images] → Navigate back to Image Upload page (Step 2)
  │   │       │   └── Claim remains in draft, user can upload more images
  │   │       └── [Submit for Human Review] → Submit claim + set status = 'human_review_pending'
  │   │           └── Show success: "Claim submitted for human review"
  │   │               └── Navigate to Claim Detail Page
  │   │
  │   └── DAMAGES DETECTED:
  │       ├── Submit claim (draft → FNOL) - NOW that we know there are damages
  │       ├── Call POST /claims/{id}/estimate with claim_id + image_ids
  │       ├── Backend aggregates all damage detections into final estimate
  │       ├── Backend calculates average confidence across all damages
  │       ├── Backend routes based on confidence threshold (0.55):
  │       │   ├── If avg confidence >= 0.55 → status = 'loss_estimated_ai'
  │       │   └── If avg confidence < 0.55 → status = 'human_review_pending'
  │       ├── Show spinner and progress messages
  │       ├── Poll claim status every 2 seconds
  │       ├── Progress indicators:
  │       │   ├── ✅ Images uploaded and analyzed
  │       │   ├── ✅ Damage detection complete
  │       │   ├── 🔄 Aggregating repair costs...
  │       │   └── ⏳ Generating estimate report...
  │       └── When status = 'loss_estimated_ai', 'customer_decision_pending', or 'human_review_pending'
  │            │
  │            ▼ (Auto-redirect)
  │       Redirect to Claim Detail Page

Step 4: Claim Detail Page (Decision)
  ├── Check claim status:
  │   ├── If status = 'human_review_pending':
  │   │   ├── Show yellow banner: "Human Review Required"
  │   │   ├── Explain: Low confidence, adjuster will review
  │   │   ├── Hide Accept/Appeal buttons
  │   │   └── Show AI estimate for reference only
  │   │
  │   ├── If status = 'loss_estimated_ai':
  │   │   ├── NOTE: This is a transient state - AI automatically transitions to customer_decision_pending
  │   │   ├── High-confidence estimates (>= 0.55) auto-transition immediately
  │   │   └── Low-confidence estimates (< 0.55) route to human_review_pending
  │   │
  │   └── If status = 'customer_decision_pending':
  │       ├── AI Estimate shown (aggregated from all images)
  │       ├── Detailed damage breakdown with annotated images
  │       ├── Total cost with reasoning
  │       └── Actions:
  │           ├── [Accept Estimate] → Payment processing
  │           └── [Appeal Estimate] → Human review queue
```

---

## 7. Page-by-Page Design

### 7.1 Login Page

**Route:** `/login`

**Purpose:** Mock authentication to enter the portal

**Layout:**
```
┌─────────────────────────────────────┐
│         Logo (Top Center)           │
│                                     │
│   ┌──────────────────────────┐    │
│   │  Welcome Back            │    │
│   │                          │    │
│   │  Customer Name:          │    │
│   │  [Select customer... ▼]  │    │
│   │                          │    │
│   │  Password:               │    │
│   │  [________________]      │    │
│   │  (fixed: password123)    │    │
│   │                          │    │
│   │  [    Login    ]         │    │
│   └──────────────────────────┘    │
│                                     │
└─────────────────────────────────────┘
```

**Database Seeding Check:**
On component mount, the login page checks if customers exist in the database:
- API Call: `GET /api/v1/customers` returns `{ count: N, has_customers: boolean }`
- If `has_customers === false`:
  - Display warning banner with red background
  - Disable customer dropdown (show message: "No customers available - seed database first")
  - Disable login button
  - Show seeding instructions:
    ```
    ⚠️ Database Not Seeded
    You MUST first seed the database with customer and policy data.
    
    Run this command:
    python scripts/seed-data.py --clean
    
    Once seeded, you can start the API server without the --clean flag to retain the data.
    ```

**Implementation Details:**
- On mount: Check customer count via `GET /api/v1/customers`
- If customers exist: Show mock authentication UI
- Dropdown list of mock customers (similar to adjustor portal pattern)
- Fixed password "password" for all customers
- Store selected customer_id in localStorage
- Redirect to HomePage on success
- If no customers: Show seeding instructions and disable login

**Mock Customer Data:**
```javascript
// Must match customers created by scripts/seed-data.py
const MOCK_CUSTOMERS = [
  { customer_id: 100, name: 'John Doe', email: 'john.doe@example.com' },
  { customer_id: 101, name: 'Jane Smith', email: 'jane.smith@example.com' },
  { customer_id: 102, name: 'Bob Johnson', email: 'bob.johnson@example.com' },
  { customer_id: 103, name: 'Alice Williams', email: 'alice.williams@example.com' },
  { customer_id: 104, name: 'Charlie Brown', email: 'charlie.brown@example.com' }
];
const MOCK_PASSWORD = 'password';
```

**Component Tree:**
```jsx
<LoginPage>
  <Card className="max-w-md mx-auto">
    <h1>Welcome Back</h1>
    <Select label="Customer Name" options={availableCustomers} />
    <Input label="Password" type="password" />
    <Button onClick={handleLogin}>Login</Button>
  </Card>
</LoginPage>
```

---

### 7.2 Home Page

**Route:** `/`

**Purpose:** Welcome page with policy overview

**Layout:**
```
┌─────────────────────────────────────────────────┐
│ Header: Logo | Welcome, Jane! | Menu           │
├─────────────────────────────────────────────────┤
│                                                 │
│  Welcome back, Jane Doe! 👋                    │
│                                                 │
│  Your Policies                                 │
│  ┌────────────────┐  ┌────────────────┐       │
│  │  🏠 Home       │  │  🚗 Auto       │       │
│  │  POL-Home-1234 │  │  PA-992384-01  │       │
│  │  (FAKE)        │  │  Active        │       │
│  │                │  │  [View →]      │       │
│  └────────────────┘  └────────────────┘       │
│                                                 │
│  Pending Actions (if any)                     │
│  ┌───────────────────────────────────────┐    │
│  │ ⚠️  Auto claim #1000                   │    │
│  │     AI estimate completed - Review...  │    │
│  │     [Review Now →]                     │    │
│  └───────────────────────────────────────┘    │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Implementation Details:**
- Fetch customer info: `GET /api/v1/customers/{id}`
- Fetch policies: `GET /api/v1/customers/{id}/policies`
- Display fake home policy (hardcoded, not clickable)
- Display active auto policy (clickable → PolicyPage)
- Check for claims needing action (status = customer_decision_pending)
- **Pending Claims Navigation:**
  - "Review Now" button on pending claims → Navigate to `/claims/{claimId}` (estimate summary with Accept/Appeal)
  - Direct navigation for claims awaiting customer decision

**Component Tree:**
```jsx
<HomePage>
  <Header />
  <WelcomeMessage customer={customer} />
  <div className="grid grid-cols-2 gap-4">
    <PolicyCard type="home" fake={true} />
    <PolicyCard type="auto" policy={autoPolicy} clickable />
  </div>
  {pendingClaims.length > 0 && (
    <AlertBanner claims={pendingClaims} />
  )}
</HomePage>
```

---

### 7.3 Policy Detail Page

**Route:** `/policy/:policyNumber`

**Purpose:** View policy details, vehicles, claim history, and manage policy actions

**Layout:**
```
┌──────────────────────────────────────────────────┐
│ Header: Logo | Welcome, Jane! | Menu            │
├──────────────────────────────────────────────────┤
│ [← Back to Home]                                 │
│                                                  │
│ Auto Policy: PA-992384-01                       │
│                                                  │
│ [Action Required Alert Banner]                  │
│ ┌────────────────────────────────────────────┐  │
│ │ ⚠️  Action Required                        │  │
│ │ You have 1 claim awaiting your decision    │  │
│ │                                            │  │
│ │ ┌────────────────────────────────────┐    │  │
│ │ │ Auto claim #1000                   │    │  │
│ │ │ AI estimate completed - Review...  │    │  │
│ │ │                    [Review Now]    │    │  │
│ │ └────────────────────────────────────┘    │  │
│ └────────────────────────────────────────────┘  │
│                                                  │
│ Quick Actions                                    │
│ ┌────────────────┐ ┌────────────────┐          │
│ │ 📄 File Claim  │ │ 💳 Pay Premium │          │
│ │ (PRIMARY)      │ │                │          │
│ └────────────────┘ └────────────────┘          │
│ ┌────────────────┐ ┌────────────────┐          │
│ │ 🚗 Manage      │ │ 👥 Update      │          │
│ │    Vehicles    │ │    Drivers     │          │
│ └────────────────┘ └────────────────┘          │
│ ┌────────────────┐                              │
│ │ ⚙️  Adjust     │                              │
│ │    Coverage    │                              │
│ └────────────────┘                              │
│                                                  │
│ Policy Information                               │
│ ┌────────────────────────────────────────────┐  │
│ │ Effective: 05/01/2024 - 05/01/2025        │  │
│ │ Premium: $1,200.50/year                    │  │
│ │ Coverage: Liability, Collision, Comp.      │  │
│ │ Bodily Injury: $250k | Property: $100k     │  │
│ │ Deductible: $500                           │  │
│ └────────────────────────────────────────────┘  │
│                                                  │
│ Covered Vehicles                                 │
│ ┌──────────────────────┐                        │
│ │ 🚗 2022 Toyota Camry │                        │
│ │ VIN: 1ABC2345...     │                        │
│ │ Color: Silver        │                        │
│ └──────────────────────┘                        │
│                                                  │
│ Claims History                                   │
│ ┌────────────────────────────────────────────┐  │
│ │ #1000 | 05/03/26 | Paid | $2,500         │  │
│ │ #999  | 03/15/26 | Closed | $1,800       │  │
│ └────────────────────────────────────────────┘  │
│                                                  │
└──────────────────────────────────────────────────┘
```

**Quick Actions Section:**

The Policy Detail Page includes a prominent "Quick Actions" section that allows customers to manage their policy. This section appears immediately after the page title and before policy details.

**Available Actions:**

1. **File a Claim** (Primary Action)
   - Icon: FileText (document icon)
   - Styling: Blue background (primary color) with white text
   - Description: "Report damage and get an instant AI-powered estimate with photo upload"
   - Action: Navigate to `/claims/new?policy={policyNumber}`
   - Rationale: Most critical action, highlighted as primary

2. **Pay Premium & Renewals**
   - Icon: CreditCard
   - Description: "Pay premiums on time to prevent policy cancellation and manage renewals"
   - Action: Navigate to payment management (future implementation)
   - Rationale: Timely payments are essential for maintaining coverage

3. **Add/Remove Vehicles**
   - Icon: Car
   - Description: "Update your policy when replacing or adding vehicles for continuous coverage"
   - Action: Navigate to vehicle management (future implementation)
   - Rationale: Ensures vehicles are properly insured

4. **Update Drivers**
   - Icon: Users
   - Description: "Add all household drivers to your policy to prevent claim issues"
   - Action: Navigate to driver management (future implementation)
   - Rationale: All drivers must be listed to avoid claim denials

5. **Adjust Coverage**
   - Icon: Settings
   - Description: "Change policy limits or add specialized coverage like gap insurance"
   - Action: Navigate to coverage adjustment (future implementation)
   - Rationale: Allows customization of coverage to match needs

**Action Card Design:**
- Responsive grid layout (1 col mobile, 2 col tablet, 3 col desktop)
- Hover effects: lift animation (-translateY) and shadow enhancement
- Primary action: blue background, white text, prominent placement
- Secondary actions: white cards with border, subtle hover states
- Each card includes icon, title, description, and chevron arrow
- Cards are clickable buttons with full accessibility

**Implementation Details:**
- Fetch policy: `GET /api/v1/customers/{id}/policies/{policyNumber}`
- Fetch claims: `GET /api/v1/customers/{id}/claims` (filter by policy_number)
- **Pending Actions Banner:**
  - Appears when any claims have status = `customer_decision_pending`
  - Displays between page title and Quick Actions section
  - Shows count of pending claims
  - Each claim displays as "Auto claim #xxx" with "Review Now" button
  - Banner has yellow/warning styling with AlertCircle icon
- **View Claim Button Behavior:**
  - If claim status = `draft` → Navigate to `/claims/{claimId}/edit` (continue filing claim from NewClaimPage)
  - If claim status = `customer_decision_pending` → Navigate to `/claims/{claimId}` (show estimate summary with Accept/Appeal buttons)
  - If claim status = `loss_estimated_ai`, `human_review_pending`, or any other status → Navigate to `/claims/{claimId}` (view claim detail page)
  - **Rationale:** Claims awaiting customer decision should go directly to the estimate page, not the upload page, to facilitate quick decision-making
  - TODO: Create claim summary view for non-AI statuses (traditional processing, etc.)
- Primary action (File Claim) is fully implemented
- Secondary actions show placeholder alerts (ready for future implementation)

**Component Files:**
- `src/components/policies/PolicyActionCard.jsx` - Reusable action card component
- `src/pages/PolicyPage.jsx` - Policy detail page with actions section

---

### 7.4 New Claim Page

**Route:** `/claims/new`

**Purpose:** File new claim with loss details and image upload

**Layout (Step 1 - Loss Details):**
```
┌──────────────────────────────────────────────────┐
│ File New Claim                                   │
│                                                  │
│ Step 1 of 2: Loss Event Details                 │
│ ━━━━━━━━━━━━━━━━────────────  50%             │
│                                                  │
│ ┌────────────────────────────────────────────┐  │
│ │ Describe what happened:                    │  │
│ │ [________________________________]         │  │
│ │ [________________________________]         │  │
│ │                                            │  │
│ │ When did the damage occur?                 │  │
│ │ [Date Picker: __/__/____]                 │  │
│ │                                            │  │
│ │ Is your vehicle drivable?                  │  │
│ │ ⚪ Yes  ⚫ No                               │  │
│ │                                            │  │
│ │ Do you have photos of the damage?          │  │
│ │ ⚫ Yes  ⚪ No                               │  │
│ │                                            │  │
│ └────────────────────────────────────────────┘  │
│                                                  │
│              [Cancel]  [Save Draft]  [Continue →]│
│                                                  │
└──────────────────────────────────────────────────┘

**Save Draft Button:**
- Available on Loss Details form
- Saves current form data and navigates back to Policy page
- Allows user to resume later from Policy page "View" button
- Claim remains in "draft" status
```

**Layout (Step 2 - Image Upload):**
```
┌──────────────────────────────────────────────────┐
│ File New Claim                                   │
│                                                  │
│ Step 2 of 3: Upload Damage Photos                │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  67%           │
│                                                  │
│ ┌────────────────────────────────────────────┐  │
│ │  📷 Drag & drop images here               │  │
│ │       or click to browse                   │  │
│ │                                            │  │
│ │  Supported: JPG, PNG, HEIC                │  │
│ │  Max size: 10MB per image                 │  │
│ │  Max images: 20                           │  │
│ └────────────────────────────────────────────┘  │
│                                                  │
│ Uploaded Images (2)                              │
│ ┌────────────────┐  ┌────────────────┐         │
│ │  [Thumbnail]   │  │  [Thumbnail]   │         │
│ │  front.jpg     │  │  rear.jpg      │         │
│ │  ✅ Analyzed   │  │  🔄 Analyzing  │         │
│ │  ├─ bumper     │  │                │         │
│ │  │  $1,750     │  │                │         │
│ │  └─ door       │  │                │         │
│ │     $1,500     │  │                │         │
│ └────────────────┘  └────────────────┘         │
│                                                  │
│              [← Back]  [Save Draft]  [Continue →]│
│                                                  │
└──────────────────────────────────────────────────┘

**Save Draft Button:**
- Available on Image Upload page
- Claim already created (in draft state)
- Images already uploaded and analyzed
- Simply navigates back to Policy page
- User can resume later from Policy page "View" button
```

**Implementation Details:**

**Step 1: Create Draft Claim**
```javascript
// POST /api/v1/customers/{id}/claims
const claimData = {
  vin: selectedVehicle.vin,
  policy_number: policy.policy_number,
  fnol_date: today,
  fnol_time: now,
  date_of_damage: form.lossDate,
  is_drivable: form.isDrivable
};
const claim = await createClaim(claimData);
```

**Step 2: Upload Images with Real-Time Analysis**
```javascript
// For each image
for (const file of files) {
  // 1. Upload image
  // POST /api/v1/customers/{id}/claims/{claimId}/images
  const formData = new FormData();
  formData.append('file', file);
  
  await uploadImage(claimId, formData, {
    onUploadProgress: (e) => {
      setProgress((e.loaded / e.total) * 100);
    }
  });
  
  // 2. Backend automatically runs YOLO analysis during upload
  // 3. Backend creates damage records in database
  // 4. Wait for analysis to complete
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  // 5. Refresh claim to get updated damages
  // GET /api/v1/customers/{id}/claims/{claimId}
  const claim = await fetchClaimDetail(customerId, claimId);
  
  // 6. Extract damages for this specific image
  // Note: image_id field contains the filename
  const imageDamages = claim.damage_assessment?.damages.filter(
    d => d.image_id === file.name
  ) || [];
  
  // 7. Display damages under thumbnail
  displayDamages(imageDamages); // Shows damage_part + cost
}

// When user clicks "Continue"
// Navigate to Step 3 (Submission & Estimate Aggregation)
navigate(`/claims/${claimId}/submit`);
```

---

### 7.4.1 Claim Analysis Page (Step 3)

**Route:** `/claims/:claimId/submit`

**Purpose:** Submit claim, generate aggregate estimate, and show processing progress

**IMPORTANT:** Individual images have ALREADY been analyzed in Step 2. This page handles:
1. Claim submission (draft → FNOL)
2. Aggregate estimate generation (combines all individual damage detections)
3. Status polling until estimate is finalized

**Layout (Analyzing):**
```
┌──────────────────────────────────────────────────┐
│ Analyzing Your Claim...                          │
│                                                  │
│ Step 3 of 3: AI Damage Assessment                │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  100%          │
│                                                  │
│ ┌────────────────────────────────────────────┐  │
│ │                                            │  │
│ │            🔄 Processing...                │  │
│ │                                            │  │
│ │   Our AI is analyzing your damage photos   │  │
│ │   and generating a detailed estimate.      │  │
│ │                                            │  │
│ │   This typically takes 10-30 seconds...    │  │
│ │                                            │  │
│ │        [Animated spinner/progress]         │  │
│ │                                            │  │
│ │   ✅ Images uploaded (2)                   │  │
│ │   🔄 Running damage detection...           │  │
│ │   ⏳ Calculating repair costs...           │  │
│ │   ⏳ Generating estimate report...         │  │
│ │                                            │  │
│ └────────────────────────────────────────────┘  │
│                                                  │
└──────────────────────────────────────────────────┘
```

**Implementation Details:**

**When page loads:**
1. Submit the claim (draft → FNOL)
2. Get claim images from claim object
3. Call generateEstimate API to aggregate all damages into final estimate
4. Poll for status = 'loss_estimated_ai' or 'customer_decision_pending'
5. Auto-redirect when complete

**Submit, Generate Estimate, and Poll:**
```javascript
// On page mount
useEffect(() => {
  const submitAndAnalyze = async () => {
    try {
      // 1. Submit the claim (draft -> FNOL)
      await submitClaim(customerId, claimId);
      
      // 2. Get claim details to fetch image IDs
      const claimResponse = await fetchClaimDetail(customerId, claimId);
      const claim = claimResponse.data;
      
      // 3. Get unique image IDs from damages
      // IMPORTANT: Images are NOT stored separately in claim.images
      // They exist as image_id (which is the filename) in each damage record
      let imageIds = [];
      if (claim.damage_assessment?.damages) {
        const ids = claim.damage_assessment.damages
          .map(d => d.image_id)
          .filter(id => id != null && id !== '');
        imageIds = Array.from(new Set(ids));
      }
      
      // 4. Generate aggregate estimate (combines all damage detections)
      // POST /claims/{claimId}/estimate
      await generateEstimate(claimId, {
        claim_id: parseInt(claimId), // Required in request body
        image_ids: imageIds,
        state: 'CA'
      });
      
      // 5. Poll for estimate completion
      const pollInterval = setInterval(async () => {
        const response = await fetchClaimDetail(customerId, claimId);
        const claim = response.data;
        
        // Check if estimate is ready
        if (claim.current_status === 'loss_estimated_ai' || 
            claim.current_status === 'customer_decision_pending') {
          // Estimate complete!
          clearInterval(pollInterval);
          navigate(`/claims/${claimId}`);
        }
      }, 2000); // Poll every 2 seconds
      
    } catch (error) {
      setError('Failed to submit claim');
    }
  };
  
  submitAndAnalyze();
}, [claimId]);
```

**Progress States:**
```javascript
const [analysisSteps, setAnalysisSteps] = useState([
  { label: 'Images uploaded', status: 'completed' },
  { label: 'Running damage detection', status: 'completed' }, // Already done in Step 2!
  { label: 'Aggregating repair costs', status: 'in_progress' },
  { label: 'Generating estimate report', status: 'pending' }
]);

// Note: Damage detection ALREADY happened during image upload (Step 2)
// This page only aggregates the detections into a final estimate

// Update steps based on backend status
// When estimate API called: mark step 3 as in_progress
// When status = loss_estimated_ai: mark all as completed
// Auto-redirect to Claim Detail Page
```

**User Experience:**
- User cannot go back once submission starts
- No cancel button (claim is being processed)
- Automatic redirect to Claim Detail Page when analysis completes
- Show error message if analysis fails (with retry button)

**Component Tree:**
```jsx
<ClaimAnalysisPage>
  <ProgressBar current={3} total={3} />
  <Card className="text-center">
    <Spinner size="lg" />
    <h2>Analyzing Your Claim...</h2>
    <p>Our AI is analyzing your damage photos...</p>
    
    <div className="steps">
      {analysisSteps.map(step => (
        <AnalysisStep
          key={step.label}
          label={step.label}
          status={step.status}
        />
      ))}
    </div>
  </Card>
</ClaimAnalysisPage>
```

---

### 7.5 Claim Detail Page

**Route:** `/claims/:claimId`

**Purpose:** View claim details, AI assessment, and take action

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│ Claim #1000                                         │
│                                                     │
│ Status: Customer decision pending                   │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 60%   │
│ Draft → FNOL → Estimated → [Decision] → Payment   │
│                                                     │
│ AI Damage Assessment                                │
│ ┌─────────────────────────────────────────────┐    │
│ │ Total Estimated Cost: $3,250                │    │
│ │ Damages Detected: 3 damages across 2 images │    │
│ │                                              │    │
│ │ ═══════════════════════════════════════════ │    │
│ │ Image: front-bumper.jpg                     │    │
│ │ ┌──────────────────────────────────────┐    │    │
│ │ │  [📷 Image with Bounding Boxes]      │    │    │
│ │ │      Shows all damage annotations    │    │    │
│ │ └──────────────────────────────────────┘    │    │
│ │                                              │    │
│ │ Damages from this image:                    │    │
│ │ ┌──────────────────────────────────────┐    │    │
│ │ │ 1. Front Bumper Dent                 │    │    │
│ │ │    Severity: 60% | Cost: $750       │    │    │
│ │ │    Labor: 2.5h | Parts: $400        │    │    │
│ │ └──────────────────────────────────────┘    │    │
│ │ ┌──────────────────────────────────────┐    │    │
│ │ │ 2. Headlight Crack                   │    │    │
│ │ │    Severity: 80% | Cost: $500       │    │    │
│ │ │    Labor: 1.0h | Parts: $350        │    │    │
│ │ └──────────────────────────────────────┘    │    │
│ │                                              │    │
│ │ ═══════════════════════════════════════════ │    │
│ │ Image: rear-door.jpg                        │    │
│ │ ┌──────────────────────────────────────┐    │    │
│ │ │  [📷 Image with Bounding Boxes]      │    │    │
│ │ └──────────────────────────────────────┘    │    │
│ │                                              │    │
│ │ Damages from this image:                    │    │
│ │ ┌──────────────────────────────────────┐    │    │
│ │ │ 3. Rear Door Scratch                 │    │    │
│ │ │    Severity: 40% | Cost: $2,000     │    │    │
│ │ │    Labor: 5.0h | Parts: $1,250      │    │    │
│ │ └──────────────────────────────────────┘    │    │
│ │                                              │    │
│ │ [Accept Estimate]  [Appeal Estimate]        │    │
│ └─────────────────────────────────────────────┘    │
│                                                     │
│ Claim Details                                       │
│ ┌─────────────────────────────────────────────┐    │
│ │ Vehicle Information                          │    │
│ │ • 2022 Toyota Camry LE                       │    │
│ │ • VIN: 1ABC23456789DEFG                      │    │
│ │ • Color: Silver                              │    │
│ │                                              │    │
│ │ Policy Summary                               │    │
│ │ • Policy Number: POL-2026-001                │    │
│ │ • Collision Deductible: $500                 │    │
│ │ • Coverage: $25,000                          │    │
│ │                                              │    │
│ │ Event Details                                │    │
│ │ • Date of Incident: April 30, 2026           │    │
│ │ • Reported: May 1, 2026 at 10:30 AM          │    │
│ │ • Vehicle Drivable: Yes                      │    │
│ │                                              │    │
│ │ Your Description                             │    │
│ │ "I was rear-ended at a red light by          │    │
│ │  another driver who was not paying           │    │
│ │  attention. There was minor damage to        │    │
│ │  the rear bumper."                           │    │
│ └─────────────────────────────────────────────┘    │
│                                                     │
│ Claim Timeline                                      │
│ ┌─────────────────────────────────────────────┐    │
│ │ ⚫ 05/03 10:30 AM - Claim Created            │    │
│ │ ⚫ 05/03 10:35 AM - Images Uploaded (2)      │    │
│ │ ⚫ 05/03 10:36 AM - AI Analysis Complete     │    │
│ │ ⚪ Awaiting your decision...                 │    │
│ └─────────────────────────────────────────────┘    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Layout (Payment Processing State):**
```
┌─────────────────────────────────────────────────────┐
│ Claim #1000                                         │
│                                                     │
│ Status: Payment Processing                          │
│                                                     │
│ ┌─────────────────────────────────────────────┐    │
│ │ ✓ You Accepted Estimate - Payment Processing│    │
│ │                                              │    │
│ │ You accepted this estimate on May 5, 2026   │    │
│ │ at 2:30 PM. Your payment is being processed.│    │
│ │                                              │    │
│ │ Payment Timeline: Payment is usually issued │    │
│ │ within 24 hours of acceptance.              │    │
│ │                                              │    │
│ │ Delivery: Please note that there may be a   │    │
│ │ delay in receiving the funds as payments    │    │
│ │ are sent through the US Postal Service.     │    │
│ │ Allow 5-7 business days for mail delivery.  │    │
│ └─────────────────────────────────────────────┘    │
│                                                     │
│ AI Damage Assessment                                │
│ ┌─────────────────────────────────────────────┐    │
│ │ Total Estimated Cost: $3,250                │    │
│ │ Damages Detected: 3 damages across 2 images │    │
│ │                                              │    │
│ │ [Damage details shown - same as above]      │    │
│ │                                              │    │
│ │ [No Accept/Appeal buttons shown]            │    │
│ └─────────────────────────────────────────────┘    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Implementation Details:**

**Claim State Detection:**
```javascript
const isHumanReviewPending = claim.current_status === 'human_review_pending';
const isPaymentProcessing = claim.current_status === 'sent_for_payment';
const isRoutedToTraditional = claim.current_status === 'routed_to_traditional';
```

**Fetch Claim Data:**
```javascript
// GET /api/v1/customers/{id}/claims/{claimId}
const claim = await fetchClaim(claimId);

// Get damages from claim response
const damages = claim.damage_assessment?.damages || [];

// Group damages by image_id
const damagesByImage = damages.reduce((acc, damage) => {
  if (!acc[damage.image_id]) {
    acc[damage.image_id] = [];
  }
  acc[damage.image_id].push(damage);
  return acc;
}, {});

// Calculate total cost
const totalCost = claim.claim_amount || 0;
```

**Claim Details Component:**
```javascript
<Card title="Claim Details" className="claim-details-card">
  <div className="details-section">
    <h4>Vehicle Information</h4>
    <ul>
      <li>{vehicle.year} {vehicle.make} {vehicle.model}</li>
      <li>VIN: {vehicle.vin}</li>
      <li>Color: {vehicle.color}</li>
    </ul>
  </div>

  <div className="details-section">
    <h4>Policy Summary</h4>
    <ul>
      <li>Policy Number: {policy.policy_number}</li>
      <li>Collision Deductible: ${policy.collision_deductible?.toLocaleString()}</li>
      <li>Coverage: ${policy.liability_limit?.toLocaleString()}</li>
    </ul>
  </div>

  <div className="details-section">
    <h4>Event Details</h4>
    <ul>
      <li>Date of Incident: {formatDate(claim.date_of_damage)}</li>
      <li>Reported: {formatDate(claim.fnol_date)} at {formatTime(claim.fnol_time)}</li>
      <li>Vehicle Drivable: {claim.is_drivable ? 'Yes' : 'No'}</li>
    </ul>
  </div>

  {claim.incident_description && (
    <div className="details-section">
      <h4>Your Description</h4>
      <p className="incident-description">{claim.incident_description}</p>
    </div>
  )}
</Card>
```

**Component Location:**
- Rendered between the "AI Damage Assessment" card and "Claim Timeline" section
- Always visible (non-editable display of claim information)
- Helps customer review all details before accepting/appealing estimate

**Data Sources:**
- `claim` object from API response
- `vehicle` data from `policy.vehicles` array (match by VIN)
- `policy` data from embedded policy response or separate fetch
```

**Display Annotated Images with Bounding Boxes:**
```jsx
// Get annotated image URL (with bounding boxes)
const annotatedImageUrl = `${API_BASE_URL}/api/v1/customers/${customerId}/claims/${claimId}/images/${imageId}?annotated=yes`;

// Display grouped by image
{Object.entries(damagesByImage).map(([imageId, imageDamages]) => (
  <div key={imageId}>
    <h3>Image: {imageId}</h3>
    
    {/* Show annotated image with bounding boxes */}
    <img 
      src={annotatedImageUrl} 
      alt={`Damage analysis for ${imageId}`}
      className="w-full rounded-lg"
    />
    
    {/* List all damages detected in this image */}
    <div className="damages-list">
      {imageDamages.map((damage, idx) => (
        <DamageCard key={damage.damage_id} damage={damage} index={idx} />
      ))}
    </div>
  </div>
))}
```

**Human Review Banner:**

When claim is in `human_review_pending` state, show a yellow banner. The banner message depends on how the claim reached this state:

1. **If customer appealed:** Show appeal date from claim events
   ```javascript
   // Fetch events when status is human_review_pending
   const eventsResponse = await fetchClaimEvents(customerId, claimId);
   const appealEvent = events.find(event => event.action === 'appeal_estimate');
   
   if (appealEvent) {
     const appealDate = new Date(`${appealEvent.event_date}T${appealEvent.event_time}`);
     // Display: "Human Review Required because you appealed the AI estimate on [date]."
   }
   ```

2. **If low confidence or no damage:** Show standard message
   - No damage: "No damage was detected in the uploaded images. A human adjuster will review your claim and assess the damage."
   - Low confidence: "Our AI has completed the initial analysis, but the confidence level is below our threshold. A human adjuster will review your claim to ensure accuracy."

3. **Timeline info:** Always show "You will be notified via email once the review is complete. This typically takes 1-2 business days."

**Accept Estimate:**

When customer clicks "Accept Estimate", show a confirmation modal with:

1. **Estimate Summary:** Display total cost prominently
2. **Important Information:**
   - Payment will be issued within 24 hours
   - Customer cannot change claim data after acceptance
   - Customer can appeal for additional loss funds if actual repair cost exceeds estimate
3. **Confirmation:** Require explicit acknowledgment before proceeding

```javascript
// On Accept Estimate button click
const handleAcceptEstimate = () => {
  setShowAcceptModal(true);
};

// On modal confirmation
const handleConfirmAccept = async () => {
  try {
    setAccepting(true);
    
    // POST /api/v1/customers/{customerId}/claims/{claimId}/accept-estimate
    await acceptEstimate(customerId, claimId);
    
    // Close modal
    setShowAcceptModal(false);
    
    // Reload claim to get updated status (sent_for_payment) and show payment processing banner
    // No alert needed - the payment processing banner provides the message
    await loadClaim();
  } catch (err) {
    console.error('Failed to accept estimate:', err);
    alert('Failed to accept estimate. Please try again or contact support.');
  } finally {
    setAccepting(false);
  }
};

// State transitions on backend:
// 1. customer_decision_pending → loss_approved (ACCEPT_ESTIMATE event)
// 2. loss_approved → sent_for_payment (INITIATE_PAYMENT event)
```

**Modal Component Structure:**
```jsx
<Modal isOpen={showAcceptModal} onClose={handleCancelAccept} title="Accept Estimate">
  {/* Estimate summary box */}
  <div className="estimate-summary">
    <p>You are accepting an estimate of:</p>
    <p className="amount">${totalCost}</p>
  </div>
  
  {/* Important information list */}
  <div className="important-info">
    <div className="info-item">
      <CheckCircle icon />
      <p><strong>Payment Processing:</strong> Payment will be issued within 24 hours...</p>
    </div>
    <div className="info-item">
      <AlertCircle icon />
      <p><strong>Claim Data:</strong> You will not be able to change claim details...</p>
    </div>
    <div className="info-item">
      <Info icon />
      <p><strong>Additional Loss Funds:</strong> You can appeal for additional funds...</p>
    </div>
  </div>
  
  {/* Acknowledgment text */}
  <div className="acknowledgment">
    <p>By clicking "Confirm & Accept", you acknowledge...</p>
  </div>
  
  {/* Action buttons */}
  <div className="actions">
    <Button variant="secondary" onClick={handleCancelAccept}>Cancel</Button>
    <Button onClick={handleConfirmAccept} disabled={accepting}>
      {accepting ? 'Processing...' : 'Confirm & Accept'}
    </Button>
  </div>
</Modal>
```

**Payment Processing Notice:**

When claim status is `sent_for_payment`, show a green success banner instead of Accept/Appeal buttons.

First, fetch the acceptance date from events:

```javascript
// In loadClaim, after fetching claim details
if (response.data.current_status === 'sent_for_payment') {
  try {
    const eventsResponse = await fetchClaimEvents(customerId, claimId);
    const events = eventsResponse.data.events || [];
    
    // Find the accept_estimate event
    const acceptEvent = events.find(event => event.action === 'accept_estimate');
    if (acceptEvent) {
      // Combine event_date and event_time to create a full datetime
      const dateTimeString = `${acceptEvent.event_date}T${acceptEvent.event_time}`;
      setAcceptanceDate(new Date(dateTimeString));
    }
  } catch (eventsErr) {
    console.error('Failed to load events:', eventsErr);
    // Don't fail the entire page load if events fail
  }
}
```

Then display the banner:

```jsx
{/* Payment Processing Notice */}
{isPaymentProcessing && (
  <div className="mb-6 p-6 bg-green-50 border-l-4 border-green-400 rounded-lg">
    <div className="flex items-start gap-3">
      <CheckCircle className="h-6 w-6 text-green-600 flex-shrink-0 mt-0.5" />
      <div>
        <h3 className="text-lg font-semibold text-green-900 mb-2">
          You Accepted Estimate - Payment Processing
        </h3>
        <p className="text-green-800 mb-2">
          {acceptanceDate ? (
            <>
              You accepted this estimate on {acceptanceDate.toLocaleDateString('en-US', {
                month: 'long',
                day: 'numeric',
                year: 'numeric'
              })} at {acceptanceDate.toLocaleTimeString('en-US', {
                hour: 'numeric',
                minute: '2-digit'
              })}. Your payment is being processed.
            </>
          ) : (
            'You accepted this estimate. Your payment is being processed.'
          )}
        </p>
        <p className="text-sm text-green-700 mb-2">
          <strong>Payment Timeline:</strong> Payment is usually issued within 24 hours of acceptance.
        </p>
        <p className="text-sm text-green-700">
          <strong>Delivery:</strong> Please note that there may be a delay in receiving the funds 
          as payments are sent through the US Postal Service. Allow 5-7 business days for mail delivery.
        </p>
      </div>
    </div>
  </div>
)}
```

**Traditional Processing Notice:**

When claim status is `routed_to_traditional`, show an orange info banner:

```jsx
{/* Traditional Processing Notice */}
{isRoutedToTraditional && (
  <div className="mb-6 p-6 bg-orange-50 border-l-4 border-orange-400 rounded-lg">
    <div className="flex items-start gap-3">
      <AlertCircle className="h-6 w-6 text-orange-600 flex-shrink-0 mt-0.5" />
      <div>
        <h3 className="text-lg font-semibold text-orange-900 mb-2">
          Claim Routed to Traditional Processing
        </h3>
        <p className="text-orange-800 mb-2">
          Your claim has been routed to our traditional claim processing. A dedicated adjuster 
          will handle your claim and may contact you to schedule a physical inspection if needed.
        </p>
        <p className="text-sm text-orange-700 mb-2">
          <strong>Processing Timeline:</strong> Traditional claims typically take 5-10 business days 
          to complete. You will be notified via email once your claim has been assessed.
        </p>
        <p className="text-sm text-orange-700">
          <strong>What to expect:</strong> An adjuster may reach out to schedule an in-person 
          inspection of your vehicle. You will receive a detailed estimate once the assessment is complete.
        </p>
      </div>
    </div>
  </div>
)}
```

**Adjustor Review Complete Notice:**

When claim has been reviewed by adjustor and returned to customer for decision (status = `customer_decision_pending` after `human_review_completed`), show a banner with adjustor's note and decision outcome:

```javascript
// Check if claim was reviewed by adjustor by looking at damages
const hasAdjustorReview = damages.some(d => d.reviewed_by_adjustor);

// Determine if appeal was denied (no cost change) or accepted (cost revised)
const aiTotal = damages.reduce((sum, d) => sum + (d.ai_total_cost || 0), 0);
const currentTotal = damages.reduce((sum, d) => sum + (d.estimated_total_cost || 0), 0);
const appealDenied = aiTotal === currentTotal;
const appealAccepted = currentTotal !== aiTotal;

// Get adjustor note (take first damage with note, or fetch from review event)
const adjustorNote = damages.find(d => d.adjustor_note)?.adjustor_note || 
  'Our adjustor has reviewed your appeal and provided a decision.';
```

Display the banner:

```jsx
{/* Adjustor Review Complete Notice */}
{hasAdjustorReview && claim.current_status === 'customer_decision_pending' && (
  <div className={`mb-6 p-6 border-l-4 rounded-lg ${
    appealAccepted ? 'bg-blue-50 border-blue-400' : 'bg-yellow-50 border-yellow-400'
  }`}>
    <div className="flex items-start gap-3">
      {appealAccepted ? (
        <CheckCircle className="h-6 w-6 text-blue-600 flex-shrink-0 mt-0.5" />
      ) : (
        <AlertTriangle className="h-6 w-6 text-yellow-600 flex-shrink-0 mt-0.5" />
      )}
      <div>
        <h3 className={`text-lg font-semibold mb-2 ${
          appealAccepted ? 'text-blue-900' : 'text-yellow-900'
        }`}>
          {appealAccepted ? 'Appeal Accepted - Estimate Revised' : 'Appeal Denied - Original Estimate Confirmed'}
        </h3>
        <div className={`mb-3 p-3 rounded ${
          appealAccepted ? 'bg-blue-100' : 'bg-yellow-100'
        }`}>
          <p className={`text-sm font-medium mb-1 ${
            appealAccepted ? 'text-blue-800' : 'text-yellow-800'
          }`}>
            Adjustor's Note:
          </p>
          <p className={`text-sm ${
            appealAccepted ? 'text-blue-900' : 'text-yellow-900'
          }`}>
            {adjustorNote}
          </p>
        </div>
        
        {appealAccepted && (
          <p className="text-sm text-blue-800 mb-2">
            <strong>Revised Estimate:</strong> ${currentTotal.toFixed(2)} 
            (Changed from AI estimate of ${aiTotal.toFixed(2)})
          </p>
        )}
        
        {appealDenied && (
          <p className="text-sm text-yellow-800 mb-2">
            <strong>Original Estimate Confirmed:</strong> ${currentTotal.toFixed(2)}
          </p>
        )}
        
        <div className="mt-3 p-3 bg-white border border-gray-200 rounded">
          <p className="text-sm text-gray-700">
            <strong>💡 Reminder:</strong> You can appeal this decision if the actual repair cost 
            exceeds this estimate. After repairs are completed, if the final invoice shows a higher 
            amount, you have the right to submit a supplemental claim with supporting documentation 
            (itemized invoice from the repair shop).
          </p>
        </div>
      </div>
    </div>
  </div>
)}
```

**Banner Display Logic:**
- **When to show**: Claim status is `customer_decision_pending` AND at least one damage has `reviewed_by_adjustor = true`
- **Appeal Accepted (Blue Banner)**: When adjustor revised the estimate (current total ≠ AI total)
  - Shows "Appeal Accepted - Estimate Revised" header
  - Displays revised estimate and original AI estimate for comparison
  - Shows adjustor's note explaining the revision
- **Appeal Denied (Yellow Banner)**: When adjustor confirmed AI estimate (no cost change)
  - Shows "Appeal Denied - Original Estimate Confirmed" header
  - Displays confirmed estimate amount
  - Shows adjustor's note explaining why AI estimate was correct
- **Always includes reminder**: Customer can still appeal if actual repair costs exceed the estimate

**Conditional Rendering of Action Buttons:**

Accept/Appeal buttons should show when claim is in `customer_decision_pending` state (including after adjustor review):

```javascript
{/* Action Buttons - Only show for customer_decision_pending */}
{damages.length > 0 && !isHumanReviewPending && !isPaymentProcessing && !isRoutedToTraditional && (
  <div className="flex gap-4 pt-6 border-t border-gray-200">
    <Button onClick={handleAcceptEstimate} className="flex-1">
      <CheckCircle className="h-5 w-5 mr-2 inline" />
      Accept Estimate
    </Button>
    <Button onClick={handleAppealEstimate} variant="secondary" className="flex-1">
      <AlertCircle className="h-5 w-5 mr-2 inline" />
      Appeal Estimate
    </Button>
  </div>
)}

{/* Info Box - Hide for payment processing, human review, and traditional processing */}
{!isHumanReviewPending && !isPaymentProcessing && !isRoutedToTraditional && (
  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
    <p className="text-sm text-blue-800">
      <strong>What happens next?</strong> Review the AI damage assessment above...
    </p>
  </div>
)}
```

**Appeal Estimate:**

When customer clicks "Appeal Estimate", determine if this is first or second appeal and show appropriate modal.

**Detecting Appeal Type:**

```javascript
// Fetch events and check for human review
const eventsResponse = await fetchClaimEvents(customerId, claimId);
const events = eventsResponse.data.events || [];

// Check if human review was completed (indicates second appeal scenario)
const hasHumanReview = events.some(
  event => event.action === 'revised_estimate' ||
           event.status === 'human_review_completed'
);
setIsSecondAppeal(hasHumanReview);
```

**First Appeal (AI Estimate):**

Show modal with reason textarea (required):

```jsx
<Modal isOpen={showAppealModal} onClose={handleCancelAppeal} title="Appeal Estimate">
  {/* Info banner */}
  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
    <p>Your appeal will be reviewed by a human adjuster who will assess your claim
    and provide a revised estimate within 1-2 business days.</p>
  </div>
  
  {/* Reason field - REQUIRED */}
  <div>
    <label>Reason for Appeal <span className="text-red-600">*</span></label>
    <Textarea
      value={appealReason}
      onChange={(e) => setAppealReason(e.target.value)}
      placeholder="e.g., Estimate seems too low, missing damage, incorrect parts identified..."
      rows={5}
      maxLength={500}
      required
    />
    <p className="text-xs text-gray-500">{appealReason.length}/500 characters</p>
  </div>
  
  {/* Action buttons */}
  <div className="flex gap-4">
    <Button variant="secondary" onClick={handleCancelAppeal}>Cancel</Button>
    <Button onClick={handleConfirmAppeal}>Submit Appeal</Button>
  </div>
</Modal>
```

**Second Appeal (Human-Reviewed Estimate):**

Show modal with warning about traditional processing:

```jsx
<Modal isOpen={showAppealModal} onClose={handleCancelAppeal} title="Appeal to Traditional Processing">
  {/* Warning banner */}
  <div className="bg-yellow-50 border-l-4 border-yellow-400 rounded-lg p-4">
    <AlertCircle icon />
    <div>
      <h4>Traditional Processing May Take Longer</h4>
      <p>This is your second appeal. Your claim will be sent to our traditional claim process,
      which may take longer to complete. A dedicated adjuster will handle your claim.</p>
    </div>
  </div>
  
  {/* Important information */}
  <div className="space-y-3">
    <div>
      <Info icon />
      <p><strong>You can still accept the current estimate:</strong> If you accept now,
      you'll receive payment within 24 hours.</p>
    </div>
    <div>
      <CheckCircle icon />
      <p><strong>Additional funds available:</strong> If the actual cost of repair exceeds
      this estimate, you can appeal for additional loss funds through our extra fund appeal process.</p>
    </div>
  </div>
  
  {/* Reason field - OPTIONAL */}
  <div>
    <label>Reason for Appeal (Optional)</label>
    <Textarea
      value={appealReason}
      onChange={(e) => setAppealReason(e.target.value)}
      placeholder="e.g., I need a physical inspection by an adjuster..."
      rows={4}
      maxLength={500}
    />
  </div>
  
  {/* Action buttons */}
  <div className="flex gap-4">
    <Button variant="secondary" onClick={handleCancelAppeal}>Cancel</Button>
    <Button onClick={handleConfirmAppeal}>Route to Traditional</Button>
  </div>
</Modal>
```

**API Call and State Transitions:**

```javascript
const handleConfirmAppeal = async () => {
  // Validate reason for first appeal
  if (!isSecondAppeal && !appealReason.trim()) {
    alert('Please provide a reason for your appeal.');
    return;
  }

  try {
    setAppealing(true);
    
    // POST /api/v1/customers/{customerId}/claims/{claimId}/appeal-estimate
    const response = await appealEstimate(customerId, claimId, appealReason.trim() || 'Customer appealed');
    
    // Close modal
    setShowAppealModal(false);
    
    // Show success message based on appeal type
    if (response.data.appeal_type === 'first') {
      alert('Appeal submitted! Your claim has been sent for human review. An adjuster will review your claim within 1-2 business days.');
      // State: customer_decision_pending → loss_appealed → human_review_pending
    } else {
      alert('Your claim has been routed to traditional processing. This process may take longer, but a dedicated adjuster will handle your claim.');
      // State: customer_decision_pending → loss_appealed → routed_to_traditional
    }
    
    // Reload claim to get updated status and show appropriate banner
    await loadClaim();
    
    // Stay on page - user will see Human Review or Traditional Processing banner
  } catch (err) {
    console.error('Failed to appeal estimate:', err);
    alert('Failed to submit appeal. Please try again or contact support.');
  } finally {
    setAppealing(false);
  }
};

// Backend state transitions:
// First appeal:  customer_decision_pending → loss_appealed → human_review_pending
//                Events: APPEAL_ESTIMATE ("Customer appealed AI estimate") + FLAG_FOR_HUMAN_REVIEW
//
// Second appeal: customer_decision_pending → loss_appealed → routed_to_traditional
//                Events: APPEAL_ESTIMATE ("Customer appealed human-reviewed estimate") + ROUTE_TO_TRADITIONAL
```

---

## 7.6 Data Model Updates: Dual-Column Estimate Approach

### 7.6.1 Overview

**Change:** Backend now uses dual-column approach for damage estimates to preserve AI baseline while allowing adjustor modifications.

**Impact on Customer Portal:** Minimal - mostly transparent to customers

**Key Changes:**
- API now returns both AI and adjustor estimates for each damage
- Customer sees the **effective estimate** (adjustor if reviewed, else AI)
- Optional: Show comparison when adjustor modified the estimate

### 7.6.2 API Response Structure Changes

**Previous Structure:**
```javascript
{
  damage_id: 1,
  labor_hours: 2.5,
  estimated_parts_cost: 400,
  estimated_total_cost: 750
}
```

**New Structure:**
```javascript
{
  damage_id: 1,
  
  // Effective estimate (what customer sees)
  labor_hours: 2.5,              // From adjustor OR AI
  estimated_parts_cost: 400,     // From adjustor OR AI
  estimated_total_cost: 750,     // From adjustor OR AI
  estimate_source: "ai",         // or "adjustor"
  
  // AI estimate (baseline - always present)
  ai_labor_hours: 2.0,
  ai_parts_cost: 350,
  ai_total_cost: 650,
  
  // Adjustor estimate (present if reviewed)
  adjustor_labor_hours: 2.5,
  adjustor_parts_cost: 400,
  adjustor_total_cost: 750,
  reviewed_by_adjustor: true,
  adjustor_note: "Revised after inspection",
  reviewed_at: "2026-05-06T14:30:00Z"
}
```

### 7.6.3 Display Logic

**Default Behavior (No UI Changes):**
- Continue using `labor_hours`, `estimated_parts_cost`, `estimated_total_cost`
- These fields now contain the **effective estimate** (adjustor if available, else AI)
- No code changes required for basic display

**Optional Enhancement (Show Comparison):**
```jsx
{/* Show effective estimate */}
<div className="text-lg font-bold">
  Estimated Cost: ${damage.estimated_total_cost}
</div>

{/* Optionally show if adjustor reviewed */}
{damage.reviewed_by_adjustor && (
  <div className="text-sm text-gray-600 mt-1">
    <span className="inline-flex items-center">
      <svg className="h-4 w-4 text-green-600 mr-1">✓</svg>
      Reviewed by adjustor
    </span>
  </div>
)}

{/* Optional: Show comparison */}
{damage.estimate_source === 'adjustor' && damage.ai_total_cost !== damage.adjustor_total_cost && (
  <div className="text-xs text-gray-500 mt-1">
    AI estimated ${damage.ai_total_cost} → Adjustor reviewed to ${damage.adjustor_total_cost}
  </div>
)}
```

### 7.6.4 Labor Hours Rounding

**Change:** Labor hours now rounded UP to nearest 0.5 increment (industry standard)

**Examples:**
- 1.2 hours → 1.5 hours
- 2.3 hours → 2.5 hours
- 3.0 hours → 3.0 hours (no change)

**Impact:**
- Labor hours displayed will always be in 0.5 increments (1.0, 1.5, 2.0, 2.5, etc.)
- No code changes needed - API handles rounding

### 7.6.5 Implementation Notes

**Files Requiring Updates:**
- `src/pages/ClaimDetailPage.jsx` - Uses damage data from API
- `src/components/claims/DamageCard.jsx` - Displays individual damage costs

**Backward Compatibility:**
- The `labor_hours`, `estimated_parts_cost`, `estimated_total_cost` fields still exist
- They now contain the effective estimate (adjustor or AI)
- Existing code continues to work without changes

**Optional Enhancements:**
- Show "Reviewed by adjustor" badge when `reviewed_by_adjustor === true`
- Show comparison: "AI: $X → Adjustor: $Y" when estimates differ
- Display `estimate_source` to indicate if AI or human reviewed

**Testing:**
- Test with AI-only estimates (no adjustor review)
- Test with adjustor-reviewed estimates
- Test comparison display (if implemented)
- Verify labor hours display in 0.5 increments

---

## 8. Component Library

### 8.1 Common Components

#### Button Component

```jsx
// src/components/common/Button.jsx
export const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'md',
  onClick,
  disabled,
  className = ''
}) => {
  const baseClasses = 'rounded-lg font-semibold transition-all duration-200';
  
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-lg',
    secondary: 'bg-white text-blue-600 border-2 border-blue-600 hover:bg-blue-50',
    danger: 'bg-red-600 text-white hover:bg-red-700',
  };
  
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };
  
  return (
    <button
      className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
};
```

#### Card Component

```jsx
// src/components/common/Card.jsx
export const Card = ({ children, className = '', title, actions }) => {
  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 p-6 ${className}`}>
      {title && (
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-semibold text-gray-900">{title}</h3>
          {actions && <div className="flex gap-2">{actions}</div>}
        </div>
      )}
      {children}
    </div>
  );
};
```

#### ProgressBar Component

```jsx
// src/components/common/ProgressBar.jsx
export const ProgressBar = ({ current, total, steps, showPercentage = true }) => {
  const percentage = (current / total) * 100;
  
  return (
    <div className="w-full">
      {steps && (
        <div className="flex justify-between mb-2">
          {steps.map((step, idx) => (
            <div
              key={idx}
              className={`text-sm ${
                idx < current ? 'text-blue-600 font-semibold' : 'text-gray-400'
              }`}
            >
              {step}
            </div>
          ))}
        </div>
      )}
      
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
          style={{ width: `${percentage}%` }}
        />
      </div>
      
      {showPercentage && (
        <div className="text-right text-sm text-gray-600 mt-1">
          {Math.round(percentage)}%
        </div>
      )}
    </div>
  );
};
```

### 8.2 Claim-Specific Components

#### DamageCard Component

```jsx
// src/components/claims/DamageCard.jsx
import { AlertCircle, Wrench, DollarSign } from 'lucide-react';

export const DamageCard = ({ damage, showDetails = true }) => {
  const severityColor = damage.severity > 0.7 ? 'red' : damage.severity > 0.4 ? 'yellow' : 'green';
  
  return (
    <div className="border border-gray-200 rounded-lg p-4">
      {/* Damage Header */}
      <div className="flex justify-between items-start mb-3">
        <h4 className="text-lg font-semibold text-gray-900">
          {damage.damage_part.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
        </h4>
        <span className="text-xl font-bold text-blue-600">
          ${damage.estimated_total_cost.toFixed(2)}
        </span>
      </div>
      
      {/* Annotated Image */}
      <BoundingBoxViewer
        originalImage={getImageUrl(customerId, damage.claim_id, damage.image_id, false)}
        annotatedImage={getImageUrl(customerId, damage.claim_id, damage.image_id, true)}
        className="mb-3"
      />
      
      {showDetails && (
        <>
          {/* Severity */}
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className={`w-5 h-5 text-${severityColor}-600`} />
            <span className="text-sm font-medium">
              Severity: {(damage.severity * 100).toFixed(0)}%
              <span className="text-gray-500 ml-2">
                ({damage.severity > 0.7 ? 'Severe' : damage.severity > 0.4 ? 'Moderate' : 'Light'})
              </span>
            </span>
          </div>
          
          {/* Internal Damage Probability */}
          <div className="flex items-center gap-2 mb-2">
            <Wrench className="w-5 h-5 text-orange-600" />
            <span className="text-sm">
              Internal Damage Probability: {(damage.internal_damage_probability * 100).toFixed(0)}%
            </span>
          </div>
          
          {/* Recommended Action */}
          <div className="flex items-center gap-2 mb-3">
            <Wrench className="w-5 h-5 text-blue-600" />
            <span className="text-sm">
              Recommended: <strong>{damage.recommended_action.replace(/-/g, ' ')}</strong>
            </span>
          </div>
          
          {/* Reasoning */}
          <div className="bg-gray-50 rounded p-3 text-sm text-gray-700">
            <strong>AI Assessment:</strong>
            <p className="mt-1">{damage.reasoning}</p>
          </div>
          
          {/* Cost Breakdown */}
          <div className="mt-3 pt-3 border-t border-gray-200">
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600">Labor ({damage.labor_hours}h)</span>
              <span>${(damage.labor_hours * laborRate).toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Parts</span>
              <span>${damage.estimated_parts_cost.toFixed(2)}</span>
            </div>
            
            {/* Optional: Show if adjustor reviewed */}
            {damage.reviewed_by_adjustor && (
              <div className="mt-2 text-xs text-green-600 flex items-center">
                <svg className="h-3 w-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                Reviewed by adjustor
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};
```

#### ImageUploader Component

```jsx
// src/components/claims/ImageUploader.jsx
import { Upload, CheckCircle, XCircle } from 'lucide-react';
import { useState } from 'react';

export const ImageUploader = ({ claimId, onUploadComplete }) => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState({});
  
  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFiles = Array.from(e.dataTransfer.files);
    handleFiles(droppedFiles);
  };
  
  const handleFiles = async (newFiles) => {
    setFiles(prev => [...prev, ...newFiles.map(f => ({
      file: f,
      status: 'pending',
      damages: null,
      error: null
    }))]);
    
    // Upload each file
    for (let i = 0; i < newFiles.length; i++) {
      const file = newFiles[i];
      await uploadFile(file, i);
    }
    
    onUploadComplete();
  };
  
  const uploadFile = async (file, index) => {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      setFiles(prev => {
        const updated = [...prev];
        updated[index].status = 'uploading';
        return updated;
      });
      
      const response = await axios.post(
        `/api/v1/customers/${customerId}/claims/${claimId}/images`,
        formData,
        {
          onUploadProgress: (e) => {
            setProgress(prev => ({
              ...prev,
              [index]: Math.round((e.loaded / e.total) * 100)
            }));
          }
        }
      );
      
      // Image uploaded successfully (analysis happens later after submission)
      setFiles(prev => {
        const updated = [...prev];
        updated[index].status = 'uploaded';
        return updated;
      });
      
    } catch (error) {
      setFiles(prev => {
        const updated = [...prev];
        updated[index].status = 'error';
        updated[index].error = error.message;
        return updated;
      });
    }
  };
  
  return (
    <div>
      {/* Drop Zone */}
      <div
        className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-blue-500 transition-colors cursor-pointer"
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        onClick={() => document.getElementById('file-input').click()}
      >
        <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
        <p className="text-lg text-gray-600 mb-2">
          Drag & drop images here, or click to browse
        </p>
        <p className="text-sm text-gray-500">
          Supported: JPG, PNG, HEIC • Max size: 10MB • Max images: 20
        </p>
        <input
          id="file-input"
          type="file"
          multiple
          accept="image/jpeg,image/png,image/heic"
          className="hidden"
          onChange={(e) => handleFiles(Array.from(e.target.files))}
        />
      </div>
      
      {/* Uploaded Files */}
      {files.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-3">
            Uploaded Images ({files.length})
          </h3>
          
          <div className="grid grid-cols-3 gap-4">
            {files.map((fileData, idx) => (
              <div key={idx} className="border rounded-lg p-3">
                {/* Thumbnail */}
                <img
                  src={URL.createObjectURL(fileData.file)}
                  alt={fileData.file.name}
                  className="w-full h-32 object-cover rounded mb-2"
                />
                
                {/* Filename */}
                <p className="text-sm font-medium truncate">
                  {fileData.file.name}
                </p>
                
                {/* Status */}
                {fileData.status === 'uploading' && (
                  <div className="mt-2">
                    <div className="flex justify-between text-xs text-gray-600 mb-1">
                      <span>Uploading...</span>
                      <span>{progress[idx]}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <div
                        className="bg-blue-600 h-1.5 rounded-full"
                        style={{ width: `${progress[idx]}%` }}
                      />
                    </div>
                  </div>
                )}
                
                {fileData.status === 'uploaded' && (
                  <div className="mt-2">
                    <div className="flex items-center gap-1 text-green-600 text-sm mb-1">
                      <CheckCircle className="w-4 h-4" />
                      Uploaded
                    </div>
                  </div>
                )}
                
                {fileData.status === 'error' && (
                  <div className="mt-2 flex items-center gap-1 text-red-600 text-sm">
                    <XCircle className="w-4 h-4" />
                    {fileData.error}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
```

#### BoundingBoxViewer Component

```jsx
// src/components/claims/BoundingBoxViewer.jsx
import { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';

export const BoundingBoxViewer = ({ 
  originalImage, 
  annotatedImage, 
  showToggle = true,
  className = ''
}) => {
  const [showAnnotated, setShowAnnotated] = useState(true);
  
  return (
    <div className={`relative ${className}`}>
      <img
        src={showAnnotated ? annotatedImage : originalImage}
        alt="Damage"
        className="w-full rounded-lg border border-gray-200"
      />
      
      {showToggle && (
        <button
          className="absolute top-2 right-2 bg-white/90 backdrop-blur-sm px-3 py-1.5 rounded-lg shadow-md flex items-center gap-2 text-sm font-medium hover:bg-white transition-all"
          onClick={() => setShowAnnotated(!showAnnotated)}
        >
          {showAnnotated ? (
            <>
              <Eye className="w-4 h-4" />
              Hide Bounding Boxes
            </>
          ) : (
            <>
              <EyeOff className="w-4 h-4" />
              Show Bounding Boxes
            </>
          )}
        </button>
      )}
    </div>
  );
};
```

### 8.3 Layout Components

#### Header Component

```jsx
// src/components/layout/Header.jsx
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export const Header = () => {
  const { customer, logout } = useAuth();

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        {/* ACME Insurance Logo */}
        <Link to="/" className="flex items-center">
          <img 
            src="/ACME-logo.png" 
            alt="ACME Insurance" 
            className="h-12 w-auto"
          />
        </Link>

        {/* Navigation & User Info */}
        <div className="flex items-center gap-6">
          {customer && (
            <>
              <span className="text-gray-700">
                Welcome, {customer.fname} {customer.lname}!
              </span>
              <button
                onClick={logout}
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                Logout
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  );
};
```

**Implementation Notes:**
- Logo location: `public/ACME-logo.png` (copied from `src/common/assets/ACME-logo.png`)
- Logo links to home page (`/`)
- Logo size: 48px height (h-12) with auto width to maintain aspect ratio
- Header displays on all pages except login
- Logo is clickable to navigate home

#### Layout Component

```jsx
// src/components/layout/Layout.jsx
import { Header } from './Header';
import { Footer } from './Footer';

export const Layout = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <main className="flex-grow max-w-7xl mx-auto px-4 py-8 w-full">
        {children}
      </main>
      <Footer />
    </div>
  );
};
```

#### Footer Component

```jsx
// src/components/layout/Footer.jsx
export const Footer = () => {
  return (
    <footer className="bg-gray-800 text-white py-6 mt-auto">
      <div className="max-w-7xl mx-auto px-4 text-center">
        <p className="text-sm">
          © 2026 ACME Insurance. All rights reserved.
        </p>
        <p className="text-xs text-gray-400 mt-2">
          AI-Powered Auto Claims Management
        </p>
      </div>
    </footer>
  );
};
```

---

## 9. API Integration

### 9.1 Configuration Loader

```javascript
// src/api/config.js
import yaml from 'js-yaml';

let config = null;

export const loadConfig = async () => {
  if (config) return config;
  
  try {
    const response = await fetch('/customer-portal-config.yaml');
    const yamlText = await response.text();
    config = yaml.load(yamlText);
    return config;
  } catch (error) {
    console.error('Failed to load config, using defaults:', error);
    // Fallback to default config
    config = {
      api: {
        base_url: 'http://localhost:8000/api/v1',
        timeout: 30000
      },
      mock: {
        customer_id: 100,
        auth_password: 'password123'
      },
      features: {
        enable_appeal: true,
        max_images_per_claim: 20,
        max_image_size_mb: 10
      }
    };
    return config;
  }
};

export const getConfig = () => {
  if (!config) {
    throw new Error('Config not loaded. Call loadConfig() first.');
  }
  return config;
};
```

### 9.2 API Client Setup

```javascript
// src/api/client.js
import axios from 'axios';
import { getConfig } from './config';

const createApiClient = () => {
  const config = getConfig();
  const API_BASE_URL = config.api.base_url;

  const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: config.api.timeout,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor (add customer_id from localStorage)
  apiClient.interceptors.request.use((config) => {
    const customerId = localStorage.getItem('customer_id');
    if (customerId) {
      config.headers['X-Customer-ID'] = customerId;
    }
    return config;
  });

  // Response interceptor (handle errors)
  apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        // Clear auth and redirect to login
        localStorage.removeItem('customer_id');
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );

  return apiClient;
};

let apiClient = null;

export const getApiClient = () => {
  if (!apiClient) {
    apiClient = createApiClient();
  }
  return apiClient;
};

export default getApiClient;
```

### 9.3 API Functions

```javascript
// src/api/claims.js
import { getApiClient } from './client';

const apiClient = getApiClient();

export const fetchCustomerClaims = (customerId) => {
  return apiClient.get(`/customers/${customerId}/claims`);
};

export const fetchClaimDetail = (customerId, claimId) => {
  return apiClient.get(`/customers/${customerId}/claims/${claimId}`);
};

export const createClaim = (customerId, claimData) => {
  return apiClient.post(`/customers/${customerId}/claims`, claimData);
};

export const submitClaim = (customerId, claimId) => {
  return apiClient.post(`/customers/${customerId}/claims/${claimId}/submit`);
};

export const acceptEstimate = (customerId, claimId, data) => {
  return apiClient.post(`/customers/${customerId}/claims/${claimId}/accept`, data);
};

export const appealEstimate = (customerId, claimId, data) => {
  return apiClient.post(`/customers/${customerId}/claims/${claimId}/appeal`, data);
};

export const fetchDamages = (claimId) => {
  return apiClient.get(`/claims/${claimId}/damages`);
};
```

```javascript
// src/api/images.js
import { getApiClient } from './client';

const apiClient = getApiClient();

export const uploadImage = (customerId, claimId, formData, onProgress) => {
  return apiClient.post(
    `/customers/${customerId}/claims/${claimId}/images`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: onProgress,
    }
  );
};

export const deleteImage = (customerId, claimId, imageId) => {
  return apiClient.delete(`/customers/${customerId}/claims/${claimId}/images/${imageId}`);
};

export const getImageUrl = (customerId, claimId, imageId, annotated = false) => {
  const baseUrl = `/customers/${customerId}/claims/${claimId}/images/${imageId}`;
  return annotated ? `${baseUrl}?annotated=yes` : baseUrl;
};
```

### 9.4 Backend Estimate Generation Flow

**Important:** The estimate generation API automatically handles state transitions based on AI confidence scores.

#### High-Confidence Estimates (>= 0.55)

When `POST /customers/{customer_id}/claims/{claim_id}/generate-estimate` is called and AI confidence is high:

1. **State Transition Sequence:**
   - `IMAGE_UPLOADED` or `FNOL` → `loss_estimated_ai` (estimate generated)
   - `loss_estimated_ai` → `customer_decision_pending` (automatically presented to customer)

2. **Events Logged:**
   - Event 1: `generate_estimate` - AI analyzes damage and creates estimate
   - Event 2: `present_estimate_to_customer` - System automatically presents estimate for decision

3. **UI Impact:**
   - Claim Analysis Page polls for status and detects `customer_decision_pending`
   - Redirects to Claim Detail Page with Accept/Appeal buttons visible
   - Status shown as "Customer decision pending" (user-friendly mapping)

#### Low-Confidence Estimates (< 0.55)

When AI confidence is below threshold:

1. **State Transition:**
   - `IMAGE_UPLOADED` or `FNOL` → `human_review_pending` (single transition, skips loss_estimated_ai)

2. **Event Logged:**
   - Event: `generate_estimate` with comment indicating low confidence and routing to human review

3. **UI Impact:**
   - Claim Analysis Page polls for status and detects `human_review_pending`
   - Redirects to Claim Detail Page with yellow "Human Review Required" banner
   - Accept/Appeal buttons hidden
   - Status shown as "Review Pending"

**Key Takeaway:** The UI should poll for `customer_decision_pending` OR `human_review_pending` after generating estimates, NOT `loss_estimated_ai` (which is transient for high-confidence cases).

### 9.5 Automatic Adjustor Assignment

**NEW REQUIREMENT:** When a claim transitions to `human_review_pending` status, the system must automatically assign it to an available adjustor with the shortest work queue.

#### Implementation Strategy

1. **Trigger Point:**
   - When claim status changes to `human_review_pending` (either from low confidence AI estimate or customer appeal)
   - Assignment happens automatically via backend API call

2. **Assignment Logic:**
   - Call `GET /api/v1/adjustors` to retrieve all active adjustors with their current workload
   - Select adjustor with the lowest `pending_reviews` count
   - In case of tie, use round-robin or random selection
   - Call `POST /api/v1/adjustors/{adjustor_id}/claims/{claim_id}/assign` to assign claim

3. **API Integration Points:**

```javascript
// src/api/adjustors.js
import { getApiClient } from './client';

const apiClient = getApiClient();

/**
 * Get all adjustors with their workload statistics
 * @returns Promise with array of adjustors and their pending review counts
 */
export const fetchAdjustors = () => {
  return apiClient.get('/adjustors');
};

/**
 * Assign a claim to a specific adjustor
 * @param {string} adjustorId - Adjustor identifier (e.g., "ADJ-001")
 * @param {number} claimId - Claim identifier
 * @returns Promise with assignment confirmation
 */
export const assignClaimToAdjustor = (adjustorId, claimId) => {
  return apiClient.post(`/adjustors/${adjustorId}/claims/${claimId}/assign`);
};

/**
 * Automatically assign claim to adjustor with shortest queue
 * @param {number} claimId - Claim identifier
 * @returns Promise with assignment details
 */
export const autoAssignClaim = async (claimId) => {
  try {
    // Fetch all active adjustors with workload
    const response = await fetchAdjustors();
    const adjustors = response.data.adjustors;
    
    // Filter to active adjustors only
    const activeAdjustors = adjustors.filter(adj => adj.status === 'active');
    
    if (activeAdjustors.length === 0) {
      throw new Error('No active adjustors available');
    }
    
    // Find adjustor with minimum pending reviews
    const selectedAdjustor = activeAdjustors.reduce((min, adj) => 
      adj.pending_reviews < min.pending_reviews ? adj : min
    );
    
    // Assign claim to selected adjustor
    const assignResponse = await assignClaimToAdjustor(selectedAdjustor.adjustor_id, claimId);
    
    return {
      adjustor: selectedAdjustor,
      assignment: assignResponse.data
    };
  } catch (error) {
    console.error('Auto-assignment failed:', error);
    throw error;
  }
};
```

4. **Usage in Claim Flow:**

When generating estimate (in Claim Analysis page):

```javascript
// After estimate generation completes
const handleEstimateComplete = async (claimId, estimate) => {
  // Check if claim was routed to human review
  const claimStatus = await fetchClaimStatus(claimId);
  
  if (claimStatus.current_status === 'human_review_pending') {
    try {
      // Automatically assign to adjustor
      const assignment = await autoAssignClaim(claimId);
      console.log(`Claim ${claimId} assigned to ${assignment.adjustor.name}`);
      
      // Optional: Show toast notification
      toast.success(`Claim assigned to adjustor ${assignment.adjustor.name} for review`);
    } catch (error) {
      console.error('Failed to assign claim:', error);
      // Non-blocking: claim is still in queue, can be manually assigned later
    }
  }
  
  // Continue with normal flow...
};
```

When customer appeals estimate:

```javascript
// In ClaimDetailPage after appeal submission
const handleAppealSubmit = async () => {
  try {
    await submitAppeal(claimId, appealReason);
    
    // Claim is now in human_review_pending status
    // Automatically assign to adjustor
    const assignment = await autoAssignClaim(claimId);
    
    alert(`Appeal submitted! Your claim has been assigned to ${assignment.adjustor.name} for review. You will receive a response within 1-2 business days.`);
    
    navigate(`/claims/${claimId}`);
  } catch (error) {
    console.error('Appeal submission failed:', error);
    alert('Failed to submit appeal. Please try again.');
  }
};
```

5. **Error Handling:**
   - If no adjustors are available, claim remains in `human_review_pending` without assignment
   - Claims without assigned adjustor are visible to all adjustors in their review queue
   - Manual assignment can be done later via Adjustor Portal if auto-assignment fails

6. **Backend Requirements:**
   - New API endpoint: `GET /api/v1/adjustors` - List all adjustors with workload
   - New API endpoint: `POST /api/v1/adjustors/{adjustor_id}/claims/{claim_id}/assign` - Assign claim
   - See **API-BACKEND-TODOS.md** for implementation details

**Benefits:**
- ✅ Balanced workload distribution across adjustors
- ✅ Faster claim processing (no manual assignment step)
- ✅ Transparent assignment tracking
- ✅ Graceful degradation if assignment fails

---

## 10. State Management

### 10.1 Auth Context

```javascript
// src/context/AuthContext.jsx
import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [customerId, setCustomerId] = useState(null);
  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // Load from localStorage on mount
    const storedId = localStorage.getItem('customer_id');
    if (storedId) {
      setCustomerId(storedId);
      // Fetch customer data
      fetchCustomer(storedId);
    } else {
      setLoading(false);
    }
  }, []);
  
  const fetchCustomer = async (id) => {
    try {
      const response = await fetch(`/api/v1/customers/${id}`);
      const data = await response.json();
      setCustomer(data.data);
    } catch (error) {
      console.error('Failed to fetch customer:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const login = (email) => {
    // Hardcoded mock authentication
    // Extract customer_id from email (e.g., jane.doe@example.com → 100)
    // For demo, just use customer_id = 100
    const mockCustomerId = '100';
    
    localStorage.setItem('customer_id', mockCustomerId);
    setCustomerId(mockCustomerId);
    fetchCustomer(mockCustomerId);
  };
  
  const logout = () => {
    localStorage.removeItem('customer_id');
    setCustomerId(null);
    setCustomer(null);
  };
  
  return (
    <AuthContext.Provider value={{ customerId, customer, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
```

---

## 11. Development Guidelines

### 11.1 Setup Instructions

```bash
# Navigate to customer UI directory
cd src/ui/customer

# Initialize React + Vite project
npm create vite@latest . -- --template react

# Install dependencies
npm install react-router-dom axios lucide-react js-yaml

# Install Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Start development server
npm run dev
```

### 11.2 Configuration File

Create `customer-portal-config.yaml`:

```yaml
api:
  base_url: "http://localhost:8000/api/v1"
  timeout: 30000

mock:
  customer_id: 100
  auth_password: "password123"

app:
  name: "Insurance Claims Portal"
  version: "1.0.0"

features:
  enable_appeal: true
  max_images_per_claim: 20
  max_image_size_mb: 10
```

**Note:** Copy this file to `public/` directory so it's accessible at runtime

### 11.3 App Initialization

The app must load configuration before rendering:

```javascript
// src/main.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { loadConfig } from './api/config';
import './index.css';

// Load config before rendering
loadConfig().then(() => {
  ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
});
```

### 11.4 Code Standards

- **Components**: Use functional components with hooks
- **Styling**: Tailwind utility classes (no inline styles)
- **API calls**: Use async/await with try/catch
- **Error handling**: Show user-friendly error messages with toast notifications
- **File naming**: PascalCase for components (Button.jsx), camelCase for utilities (formatters.js)

### 11.5 Testing Strategy

```bash
# Unit tests (future)
npm test

# E2E tests (future)
npm run test:e2e
```

---

## 12. Deployment

### 12.1 Build for Production

```bash
cd src/ui/customer
npm run build

# Output: dist/ directory with static files
```

### 12.2 Serve with FastAPI

```python
# In src/api/main.py
from fastapi.staticfiles import StaticFiles

# Mount the built React app
app.mount("/", StaticFiles(directory="src/ui/customer/dist", html=True), name="static")
```

---

**END OF DOCUMENT**
