/**
 * Axios HTTP client configuration with interceptors
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

  // Request interceptor - add customer_id from localStorage
  apiClient.interceptors.request.use(
    (requestConfig) => {
      const customerId = localStorage.getItem('customer_id');
      if (customerId) {
        requestConfig.headers['X-Customer-ID'] = customerId;
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
        localStorage.removeItem('customer_id');
        window.location.href = '/login';
      }

      // Handle network errors
      if (!error.response) {
        console.error('Network error:', error.message);
        error.message = 'Network error. Please check your connection.';
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
