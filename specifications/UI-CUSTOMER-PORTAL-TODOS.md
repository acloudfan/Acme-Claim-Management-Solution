# Customer Portal Implementation TODO

**Project:** AI-Powered Auto Insurance Claims - Customer Portal  
**Status:** In Progress  
**Last Updated:** 2026-05-05

---

## Overview

This document tracks the implementation progress of the Customer Portal UI, a React-based web application for policyholders to file and manage auto insurance claims with AI-powered damage assessment.

**Reference Documents:**
- Design Specification: `specifications/UI-CUSTOMER-PORTAL-DESIGN.md`
- UI Samples: `specifications/ui-sample-images/`
- API Specs: `specifications/API-SPECIFICATIONS.md`
- Quickstart Guide: `UI-PORTAL-QUICKSTART.md`

---

## Recent Changes (2026-05-05)

### ⚠️ CRITICAL: Correct Workflow - Real-Time Analysis During Upload

**IMPORTANT:** Images ARE analyzed in real-time during upload. Do NOT remove this functionality!

**CORRECT FLOW (3 steps, 4 pages):**
1. **Loss Details Form** - Capture incident information
2. **Upload Images with Real-Time Analysis** - Each image is:
   - Uploaded to backend via `POST /customers/{id}/claims/{id}/images`
   - Backend automatically runs YOLO detection during upload
   - Backend creates damage records in database
   - Frontend waits ~1.5 seconds for analysis completion
   - Frontend refetches claim via `GET /customers/{id}/claims/{id}`
   - Frontend extracts `damage_assessment.damages` array
   - Frontend filters by `image_id` to match current image filename
   - Frontend displays damages under thumbnail: `damage_part: $cost`
3. **Claim Analysis Page** (submission + estimate aggregation):
   - Page loads and fetches claim details
   - CHECK: Are there damages detected?
     - **NO DAMAGES:** 
       - Do NOT submit claim to FNOL (keep in draft so images can be re-uploaded)
       - Show error screen with two options:
         - [Try New Images] → Navigate back to upload page (claim stays draft)
         - [Submit for Human Review] → Submit claim + set status to 'human_review_pending'
     - **DAMAGES FOUND:** Continue with analysis:
       - Submit claim to FNOL (draft → FNOL) - now that damages exist
       - Calls `POST /claims/{id}/estimate` with all image IDs
       - Backend aggregates individual damage detections into final estimate
       - Backend calculates average confidence and routes based on threshold (0.55)
       - Polls for status = 'loss_estimated_ai', 'human_review_pending', or 'customer_decision_pending'
       - Auto-redirects to Claim Detail Page when complete
4. **View Results** - Show complete estimate with all damages and annotated images

**Why Real-Time Analysis Matters:**
- ✅ Immediate user feedback - users see damages as they upload
- ✅ Backend already performs YOLO during upload (architecture design)
- ✅ Better UX - users know analysis is working
- ✅ Prevents "waiting in the dark" syndrome
- ✅ Matches actual backend implementation

**Backend Architecture (CRITICAL TO UNDERSTAND):**
- `POST /customers/{id}/claims/{id}/images` → Uploads file AND runs YOLO analysis automatically
- YOLO creates damage records immediately in database
- `GET /customers/{id}/claims/{id}` → Returns `damage_assessment` with nested `damages` array
- ⚠️ **Images are NOT stored separately** - they exist as `image_id` field in each damage record
- ⚠️ **Field name is `image_id`, NOT `image_filename`** - this contains the filename
- To get image IDs: Extract unique `image_id` values from `damage_assessment.damages` array
- `POST /claims/{id}/estimate` → Requires `claim_id` + `image_ids` + `state` in request body
  - Yes, `claim_id` must be in BOTH URL path AND request body (API design)

**Data Structure Reference:**
```javascript
// Claim response from GET /customers/{id}/claims/{id}
{
  claim_id: 123,
  current_status: "draft",
  damage_assessment: {
    total_estimated_cost: 3250.00,
    damage_count: 2,
    damages: [  // Array of damage detections
      {
        damage_id: 1,
        damage_part: "front-bumper",
        damage_type: "dent",
        image_id: "image1.jpg",  // ← Filter by this (filename)
        estimated_total_cost: 1750.00,
        severity: 0.8,
        ...
      }
    ]
  }
}
```

**Implementation Status:**
- Phase 4: Image upload WITH real-time analysis display ✅ (RESTORED 2026-05-05)
- Phase 4.5: Claim submission + estimate aggregation ✅ (COMPLETED 2026-05-05)
- Phase 5: Claim detail with accept/appeal actions (IN PROGRESS)

---

## Phase 1: Authentication & Home Page

**Goal:** Basic app structure with login and home page

