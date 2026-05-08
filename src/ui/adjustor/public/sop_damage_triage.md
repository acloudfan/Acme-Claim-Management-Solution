# ACME Insurance - Damage Triage Standard Operating Procedure (SOP)

**Version:** 2.0  
**Last Updated:** 2026-05-08  
**Purpose:** Guide AI agents and human adjustors in triaging vehicle damage claims  
**Scope:** Automated and manual claim processing workflows

---

## Table of Contents

1. [Overview](#overview)
2. [Confidence Thresholds](#confidence-thresholds)
3. [Triage Decision Tree](#triage-decision-tree)
4. [Fraud Detection Protocol](#fraud-detection-protocol)
5. [Auto-Approval Scenarios](#auto-approval-scenarios)
6. [Human Review Scenarios](#human-review-scenarios)
7. [Customer Appeal Process](#customer-appeal-process)
8. [Damage Assessment Guidelines](#damage-assessment-guidelines)

---

## Overview

ACME Insurance uses a hybrid AI-human approach to claims processing:

1. **AI Analysis Phase**: YOLO damage detection + Vision Language Model analysis
2. **Fraud Detection Phase**: Multi-signal fraud risk scoring
3. **Confidence-Based Routing**: Auto-approve vs. human review
4. **Customer Appeal Option**: Customers can request human review

**Key Principle**: When in doubt, route to human review. Customer satisfaction and fraud prevention take priority over speed.

---

## Confidence Thresholds

AI confidence scores determine automatic routing:

| Confidence Level | Score Range | Action | Rationale |
|-----------------|-------------|--------|-----------|
| **High Confidence** | ≥ 0.55 | Auto-present estimate to customer | AI is confident enough to provide immediate estimate |
| **Medium Confidence** | 0.35 - 0.54 | Present estimate with appeal option | AI provides estimate but customer can easily appeal |
| **Low Confidence** | < 0.35 | Route to traditional process | AI uncertainty too high; needs human expertise |

> **Important Note:** Confidence thresholds can be adjusted over time based on model performance and business requirements. Always check the current configuration in the Admin Portal or api-config.yaml at the time of processing. The values shown above reflect the configuration as of this document's last update date.

**Override Conditions:**
- Total estimate ≥ $5,000 → Always requires human review (regardless of confidence)
- Fraud risk score ≥ 0.1 → Always routes to human review
- Customer appeal → Always routes to human adjustor

---

## Triage Decision Tree

Follow this decision tree in order (first match wins):

### 1. Fraud Detection Check (Highest Priority)

**IF** `fraud_risk_score >= 0.7`:
- **Action:** FRAUD_DETECTED
- **Routing:** Fraud review team
- **Rationale:** High fraud risk requires immediate specialist review
- **Next Steps:** 
  - Review all fraud signals (make mismatch, AI-generated images, color mismatch, pattern anomalies)
  - Contact customer for clarification if needed
  - Recommend rejection or traditional investigation
  - Document fraud indicators in claim notes

**ELSE IF** `fraud_risk_score >= 0.4`:
- **Action:** ADJUSTOR_REVIEW (Medium Risk)
- **Routing:** Adjustor queue with fraud flags
- **Rationale:** Suspicious signals detected but not conclusive
- **Next Steps:**
  - Verify vehicle registration matches images
  - Check image authenticity (AI-generated detection)
  - Review customer claim history
  - Approve or escalate based on findings

**ELSE IF** `fraud_risk_score >= 0.1`:
- **Action:** ADJUSTOR_REVIEW (Low Risk Flag)
- **Routing:** Adjustor queue with informational flags
- **Rationale:** Minor inconsistencies detected; review for context
- **Next Steps:**
  - Quick verification of flagged items
  - Approve if explainable, escalate if concerns remain

### 2. Amount-Based Review

**IF** `total_estimate >= $5000`:
- **Action:** ADJUSTOR_REVIEW
- **Routing:** Adjustor queue (high-value claims)
- **Rationale:** Large financial exposure requires human oversight
- **Next Steps:**
  - Review all damage assessments for accuracy
  - Verify parts and labor estimates are reasonable
  - Check for hidden or internal damage
  - Approve, adjust estimate, or request additional photos

### 3. Confidence-Based Auto-Approval

**IF** `ai_confidence >= 0.55 AND total_estimate < $5000 AND fraud_risk_score < 0.1`:
- **Action:** APPROVED (Auto-approved)
- **Routing:** Customer notification
- **Rationale:** High confidence, low risk, manageable amount
- **Next Steps:**
  - Present estimate to customer
  - Provide repair shop recommendations
  - Process payment once customer accepts
  - Monitor for any post-approval issues

### 4. Medium Confidence Routing

**IF** `ai_confidence >= 0.35 AND ai_confidence < 0.55 AND total_estimate < $5000 AND fraud_risk_score < 0.1`:
- **Action:** APPROVED (with appeal option)
- **Routing:** Customer notification with easy appeal access
- **Rationale:** AI is moderately confident; let customer decide
- **Next Steps:**
  - Present estimate to customer
  - Make appeal button prominently visible
  - If customer accepts → process as approved
  - If customer appeals → route to adjustor review

### 5. Low Confidence Routing

**IF** `ai_confidence < 0.35`:
- **Action:** ADJUSTOR_REVIEW
- **Routing:** Adjustor queue (low confidence)
- **Rationale:** AI cannot reliably assess damage; human expertise needed
- **Next Steps:**
  - Review photos for clarity and coverage
  - May request additional photos or angles
  - Perform manual damage assessment
  - Generate or adjust estimate manually

### 6. Customer Appeal

**IF** `claim_state == CUSTOMER_APPEAL`:
- **Action:** ADJUSTOR_REVIEW
- **Routing:** Adjustor queue (priority: 48-hour SLA)
- **Rationale:** Customer disagrees with AI estimate
- **Next Steps:**
  - Read customer's appeal reason carefully
  - Common issues: "radiator damage," "frame damage," "internal damage not visible"
  - Review all photos again with customer's context
  - Add manual damage assessments if warranted
  - Revise estimate and explain changes to customer

---

## Fraud Detection Protocol

### Fraud Signals Detected by System

1. **Vehicle Make/Model Mismatch**
   - **Detection:** VLM compares vehicle in images to registered vehicle
   - **Example:** Customer owns Chevy Silverado but images show Ford F-150
   - **Risk:** HIGH (typically fraud_risk_score ≥ 0.7)
   - **Action:** Route to fraud team immediately

2. **AI-Generated Image Detection**
   - **Detection:** VLM analyzes for AI generation artifacts
   - **Indicators:** Lighting inconsistencies, texture anomalies, unnatural damage patterns, metadata discrepancies
   - **Example:** Customer uploads AI-manipulated photo with fake damage added
   - **Risk:** HIGH (typically fraud_risk_score ≥ 0.7)
   - **Action:** Route to fraud team with detailed VLM analysis

3. **Color Mismatch**
   - **Detection:** VLM checks if vehicle color matches registration
   - **Example:** Registered vehicle is black but images show silver vehicle
   - **Risk:** MEDIUM to HIGH (fraud_risk_score 0.4-0.7)
   - **Action:** Route to adjustor for verification

4. **Pattern Anomalies**
   - **Detection:** Historical claim patterns, velocity, frequency
   - **Example:** Multiple claims in short period, similar damage patterns
   - **Risk:** MEDIUM (fraud_risk_score 0.4-0.6)
   - **Action:** Flag for adjustor review

### Fraud Review Process

**For High-Risk Cases (score ≥ 0.7):**
1. **DO NOT auto-approve** under any circumstances
2. Review all fraud signals provided by system
3. Contact customer to clarify discrepancies
4. Request additional documentation (VIN verification, police report, additional photos)
5. If fraud confirmed: REJECT claim, notify fraud department, document for policy review
6. If legitimate explanation: Downgrade risk and process normally

**For Medium-Risk Cases (score 0.4-0.7):**
1. Review flagged signals
2. Verify easily-checkable items (VIN, registration, color)
3. If explanations are reasonable: Approve with notation
4. If concerns remain: Escalate to fraud team

---

## Auto-Approval Scenarios

### Scenario: High-Confidence Minor to Moderate Damage

**Criteria:**
- AI confidence ≥ 0.55
- Total estimate < $5,000
- Fraud risk score < 0.1
- Clear photos showing damage
- Damage types: scratches, dents, bumper damage, headlight/taillight damage

**Action:** APPROVED (immediate)

**Next Steps:**
1. Present estimate breakdown to customer
2. Show detected damages with images
3. Provide repair shop recommendations
4. Allow customer to accept estimate
5. Process payment upon acceptance

**Customer Communication:**
```
Good news! We've reviewed your claim and approved your estimate.

Estimated Repair Cost: $X,XXX.XX
Your Deductible: $XXX.XX
Insurance Payment: $X,XXX.XX

Damages Detected:
- [Damage 1]: [Part] - [Severity]
- [Damage 2]: [Part] - [Severity]

You can accept this estimate and proceed with repairs, or appeal if you believe 
additional damage exists that wasn't captured in the analysis.
```

---

## Human Review Scenarios

### low-confidence

**Trigger:** AI confidence < 0.35

**Rationale:** AI cannot reliably assess damage severity, parts affected, or repair approach. Human expertise required.

**Common Causes:**
- Poor photo quality (blurry, low resolution, bad lighting)
- Unusual damage patterns not in training data
- Obscured damage (dirt, angle, obstruction)
- Complex damage requiring internal inspection
- Rare vehicle models or custom modifications

**Action:** ADJUSTOR_REVIEW

**Next Steps:**
1. Review all uploaded photos
2. Assess photo quality and coverage
3. If photos inadequate: Request additional photos with specific angles
4. If photos adequate but damage complex: Perform manual assessment
5. Check for internal damage indicators (fluid leaks, misalignment, unusual gaps)
6. Generate manual estimate or adjust AI estimate
7. Add explanatory notes for customer

**Adjustor Guidance:**
- Look for damage the AI might have missed (undercarriage, internal components)
- Consider secondary damage (e.g., impact to bumper may have damaged radiator)
- Use your experience to spot damage patterns AI hasn't learned yet
- Document your reasoning for future AI training

### moderate-damage

**Trigger:** Moderate severity damage detected OR customer appeal

**Rationale:** Moderate damage often has hidden components or repair complexity that requires verification.

**Common Damage Types:**
- Door panel damage (may affect door mechanism)
- Quarter panel damage (may affect structural integrity)
- Hood damage (may affect latch, hinges, or engine components)
- Bumper damage with impact force indicators

**Action:** ADJUSTOR_REVIEW

**Next Steps:**
1. Verify visible damage assessment
2. Evaluate likelihood of internal damage
3. Check for alignment issues in photos
4. Consider whether full replacement vs. repair is more appropriate
5. Adjust severity ratings if needed
6. Revise cost estimate based on professional judgment
7. Add manual damage entries for internal/hidden damage

### severe-damage

**Trigger:** Severe damage detected OR structural damage indicators OR safety concerns

**Rationale:** Severe damage requires specialist assessment and may involve safety issues, total loss consideration, or complex repairs.

**Indicators:**
- Structural damage (frame, unibody, pillars)
- Multiple panels damaged in one incident
- Deployment of airbags
- Fluid leaks (oil, coolant, transmission, brake)
- Severe misalignment of panels or wheels
- Damage to critical safety systems

**Action:** ESCALATE to senior assessor

**Next Steps:**
1. Document all visible severe damage
2. Flag potential safety concerns
3. Consider total loss vs. repair economics
4. If repairable: Estimate structural repair time and cost
5. Require in-person inspection if needed
6. Coordinate with body shop for detailed assessment
7. May require additional safety inspections post-repair

### high-value-claims

**Trigger:** Total estimate ≥ $5,000

**Rationale:** Large financial exposure requires verification to prevent over-payment and ensure accurate assessment.

**Action:** ADJUSTOR_REVIEW

**Next Steps:**
1. Review each line item in estimate
2. Verify parts pricing against market rates
3. Verify labor hours are reasonable for damage type
4. Check for duplicate or overlapping damage entries
5. Consider whether damage severity justifies high cost
6. Look for potential cost savings (aftermarket vs. OEM parts, repair vs. replace)
7. Approve, adjust estimate, or request additional information

---

## Customer Appeal Process

### When Customer Appeals

**Trigger:** Customer clicks "Appeal Decision" button

**Common Appeal Reasons:**
- "There's more damage than the estimate shows"
- "Radiator/frame/internal component is damaged"
- "The estimate doesn't cover paint blending"
- "Repair shop quoted higher amount"
- "Damage is more severe than AI assessed"

**Action:** ADJUSTOR_REVIEW (Priority: 48-hour SLA)

**Next Steps:**
1. **Read the customer's appeal carefully** - they may have spotted damage you missed
2. Review all photos again with customer's concern in mind
3. Look specifically for the damage type mentioned (radiator, frame, internal)
4. Consider customer's perspective - they see the vehicle daily
5. Add manual damage assessments if customer's concern is valid
6. Adjust severity ratings if damage is worse than AI assessed
7. Revise estimate and explain changes clearly
8. If no changes warranted, explain why original estimate stands

**Adjustor Mindset:**
- Assume customer is honest unless evidence suggests otherwise
- Internal damage is often not visible in photos
- Customer knows their vehicle better than we do
- Err on the side of the customer for borderline cases
- Document your reasoning clearly for both approvals and denials

**Response Template (Approval with Adjustment):**
```
Thank you for your appeal. After careful review by our adjustor, we've revised your estimate.

Original Estimate: $X,XXX.XX
Revised Estimate: $X,XXX.XX
Increase: $XXX.XX

Additional Damages Added:
- [Component]: [Damage Type] - [Reason for addition]

Your concern about [specific issue mentioned] was valid. We've updated the 
estimate to reflect this additional damage. You can now proceed with repairs.
```

**Response Template (Denial with Explanation):**
```
Thank you for your appeal. After careful review by our adjustor, we're maintaining 
the original estimate of $X,XXX.XX.

Reason:
[Detailed explanation of why the additional damage is not covered or not present]

If you believe there is additional damage that isn't visible in your photos, 
you may:
1. Upload additional photos showing the specific damage
2. Obtain an estimate from a licensed repair shop for our review
3. Request an in-person inspection (available for estimates over $3,000)
```

---

## Damage Assessment Guidelines

### Damage Types Recognized by System

1. **Scratch** - Surface-level paint damage
   - Minor: < 6 inches, single panel
   - Moderate: 6-24 inches, may cross panels
   - Severe: > 24 inches, deep to primer/metal, or keying

2. **Dent** - Depression in body panel without paint damage
   - Minor: < 2 inches diameter, shallow
   - Moderate: 2-6 inches diameter, noticeable depth
   - Severe: > 6 inches, deep, or multiple dents

3. **Crack** - Split or fracture in component
   - Minor: Small crack in plastic component
   - Moderate: Crack in headlight/taillight lens
   - Severe: Crack in windshield, structural component

4. **Broken** - Component fractured or detached
   - Minor: Broken mirror cover, trim piece
   - Moderate: Broken headlight/taillight assembly
   - Severe: Broken structural component, suspension

5. **Missing** - Component completely absent
   - Any missing component is at least moderate severity
   - Requires full replacement

6. **Damaged** - General damage category
   - Used when specific type unclear from photos
   - Severity based on repair complexity

### Part Categories and Typical Costs

**Exterior Panels:**
- Front/Rear Bumper: $800-2,500 (replace) or $200-600 (repair)
- Hood: $400-1,200 (replace)
- Fender: $300-1,000 (replace)
- Door: $500-1,500 (replace)
- Quarter Panel: $1,000-3,000 (replace/repair)

**Lighting:**
- Headlight Assembly: $150-800
- Taillight Assembly: $100-500
- Fog Light: $50-200

**Glass:**
- Windshield: $200-500
- Side Window: $150-350
- Rear Window: $200-600

**Interior (if visible):**
- Damage usually indicates more severe impact
- Check for airbag deployment ($1,000+ per airbag)

**Internal Components (not typically visible):**
- Radiator: $300-800
- Condenser: $200-500
- Frame damage: $1,500-5,000+

### Labor Rate Guidelines

- Paint/body work: $50-100/hour (varies by region)
- Mechanical repair: $80-150/hour
- Standard repair times from industry databases (Mitchell, CCC)

### When to Add Manual Damage Entries

**Add manual damage if:**
1. Customer appeals and mentions specific internal damage
2. Photos show indicators of hidden damage (fluid leaks, misalignment, gaps)
3. Impact severity suggests likely internal damage (e.g., severe front damage → radiator)
4. Your expertise indicates damage AI missed
5. Repair shop provides estimate with additional items

**Examples:**
- Front bumper severely damaged → Likely radiator/condenser damage
- Door impact → Possible door mechanism/window regulator damage
- Quarter panel damage → Possible wheel well/suspension damage
- Hood buckled → Possible latch/hinge/core support damage

---

## Summary Decision Matrix

| Condition | Confidence | Fraud Risk | Amount | Action | Routing |
|-----------|-----------|------------|---------|---------|---------|
| High fraud risk | Any | ≥ 0.7 | Any | FRAUD_DETECTED | Fraud team |
| Medium fraud risk | Any | 0.4-0.7 | Any | ADJUSTOR_REVIEW | Adjustor queue |
| High amount | Any | < 0.4 | ≥ $5,000 | ADJUSTOR_REVIEW | Adjustor queue |
| High confidence, clean | ≥ 0.55 | < 0.1 | < $5,000 | APPROVED | Customer |
| Medium confidence, clean | 0.35-0.54 | < 0.1 | < $5,000 | APPROVED* | Customer |
| Low confidence | < 0.35 | < 0.1 | Any | ADJUSTOR_REVIEW | Adjustor queue |
| Customer appeal | Any | Any | Any | ADJUSTOR_REVIEW | Adjustor queue |

*With prominent appeal option

---

## Key Principles for LLM Assessment

1. **Safety First**: When uncertain, route to human review
2. **Fraud Vigilance**: Take all fraud signals seriously
3. **Customer Empathy**: Assume customers are honest; investigate discrepancies fairly
4. **Hidden Damage Awareness**: Visible damage often indicates hidden internal damage
5. **Documentation**: Always explain reasoning for decisions
6. **Consistency**: Apply rules uniformly across all claims
7. **Escalation**: Don't hesitate to escalate complex or high-risk cases

---

**End of SOP**

*This document should be updated as policies, thresholds, or processes change.*
