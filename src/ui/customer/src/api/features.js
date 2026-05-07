/**
 * Feature flags API
 */
import { getApiClient } from './client';

/**
 * Get feature flags from API
 * @returns {Promise<Object>} Feature flags object
 */
export const getFeatureFlags = async () => {
  const client = getApiClient();
  const response = await client.get('/admin/features');
  return response.data;
};
