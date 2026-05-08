/**
 * Executive Portal API endpoints
 */
import { getApiClient } from './client';

/**
 * Fetch all KPIs
 * @param {string} timePeriod - Time period filter (last_week, last_month, last_quarter, custom)
 * @param {string} startDate - Start date for custom period (YYYY-MM-DD)
 * @param {string} endDate - End date for custom period (YYYY-MM-DD)
 * @returns {Promise<Object>} KPI data
 */
export async function fetchKPIs(timePeriod = 'last_quarter', startDate = null, endDate = null) {
  const client = getApiClient();
  const params = { time_period: timePeriod, compare_to_previous: true };

  if (timePeriod === 'custom' && startDate && endDate) {
    params.start_date = startDate;
    params.end_date = endDate;
  }

  const response = await client.get('/executive/kpis', { params });
  return response.data;
}

/**
 * Fetch trend data for specific KPI
 * @param {string} kpiName - KPI name (cycle_time, auto_adjudication_rate, cost_per_claim, fraud_detection_rate)
 * @param {string} granularity - Time granularity (daily, weekly, monthly)
 * @param {string} startDate - Start date (YYYY-MM-DD)
 * @param {string} endDate - End date (YYYY-MM-DD)
 * @returns {Promise<Object>} Trend data
 */
export async function fetchTrendData(kpiName, granularity = 'monthly', startDate = null, endDate = null) {
  const client = getApiClient();
  const params = { granularity };

  if (startDate && endDate) {
    params.start_date = startDate;
    params.end_date = endDate;
  }

  const response = await client.get(`/executive/trends/${kpiName}`, { params });
  return response.data;
}

/**
 * Execute preset or custom query
 * @param {string} queryType - Query type (preset, custom)
 * @param {string} presetId - Preset query ID
 * @param {Object} timeRange - Time range filter {start_date, end_date}
 * @param {string} customQuery - Custom NLP query text
 * @returns {Promise<Object>} Query results
 */
export async function executeQuery(queryType, presetId = null, timeRange = {}, customQuery = null) {
  const client = getApiClient();

  const requestBody = {
    query_type: queryType,
    time_range: timeRange
  };

  if (queryType === 'preset') {
    requestBody.preset_id = presetId;
  } else if (queryType === 'custom') {
    requestBody.custom_query = customQuery;
  }

  const response = await client.post('/executive/query', requestBody);
  return response.data;
}

/**
 * Fetch claim details for drill-down
 * @param {number} claimId - Claim ID
 * @returns {Promise<Object>} Claim details
 */
export async function fetchClaimDetails(claimId) {
  const client = getApiClient();
  const response = await client.get(`/executive/drilldown/${claimId}`);
  return response.data;
}

/**
 * Export dashboard data
 * @param {string} format - Export format (pdf, csv, png)
 * @param {string} kpi - KPI filter (all, cycle_time, etc.)
 * @param {string} timePeriod - Time period filter
 * @returns {Promise<Blob>} File blob
 */
export async function exportDashboard(format, kpi = 'all', timePeriod = 'last_quarter') {
  const client = getApiClient();
  const response = await client.get(`/executive/export/${format}`, {
    params: { kpi, time_period: timePeriod },
    responseType: 'blob'
  });
  return response.data;
}

/**
 * Preset query definitions
 */
export const PRESET_QUERIES = [
  {
    id: 'processing_path',
    label: 'Claims by Processing Path',
    description: 'How many claims were auto-approved vs human-reviewed?'
  },
  {
    id: 'adjustment_rate',
    label: 'Adjustment Rate Analysis',
    description: 'How many estimates needed adjustment during repairs?'
  },
  {
    id: 'human_intervention',
    label: 'Human Intervention Trends',
    description: 'Show human review rate trend over 3 months'
  },
  {
    id: 'fraud_effectiveness',
    label: 'Fraud Detection Effectiveness',
    description: "What's the fraud detection rate by month?"
  }
];
