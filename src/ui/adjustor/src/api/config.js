import yaml from 'js-yaml';

let config = null;

export const loadConfig = async () => {
  if (config) return config;

  try {
    const response = await fetch('/adjustor-portal-config.yaml');
    const yamlText = await response.text();
    config = yaml.load(yamlText);
    return config;
  } catch (error) {
    console.error('Failed to load config, using defaults:', error);
    // Fallback to default config
    config = {
      api: {
        base_url: 'http://localhost:8000/api/v1',
        timeout: 120000  // 2 minutes - fraud detection takes ~60 seconds
      },
      auth: {
        mock_password: 'adjustor123'
      },
      features: {
        enable_zoom: true,
        enable_manual_damages: true
      },
      branding: {
        company_name: 'ACME Insurance',
        logo_path: '/assets/ACME-logo.png'
      }
    };
    return config;
  }
};

export const getConfig = () => {
  if (!config) {
    throw new Error('Config not loaded. Call loadConfig() first.');
  }
  return config;
};
