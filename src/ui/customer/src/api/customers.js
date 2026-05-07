/**
 * Customer API functions
 */
import { getApiClient } from './client';

const apiClient = () => getApiClient();

/**
 * Get customer by ID
 * @param {number} customerId - Customer ID
 * @param {boolean} includePolicies - Include policies and vehicles
 * @returns {Promise} Customer data
 */
export const fetchCustomer = (customerId, includePolicies = false) => {
  return apiClient().get(`/customers/${customerId}`, {
    params: { include_policies: includePolicies }
  });
};

/**
 * Get customer policies
 * @param {number} customerId - Customer ID
 * @returns {Promise} List of policies
 */
export const fetchCustomerPolicies = (customerId) => {
  return apiClient().get(`/customers/${customerId}/policies`);
};

/**
 * Get specific policy
 * @param {number} customerId - Customer ID
 * @param {string} policyNumber - Policy number
 * @returns {Promise} Policy data
 */
export const fetchPolicy = (customerId, policyNumber) => {
  return apiClient().get(`/customers/${customerId}/policies/${policyNumber}`);
};

/**
 * Get customer claims
 * @param {number} customerId - Customer ID
 * @param {object} filters - Optional filters (e.g., { status: 'customer_decision_pending' })
 * @returns {Promise} List of claims
 */
export const fetchCustomerClaims = (customerId, filters = {}) => {
  return apiClient().get(`/customers/${customerId}/claims`, {
    params: filters
  });
};

/**
 * Create new claim in draft state
 * @param {number} customerId - Customer ID
 * @param {object} claimData - Claim data (vin, policy_number, fnol_date, etc.)
 * @returns {Promise} Created claim
 */
export const createClaim = (customerId, claimData) => {
  return apiClient().post(`/customers/${customerId}/claims`, claimData);
};

/**
 * Get specific claim details
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @returns {Promise} Claim details
 */
export const fetchClaimDetail = (customerId, claimId) => {
  return apiClient().get(`/customers/${customerId}/claims/${claimId}`);
};

/**
 * Submit claim for processing (draft -> FNOL)
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @returns {Promise} Updated claim
 */
export const submitClaim = (customerId, claimId) => {
  return apiClient().post(`/customers/${customerId}/claims/${claimId}/submit`);
};

/**
 * Generate AI damage estimate for claim
 * @param {number} claimId - Claim ID
 * @param {object} estimateData - Estimate request data (image_ids, state)
 * @returns {Promise} Estimate response
 */
export const generateEstimate = (claimId, estimateData) => {
  return apiClient().post(`/claims/${claimId}/estimate`, estimateData);
};

/**
 * Request human review for claim (no damages detected or customer preference)
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @returns {Promise} Updated claim
 */
export const requestHumanReview = (customerId, claimId) => {
  return apiClient().post(`/customers/${customerId}/claims/${claimId}/request-human-review`);
};

/**
 * Delete claim (only draft claims can be deleted)
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @returns {Promise} Empty response
 */
export const deleteClaim = (customerId, claimId) => {
  return apiClient().delete(`/customers/${customerId}/claims/${claimId}`);
};

/**
 * Upload claim image
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @param {FormData} formData - Form data with file
 * @param {Function} onUploadProgress - Progress callback
 * @returns {Promise} Upload response
 */
export const uploadClaimImage = (customerId, claimId, formData, onUploadProgress) => {
  return apiClient().post(`/customers/${customerId}/claims/${claimId}/images`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress,
  });
};

/**
 * Get claim images list
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @returns {Promise} List of image metadata
 */
export const fetchClaimImages = (customerId, claimId) => {
  return apiClient().get(`/customers/${customerId}/claims/${claimId}/images`);
};

/**
 * Delete claim image
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @param {string} imageId - Image filename
 * @returns {Promise} Empty response
 */
export const deleteClaimImage = (customerId, claimId, imageId) => {
  return apiClient().delete(`/customers/${customerId}/claims/${claimId}/images/${imageId}`);
};

/**
 * Accept AI estimate
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @returns {Promise} Updated claim data
 */
export const acceptEstimate = (customerId, claimId) => {
  return apiClient().post(`/customers/${customerId}/claims/${claimId}/accept-estimate`);
};

/**
 * Get claim events
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @param {object} filters - Optional filters (e.g., { actor_type: 'customer', limit: 10 })
 * @returns {Promise} List of claim events
 */
export const fetchClaimEvents = (customerId, claimId, filters = {}) => {
  return apiClient().get(`/customers/${customerId}/claims/${claimId}/events`, {
    params: filters
  });
};

/**
 * Appeal AI or human-reviewed estimate
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @param {string} reason - Reason for appeal
 * @returns {Promise} Appeal result with appeal_type and updated claim
 */
export const appealEstimate = (customerId, claimId, reason) => {
  return apiClient().post(`/customers/${customerId}/claims/${claimId}/appeal-estimate`, {
    reason
  });
};
