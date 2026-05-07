/**
 * API client configuration with interceptors
 */
import axios from 'axios';
import { getConfig } from './config';

let apiClient = null;

export const getApiClient = () => {
  if (apiClient) return apiClient;

  const config = getConfig();
  const baseURL = config.api.base_url;
  const timeout = config.api.timeout;

  apiClient = axios.create({
    baseURL,
    timeout,
    headers: {
      'Content-Type': 'application/json',
    },
    withCredentials: false,  // Don't send cookies (we use custom headers)
  });

  // Request interceptor - add adjustor ID header
  apiClient.interceptors.request.use(
    (config) => {
      const adjustorId = localStorage.getItem('adjustor_id');
      if (adjustorId) {
        config.headers['X-Adjustor-ID'] = adjustorId;
      }

      // For blob requests, remove Content-Type header to let browser set it
      if (config.responseType === 'blob') {
        delete config.headers['Content-Type'];
      }

      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor - handle 401 errors
  apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        // Unauthorized - redirect to login
        localStorage.removeItem('adjustor_id');
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );

  return apiClient;
};
