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

// Status display names
export const STATUS_LABELS = {
  [CLAIM_STATUS.DRAFT]: 'Draft',
  [CLAIM_STATUS.FNOL]: 'First Notice of Loss',
  [CLAIM_STATUS.IMAGE_UPLOADED]: 'Images Uploaded',
  [CLAIM_STATUS.LOSS_ESTIMATED_AI]: 'AI Estimate Generated',
  [CLAIM_STATUS.CUSTOMER_DECISION_PENDING]: 'Awaiting Your Decision',
  [CLAIM_STATUS.LOSS_APPROVED]: 'Approved',
  [CLAIM_STATUS.LOSS_APPEALED]: 'Appealed',
  [CLAIM_STATUS.HUMAN_REVIEW_PENDING]: 'Under Human Review',
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
  [CLAIM_STATUS.LOSS_ESTIMATED_AI]: 'bg-info-light text-info-dark',
  [CLAIM_STATUS.CUSTOMER_DECISION_PENDING]: 'bg-warning-light text-warning-dark',
  [CLAIM_STATUS.LOSS_APPROVED]: 'bg-success-light text-success-dark',
  [CLAIM_STATUS.LOSS_APPEALED]: 'bg-warning-light text-warning-dark',
  [CLAIM_STATUS.HUMAN_REVIEW_PENDING]: 'bg-warning-light text-warning-dark',
  [CLAIM_STATUS.HUMAN_REVIEW_COMPLETED]: 'bg-info-light text-info-dark',
  [CLAIM_STATUS.SENT_FOR_PAYMENT]: 'bg-success-light text-success-dark',
  [CLAIM_STATUS.CLAIM_PAID]: 'bg-success-light text-success-dark',
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
  [SEVERITY.LIGHT]: 'text-success-dark',
  [SEVERITY.MODERATE]: 'text-warning-dark',
  [SEVERITY.SEVERE]: 'text-error-dark',
};

// Image upload constraints
export const IMAGE_CONSTRAINTS = {
  MAX_SIZE_MB: 10,
  MAX_COUNT: 20,
  ALLOWED_TYPES: ['image/jpeg', 'image/jpg', 'image/png', 'image/heic'],
  ALLOWED_EXTENSIONS: ['.jpg', '.jpeg', '.png', '.heic'],
};
