/**
 * API functions for claim endpoints
 */
import { getApiClient } from './client';

/**
 * Complete a claim review
 * @param {number} claimId - Claim ID
 * @param {object} reviewData - Review data (action, notes, revised_estimate_total)
 * @returns {Promise} API response
 */
export const completeReview = async (claimId, reviewData) => {
  const client = getApiClient();
  const response = await client.post(`/claims/${claimId}/review/complete`, reviewData);
  return response.data;
};

/**
 * Add a manual damage to a claim
 * @param {number} claimId - Claim ID
 * @param {object} damageData - Damage data
 * @returns {Promise} API response
 */
export const addManualDamage = async (claimId, damageData) => {
  const client = getApiClient();
  const response = await client.post(`/claims/${claimId}/damages`, damageData);
  return response.data;
};

/**
 * Update damage costs
 * @param {number} claimId - Claim ID
 * @param {string} damageId - Damage ID
 * @param {object} updateData - Updated damage data
 * @returns {Promise} API response
 */
export const updateDamageCosts = async (claimId, damageId, updateData) => {
  const client = getApiClient();
  const response = await client.patch(`/claims/${claimId}/damages/${damageId}`, updateData);
  return response.data;
};

/**
 * Fetch claim events (using customer endpoint)
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @returns {Promise} API response
 */
export const fetchClaimEvents = async (customerId, claimId) => {
  const client = getApiClient();
  const response = await client.get(`/customers/${customerId}/claims/${claimId}/events`);
  return response.data;
};

/**
 * Fetch claim details (using customer endpoint)
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @returns {Promise} API response
 */
export const fetchClaimDetails = async (customerId, claimId) => {
  const client = getApiClient();
  const response = await client.get(`/customers/${customerId}/claims/${claimId}`);
  return response.data;
};

/**
 * Fetch claim images metadata (using customer endpoint)
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @returns {Promise} API response
 */
export const fetchClaimImages = async (customerId, claimId) => {
  const client = getApiClient();
  const response = await client.get(`/customers/${customerId}/claims/${claimId}/images`);
  return response.data;
};

/**
 * Fetch claim image (original)
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @param {string} imageId - Image ID
 * @returns {Promise} Image blob
 */
export const fetchClaimImage = async (customerId, claimId, imageId) => {
  const client = getApiClient();
  const response = await client.get(
    `/customers/${customerId}/claims/${claimId}/images/${imageId}`,
    { responseType: 'blob' }
  );
  return response.data;
};

/**
 * Fetch claim image with bounding boxes (annotated)
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @param {string} imageId - Image ID
 * @returns {Promise} Annotated image blob
 */
export const fetchAnnotatedImage = async (customerId, claimId, imageId) => {
  const client = getApiClient();
  const response = await client.get(
    `/customers/${customerId}/claims/${claimId}/images/${imageId}/annotated`,
    { responseType: 'blob' }
  );
  return response.data;
};

/**
 * Fetch fraud signals for a claim
 * @param {number} claimId - Claim ID
 * @returns {Promise} API response with fraud analysis data
 */
export const fetchFraudSignals = async (claimId) => {
  const client = getApiClient();
  try {
    const response = await client.get(`/claims/${claimId}/fraud-signals`);
    return response.data;
  } catch (error) {
    // Return empty fraud data if endpoint doesn't exist or no fraud data
    console.log('No fraud signals found for claim:', claimId);
    return {
      overall_risk_score: 0,
      signals: []
    };
  }
};