### Setup & Infrastructure
- [x] Initialize Vite + React project in `src/ui/customer/`
- [x] Install dependencies (react-router-dom, axios, lucide-react, js-yaml, tailwindcss)
- [x] Configure Tailwind CSS with custom color palette (#2563eb - insurance blue)
- [x] Create `customer-portal-config.yaml` configuration file
- [x] Set up project directory structure (components, pages, api, utils, hooks, context)
- [x] Configure Vite for development and production builds

### Configuration & API Client
- [x] Create config loader (`src/api/config.js`) for YAML configuration
- [x] Create Axios API client (`src/api/client.js`) with interceptors
- [x] Create API functions module (`src/api/customers.js`, `src/api/claims.js`, `src/api/images.js`)
- [x] Set up AuthContext for authentication state management

### Common Components
- [x] Button component (primary, secondary, danger, ghost variants)
- [x] Card component
- [x] Input component (text, password, with error handling)
- [x] Spinner/Loading component
- [x] Badge component (status indicators with color variants)

### Layout Components
- [x] Header component (logo, welcome message, logout button)
- [x] Footer component
- [x] Layout wrapper component

### Pages
- [x] Login Page
  - [x] Login form with email/phone and password fields
  - [x] Mock authentication (password: "password123")
  - [x] Store customer_id in localStorage
  - [x] Redirect to home page on success
  - [x] Styled with insurance-blue gradient background

- [x] Home Page
  - [x] Welcome banner with customer name
  - [x] Policy cards grid (auto + fake home policy)
  - [x] Fetch customer data from API: `GET /api/v1/customers/100`
  - [x] Fetch policies from API: `GET /api/v1/customers/100/policies`
  - [x] Display fake home insurance policy (hardcoded, non-clickable)
  - [x] Display active auto policy (clickable → PolicyPage)
  - [x] Pending actions alert banner (for claims needing decision)
  - [x] Error handling and loading states

### Routing
- [x] Set up React Router with routes: `/login`, `/`
- [x] Protected route wrapper (redirect to login if not authenticated)
- [x] Navigation between pages
- [x] Config loading before app render

### Testing & Documentation
- [ ] Manual test: Login flow works
- [ ] Manual test: Home page displays customer data and policies
- [ ] Manual test: Navigation between pages
- [ ] Update `UI-PORTAL-QUICKSTART.md` with any additional setup notes
- [ ] Update this TODO with final status

**Status:** 🟡 Implementation Complete - Awaiting Testing

---

## Phase 2: Policy Details & Navigation

**Goal:** View policy details, vehicles, claims history, and policy management actions

### Components
- [x] PolicyCard component (displays policy summary) - *Fixed onClick handler*
- [x] VehicleCard component (displays vehicle details with VIN, make, model, color)
- [x] PolicyActionCard component (reusable action card with hover effects)
- [ ] ClaimListItem component (displays claim summary in history) - *Not needed - using table*
- [ ] Breadcrumb navigation component - *Deferred*

### Pages
- [x] Policy Detail Page (`/policy/:policyNumber`)
  - [x] Display policy information (dates, premium, coverage)
  - [x] Display detailed coverage limits (bodily injury, property damage, deductible)
  - [x] Quick Actions section with policy management options
    - [x] File a Claim (primary action - blue, functional)
    - [x] Pay Premium & Renewals (placeholder)
    - [x] Add/Remove Vehicles (placeholder)
    - [x] Update Drivers (placeholder)
    - [x] Adjust Coverage (placeholder)
  - [x] Display covered vehicles grid
  - [x] Display claims history table with status badges
  - [x] Click claim row → navigate to ClaimDetailPage (route ready)
  - [x] Back button → navigate to HomePage
  - [x] Fetch policy: `GET /api/v1/customers/100/policies/{policyNumber}`
  - [x] Fetch claims: `GET /api/v1/customers/100/claims` (filtered by policy)
  - [x] Professional styling with hover effects and responsive grid

### Navigation
- [x] Back button functionality (arrow icon + text)
- [x] Policy page route added to App.jsx (`/policy/:policyNumber`)
- [x] Navigation from HomePage to PolicyPage (click policy card)
- [x] Navigation from PolicyPage to NewClaimPage (File Claim action)
- [ ] Breadcrumb navigation on all pages - *Deferred to Phase 6*
- [ ] Active route highlighting in header - *Deferred to Phase 6*

### Bug Fixes
- [x] Fixed Card component to accept and pass onClick prop
- [x] Fixed PolicyCard to properly handle policy clicks
- [x] Fixed date field mismatch (start_date/end_date vs effective_date/expiration_date)
- [x] Added policy_type field to PolicyResponse schema (defaulting to "auto")
- [x] Added fetchCustomerClaims function to customers.js API

### Testing
- [x] Manual test: Policy page displays all information correctly
- [x] Manual test: Vehicle cards render properly
- [x] Manual test: Claims history table displays correctly with status badges
- [x] Manual test: Navigation flows work (Home → Policy → back to Home)
- [x] Manual test: Quick Actions section renders with proper styling
- [x] Manual test: File Claim action navigates correctly (ready for Phase 3)
- [x] Manual test: Placeholder actions show alerts
- [x] Update this TODO with completion status

### Documentation Updates
- [x] Updated `UI-CUSTOMER-PORTAL-DESIGN.md` section 7.3 with Quick Actions
- [x] Documented all 5 policy actions with rationale and descriptions
- [x] Updated layout diagram to show Quick Actions section
- [x] Documented PolicyActionCard component specifications
- [x] Updated this TODO file with Phase 2 completion

**Status:** ✅ Complete (with placeholder actions ready for future implementation)

---

## Phase 3: New Claim Workflow (Critical Path)

**Goal:** File new claim with loss details form (Step 1 of 2)

### Components
- [x] ProgressBar component (show step progress with percentage and step labels)
- [x] DatePicker component (for loss date) - *Using native HTML5 date input*
- [x] RadioGroup component (Yes/No questions with custom styling)
- [x] Textarea component (loss description with label and error handling)
- [x] Form validation utilities - *Inline validation in component*

### Pages
- [x] New Claim Page - Step 1: Loss Details (`/claims/new`)
  - [x] Loss event description textarea (required, clears error on input)
  - [x] Loss event date picker (required, validates not in future)
  - [x] "Is vehicle drivable?" radio buttons (Yes/No)
  - [x] "Do you have damage photos?" radio buttons (Yes/No)
  - [x] Form validation (all required fields, date validation)
  - [x] Progress indicator (Step 1 of 2 - 50%) with visual bar
  - [x] Cancel button → navigate back to PolicyPage
  - [x] Continue button → creates draft claim via API
  - [x] Create draft claim via API: `POST /api/v1/customers/100/claims`
  - [x] Display vehicle information from policy
  - [x] Professional styling with Insurance Blue theme
  - [x] Error message display with AlertCircle icon
  - [x] Loading/submitting states

### API Integration
- [x] Created `createClaim` API function in `customers.js`
- [x] Created `submitClaim` API function in `customers.js` (ready for Phase 4)
- [x] Handle API errors and display user-friendly messages
- [x] Claim ID returned from API (ready for Step 2)
- [x] Auto-select first vehicle from policy
- [x] Generate FNOL date and time automatically

### Form State Management
- [x] Use React hooks for form state (useState)
- [x] Form validation before API call
- [x] Clear field errors on input change
- [x] Error state for each field
- [x] Disable submit button during API call
- [x] Query params to pass policy number (`?policy={policyNumber}`)

### Navigation & Routing
- [x] Added `/claims/new` route to App.jsx
- [x] Protected route (requires authentication)
- [x] Back button to Policy Page
- [x] Cancel button to Policy Page
- [x] Navigation from Policy Page "File Claim" action

### Testing
- [x] Manual test: Form validation works (all required fields)
- [x] Manual test: Date validation (cannot be in future)
- [x] Manual test: Error messages display correctly
- [x] Manual test: Draft claim is created via API
- [x] Manual test: Cancel button returns to policy page
- [x] Manual test: Loading states work correctly
- [x] Manual test: Policy information displays correctly
- [x] Manual test: Success alert shown (placeholder for Step 2)
- [x] Update this TODO with completion status

### Notes
- Step 2 (Image Upload) will be implemented in Phase 4
- Currently shows success alert and returns to policy page after claim creation
- Form data structure matches API requirements exactly
- Vehicle auto-selected from policy (first vehicle in list)

**Status:** ✅ Complete (Integrated with Phase 4 Image Upload)

---

## Phase 4: Image Upload with Real-Time Analysis (Step 2 of 3)

**Goal:** Upload damage photos with immediate YOLO-based damage detection display

### Components
- [x] ImageUploadPage component (complete page, not separate components)
  - [x] Drag & drop zone
  - [x] File input (click to browse)
  - [x] File validation (type, size)
  - [x] Multiple file support (max 20 images)
  - [x] Upload progress bars (per image with percentage)
  - [x] Image thumbnails grid (responsive 1-3 columns)
  - [x] Remove file button (for error states)
  - [x] Status indicators per file (pending, uploading, analyzing, analyzed, error)
  - [x] Inline thumbnail previews using createObjectURL
  - [x] Success/error icons (CheckCircle, XCircle, Loader)

### Pages
- [x] Image Upload Page - `/claims/{claimId}/upload`
  - [x] Progress indicator (Step 2 of 3 - 67%)
  - [x] Drag & drop image upload zone with hover effects
  - [x] Display "Supported: JPG, PNG, HEIC • Max size: 10MB • Max images: 20"
  - [x] Grid of uploaded image thumbnails
  - [x] Show upload progress for each image (with percentage)
  - [x] Show "Analyzing..." status while backend runs YOLO
  - [x] Display detected damages under each thumbnail (damage_part + cost)
  - [x] Display status under each thumbnail (analyzed, error, etc.)
  - [x] Back button → return to previous page
  - [x] Continue button (NOT Submit Claim) with validation
  - [x] Professional insurance-blue styling

### API Integration
- [x] Upload image API: `POST /api/v1/customers/{customerId}/claims/{claimId}/images`
- [x] Created `uploadClaimImage` function with FormData and progress tracking
- [x] Track upload progress with `onUploadProgress` callback
- [x] Handle API errors (file too large, duplicate filename, max images reached)
- [x] Created `fetchClaimDetail` API function
- [x] Fetch claim with damages: `GET /api/v1/customers/{customerId}/claims/{claimId}`
- [x] Access damages via `claim.damage_assessment.damages` array

### Image Upload Flow with Real-Time Analysis
- [x] Upload images sequentially (one-by-one with status tracking)
- [x] Update UI with real-time progress per file
- [x] Status flow: pending → uploading → analyzing → analyzed
- [x] After upload completes:
  - [x] Wait 1.5 seconds for backend YOLO processing
  - [x] Refetch claim via `fetchClaimDetail()` 
  - [x] Extract `damage_assessment.damages` array
  - [x] Filter damages by `image_id` matching uploaded filename
  - [x] Display damages under thumbnail (damage_part + estimated_total_cost)
- [x] Show "No damage detected" if damages array is empty for that image
- [x] Allow removing images in error state
- [x] Prevent continue button during active uploads or analysis

### Navigation to Submission Page
- [x] Validation before continuing (at least 1 image, no errors, all analyzed)
- [x] Continue button navigates to Submission Page: `/claims/{claimId}/submit`
- [x] No claim submission on this page - just navigation
- [x] Damages already detected and stored in database
- [x] Next page will submit claim and aggregate damages into final estimate

### Routing & Navigation
- [x] Added `/claims/:claimId/upload` route to App.jsx
- [x] Protected route (requires authentication)
- [x] Navigation from NewClaimPage after draft creation
- [x] Back button to return to previous page (loss details)
- [x] Continue button navigates to ClaimAnalysisPage (Phase 4.5)

### Testing
- [x] Manual test: Click to browse file upload works
- [x] Manual test: File validation (max 20 images)
- [x] Manual test: Upload progress displays correctly
- [x] Manual test: Status transitions work (pending → uploading → analyzing → analyzed)
- [x] Manual test: Damage detection displays under thumbnails after analysis
- [x] Manual test: Multiple damages show correctly for single image
- [x] Manual test: "No damage detected" message for images without damage
- [x] Manual test: Error handling works (display error status)
- [x] Manual test: Remove file button works
- [x] Manual test: Continue button validation (requires all images analyzed)
- [x] Manual test: Continue button navigates to submission page
- [x] Manual test: Refetch claim works and damages display correctly
- [x] Update this TODO with completion status

### Notes
- ✅ Images ARE analyzed in real-time during upload (backend automatic)
- ✅ YOLO runs on backend during `POST /images` endpoint
- ✅ Frontend displays detected damages immediately after each upload
- ⚠️ DO NOT remove analysis display - it's a core feature
- Next page (Phase 4.5) handles claim submission and estimate aggregation

### Documentation Updates
- [x] Updated UI-CUSTOMER-PORTAL-DESIGN.md section 7.4 (2026-05-05)
- [x] Restored real-time analysis display in layout diagram
- [x] Updated implementation details with correct data flow
- [x] Updated user flow in section 6.2 to show analysis during upload
- [x] Added CRITICAL warnings to prevent future removal

**Status:** ✅ Complete (RESTORED real-time analysis - 2026-05-05)

---

## Phase 4.5: Claim Submission & Estimate Aggregation (Step 3 of 3)

**Goal:** Submit claim, generate aggregate estimate, and show processing progress

**IMPORTANT:** Damage detection has ALREADY been completed in Phase 4. This page only:
1. Submits the claim (draft → FNOL)
2. Aggregates individual damage detections into a final estimate record
3. Polls for completion

### Components
- [x] ClaimAnalysisPage component (full page, no sub-components needed)
  - [x] Progress indicator (Step 3 of 3 - 100%)
  - [x] Centered card with spinner animation
  - [x] Progress steps with status icons (completed ✅, in_progress 🔄, pending ⏳)
  - [x] Styled with insurance blue theme

### Pages
- [x] Claim Analysis Page - `/claims/:claimId/submit`
  - [x] Progress indicator (Step 3 of 3 - 100%)
  - [x] Centered card with large spinner
  - [x] Page title: "Analyzing Your Claim..." (actually: "Processing Your Claim")
  - [x] Subtitle: "Our AI is analyzing..." (updated to reflect aggregation)
  - [x] Time estimate: "This typically takes 10-30 seconds..."
  - [x] Progress steps display:
    - [x] ✅ Images uploaded and analyzed (2)
    - [x] ✅ Damage detection complete
    - [x] 🔄 Aggregating repair costs...
    - [x] ⏳ Generating estimate report...
  - [x] Auto-submit claim on page load
  - [x] Call generateEstimate API to aggregate damages
  - [x] Poll for completion every 2 seconds
  - [x] Check status = 'loss_estimated_ai' or 'customer_decision_pending'
  - [x] Auto-redirect to Claim Detail Page when complete
  - [x] Error handling with retry button if submission/aggregation fails

### API Integration
- [x] Auto-submit on mount: `POST /api/v1/customers/{customerId}/claims/{claimId}/submit`
- [x] Fetch claim to get image IDs: `GET /api/v1/customers/{customerId}/claims/{claimId}`
- [x] Generate aggregate estimate: `POST /api/v1/claims/{claimId}/estimate`
  - [x] Pass `image_ids` array (extracted from claim.images)
  - [x] Pass `state` parameter for labor rates (default: 'CA')
- [x] Poll claim status: `GET /api/v1/customers/{customerId}/claims/{claimId}`
- [x] Check for status: 'loss_estimated_ai' or 'customer_decision_pending'
- [x] Handle error status (show error message with retry)
- [x] Created `generateEstimate()` function in `customers.js` API module
- [ ] **NEW: Auto-assign to adjustor if status is 'human_review_pending'**
  - [ ] Create `src/api/adjustors.js` module with:
    - [ ] `fetchAdjustors()` - Get all adjustors with workload
    - [ ] `assignClaimToAdjustor(adjustorId, claimId)` - Assign claim
    - [ ] `autoAssignClaim(claimId)` - Find adjustor with shortest queue and assign
  - [ ] In ClaimAnalysisPage, after polling completes:
    - [ ] Check if status is 'human_review_pending'
    - [ ] Call `autoAssignClaim(claimId)` to assign to adjustor
    - [ ] Log assignment result (non-blocking, failure is acceptable)
    - [ ] Optional: Show toast notification with adjustor name
  - [ ] See section 9.5 in UI-CUSTOMER-PORTAL-DESIGN.md for implementation details

### Submission & Aggregation Flow
```javascript
useEffect(() => {
  const submitAndGenerateEstimate = async () => {
    try {
      // 1. Submit the claim (draft → FNOL)
      await submitClaim(customerId, claimId);
      
      // 2. Get claim details to fetch image IDs
      const claimResponse = await fetchClaimDetail(customerId, claimId);
      const claim = claimResponse.data;
      
      // IMPORTANT: Images are NOT in claim.images - extract from damages
      // Field name is image_id (contains the filename)
      let imageIds = [];
      if (claim.damage_assessment?.damages) {
        const ids = claim.damage_assessment.damages
          .map(d => d.image_id)
          .filter(id => id != null && id !== '');
        imageIds = Array.from(new Set(ids));
      }
      
      // 3. Generate aggregate estimate (combines all damage detections)
      await generateEstimate(claimId, {
        image_ids: imageIds,
        state: 'CA'
      });
      
      // 4. Poll for estimate completion
      const pollInterval = setInterval(async () => {
        const response = await fetchClaimDetail(customerId, claimId);
        const claim = response.data;
        
        // Check if estimate is ready
        if (claim.current_status === 'loss_estimated_ai' || 
            claim.current_status === 'customer_decision_pending') {
          clearInterval(pollInterval);
          navigate(`/claims/${claimId}`);
        }
      }, 2000);
      
    } catch (error) {
      setError('Failed to submit claim');
    }
  };
  
  submitAndAnalyze();
}, [claimId]);
```

### Progress State Management
- [x] Track steps with status (completed, in_progress, pending)
- [x] Update step status after each API call
- [x] Animate spinner during processing
- [x] Show step icons based on status (✅🔄⏳)

### User Experience
- [x] No back button (submission in progress)
- [x] No cancel button (claim is being processed)
- [x] Automatic redirect when complete
- [x] Clear error messages if failure occurs
- [x] Retry button on error state with full workflow restart

### Routing & Navigation
- [x] Added `/claims/:claimId/submit` route to App.jsx
- [x] Protected route (requires authentication)
- [x] Navigation from ImageUploadPage (Continue button)
- [x] Auto-redirect to ClaimDetailPage on success

### Testing
- [x] Manual test: Page auto-submits claim on load
- [x] Manual test: generateEstimate API is called with correct image IDs
- [x] Manual test: Spinner and progress messages display
- [x] Manual test: Polling updates claim status
- [x] Manual test: Auto-redirect works when aggregation completes
- [x] Manual test: Error handling with retry button
- [x] Manual test: Progress steps update correctly
- [x] Manual test: Console logs show correct status values
- [x] Update this TODO with completion status

### Notes
- ✅ Damage detection ALREADY completed in Phase 4 (during upload)
- ✅ This page only aggregates detections into final estimate
- ✅ Page is fully automatic - no user interaction required
- ✅ User cannot go back once submission starts
- ✅ Polling interval: 2 seconds
- ✅ Estimate generation typically takes 5-10 seconds
- ✅ Console logging added for debugging status transitions

### Documentation Updates
- [x] Added section 7.4.1 to UI-CUSTOMER-PORTAL-DESIGN.md (2026-05-05)
- [x] Documented ClaimAnalysisPage layout and implementation
- [x] Updated user flow in section 6.2
- [x] Added ClaimAnalysisPage.jsx to project structure
- [x] Clarified that this page aggregates, not analyzes

**Status:** ✅ Complete (Implemented 2026-05-05)

---

## Phase 5: Claim Review & Decision (After Analysis)

**Goal:** View completed AI assessment with annotated images and accept/appeal estimates

### Components
- [ ] DamageCard component
  - [ ] Display damage part name
  - [ ] Show annotated image with bounding boxes
  - [ ] BoundingBoxViewer with toggle (original ↔ annotated)
  - [ ] Severity indicator (light/moderate/severe)
  - [ ] Internal damage probability
  - [ ] Recommended action
  - [ ] AI reasoning text
  - [ ] Cost breakdown (labor + parts)

- [ ] BoundingBoxViewer component
  - [ ] Display image (original or annotated)
  - [ ] Toggle button to switch between original and annotated
  - [ ] Eye/EyeOff icons from lucide-react

- [ ] ClaimTimeline component
  - [ ] Display event history as timeline
  - [ ] Event icons (customer, AI, adjustor, admin)
  - [ ] Event timestamps
  - [ ] Event descriptions

- [ ] ConfirmationDialog component (reusable)
  - [ ] Modal overlay
  - [ ] Title, message, action buttons
  - [ ] Confirm/Cancel buttons

- [ ] AppealDialog component
  - [ ] Modal with textarea for appeal reason
  - [ ] Placeholder text with examples
  - [ ] Submit/Cancel buttons

### Pages
- [x] Claim Detail Page (`/claims/:claimId`) - PARTIALLY COMPLETE
  - [x] Display claim status with badge
  - [x] AI Damage Assessment section
    - [x] Total estimated cost (sum of all damages)
    - [x] Damage count across images
  - [x] Group damages by image
  - [x] Display annotated images with bounding boxes
  - [x] DamageCard for each detected damage
  - [x] Accept Estimate button (placeholder)
  - [x] Appeal Estimate button (placeholder)
  - [x] Human review pending notice
  - [x] No damage detected handling
  - [x] **Claim Details Card** (NEW - 2026-05-06)
    - [x] Display vehicle information (year, make, model, VIN, color)
    - [x] Display policy summary (policy number, deductibles, coverage limits)
    - [x] Display event details (incident date, report date/time, drivability)
    - [x] Display customer's incident description
    - [x] Non-editable (read-only display)
    - [x] Positioned between AI estimate and "What Happens Next?" sections
    - [x] Fetch policy: `GET /api/v1/customers/{customerId}/policies/{policyNumber}`
    - [x] Match vehicle by VIN from policy.vehicles array
  - [ ] **TODO: Claim Summary View** for non-AI statuses (traditional processing, routed_to_traditional, etc.)
  - [ ] Claim Timeline section (event history)
  - [ ] Progress bar showing state machine flow
  - [x] Fetch claim: `GET /api/v1/customers/100/claims/{claimId}`
  
- [x] Policy Page - View Button Behavior
  - [x] If claim status = `draft` → Navigate to edit mode (`/claims/{id}/edit`)
  - [x] If claim status ≠ `draft` → Navigate to claim detail (`/claims/{id}`)
  - [ ] **TODO: Handle claims in non-AI statuses** (show appropriate summary/message)

- [ ] Save Draft Functionality
  - [ ] Add "Save Draft" button to NewClaimPage (loss details form)
  - [ ] Add "Save Draft" button to ImageUploadPage
  - [ ] Save Draft on NewClaimPage: Create/update claim in draft, navigate to Policy page
  - [ ] Save Draft on ImageUploadPage: Navigate to Policy page (claim already saved)
  - [ ] Show success message when draft saved

### Image Serving Integration
- [ ] Implement `getImageUrl()` helper function
- [ ] Fetch original image: `GET /api/v1/customers/100/claims/{claimId}/images/{imageId}`
- [ ] Fetch annotated image: `GET /api/v1/customers/100/claims/{claimId}/images/{imageId}?annotated=yes`
- [ ] Display images in BoundingBoxViewer

### Accept Estimate Flow
- [ ] Click "Accept Estimate" button
- [ ] Call API: `POST /api/v1/customers/100/claims/{claimId}/accept`
- [ ] Show success toast notification
- [ ] Refresh claim data to show updated status
- [ ] Display new status: "Sent for Payment"

### Appeal Estimate Flow
- [ ] Click "Appeal Estimate" button
- [ ] Show AppealDialog modal
- [ ] User enters appeal reason (required)
- [ ] Call API: `POST /api/v1/customers/100/claims/{claimId}/appeal`
- [ ] **NEW: Auto-assign to adjustor after appeal:**
  - [ ] After appeal API succeeds, claim status becomes 'human_review_pending'
  - [ ] Call `autoAssignClaim(claimId)` from `src/api/adjustors.js`
  - [ ] If assignment succeeds, show toast: "Your appeal has been submitted for review by [adjustor name]"
  - [ ] If assignment fails (non-blocking), show generic message: "Your appeal has been submitted for human review"
  - [ ] See section 9.5 in UI-CUSTOMER-PORTAL-DESIGN.md for implementation details
- [ ] Refresh claim data to show updated status
- [ ] Display new status: "Human Review Pending"

### Testing
- [ ] Manual test: Claim detail page displays all information
- [ ] Manual test: DamageCards render with all fields
- [ ] Manual test: BoundingBoxViewer toggle works (original ↔ annotated)
- [ ] Manual test: Images load correctly from API
- [ ] Manual test: Accept estimate flow works end-to-end
- [ ] Manual test: Appeal estimate flow works end-to-end
- [ ] Manual test: Timeline displays event history
- [ ] Manual test: Status updates after accept/appeal
- [ ] Update this TODO with completion status

**Status:** 🔴 Not Started

---

## Phase 6: Polish & Refinement

**Goal:** Final UI polish, error handling, and responsive design

### Error Handling
- [ ] Global error boundary component
- [ ] API error interceptor with user-friendly messages
- [ ] Toast notification system (success, error, info, warning)
- [ ] 404 Not Found page
- [ ] Network error handling (offline detection)
- [ ] Form validation error messages

### Loading States
- [ ] Skeleton loaders for cards
- [ ] Spinner for page loads
- [ ] Loading states for buttons (prevent double-click)
- [ ] Image loading placeholders
- [ ] Optimistic UI updates

### Status Badges & Indicators
- [ ] Claim status badge component (color-coded)
- [ ] Status icon mapping (draft, FNOL, estimated, pending, approved, paid, etc.)
- [ ] Severity badges (light/moderate/severe)
- [ ] Confidence indicators (high/medium/low)

### Responsive Design
- [ ] Test on different screen sizes (desktop focus)
- [ ] Ensure images scale properly
- [ ] Responsive grid layouts
- [ ] Mobile-friendly navigation (future enhancement)

### Accessibility
- [ ] ARIA labels for interactive elements
- [ ] Keyboard navigation support
- [ ] Focus states for buttons/inputs
- [ ] Alt text for images
- [ ] Color contrast compliance

### Performance Optimization
- [ ] Image lazy loading
- [ ] Code splitting by route
- [ ] Memoize expensive computations
- [ ] Debounce search/filter inputs
- [ ] Optimize bundle size

### Visual Polish
- [ ] Smooth transitions and animations
- [ ] Hover states for interactive elements
- [ ] Consistent spacing and alignment
- [ ] Typography hierarchy
- [ ] Icon consistency (lucide-react)
- [ ] Custom scrollbars (optional)

### Documentation
- [ ] Update `UI-PORTAL-QUICKSTART.md` with final setup
- [ ] Add troubleshooting section
- [ ] Document environment variables
- [ ] Add screenshots to documentation

### Testing & Validation
- [ ] Test all user flows end-to-end
- [ ] Test error scenarios (API failures, network issues)
- [ ] Test with different data states (no claims, multiple claims, etc.)
- [ ] Verify API integration with backend
- [ ] Cross-browser testing (Chrome, Firefox, Safari, Edge)
- [ ] Performance testing (Lighthouse audit)

### Final Checklist
- [ ] All phases 1-5 are complete and tested
- [ ] No console errors or warnings
- [ ] All images and assets load correctly
- [ ] Configuration file is properly documented
- [ ] Quickstart guide is accurate and complete
- [ ] Code is clean and well-commented
- [ ] Production build works (`npm run build`)

**Status:** 🔴 Not Started

---

## Future Enhancements (Out of Scope)

- [ ] Multiple customer support (login with different accounts)
- [ ] Mobile responsive design (full support)
- [ ] Progressive Web App (PWA) features
- [ ] Real-time notifications (WebSocket)
- [ ] Multi-language support (i18n)
- [ ] Dark mode theme
- [ ] Downloadable claim reports (PDF)
- [ ] Email notifications
- [ ] SMS notifications
- [ ] Payment integration
- [ ] Document upload (non-image files)
- [ ] Video upload support
- [ ] Live chat support
- [ ] Claim comments/notes
- [ ] Claim editing after submission
- [ ] Claim cancellation
- [ ] Policy management (update coverage, add vehicles)
- [ ] User profile editing
- [ ] Password reset flow
- [ ] Two-factor authentication

---

## Notes & Decisions

### Color Palette Decision
- Using a custom blue palette inspired by insurance industry standards
- Avoiding exact GEICO colors to prevent brand confusion
- Primary blue: TBD (slightly different from #0046BE)

### Mock Data Strategy
- Hardcoded Customer ID: 100
- Fake home insurance policy: POL-Home-1234 (non-interactive)
- Real auto policy data from API

### Technology Choices
- React 18 (functional components with hooks)
- Vite (build tool)
- Tailwind CSS (styling)
- Axios (HTTP client)
- lucide-react (icons)
- js-yaml (config parsing)
- No state management library (React Context only)

### File Structure Convention
- PascalCase for components (Button.jsx)
- camelCase for utilities (formatters.js)
- kebab-case for config files (customer-portal-config.yaml)

---

## Changelog

### 2026-05-06
- **NEW FEATURE:** Claim Details Card on Claim Detail Page (Phase 5)
  - Created ClaimDetailsCard component (`src/ui/customer/src/components/claims/ClaimDetailsCard.jsx`)
  - Displays vehicle information, policy summary, event details, and incident description
  - Non-editable (read-only) presentation
  - Positioned between AI Damage Assessment and "What Happens Next?" sections
  - Integrated into ClaimDetailPage with policy data fetching
  - Updated UI-CUSTOMER-PORTAL-DESIGN.md with layout diagram and implementation details
  - Created comprehensive documentation: CLAIM-DETAILS-CARD-IMPLEMENTATION.md

### 2026-05-05 (CRITICAL UPDATE - RESTORED REAL-TIME ANALYSIS + IMAGE ID FIX)
- **CRITICAL FIX:** Restored real-time damage analysis display on ImageUploadPage
- **CRITICAL FIX:** Fixed image ID extraction in ClaimAnalysisPage
  - Images are NOT in `claim.images` - they're in damage records as `image_id` field
  - Field name is `image_id`, NOT `image_filename` (contains the filename)
  - Extract unique IDs: `damage_assessment.damages.map(d => d.image_id)`
  - Filter out null/empty values before creating Set
  - Use Set to get unique filenames (multiple damages can reference same image)
- **CRITICAL FIX:** Added `claim_id` to estimate request body
  - API requires `claim_id` in BOTH URL path AND request body
  - Request: `{ claim_id: int, image_ids: string[], state: string }`
- **IMPORTANT:** Images ARE analyzed during upload (backend automatic YOLO processing)
- Updated Phase 4 to correctly reflect real-time analysis workflow
- Updated Phase 4.5 to clarify it aggregates damages, not analyzes them
- Fixed ImageUploadPage to:
  - Wait ~1.5s after upload for backend YOLO completion
  - Refetch claim via `GET /customers/{id}/claims/{id}`
  - Extract `damage_assessment.damages` array
  - Filter by `image_id` (NOT `image_filename`) to match current image filename
  - Display damages under thumbnails (damage_part + cost)
- Created ClaimAnalysisPage with:
  - Auto-submit claim (draft → FNOL)
  - Call `generateEstimate()` API to aggregate damages
  - Poll for status = 'loss_estimated_ai'
  - Auto-redirect when complete
- Added `generateEstimate()` function to customers.js API
- Updated documentation with CRITICAL warnings to prevent future removal
- Added detailed backend architecture notes
- Status flow: pending → uploading → analyzing → analyzed (RESTORED)

### 2026-05-04
- Completed Phase 1, 2, 3, and 4
- Implemented core claim filing workflow
- Added policy management actions
- Created image upload functionality

---

**Last Updated:** 2026-05-05  
**Maintained By:** Claude Code
