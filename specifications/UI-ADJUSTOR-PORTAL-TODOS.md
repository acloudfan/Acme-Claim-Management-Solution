# Adjustor Portal Implementation TODOs
## Task Breakdown for Building the Adjustor Portal UI

**Version:** 1.2  
**Date:** 2026-05-05  
**Status:** Implementation Checklist  
**Priority:** P0 (MVP), P1 (Core), P2 (Enhancement)

**Note:** For backend API and database tasks, see **[API-BACKEND-TODOS.md](./API-BACKEND-TODOS.md)**

---

## Table of Contents

1. [Frontend Setup](#frontend-setup)
2. [Authentication & Authorization](#authentication--authorization)
3. [Core UI Components](#core-ui-components)
4. [Page Implementation](#page-implementation)
5. [API Integration](#api-integration)
6. [Testing & Validation](#testing--validation)
7. [Documentation & Deployment](#documentation--deployment)

---

## Required Backend APIs

**Note:** All backend API and database implementation tasks have been moved to **[API-BACKEND-TODOS.md](./API-BACKEND-TODOS.md)**.

The adjustor portal UI requires the following backend endpoints:

| API Endpoint | Status | Document Reference |
|--------------|--------|-------------------|
| `GET /adjustors/{adjustor_id}/claims/pending` | ❌ **MISSING** | [API-BACKEND-TODOS.md](./API-BACKEND-TODOS.md) Task 4.1 |
| `GET /adjustors/{adjustor_id}/statistics` | ❌ **MISSING** | [API-BACKEND-TODOS.md](./API-BACKEND-TODOS.md) Task 4.1 |
| `POST /claims/{claim_id}/review/complete` | ❌ **MISSING** | [API-BACKEND-TODOS.md](./API-BACKEND-TODOS.md) Task 4.2 |
| `POST /claims/{claim_id}/damages` | ❌ **MISSING** | [API-BACKEND-TODOS.md](./API-BACKEND-TODOS.md) Task 4.2 |
| `PATCH /claims/{claim_id}/damages/{damage_id}` | ❌ **MISSING** | [API-BACKEND-TODOS.md](./API-BACKEND-TODOS.md) Task 4.2 |
| `GET /customers/{customer_id}/claims/{claim_id}` | ✅ **EXISTS** | Already in `customers.py` |
| `GET /customers/{customer_id}/claims/{claim_id}/events` | ✅ **EXISTS** | Already in `customers.py` |
| `GET /customers/{customer_id}/claims/{claim_id}/images` | ✅ **EXISTS** | Already in `customers.py` |

**Action Required:** Complete all backend tasks in [API-BACKEND-TODOS.md](./API-BACKEND-TODOS.md) before implementing the adjustor portal UI.

---

---

## Frontend Setup

### Phase 1: Project Initialization

#### **Task 1.1: Create Adjustor Portal Directory** (P0)
- [x] Create directory: `src/ui/adjustor/`
- [x] Initialize Vite project:
  ```bash
  cd src/ui/adjustor
  npm create vite@latest . -- --template react
  ```
- [x] Install dependencies:
  ```bash
  npm install react react-dom react-router-dom axios js-yaml lucide-react react-zoom-pan-pinch
  npm install -D tailwindcss postcss autoprefixer eslint
  ```

**Acceptance Criteria:**
- Vite dev server runs successfully
- React app renders default "Hello World"
- No errors in console

---

#### **Task 1.2: Configure Tailwind CSS (Corporate Theme)** (P0)
- [x] Run: `npx tailwindcss init -p`
- [x] Update `tailwind.config.js` with corporate color palette (see Appendix A in design doc)
- [x] Update `src/index.css`:
  ```css
  @tailwind base;
  @tailwind components;
  @tailwind utilities;
  ```
- [x] Add custom utility classes (card shadows, etc.)

**Acceptance Criteria:**
- Tailwind classes work in components
- Corporate colors available (primary-900, accent, etc.)
- Custom utilities functional

---

#### **Task 1.3: Create Project Structure** (P0)
- [x] Create directories matching customer portal structure:
  ```
  src/
  ├── api/           # API integration
  ├── assets/        # Static assets
  ├── components/    # Reusable UI components
  │   ├── common/    # Shared components (Button, Card, etc.)
  │   ├── layout/    # Header, Footer, Layout
  │   └── claims/    # Claim-specific components
  ├── context/       # AuthContext
  ├── hooks/         # Custom hooks
  ├── pages/         # LoginPage, DashboardPage, etc.
  ├── utils/         # constants, formatters, validators
  ├── App.jsx
  ├── main.jsx
  └── index.css
  ```
- [x] Create placeholder files (e.g., `README.md` in each folder)

**Note:** This folder structure MUST exactly match the customer portal at `src/ui/customer/src/` for consistency.

**Acceptance Criteria:**
- Directory structure matches customer portal exactly
- All folders exist
- No build errors

---

#### **Task 1.4: Configuration File Setup** (P0)
- [x] Create `public/adjustor-portal-config.yaml`:
  ```yaml
  api:
    base_url: "http://localhost:8000/api/v1"
    timeout: 30000
  
  auth:
    mock_password: "adjustor123"
  
  features:
    enable_zoom: true
    enable_manual_damages: true
  
  branding:
    company_name: "ACME Insurance"
    logo_path: "/src/common/assets/ACME-logo.png"
  ```
- [x] Create `src/api/config.js` to load YAML config (copy from customer portal)

**Acceptance Criteria:**
- Config loads in browser
- `config.base_url` accessible in code
- Fallback to defaults if YAML missing

---

#### **Task 1.5: Copy ACME Logo** (P0)
- [ ] Verify logo exists at `src/common/assets/ACME-logo.png`
- [ ] If building separate deployable app, copy logo to `src/ui/adjustor/public/assets/ACME-logo.png`
- [ ] Update image paths in components to reference logo correctly

**Acceptance Criteria:**
- Logo file accessible from adjustor portal
- Logo displays correctly in Header and LoginPage
- No broken image links

**Note:** Logo is already copied to shared location: `src/common/assets/ACME-logo.png`

---

---

## Authentication & Authorization

### Phase 2: Auth Context

#### **Task 2.1: Create AuthContext** (P0)
- [x] Create `src/context/AuthContext.jsx`
- [x] Implement mock authentication:
  - Hardcoded adjustor list (ADJ-001, ADJ-002, ADJ-003)
  - Hardcoded password: `adjustor123`
  - Store adjustor_id in localStorage
- [x] Export `AuthProvider` and `useAuth` hook

**Acceptance Criteria:**
- `useAuth()` returns adjustorId, adjustor, loading, login, logout, isAuthenticated
- localStorage persists adjustor_id across page refreshes
- Logout clears localStorage

---

#### **Task 2.2: Protected Routes** (P1)
- [x] Create `src/components/layout/ProtectedRoute.jsx`
- [x] Check `isAuthenticated()`
- [x] Redirect to `/login` if not authenticated

**Acceptance Criteria:**
- Unauthenticated users redirected to login
- Authenticated users can access protected pages
- No flash of protected content on redirect

---

---

## Core UI Components

### Phase 3: Shared Components (from Customer Portal)

#### **Task 3.1: Copy Common Components** (P0)
- [x] Copy from `src/ui/customer/src/components/common/`:
  - `Button.jsx`
  - `Card.jsx`
  - `Input.jsx`
  - `Textarea.jsx`
  - `Modal.jsx`
  - `Badge.jsx`
  - `Spinner.jsx`
- [x] Update colors to match corporate theme (replace primary colors)

**Acceptance Criteria:**
- All components render correctly
- Colors match corporate theme
- No console errors

---

#### **Task 3.2: Copy Utility Functions** (P0)
- [x] Copy from `src/ui/customer/src/utils/`:
  - `formatters.js` (date, currency formatting)
  - `constants.js` (status, severity enums)
- [x] Update constants if needed (add adjustor-specific statuses)

**Acceptance Criteria:**
- `formatCurrency()` works correctly
- `formatDate()` works correctly
- Constants match backend enums

---

### Phase 4: Layout Components

#### **Task 4.1: Create Header Component** (P0)
- [x] Create `src/components/layout/Header.jsx`
- [x] Design:
  - ACME Insurance logo (from `src/common/assets/ACME-logo.png`)
  - Logo size: ~120px width
  - Logo links to `/dashboard`
  - Company name: "ACME Insurance - Adjustor Portal"
  - Adjustor name display (right side)
  - Logout button
- [x] Style with corporate theme (dark primary-900 background)
- [x] Use inverted/brightened logo colors for dark background

**Acceptance Criteria:**
- Header displays ACME logo linking to dashboard
- Header displays adjustor name from AuthContext
- Logout button clears auth and redirects to login
- Header hidden on login page
- Logo colors work on dark background

---

#### **Task 4.2: Create Layout Component** (P0)
- [x] Create `src/components/layout/Layout.jsx`
- [x] Wrap pages with: Header + main content + Footer
- [x] Add responsive padding/margins

**Acceptance Criteria:**
- Layout wraps all pages except login
- Content centered with max-width
- Footer at bottom

---

#### **Task 4.3: Create Footer Component** (P1)
- [x] Create `src/components/layout/Footer.jsx`
- [x] Display: "© 2026 ACME Insurance. All rights reserved."
- [x] Include version number and subtitle: "AI-Powered Claims Adjustor Portal"

**Acceptance Criteria:**
- Footer visible on all pages
- Displays version from config

---

### Phase 5: Claim-Specific Components

#### **Task 5.1: Create ImageViewer Component** (P1)
- [x] Create `src/components/claims/ImageViewer.jsx`
- [x] Install: `npm install react-zoom-pan-pinch`
- [x] Features:
  - Zoom in/out (mouse wheel or buttons)
  - Pan (click and drag)
  - Navigate images (left/right arrows)
  - Overlay AI bounding boxes
  - Toggle boxes on/off
  - Show confidence % on hover
- [x] Use `TransformWrapper` and `TransformComponent` from library

**Acceptance Criteria:**
- Image loads and displays correctly
- Zoom/pan works smoothly
- Bounding boxes positioned accurately
- Confidence tooltip shows on hover

---

#### **Task 5.2: Create DamageList Component** (P0)
- [x] Create `src/components/claims/DamageList.jsx`
- [x] Display damages as cards with:
  - Damage type + location
  - Severity, confidence (AI only)
  - Costs breakdown (labor, parts, total)
  - [Edit] button (if editable)
- [x] Pass `onEdit` callback

**Acceptance Criteria:**
- Damages render as list
- Cost formatting correct ($1,234.00)
- Edit button triggers callback

---

#### **Task 5.3: Create DamageEditor Component** (P1)
- [x] Create `src/components/claims/DamageEditor.jsx`
- [x] Modal with form fields:
  - Labor Hours (input)
  - Labor Rate (input)
  - Parts Cost (input)
  - Adjustor Note (textarea, required if changed)
  - Total (calculated, read-only)
- [x] Validation:
  - Warn if change > 50%
  - Require note if any field changes
- [x] [Save] and [Cancel] buttons

**Acceptance Criteria:**
- Modal opens/closes correctly
- Form fields pre-filled with existing values
- Validation works (errors shown)
- Total recalculates on input change
- Save callback receives updated damage object

---

#### **Task 5.4: Create DamageCreator Component** (P1)
- [x] Create `src/components/claims/DamageCreator.jsx`
- [x] Modal with form fields:
  - Damage Type (dropdown)
  - Location (dropdown)
  - Description (textarea)
  - Severity (dropdown)
  - Image ID (dropdown, optional)
  - Labor Hours (input)
  - Labor Rate (input)
  - Parts Cost (input)
  - Adjustor Note (textarea, required)
  - Total (calculated, read-only)
- [x] Validation rules (see design doc section 11.2)
- [x] [Add Damage] and [Cancel] buttons

**Acceptance Criteria:**
- Form validates correctly
- All required fields enforced
- Total auto-calculates
- Add callback receives new damage object

---

#### **Task 5.5: Create CostSummary Component** (P1)
- [x] Create `src/components/claims/CostSummary.jsx`
- [x] Display:
  - Original AI Estimate
  - Revised Estimate
  - Difference ($ and %)
  - List of changes (added damages, adjusted damages)
- [x] Show warning badge if change > 100%

**Acceptance Criteria:**
- Calculations accurate
- Change % formatted correctly (e.g., "+109%")
- Warning badge shows when appropriate

---

#### **Task 5.6: Create NotesEditor Component** (P0)
- [x] Create `src/components/claims/NotesEditor.jsx`
- [x] Two stacked textareas:
  - Customer Note (1000 char limit)
  - Internal Note (2000 char limit)
- [x] Character counters
- [x] Validation messages

**Acceptance Criteria:**
- Both textareas functional
- Character counters update in real-time
- Max length enforced
- Error messages display below textareas

---

#### **Task 5.7: Create EventTimeline Component** (P2)
- [x] Create `src/components/claims/EventTimeline.jsx`
- [x] Vertical timeline with:
  - Date/time
  - Actor (customer, AI, adjustor)
  - Action
  - Status
  - Comments (expandable)
- [x] Color-coded bullets (blue=customer, green=AI, amber=adjustor)

**Acceptance Criteria:**
- Events render in chronological order
- Colors match actor type
- Expandable comments work

---

---

## Page Implementation

### Phase 6: Authentication Pages

#### **Task 6.1: Create LoginPage** (P0) ✅ COMPLETED IN PHASE 2
- [x] Create `src/pages/LoginPage.jsx`
- [x] Layout:
  - Centered card (max-width 400px)
  - ACME Insurance logo at top (from `src/common/assets/ACME-logo.png`)
  - Logo size: ~80-100px width
  - Title: "ACME Insurance - Adjustor Portal"
  - Adjustor ID dropdown (ADJ-001, ADJ-002, ADJ-003)
  - Password input
  - [Login] button
  - Version info at bottom
- [x] Form handling:
  - Call `useAuth().login(adjustorId, password)`
  - On success: redirect to `/dashboard`
  - On error: show error message below form
- [x] Style with corporate theme

**Acceptance Criteria:**
- Login page renders correctly with ACME logo
- Form submits on button click or Enter key
- Invalid password shows error
- Valid login redirects to dashboard
- Adjustor name persists in header

---

### Phase 7: Dashboard & Queue Pages

#### **Task 7.1: Create DashboardPage** (P0)
- [x] Create `src/pages/DashboardPage.jsx`
- [x] Sections:
  - Workload Summary (stat cards: pending, completed today, avg time)
  - Recent Pending Claims (table with 5 most recent)
  - Quick Actions (buttons: View Queue, My Stats, Help)
- [x] Fetch data:
  - `GET /adjustors/{adjustor_id}/claims/pending?limit=5`
  - `GET /adjustors/{adjustor_id}/statistics`
- [x] Click claim row → navigate to `/claims/{claim_id}/review`

**Acceptance Criteria:**
- Dashboard loads and displays data
- Stat cards show correct counts
- Recent claims table clickable
- Navigation works

---

#### **Task 7.2: Create ClaimQueuePage** (P0)
- [x] Create `src/pages/ClaimQueuePage.jsx`
- [x] Features:
  - Filter chips (All, Appeals, Low Confidence, No Damage)
  - Sort dropdown (Oldest, Highest Amount, Customer Name)
  - Search bar (claim ID, customer name, VIN)
  - Table with columns: Claim ID, Customer, Vehicle, AI Estimate, Age
  - Pagination (20 per page)
- [x] Fetch data:
  - `GET /adjustors/{adjustor_id}/claims/pending?filters...`
- [x] Click row → navigate to `/claims/{claim_id}/review`

**Acceptance Criteria:**
- Filters update query params and refetch
- Sort works correctly
- Search debounced (500ms)
- Pagination works
- Table rows clickable

---

### Phase 8: Claim Review Pages

#### **Task 8.1: Create ClaimDetailPage (Review Page)** (P0)
- [x] Create `src/pages/ClaimDetailPage.jsx`
- [x] **Layout**: 70/30 split-screen
  - **Left Panel (70%)**: Scrollable claim content
  - **Right Panel (30%)**: Fixed chatbot placeholder (for Phase 9)
- [x] Left Panel Sections:
  - Claim Overview (customer, vehicle, policy info)
  - AI Estimate Summary (total, damages count, confidence, reason for review)
  - Damage Images (ImageViewer component)
  - Damages List (DamageList component with edit/add controls)
  - Event Timeline (EventTimeline component, expandable)
  - Review Actions ([Complete Review] button)
- [ ] Right Panel:
  - Placeholder card: "AI Research Assistant - Coming Soon"
  - Message: "Natural language assistant for repair research will be available in a future release"
  - Reserve 30% width with proper styling
- [ ] Fetch data:
  - `GET /claims/{claim_id}/review` (or reuse existing endpoints)
  - `GET /customers/{customer_id}/claims/{claim_id}` (customer portal endpoint)
  - `GET /customers/{customer_id}/claims/{claim_id}/events`
  - `GET /customers/{customer_id}/claims/{claim_id}/images`
- [ ] State management:
  - Track damages array (with edits)
  - Track added damages
  - Recalculate total on changes
- [ ] Actions:
  - Edit damage → open DamageEditor modal, update state on save
  - Add damage → open DamageCreator modal, append to damages array
  - Complete Review → navigate to `/claims/{claim_id}/review/complete` with state

**Acceptance Criteria:**
- Split-screen layout renders correctly (70/30)
- Left panel scrollable, right panel fixed
- All sections render correctly in left panel
- Chatbot placeholder visible in right panel
- Data loads without errors
- Images display with zoom/pan
- Edit damage works (modal opens, saves, updates list)
- Add damage works (modal opens, creates new damage)
- Totals recalculate correctly
- Complete Review button navigates with state

---

#### **Task 8.2: Create ReviewCompletePage** (P0)
- [x] Create `src/pages/ReviewCompletePage.jsx`
- [x] Sections:
  - Cost Summary (CostSummary component)
  - Review Decision (radio buttons: Deny Appeal / Revise Estimate)
  - Customer Note (textarea, required)
  - Internal Note (textarea, required)
  - [Submit Review] and [← Back to Edit] buttons
- [x] Validation:
  - Require review decision selected
  - Require both notes filled (min 10 chars)
  - Warn if cost change > 100%
- [x] Submission:
  - Call `POST /claims/{claim_id}/review/complete`
  - Body: `{ action, customer_note, internal_note, revised_estimate_total }`
  - On success: show success toast, redirect to `/dashboard`
  - On error: show error message

**Acceptance Criteria:**
- Cost summary accurate
- Radio buttons work
- Notes validate correctly
- Submit button disabled until valid
- Confirmation modal shows before submit
- Success redirects to dashboard
- Error displays message

---

---

## API Integration

### Phase 9: API Client

#### **Task 9.1: Create API Client** (P0)
- [x] Create `src/api/client.js` (copy from customer portal)
- [x] Configure interceptors:
  - Request: Add `X-Adjustor-ID` header from localStorage
  - Response: Handle 401 (redirect to login)
- [x] Export `getApiClient()` function

**Acceptance Criteria:**
- API client configured correctly
- Headers added automatically
- 401 redirects to login

---

#### **Task 9.2: Create Adjustor API Module** (P0)
- [x] Create `src/api/adjustors.js`
- [x] Implement functions:
  - `fetchPendingClaims(adjustorId, filters)`
  - `fetchAdjustorStatistics(adjustorId)`

**Acceptance Criteria:**
- Functions return promises
- Query params formatted correctly
- Errors handled gracefully

---

#### **Task 9.3: Create Claims API Module** (P0)
- [x] Create `src/api/claims.js`
- [x] Implement functions:
  - `fetchClaimForReview(claimId)` (P1, or reuse customer endpoints)
  - `completeReview(claimId, reviewData)`
  - `addManualDamage(claimId, damageData)`
  - `updateDamageCosts(claimId, damageId, updateData)`
  - `fetchClaimEvents(claimId)` (P1, or reuse customer endpoint)

**Acceptance Criteria:**
- All functions callable
- Request bodies formatted correctly
- Responses parsed correctly

---

---

## Testing & Validation

### Phase 10: Manual Testing

#### **Task 10.1: Test Authentication Flow** (P0)
- [ ] Test login with valid credentials → redirects to dashboard
- [ ] Test login with invalid password → shows error
- [ ] Test logout → clears localStorage, redirects to login
- [ ] Test protected routes → redirects if not authenticated
- [ ] Test localStorage persistence → refresh page, still logged in

**Acceptance Criteria:**
- All auth flows work as expected
- No console errors

---

#### **Task 10.2: Test Dashboard & Queue** (P0)
- [ ] Test dashboard loads statistics and recent claims
- [ ] Test queue page loads all pending claims
- [ ] Test filters (Appeals, Low Confidence, No Damage)
- [ ] Test sort (Oldest, Highest Amount, Customer Name)
- [ ] Test search (by claim ID, customer name)
- [ ] Test pagination (next/prev buttons)
- [ ] Test click claim → navigates to review page

**Acceptance Criteria:**
- All features functional
- Data updates correctly
- Navigation works

---

#### **Task 10.3: Test Claim Review Workflow** (P0)
- [ ] Test claim detail page loads all sections
- [ ] Test image viewer (zoom, pan, bounding boxes)
- [ ] Test edit damage:
  - Open modal
  - Change labor hours
  - Add adjustor note
  - Save
  - Verify total recalculated
- [ ] Test add manual damage:
  - Open modal
  - Fill all fields
  - Save
  - Verify damage added to list
  - Verify total recalculated
- [ ] Test complete review:
  - Navigate to completion page
  - Select "Deny Appeal"
  - Fill customer note
  - Fill internal note
  - Submit
  - Verify redirects to dashboard
  - Verify claim status updated (via API or customer portal)
- [ ] Test complete review with revisions:
  - Edit 1 damage
  - Add 1 manual damage
  - Complete review → select "Revise Estimate"
  - Fill notes
  - Submit
  - Verify revised estimate total correct
  - Verify claim returned to customer

**Acceptance Criteria:**
- All workflows complete successfully
- Data persists correctly
- State transitions valid
- No console errors

---

#### **Task 10.4: Test Edge Cases** (P1)
- [ ] Test with claim that has 0 damages (no damage detected)
- [ ] Test with claim that has 10+ damages (long list)
- [ ] Test with invalid claim ID (404 error)
- [ ] Test with network failure (offline, API down)
- [ ] Test with extremely large cost change (>100%)
- [ ] Test validation errors (empty notes, invalid labor hours)

**Acceptance Criteria:**
- Errors handled gracefully
- User-friendly error messages
- No crashes

---

### Phase 11: End-to-End Testing (P2)

#### **Task 11.1: E2E Test: Full Review Workflow** (P2)
- [ ] Use Cypress or Playwright
- [ ] Test:
  - Login
  - Navigate to queue
  - Select claim
  - Edit damage
  - Add manual damage
  - Complete review
  - Verify success

**Acceptance Criteria:**
- Test passes consistently
- Covers happy path

---

#### **Task 11.2: E2E Test: Deny Appeal Workflow** (P2)
- [ ] Test:
  - Login
  - Select claim
  - Review (no changes)
  - Complete review → Deny Appeal
  - Fill notes
  - Submit
  - Verify claim returned to customer with same estimate

**Acceptance Criteria:**
- Test passes
- Claim status correct

---

---

## Documentation & Deployment

### Phase 12: Documentation

#### **Task 12.1: Create README.md** (P1)
- [ ] Create `src/ui/adjustor/README.md`
- [ ] Sections:
  - Overview
  - Setup instructions (install, config, run)
  - Login credentials (ADJ-001, password123)
  - Development workflow
  - Build for production

**Acceptance Criteria:**
- README complete and accurate
- New developer can set up portal using README

---

#### **Task 12.2: Add Inline Code Comments** (P2)
- [ ] Add JSDoc comments to exported functions
- [ ] Add comments for complex business logic
- [ ] Add TODO comments for future enhancements

**Acceptance Criteria:**
- Code readable and maintainable
- Complex sections explained

---

#### **Task 12.3: Update IMPLEMENTATION-CHECKLIST.md** (P1)
- [ ] Add adjustor portal to implementation checklist
- [ ] Mark completed tasks
- [ ] Note any deviations from original plan

**Acceptance Criteria:**
- Checklist reflects current state
- Stakeholders can track progress

---

### Phase 13: Deployment

#### **Task 13.1: Build Production Bundle** (P1)
- [ ] Run: `npm run build`
- [ ] Test production build locally: `npm run preview`
- [ ] Verify all features work in production mode

**Acceptance Criteria:**
- Build completes without errors
- Production app functional

---

#### **Task 13.2: Deploy to Hosting (P2)** (Optional)
- [ ] Choose hosting (Netlify, Vercel, AWS S3, etc.)
- [ ] Configure build settings
- [ ] Deploy
- [ ] Test deployed app

**Acceptance Criteria:**
- App accessible via public URL
- All features work in production

---

#### **Task 13.3: Configure Environment Variables** (P1)
- [ ] Create `.env.production` file:
  ```
  VITE_API_BASE_URL=https://api.insureco.com/api/v1
  ```
- [ ] Update config to use environment variables
- [ ] Test with different API URLs

**Acceptance Criteria:**
- Environment variables work correctly
- Can switch between dev/prod APIs

---

---

## AI Research Assistant (Chatbot)

### Phase 9: Chatbot Integration

#### **Task 9.1: Create ChatBot Component** (P2)
- [ ] Create `src/components/claims/ChatBot.jsx`
- [ ] Features:
  - Chat message display (user vs assistant)
  - Message history scrolling
  - Input field with send button
  - Loading indicator while waiting for response
  - Copy message button
  - Clear chat button
  - Timestamp for messages
- [ ] Design:
  - Professional chat UI
  - User messages: right-aligned, light blue background
  - Assistant messages: left-aligned, gray background
  - Avatar icons (👤 for user, 🤖 for assistant)
  - Auto-scroll to latest message

**Acceptance Criteria:**
- Chat UI renders correctly
- Messages display in chronological order
- Input field functional
- Send button triggers message submission
- Loading state shows while waiting

---

#### **Task 9.2: Create ChatBot API Integration** (P2)
- [ ] Create `src/api/chatbot.js`
- [ ] Implement function:
  - `sendChatMessage(claimId, message, conversationHistory)`
  - POST to `/chatbot/query` or integrate with LLM API
  - Include claim context (claim_id, damages, images, etc.)
  - Return assistant response
- [ ] Handle streaming responses (optional)
- [ ] Error handling for API failures

**Acceptance Criteria:**
- API calls work correctly
- Claim context included in requests
- Responses parsed and returned
- Errors handled gracefully

---

#### **Task 9.3: Integrate ChatBot into ClaimDetailPage** (P2)
- [ ] Update `src/pages/ClaimDetailPage.jsx`
- [ ] Replace placeholder in right panel with ChatBot component
- [ ] Pass claim context to chatbot:
  - Claim ID
  - Customer info
  - Vehicle info
  - Current damages
  - Images
- [ ] State management:
  - Track conversation history
  - Persist chat during session
  - Clear on page navigation (optional)
- [ ] Pre-populate suggested questions (optional):
  - "What's the typical repair time for [damage]?"
  - "What parts are needed for [vehicle]?"
  - "Is this damage covered under the policy?"

**Acceptance Criteria:**
- ChatBot replaces placeholder
- Chatbot receives claim context
- Conversation history maintained
- Questions answered with context-aware responses
- Chat persists while on same claim

---

#### **Task 9.4: Implement Chatbot Research Capabilities** (P2)
- [ ] Research domains to support:
  - **Repair Procedures**: Mitchell, AllData, OEM manuals
  - **Parts Pricing**: Aftermarket vs OEM pricing
  - **Labor Standards**: Flat rate labor times
  - **Policy Coverage**: Coverage rules, exclusions, limits
  - **Damage Assessment**: Severity guidelines, industry standards
  - **Regulatory Compliance**: State-specific requirements
- [ ] Integration options:
  - RAG (Retrieval-Augmented Generation) with knowledge base
  - API integrations with third-party data providers
  - LLM with prompt engineering for domain expertise
- [ ] Citation/source tracking for responses

**Acceptance Criteria:**
- Chatbot can answer domain-specific questions
- Responses are accurate and helpful
- Sources cited when available
- Responses tailored to current claim context

---

#### **Task 9.5: Testing & Validation** (P2)
- [ ] Test chatbot with various questions:
  - Repair procedure queries
  - Parts pricing questions
  - Labor time estimates
  - Policy coverage interpretation
  - General insurance questions
- [ ] Test error cases:
  - API failures
  - Invalid questions
  - Out-of-scope queries
- [ ] Performance testing:
  - Response time < 5 seconds
  - Handles concurrent users
- [ ] User feedback mechanism:
  - Thumbs up/down on responses
  - Report incorrect answers

**Acceptance Criteria:**
- Chatbot handles common questions correctly
- Error states handled gracefully
- Performance meets requirements
- Feedback mechanism functional

---

---

## Summary: Task Priority Matrix

**Note:** Backend tasks are in [API-BACKEND-TODOS.md](./API-BACKEND-TODOS.md)

| Priority | Phase | Tasks | Estimated Hours |
|----------|-------|-------|-----------------|
| **P0 (MVP)** | Frontend Setup | 1.1-1.4, 2.1, 3.1-3.2 | 6h |
| **P0 (MVP)** | Core Components | 4.1-4.2, 5.2, 5.6 | 8h |
| **P0 (MVP)** | Pages | 6.1, 7.1-7.2, 8.2 | 12h |
| **P0 (MVP)** | API Integration | 9.1-9.3 | 4h |
| **P0 (MVP)** | Testing | 10.1-10.3 | 6h |
| **P1 (Core)** | Components | 4.3, 5.1, 5.3-5.5 | 10h |
| **P1 (Core)** | Pages | 8.1 (with split-screen) | 10h |
| **P1 (Core)** | Testing & Docs | 10.4, 12.1-12.3, 13.1-13.3 | 8h |
| **P2 (Enhancement)** | Testing | 11.1-11.2 | 6h |
| **P2 (Enhancement)** | Components | 5.7 | 2h |
| **P2 (Enhancement)** | Chatbot | 9.1-9.5 | 20h |

**Total Estimated Hours (UI Only):** ~92 hours (11.5 days at 8h/day)

**MVP (P0 only):** ~36 hours (4.5 days)

**MVP + Core (P0 + P1):** ~64 hours (8 days)

**Full Implementation (P0 + P1 + P2):** ~92 hours (11.5 days)

**Backend Estimate:** See [API-BACKEND-TODOS.md](./API-BACKEND-TODOS.md) (~24 hours)

---

## Next Steps

1. **Complete backend API implementation first** (see [API-BACKEND-TODOS.md](./API-BACKEND-TODOS.md))
2. **Review this TODO document with stakeholders**
3. **Get approval on priorities and timeline**
4. **Start with Phase 1 (Frontend Setup)**
5. **Implement in order: Setup → Auth → Components → Pages → Integration → Testing**
6. **Deploy MVP (P0 tasks only) for initial feedback**
7. **Implement Phase 8 with split-screen layout (70/30) and chatbot placeholder**
8. **Phase 9 (Chatbot) is optional enhancement - can be deferred to future release**
9. **Iterate with P1 and P2 enhancements**

## Implementation Notes

### Split-Screen Layout (Phase 8)
- Use CSS Grid or Flexbox for 70/30 split
- Left panel: `flex: 0 0 70%` or `grid-template-columns: 70% 30%`
- Right panel: Fixed position with `position: sticky; top: 0;` to stay visible while scrolling
- Responsive: On mobile/tablet, stack vertically (left panel 100%, right panel below)

### Chatbot Placeholder (Phase 8)
- Simple card component with:
  - Robot icon 🤖
  - Title: "AI Research Assistant"
  - Subtitle: "Coming Soon"
  - Description of planned features
  - Styled to match corporate theme
- Replace placeholder with actual ChatBot component in Phase 9

---

**End of UI TODOs Document**
