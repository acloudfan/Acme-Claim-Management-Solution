/**
 * API functions for adjustor endpoints
 */
import { getApiClient } from './client';

/**
 * Fetch pending claims for an adjustor
 * @param {string} adjustorId - Adjustor ID
 * @param {object} filters - Optional filters (limit, offset, etc.)
 * @returns {Promise} API response
 */
export const fetchPendingClaims = async (adjustorId, filters = {}) => {
  const client = getApiClient();
  const params = new URLSearchParams();

  if (filters.limit) params.append('limit', filters.limit);
  if (filters.offset) params.append('offset', filters.offset);
  if (filters.sort_by) params.append('sort_by', filters.sort_by);
  if (filters.sort_order) params.append('sort_order', filters.sort_order);

  const response = await client.get(`/adjustors/${adjustorId}/claims/pending?${params.toString()}`);
  return response.data;
};

/**
 * Fetch adjustor statistics
 * @param {string} adjustorId - Adjustor ID
 * @returns {Promise} API response
 */
export const fetchAdjustorStatistics = async (adjustorId) => {
  const client = getApiClient();
  const response = await client.get(`/adjustors/${adjustorId}/statistics`);
  return response.data;
};
