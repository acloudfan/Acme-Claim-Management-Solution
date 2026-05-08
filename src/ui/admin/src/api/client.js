/**
 * Axios HTTP client configuration with interceptors
 * Admin Portal API Client
 */
import axios from 'axios';
import { getConfig } from './config';

/**
 * Create and configure Axios instance
 * @returns {AxiosInstance} Configured axios instance
 */
const createApiClient = () => {
  const config = getConfig();

  const apiClient = axios.create({
    baseURL: config.api.base_url,
    timeout: config.api.timeout,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor - add admin_id from localStorage
  apiClient.interceptors.request.use(
    (requestConfig) => {
      const adminId = localStorage.getItem('admin_id') || config.auth.default_admin_id;
      if (adminId) {
        requestConfig.headers['X-Admin-ID'] = adminId;
      }
      return requestConfig;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor - handle common errors
  apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
      // Handle 401 Unauthorized - clear auth and redirect to login
      if (error.response?.status === 401) {
        localStorage.removeItem('admin_id');
        window.location.href = '/login';
      }

      // Handle network errors (API server not running)
      if (!error.response) {
        console.error('Network error:', error.message);
        error.message = 'The backend API server is not responding. Please start it to continue.';
      }

      return Promise.reject(error);
    }
  );

  return apiClient;
};

// Singleton instance
let apiClient = null;

/**
 * Get API client instance
 * @returns {AxiosInstance} Axios client
 */
export const getApiClient = () => {
  if (!apiClient) {
    apiClient = createApiClient();
  }
  return apiClient;
};

export default getApiClient;
