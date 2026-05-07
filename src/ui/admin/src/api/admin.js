/**
 * Admin API functions for configuration management
 */
import { getApiClient } from './client';

/**
 * Load current API configuration
 * @returns {Promise<Object>} Configuration response with config, file_path, last_modified
 */
export const loadConfig = async () => {
  const client = getApiClient();
  const response = await client.get('/admin/config');
  return response.data;
};

/**
 * Save updated configuration
 * @param {Object} config - Full configuration object to save
 * @returns {Promise<Object>} Save response with success, backup_file, restart_required
 */
export const saveConfig = async (config) => {
  const client = getApiClient();
  const response = await client.post('/admin/config', { config });
  return response.data;
};

/**
 * List all configuration backup files
 * @returns {Promise<Object>} Backup list response with backups array, total_count
 */
export const listBackups = async () => {
  const client = getApiClient();
  const response = await client.get('/admin/config/backups');
  return response.data;
};

/**
 * Restore configuration from a backup file
 * @param {string} backupFilename - Backup filename to restore from
 * @returns {Promise<Object>} Restore response with success, backup_of_current, restart_required
 */
export const restoreBackup = async (backupFilename) => {
  const client = getApiClient();
  const response = await client.post('/admin/config/restore', {
    backup_filename: backupFilename
  });
  return response.data;
};

/**
 * Reload API configuration without restarting the server
 * @returns {Promise<Object>} Reload response with success, message, timestamp
 */
export const reloadConfig = async () => {
  const client = getApiClient();
  const response = await client.post('/admin/config/reload');
  return response.data;
};
