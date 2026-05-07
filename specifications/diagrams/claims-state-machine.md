# Claims Processing State Machine

This document defines the state machine for AI-powered auto insurance claim processing, covering all states from initial claim creation (draft) through claim closure.

## State Diagram

> **Color Palette**: This diagram uses the standardized color scheme defined in [`color-palette-dark.css`](./color-palette-dark.css)

```mermaid
%% Color Palette: color-palette-dark.css
stateDiagram-v2
    [*] --> draft
    
    draft --> FNOL : Customer submits claim for processing
    
    FNOL --> image_uploaded : Customer uploads damage photos
    FNOL --> loss_estimated_ai : AI generates estimate directly
    
    image_uploaded --> loss_estimated_ai : AI processes images
    
    loss_estimated_ai --> customer_decision_pending : High confidence (conf > 0.55)
    
    customer_decision_pending --> loss_approved : Customer accepts estimate
    customer_decision_pending --> loss_appealed : Customer rejects estimate
    
    loss_approved --> sent_for_payment : Process payment
    
    loss_appealed --> human_review_pending : First appeal - escalate for adjuster review
    loss_appealed --> routed_to_traditional : Second appeal - route to traditional
    
    human_review_pending --> human_review_completed : Adjuster reviews claim
    
    human_review_completed --> customer_decision_pending : Present revised estimate
    human_review_completed --> routed_to_traditional : Requires traditional process
    
    sent_for_payment --> claim_paid : Payment issued
    claim_paid --> claim_closed : Payment confirmed
    
    routed_to_traditional --> traditional_processing_active : Begin traditional workflow

    state traditional_processing_active {
        [*] --> TraditionalClaimProcessing
        TraditionalClaimProcessing : Traditional claim processing
        TraditionalClaimProcessing : Manual assessment and estimation
    }

    traditional_processing_active --> claim_closed : Processing complete
    
    claim_closed --> [*]
    
    note right of traditional_processing_active
        This involves physical inspection
        of the damage by an adjustor.
    end note
    
    note right of draft
        Draft state
        Initial claim creation
        Customer can edit details
    end note
    
    note right of FNOL
        First Notice of Loss
        Claim submitted for processing
        No further edits allowed
    end note
    
    note right of loss_estimated_ai
        AI damage detection
        Confidence scoring
        Fraud/risk assessment
    end note
    
    note right of human_review_pending
        Triggered by:
        - High fraud risk (>0.1)
        - Medium confidence (0.35-0.55)
        - Customer rejection
    end note
    
    note right of human_review_completed
        Routed to traditional when:
        (a) Technical difficulties in gauging the loss
        (b) Customer rejected both AI and human-reviewed claims
    end note
    
    note right of traditional_claim_processing
        Traditional processing includes:
        - Physical inspection
        - Scheduling coordination
        - Manual estimation
    end note

    %% Color coding for state categories
    classDef draftState fill:#6C757D,stroke:#545B62,stroke-width:2px,color:#fff
    classDef initialState fill:#4A90E2,stroke:#2E5C8A,stroke-width:2px,color:#fff
    classDef aiProcessing fill:#7B68EE,stroke:#5A4DB3,stroke-width:2px,color:#fff
    classDef customerAction fill:#50C878,stroke:#3A9B5C,stroke-width:2px,color:#fff
    classDef humanReview fill:#FF8C42,stroke:#CC6F35,stroke-width:2px,color:#fff
    classDef approved fill:#28A745,stroke:#1E7E34,stroke-width:2px,color:#fff
    classDef appealed fill:#FFC107,stroke:#E0A800,stroke-width:2px,color:#000
    classDef payment fill:#20C997,stroke:#17A673,stroke-width:2px,color:#fff
    classDef traditional fill:#6C757D,stroke:#545B62,stroke-width:2px,color:#fff
    classDef scheduling fill:#9C88B5,stroke:#7A6A92,stroke-width:2px,color:#fff
    classDef terminal fill:#DC3545,stroke:#BD2130,stroke-width:2px,color:#fff

    class draft draftState
    class FNOL,image_uploaded initialState
    class loss_estimated_ai aiProcessing
    class customer_decision_pending customerAction
    class loss_approved approved
    class loss_appealed appealed
    class human_review_pending,human_review_completed humanReview
    class sent_for_payment,claim_paid payment
    class routed_to_traditional,traditional_processing_active traditional
    class claim_closed terminal
```

