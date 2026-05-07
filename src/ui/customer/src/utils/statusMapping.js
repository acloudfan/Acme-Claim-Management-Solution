/**
 * Status mapping utilities for claim statuses
 * Maps backend status values to user-friendly display labels
 */

/**
 * Map backend claim status to user-friendly display label
 * @param {string} status - Backend status value
 * @returns {string} User-friendly display label
 */
export const getStatusLabel = (status) => {
  const statusMap = {
    'draft': 'Draft',
    'FNOL': 'Submitted',
    'image_uploaded': 'Images Uploaded',
    'loss_estimated_ai': 'Loss Estimate Prepared',
    'human_review_pending': 'Review Pending',
    'customer_decision_pending': 'Customer decision pending',
    'loss_approved': 'Approved',
    'loss_appealed': 'Appealed',
    'sent_for_payment': 'Payment Processing',
    'claim_paid': 'Paid',
    'routed_to_traditional': 'Traditional Processing',
    'traditional_processing_active': 'Traditional Processing',
    'claim_closed': 'Closed',
  };

  return statusMap[status] || status;
};

/**
 * Get badge variant for a given status
 * @param {string} status - Backend status value
 * @returns {string} Badge variant (success, warning, error, info)
 */
export const getStatusVariant = (status) => {
  const variantMap = {
    // Success states
    'loss_approved': 'success',
    'claim_paid': 'success',
    'claim_closed': 'success',

    // Warning states
    'human_review_pending': 'warning',
    'loss_appealed': 'warning',
    'routed_to_traditional': 'warning',
    'traditional_processing_active': 'warning',

    // Error states
    'error': 'error',

    // Info states (processing, in progress)
    'draft': 'info',
    'FNOL': 'info',
    'image_uploaded': 'info',
    'loss_estimated_ai': 'info',
    'customer_decision_pending': 'info',
    'sent_for_payment': 'info',
  };

  return variantMap[status] || 'info';
};
