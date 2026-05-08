/**
 * Load portal configuration from YAML file
 */
import yaml from 'js-yaml';

let config = null;

export async function loadConfig() {
  if (config) return config;

  try {
    const response = await fetch('/executive-portal-config.yaml');
    if (!response.ok) {
      throw new Error(`Failed to load config: ${response.statusText}`);
    }
    const text = await response.text();
    config = yaml.load(text);
    console.log('Executive Portal Config loaded:', config);
    return config;
  } catch (error) {
    console.error('Error loading executive portal config:', error);
    // Return default config as fallback
    config = {
      api: {
        base_url: 'http://localhost:8000/api/v1',
        timeout: 30000
      },
      auth: {
        require_login: false,
        default_executive_id: 'exec_001'
      },
      portal_links: {
        customer_portal_url: 'http://localhost:5173',
        adjustor_portal_url: 'http://localhost:5174',
        admin_portal_url: 'http://localhost:5170'
      },
      dashboard: {
        default_time_period: 'last_quarter',
        auto_refresh: false
      },
      features: {
        enable_export: true,
        enable_drill_down: true,
        enable_nlp_queries: false
      }
    };
    return config;
  }
}

export function getConfig() {
  if (!config) {
    throw new Error('Config not loaded. Call loadConfig() first.');
  }
  return config;
}