## Color Legend

The state diagram uses consistent color coding to represent different categories of states:

| Color | Category | States | Meaning |
|-------|----------|--------|---------|
| ⚫ **Gray (Draft)** | Draft State | draft | Claim creation in progress |
| 🔵 **Blue** | Initial States | FNOL, image_uploaded | Claim intake and data collection |
| 🟣 **Purple** | AI Processing | loss_estimated_ai | Automated damage detection and estimation |
| 🟢 **Green (Light)** | Customer Action | customer_decision_pending | Customer reviewing and making decisions |
| 🟢 **Green (Dark)** | Approved | loss_approved | Customer accepted estimate |
| 🟡 **Yellow** | Appealed | loss_appealed | Customer rejected/disputed estimate |
| 🟠 **Orange** | Human Review | human_review_pending, human_review_completed | Manual adjuster intervention |
| 🟢 **Teal** | Payment | sent_for_payment | Payment processing |
| ⚫ **Gray** | Traditional | routed_to_traditional, traditional_claim_processing | Legacy workflow path |
| 🟣 **Lavender** | Scheduling | garage_scheduling_pending, adjustor_scheduling_pending | Appointment coordination |
| 🔴 **Red** | Terminal | claim_closed | Final claim closure state |

## State Definitions

### Draft State

| State | Description | Entry Conditions |
|-------|-------------|------------------|
| **draft** | Initial claim creation state | Claim is created via API |

### Initial States

| State | Description | Entry Conditions |
|-------|-------------|------------------|
| **FNOL** | First Notice of Loss - customer submits claim | Customer submits draft claim for processing |
| **image_uploaded** | Customer has submitted damage photos | Photos uploaded via mobile app or web portal |

### AI Processing Path

| State | Description | Entry Conditions |
|-------|-------------|------------------|
| **loss_estimated_ai** | AI has analyzed images and generated damage estimate | Images successfully processed by CV model |
| **customer_decision_pending** | Customer reviewing AI estimate | High confidence estimate (>0.55) presented to customer |
| **loss_approved** | Customer accepted AI estimate | Customer confirms acceptance of estimate |
| **loss_appealed** | Customer rejected AI estimate | Customer disputes or rejects estimate |

### Human Review Path

| State | Description | Entry Conditions |
|-------|-------------|------------------|
| **human_review_pending** | Claim queued for adjuster review | Fraud risk >0.1, confidence 0.35-0.55, or customer rejection |
| **human_review_completed** | Adjuster has completed review | Adjuster provides decision/revised estimate |

### Payment & Closure Path

| State | Description | Entry Conditions |
|-------|-------------|------------------|
| **sent_for_payment** | Payment being processed | Approved claim (AI or human review) |

### Traditional Processing Path

| State | Description | Entry Conditions |
|-------|-------------|------------------|
| **routed_to_traditional** | Claim moved to traditional workflow | Low confidence (<0.35), adjuster escalation, or complex case |
| **traditional_claim_processing** | Active traditional processing | Traditional workflow initiated |
| **garage_scheduling_pending** | Scheduling garage repair appointment | Vehicle is drivable, ready for shop intake |
| **adjustor_scheduling_pending** | Scheduling field adjuster visit | Vehicle non-drivable or requires in-person inspection |

### Terminal State

| State | Description | Entry Conditions |
|-------|-------------|------------------|
| **claim_closed** | Final state - claim resolved | Payment issued, or traditional process complete |

## Transition Rules

### Draft to FNOL Transition

1. **draft → FNOL**
   - **Condition**: Customer submits claim via submit endpoint
   - **Action**: Claim enters processing workflow
   - **Event**: `submit_claim` action logged

### AI Processing Transitions

2. **loss_estimated_ai → customer_decision_pending**
   - **Condition**: Confidence score > 0.55 AND fraud risk ≤ 0.1
   - **Action**: Present AI estimate to customer

3. **loss_estimated_ai → human_review_pending**
   - **Condition**: Fraud risk > 0.1 OR confidence score 0.35-0.55
   - **Action**: Flag for manual adjuster review

