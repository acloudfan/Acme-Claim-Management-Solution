/**
 * Claims API functions
 */
import { getApiClient } from './client';

const apiClient = () => getApiClient();

/**
 * Create new claim (draft state)
 * @param {number} customerId - Customer ID
 * @param {Object} claimData - Claim data
 * @returns {Promise} Created claim
 */
export const createClaim = (customerId, claimData) => {
  return apiClient().post(`/customers/${customerId}/claims`, claimData);
};

/**
 * Submit claim for processing (draft → FNOL)
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @returns {Promise} Updated claim
 */
export const submitClaim = (customerId, claimId) => {
  return apiClient().post(`/customers/${customerId}/claims/${claimId}/submit`);
};

/**
 * Get all claims for customer
 * @param {number} customerId - Customer ID
 * @param {Object} params - Query parameters (status, limit, offset)
 * @returns {Promise} List of claims
 */
export const fetchCustomerClaims = (customerId, params = {}) => {
  return apiClient().get(`/customers/${customerId}/claims`, { params });
};

/**
 * Get specific claim with damages
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @returns {Promise} Claim with damage assessment
 */
export const fetchClaimDetail = (customerId, claimId) => {
  return apiClient().get(`/customers/${customerId}/claims/${claimId}`);
};

/**
 * Accept estimate
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @param {Object} data - Acceptance data
 * @returns {Promise} Updated claim
 */
export const acceptEstimate = (customerId, claimId, data) => {
  return apiClient().post(`/customers/${customerId}/claims/${claimId}/accept`, data);
};

/**
 * Appeal estimate
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @param {Object} data - Appeal data (reason, etc.)
 * @returns {Promise} Updated claim
 */
export const appealEstimate = (customerId, claimId, data) => {
  return apiClient().post(`/customers/${customerId}/claims/${claimId}/appeal`, data);
};

/**
 * Get damages for a claim
 * @param {number} claimId - Claim ID
 * @returns {Promise} List of damages
 */
export const fetchDamages = (claimId) => {
  return apiClient().get(`/claims/${claimId}/damages`);
};

/**
 * Get claim events (timeline)
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @param {Object} params - Query parameters
 * @returns {Promise} Event history
 */
export const fetchClaimEvents = (customerId, claimId, params = {}) => {
  return apiClient().get(`/customers/${customerId}/claims/${claimId}/events`, { params });
};
