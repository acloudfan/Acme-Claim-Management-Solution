/**
 * Image upload and retrieval API functions
 */
import { getApiClient } from './client';

const apiClient = () => getApiClient();

/**
 * Upload damage photo
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @param {FormData} formData - Form data with file
 * @param {Function} onProgress - Upload progress callback
 * @returns {Promise} Upload response
 */
export const uploadImage = (customerId, claimId, formData, onProgress) => {
  return apiClient().post(
    `/customers/${customerId}/claims/${claimId}/images`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: onProgress,
    }
  );
};

/**
 * Delete damage photo
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @param {string} imageId - Image filename
 * @returns {Promise} Deletion response
 */
export const deleteImage = (customerId, claimId, imageId) => {
  return apiClient().delete(`/customers/${customerId}/claims/${claimId}/images/${imageId}`);
};

/**
 * Get image URL (original or annotated)
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @param {string} imageId - Image filename
 * @param {boolean} annotated - Get annotated version with bounding boxes
 * @returns {string} Image URL
 */
export const getImageUrl = (customerId, claimId, imageId, annotated = false) => {
  const baseUrl = `/customers/${customerId}/claims/${claimId}/images/${imageId}`;
  const fullUrl = `${apiClient().defaults.baseURL}${baseUrl}`;
  return annotated ? `${fullUrl}?annotated=yes` : fullUrl;
};

/**
 * Get list of images for a claim
 * @param {number} customerId - Customer ID
 * @param {number} claimId - Claim ID
 * @returns {Promise} List of image metadata
 */
export const fetchClaimImages = (customerId, claimId) => {
  return apiClient().get(`/customers/${customerId}/claims/${claimId}/images`);
};