### Customer Decision Transitions

4. **customer_decision_pending → loss_approved**
   - **Condition**: Customer accepts estimate
   - **Action**: Proceed to payment

5. **customer_decision_pending → loss_appealed**
   - **Condition**: Customer rejects estimate
   - **Action**: Escalate to human review

### Human Review Transitions

5. **loss_appealed → human_review_pending**
   - **Condition**: First customer appeal received
   - **Action**: Queue for adjuster override

6. **loss_appealed → routed_to_traditional**
   - **Condition**: Second customer appeal received (after human review)
   - **Action**: Automatically route to traditional processing

7. **human_review_pending → human_review_completed**
   - **Condition**: Adjuster completes review
   - **Action**: Generate revised estimate or routing decision

8. **human_review_completed → customer_decision_pending**
   - **Condition**: Adjuster provides revised estimate
   - **Action**: Present updated estimate to customer

9. **human_review_completed → routed_to_traditional**
   - **Condition**: Adjuster determines traditional process required
   - **Action**: Route to traditional workflow

### Payment & Traditional Processing Transitions

10. **loss_approved → sent_for_payment**
    - **Condition**: Estimate approved (AI or human review)
    - **Action**: Initiate payment processing

11. **sent_for_payment → claim_closed**
    - **Condition**: Payment successfully issued
    - **Action**: Close claim

12. **routed_to_traditional → traditional_claim_processing**
    - **Condition**: Traditional workflow initiated
    - **Action**: Begin manual processing

13. **traditional_claim_processing → garage_scheduling_pending**
    - **Condition**: Vehicle is drivable
    - **Action**: Schedule garage repair appointment

14. **traditional_claim_processing → adjustor_scheduling_pending**
    - **Condition**: Vehicle non-drivable or complex damage
    - **Action**: Schedule field adjuster visit

15. **garage_scheduling_pending → claim_closed**
    - **Condition**: Repair appointment scheduled
    - **Action**: Close claim (repair tracking out of scope)

16. **adjustor_scheduling_pending → claim_closed**
    - **Condition**: Field inspection scheduled
    - **Action**: Close claim (inspection outcome tracked separately)

## Business Rules

### AI Decision Thresholds

- **High Confidence**: Confidence > 0.55 → Direct to customer
- **Medium Confidence**: 0.35 < Confidence ≤ 0.55 → Human review
- **Low Confidence**: Confidence ≤ 0.35 → Traditional process
- **Fraud Risk**: Risk > 0.1 → Human review (regardless of confidence)

### Escalation Paths

1. **AI → Human Review**: Triggered by fraud risk, medium confidence, or customer rejection
2. **Human Review → Traditional**: Triggered by adjuster determination (complexity, damage severity) OR second customer appeal
3. **Customer Appeal Workflow**:
   - **First Appeal**: Customer rejects AI estimate → Human review → Revised estimate presented
   - **Second Appeal**: Customer rejects human-reviewed estimate → Automatically routes to traditional processing
   - **Rationale**: Prevents infinite appeal loops, ensures fair review process, escalates persistent disputes to physical inspection

### Terminal Conditions

All paths converge to **claim_closed**:
- **AI Path**: Customer accepts → Payment → Closed
- **Human Review Path**: Adjuster revises → Customer accepts → Payment → Closed
- **Traditional Path**: Scheduling complete → Closed (repair/inspection tracking external)

## Integration Points

### Upstream Systems
- **FNOL Intake System**: Creates initial claim record
- **Mobile App / Web Portal**: Image upload interface
- **AI Damage Detection Service**: Processes images, returns confidence scores

### Downstream Systems
- **Payment Processing**: Handles approved claim payouts
- **Scheduling System**: Coordinates garage appointments and adjuster visits
- **Claims Management System**: Tracks claim status and history

## Notes

- This state machine focuses on **claim triage and approval** workflow
- Post-closure activities (repair tracking, quality assurance, subrogation) are out of scope
- States are **mutually exclusive** - a claim exists in exactly one state at any time
- All transitions are **auditable** - each state change should be logged with timestamp, actor, and reason
- **Idempotency**: Re-entering a state (e.g., customer_decision_pending after human review) should preserve claim history

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-03 | Initial | Created comprehensive state machine with AI and traditional paths |
