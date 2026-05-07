/**
 * Configuration loader for YAML-based settings.
 * Loads customer-portal-config.yaml from public directory.
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
    const response = await fetch('/customer-portal-config.yaml');
    if (!response.ok) {
      throw new Error(`Failed to load config: ${response.statusText}`);
    }
    const yamlText = await response.text();
    config = yaml.load(yamlText);
    console.log('Configuration loaded successfully');
    return config;
  } catch (error) {
    console.error('Failed to load config, using defaults:', error);
    // Fallback to default configuration
    config = {
      api: {
        base_url: 'http://localhost:8000/api/v1',
        timeout: 120000  // 2 minutes - fraud detection takes ~60 seconds
      },
      mock: {
        customer_id: 100,
        auth_password: 'password123'
      },
      app: {
        name: 'Insurance Claims Portal',
        version: '1.0.0'
      },
      features: {
        enable_appeal: true,
        max_images_per_claim: 20,
        max_image_size_mb: 10
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
