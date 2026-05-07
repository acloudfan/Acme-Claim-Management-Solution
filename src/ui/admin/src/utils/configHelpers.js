/**
 * Helper functions for working with nested configuration objects
 */

/**
 * Get nested value from config using dot notation path
 * @param {Object} config - Configuration object
 * @param {string} path - Dot-separated path (e.g., "ai.confidence.high_threshold")
 * @returns {*} Value at path, or undefined if not found
 */
export const getNestedValue = (config, path) => {
  if (!config || !path) return undefined;

  const keys = path.split('.');
  let value = config;

  for (const key of keys) {
    if (value === null || value === undefined || typeof value !== 'object') {
      return undefined;
    }
    value = value[key];
  }

  return value;
};

/**
 * Set nested value in config using dot notation path
 * @param {Object} config - Configuration object (will be cloned)
 * @param {string} path - Dot-separated path
 * @param {*} value - Value to set
 * @returns {Object} New config object with updated value
 */
export const setNestedValue = (config, path, value) => {
  if (!config || !path) return config;

  // Deep clone to avoid mutations
  const newConfig = JSON.parse(JSON.stringify(config));

  const keys = path.split('.');
  let current = newConfig;

  // Navigate to parent object
  for (let i = 0; i < keys.length - 1; i++) {
    const key = keys[i];
    if (!current[key] || typeof current[key] !== 'object') {
      current[key] = {};
    }
    current = current[key];
  }

  // Set value at final key
  current[keys[keys.length - 1]] = value;

  return newConfig;
};

/**
 * Deep clone an object
 * @param {Object} obj - Object to clone
 * @returns {Object} Cloned object
 */
export const deepClone = (obj) => {
  return JSON.parse(JSON.stringify(obj));
};

/**
 * Validate a single field value
 * @param {string} path - Dot-separated path
 * @param {*} value - Value to validate
 * @param {Object} ranges - Validation ranges object
 * @returns {string|null} Error message, or null if valid
 */
export const validateField = (path, value, ranges) => {
  // Type validation
  if (value === null || value === undefined || value === '') {
    return 'Value is required';
  }

  // Range validation for numeric fields
  if (ranges[path]) {
    const { min, max } = ranges[path];

    if (typeof value !== 'number') {
      return 'Must be a number';
    }

    if (value < min || value > max) {
      return `Must be between ${min} and ${max}`;
    }
  }

  // Consistency checks
  if (path === 'ai.confidence.low_threshold') {
    // Low must be less than high
    return null; // Will be checked in validateConsistency
  }

  if (path === 'agents.fraud_detector.medium_risk_threshold') {
    // Medium must be less than high
    return null; // Will be checked in validateConsistency
  }

  return null;
};

/**
 * Validate consistency between related fields
 * @param {Object} config - Full configuration object
 * @returns {Object} Object mapping field paths to error messages
 */
export const validateConsistency = (config) => {
  const errors = {};

  // AI Confidence: low < high
  const lowConf = getNestedValue(config, 'ai.confidence.low_threshold');
  const highConf = getNestedValue(config, 'ai.confidence.high_threshold');
  if (lowConf !== undefined && highConf !== undefined && lowConf >= highConf) {
    errors['ai.confidence.low_threshold'] = 'Must be less than high threshold';
  }

  // Fraud Risk: medium < high
  const mediumRisk = getNestedValue(config, 'agents.fraud_detector.medium_risk_threshold');
  const highRisk = getNestedValue(config, 'agents.fraud_detector.high_risk_threshold');
  if (mediumRisk !== undefined && highRisk !== undefined && mediumRisk >= highRisk) {
    errors['agents.fraud_detector.medium_risk_threshold'] = 'Must be less than high risk threshold';
  }

  return errors;
};

/**
 * Format bytes as human-readable string
 * @param {number} bytes - Size in bytes
 * @returns {string} Formatted string (e.g., "12.3 KB", "1.5 MB")
 */
export const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B';

  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
};
