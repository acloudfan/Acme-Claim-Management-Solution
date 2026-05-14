/**
 * Constants for Executive Portal
 */

export const TIME_PERIODS = [
  { value: 'all', label: 'All Data (6 Months)' },
  { value: 'last_quarter', label: 'Last Quarter (3 Months)' },
  { value: 'last_month', label: 'Last Month' },
  { value: 'last_week', label: 'Last Week' },
  { value: 'custom', label: 'Custom Range' }
];

export const KPI_NAMES = {
  CYCLE_TIME_SAVINGS: 'cycle_time_savings',
  TOTAL_SAVINGS: 'total_savings',
  AUTO_ADJUDICATION: 'auto_adjudication_rate'
};

export const KPI_LABELS = {
  [KPI_NAMES.CYCLE_TIME_SAVINGS]: 'Cycle Time Savings',
  [KPI_NAMES.TOTAL_SAVINGS]: 'LAE Savings',
  [KPI_NAMES.AUTO_ADJUDICATION]: 'Auto-Adjudication Rate'
};

export const CHART_COLORS = {
  blue: '#3b82f6',
  green: '#22c55e',
  yellow: '#f59e0b',
  red: '#ef4444',
  purple: '#a855f7',
  teal: '#14b8a6'
};

export const EXPORT_FORMATS = [
  { value: 'pdf', label: 'PDF Report', icon: '📄' },
  { value: 'csv', label: 'CSV Data', icon: '📊' },
  { value: 'png', label: 'Charts PNG', icon: '📈' }
];
