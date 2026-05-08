/**
 * Utility functions for formatting values
 */

/**
 * Format number as currency
 * @param {number} value - Value to format
 * @param {string} currency - Currency code (default: USD)
 * @returns {string} Formatted currency string
 */
export function formatCurrency(value, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(value);
}

/**
 * Format number as percentage
 * @param {number} value - Value to format (0-100)
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted percentage string
 */
export function formatPercent(value, decimals = 1) {
  return `${value.toFixed(decimals)}%`;
}

/**
 * Format number with abbreviation (K, M, B)
 * @param {number} value - Value to format
 * @returns {string} Formatted number string
 */
export function formatNumber(value) {
  if (value >= 1000000000) {
    return `${(value / 1000000000).toFixed(1)}B`;
  } else if (value >= 1000000) {
    return `${(value / 1000000).toFixed(1)}M`;
  } else if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}K`;
  }
  return value.toFixed(0);
}

/**
 * Format date as string
 * @param {string|Date} date - Date to format
 * @param {string} format - Format type (short, long, full)
 * @returns {string} Formatted date string
 */
export function formatDate(date, format = 'short') {
  const d = typeof date === 'string' ? new Date(date) : date;

  if (format === 'short') {
    return d.toLocaleDateString('en-US', {
      month: 'numeric',
      day: 'numeric',
      year: 'numeric'
    });
  } else if (format === 'long') {
    return d.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    });
  } else if (format === 'full') {
    return d.toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    });
  }

  return d.toLocaleDateString();
}

/**
 * Format datetime as string
 * @param {string|Date} datetime - Datetime to format
 * @returns {string} Formatted datetime string
 */
export function formatDateTime(datetime) {
  const d = typeof datetime === 'string' ? new Date(datetime) : datetime;
  return d.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });
}

/**
 * Format trend indicator with arrow
 * @param {string} trend - Trend direction (up, down, stable)
 * @param {number} changePercent - Change percentage
 * @returns {Object} Icon and color
 */
export function formatTrend(trend, changePercent) {
  if (trend === 'up') {
    return {
      icon: '↑',
      color: changePercent > 0 ? 'text-success-600' : 'text-error-600',
      label: `${changePercent > 0 ? '+' : ''}${changePercent.toFixed(1)}%`
    };
  } else if (trend === 'down') {
    return {
      icon: '↓',
      color: changePercent < 0 ? 'text-success-600' : 'text-error-600',
      label: `${changePercent.toFixed(1)}%`
    };
  } else {
    return {
      icon: '─',
      color: 'text-gray-600',
      label: '0%'
    };
  }
}

/**
 * Get KPI status color
 * @param {string} status - Status (good, warning, critical)
 * @returns {string} Tailwind color class
 */
export function getStatusColor(status) {
  switch (status) {
    case 'good':
      return 'text-success-600 bg-success-50 border-success-200';
    case 'warning':
      return 'text-warning-600 bg-warning-50 border-warning-200';
    case 'critical':
      return 'text-error-600 bg-error-50 border-error-200';
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200';
  }
}

/**
 * Format KPI value based on unit
 * @param {number} value - Value to format
 * @param {string} unit - Unit type (days, percent, dollars)
 * @returns {string} Formatted value string
 */
export function formatKPIValue(value, unit) {
  switch (unit) {
    case 'days':
      return `${value.toFixed(1)} days`;
    case 'days_saved':
      return `${value.toFixed(1)} days`;
    case 'percent':
      return `${value.toFixed(1)}%`;
    case 'dollars':
      return formatCurrency(value);
    default:
      return value.toString();
  }
}
