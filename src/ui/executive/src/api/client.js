/**
 * Axios client for API requests
 */
import axios from 'axios';
import { getConfig } from './config';

let apiClient = null;

export function getApiClient() {
  if (apiClient) return apiClient;

  const config = getConfig();

  apiClient = axios.create({
    baseURL: config.api.base_url,
    timeout: config.api.timeout,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor
  apiClient.interceptors.request.use(
    (config) => {
      // Add executive ID header (no auth in prototype)
      const executiveId = localStorage.getItem('executive_id') || 'exec_001';
      config.headers['X-Executive-ID'] = executiveId;

      console.log('API Request:', config.method.toUpperCase(), config.url);
      return config;
    },
    (error) => {
      console.error('Request error:', error);
      return Promise.reject(error);
    }
  );

  // Response interceptor
  apiClient.interceptors.response.use(
    (response) => {
      console.log('API Response:', response.status, response.config.url);
      return response;
    },
    (error) => {
      console.error('Response error:', error.response?.status, error.response?.data);

      // Handle common errors
      if (error.response) {
        // Server responded with error status
        const { status, data } = error.response;

        if (status === 404) {
          console.error('Resource not found');
        } else if (status === 500) {
          console.error('Server error:', data.detail);
        }
      } else if (error.request) {
        // Request made but no response
        console.error('No response from server. Is the API running?');
      }

      return Promise.reject(error);
    }
  );

  return apiClient;
}
