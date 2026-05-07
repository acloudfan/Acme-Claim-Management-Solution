/**
 * Application constants
 */

// Claim statuses
export const CLAIM_STATUS = {
  DRAFT: 'draft',
  FNOL: 'FNOL',
  IMAGE_UPLOADED: 'image_uploaded',
  LOSS_ESTIMATED_AI: 'loss_estimated_ai',
  CUSTOMER_DECISION_PENDING: 'customer_decision_pending',
  LOSS_APPROVED: 'loss_approved',
  LOSS_APPEALED: 'loss_appealed',
  HUMAN_REVIEW_PENDING: 'human_review_pending',
  HUMAN_REVIEW_COMPLETED: 'human_review_completed',
  SENT_FOR_PAYMENT: 'sent_for_payment',
  CLAIM_PAID: 'claim_paid',
  ROUTED_TO_TRADITIONAL: 'routed_to_traditional',
  CLAIM_CLOSED: 'claim_closed',
};

// Status display names for adjustor portal
export const STATUS_LABELS = {
  [CLAIM_STATUS.DRAFT]: 'Draft',
  [CLAIM_STATUS.FNOL]: 'First Notice of Loss',
  [CLAIM_STATUS.IMAGE_UPLOADED]: 'Images Uploaded',
  [CLAIM_STATUS.LOSS_ESTIMATED_AI]: 'AI Estimate Generated',
  [CLAIM_STATUS.CUSTOMER_DECISION_PENDING]: 'Customer Decision Pending',
  [CLAIM_STATUS.LOSS_APPROVED]: 'Approved',
  [CLAIM_STATUS.LOSS_APPEALED]: 'Appealed',
  [CLAIM_STATUS.HUMAN_REVIEW_PENDING]: 'Pending Review',
  [CLAIM_STATUS.HUMAN_REVIEW_COMPLETED]: 'Review Complete',
  [CLAIM_STATUS.SENT_FOR_PAYMENT]: 'Processing Payment',
  [CLAIM_STATUS.CLAIM_PAID]: 'Paid',
  [CLAIM_STATUS.ROUTED_TO_TRADITIONAL]: 'Traditional Processing',
  [CLAIM_STATUS.CLAIM_CLOSED]: 'Closed',
};

// Status colors (Tailwind CSS classes)
export const STATUS_COLORS = {
  [CLAIM_STATUS.DRAFT]: 'bg-gray-100 text-gray-800',
  [CLAIM_STATUS.FNOL]: 'bg-blue-100 text-blue-800',
  [CLAIM_STATUS.IMAGE_UPLOADED]: 'bg-blue-100 text-blue-800',
  [CLAIM_STATUS.LOSS_ESTIMATED_AI]: 'bg-blue-100 text-blue-800',
  [CLAIM_STATUS.CUSTOMER_DECISION_PENDING]: 'bg-yellow-100 text-yellow-800',
  [CLAIM_STATUS.LOSS_APPROVED]: 'bg-green-100 text-green-800',
  [CLAIM_STATUS.LOSS_APPEALED]: 'bg-yellow-100 text-yellow-800',
  [CLAIM_STATUS.HUMAN_REVIEW_PENDING]: 'bg-yellow-100 text-yellow-800',
  [CLAIM_STATUS.HUMAN_REVIEW_COMPLETED]: 'bg-blue-100 text-blue-800',
  [CLAIM_STATUS.SENT_FOR_PAYMENT]: 'bg-green-100 text-green-800',
  [CLAIM_STATUS.CLAIM_PAID]: 'bg-green-100 text-green-800',
  [CLAIM_STATUS.ROUTED_TO_TRADITIONAL]: 'bg-gray-100 text-gray-800',
  [CLAIM_STATUS.CLAIM_CLOSED]: 'bg-gray-100 text-gray-800',
};

// Severity levels
export const SEVERITY = {
  LIGHT: 'light',
  MODERATE: 'moderate',
  SEVERE: 'severe',
};

// Severity display
export const SEVERITY_LABELS = {
  [SEVERITY.LIGHT]: 'Light',
  [SEVERITY.MODERATE]: 'Moderate',
  [SEVERITY.SEVERE]: 'Severe',
};

// Severity colors
export const SEVERITY_COLORS = {
  [SEVERITY.LIGHT]: 'text-green-700',
  [SEVERITY.MODERATE]: 'text-yellow-700',
  [SEVERITY.SEVERE]: 'text-red-700',
};

// Damage types
export const DAMAGE_TYPES = {
  SCRATCH: 'scratch',
  DENT: 'dent',
  BROKEN_PART: 'broken_part',
  PAINT_DAMAGE: 'paint_damage',
  GLASS_DAMAGE: 'glass_damage',
};

// Damage type labels
export const DAMAGE_TYPE_LABELS = {
  [DAMAGE_TYPES.SCRATCH]: 'Scratch',
  [DAMAGE_TYPES.DENT]: 'Dent',
  [DAMAGE_TYPES.BROKEN_PART]: 'Broken Part',
  [DAMAGE_TYPES.PAINT_DAMAGE]: 'Paint Damage',
  [DAMAGE_TYPES.GLASS_DAMAGE]: 'Glass Damage',
};

// Review reasons
export const REVIEW_REASONS = {
  FRAUD_SIGNALS: 'fraud_signals',
  LOW_CONFIDENCE: 'low_confidence',
  APPEAL: 'customer_appeal',  // Backend uses 'customer_appeal'
  NO_DAMAGE: 'no_damage_detected',
  HIGH_ESTIMATE: 'high_estimate',
};

// Review reason labels
export const REVIEW_REASON_LABELS = {
  'fraud_signals': 'Fraud Signals',
  'low_confidence': 'Low AI Confidence',
  'customer_appeal': 'Customer Appeal',
  'appeal': 'Customer Appeal',  // Legacy support
  'no_damage_detected': 'No Damage Detected',
  'high_estimate': 'High Estimate Amount',
};

// Fraud risk levels
export const FRAUD_RISK_LEVELS = {
  LOW: { min: 0.0, max: 0.3, color: 'success', label: 'Low Risk', bgClass: 'bg-green-50', textClass: 'text-green-700', borderClass: 'border-green-400' },
  MEDIUM: { min: 0.3, max: 0.7, color: 'warning', label: 'Medium Risk', bgClass: 'bg-amber-50', textClass: 'text-amber-700', borderClass: 'border-amber-400' },
  HIGH: { min: 0.7, max: 1.0, color: 'danger', label: 'High Risk', bgClass: 'bg-red-50', textClass: 'text-red-700', borderClass: 'border-red-400' }
};

/**
 * Get fraud risk level based on score
 */
export const getFraudRiskLevel = (score) => {
  if (score < FRAUD_RISK_LEVELS.LOW.max) return FRAUD_RISK_LEVELS.LOW;
  if (score < FRAUD_RISK_LEVELS.MEDIUM.max) return FRAUD_RISK_LEVELS.MEDIUM;
  return FRAUD_RISK_LEVELS.HIGH;
};
