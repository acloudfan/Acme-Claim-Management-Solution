/**
 * Configuration loader for YAML-based settings.
 * Loads admin-portal-config.yaml from public directory.
 */
import yaml from 'js-yaml';

let config = null;

/**
 * Load configuration from YAML file
 * @returns {Promise<Object>} Configuration object
 */
export const loadConfig = async () => {
  if (config) return config;

  try {
    const response = await fetch('/admin-portal-config.yaml');
    if (!response.ok) {
      throw new Error(`Failed to load config: ${response.statusText}`);
    }
    const yamlText = await response.text();
    config = yaml.load(yamlText);
    console.log('Admin configuration loaded successfully');
    return config;
  } catch (error) {
    console.error('Failed to load config, using defaults:', error);
    // Fallback to default configuration
    config = {
      api: {
        base_url: 'http://localhost:8000/api/v1',
        timeout: 30000  // 30 seconds
      },
      auth: {
        require_login: false,
        default_admin_id: 'admin_001'
      },
      portal_links: {
        customer_portal_url: 'http://localhost:5173',
        adjustor_portal_url: 'http://localhost:5174',
        executive_portal_url: null
      },
      features: {
        enable_backup_restore: true,
        enable_validation_preview: false,
        enable_auto_restart: false
      }
    };
    return config;
  }
};

/**
 * Get loaded configuration
 * @returns {Object} Configuration object
 * @throws {Error} If configuration hasn't been loaded yet
 */
export const getConfig = () => {
  if (!config) {
    throw new Error('Config not loaded. Call loadConfig() first in main.jsx');
  }
  return config;
};
