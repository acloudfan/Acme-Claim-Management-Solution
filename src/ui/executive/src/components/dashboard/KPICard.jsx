/**
 * KPI Card Component
 * Displays single KPI with trend, mini chart, and status
 */
import { TrendingUp, TrendingDown, Minus, Info } from 'lucide-react';
import { BarChart, Bar, ResponsiveContainer } from 'recharts';
import { formatKPIValue, getStatusColor } from '../../utils/formatters';

export default function KPICard({
  title,
  kpi,
  miniChartData = [],
  onDrillDown,
  onShowNarrative
}) {
  if (!kpi) return null;

  const { current_value, unit, trend, change_percent, target, status } = kpi;

  // Trend icon and color
  const getTrendIcon = () => {
    if (trend === 'up') return <TrendingUp className="w-5 h-5" />;
    if (trend === 'down') return <TrendingDown className="w-5 h-5" />;
    return <Minus className="w-5 h-5" />;
  };

  // Determine if trend is good (depends on KPI)
  const isGoodTrend = () => {
    // For cycle_time and cost_per_claim, down is good
    // For auto_adjudication_rate and fraud_detection_rate, up is good
    const downIsGood = ['cycle_time', 'cost_per_claim'].includes(title.toLowerCase().replace(/\s+/g, '_'));

    if (trend === 'down' && downIsGood) return true;
    if (trend === 'up' && !downIsGood) return true;
    return false;
  };

  const trendColor = isGoodTrend() ? 'text-success-600' :
                     trend === 'stable' ? 'text-gray-600' : 'text-error-600';

  const statusColors = getStatusColor(status);

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      {/* Title */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-medium text-gray-600">{title}</h3>
          {onShowNarrative && (
            <button
              onClick={onShowNarrative}
              className="p-1 hover:bg-gray-100 rounded transition-colors"
              aria-label="Show help"
            >
              <Info className="w-4 h-4 text-gray-400 hover:text-primary-600" />
            </button>
          )}
        </div>
        <div className={`px-2 py-1 rounded text-xs font-semibold border ${statusColors}`}>
          {status.toUpperCase()}
        </div>
      </div>

      {/* Value */}
      <div className="mb-3">
        <div className="flex items-baseline gap-2">
          <span className="text-4xl font-bold text-gray-900">
            {formatKPIValue(current_value, unit).split(' ')[0]}
          </span>
          <span className="text-lg text-gray-600">
            {unit === 'days' ? 'days' : unit === 'percent' ? '%' : ''}
          </span>
        </div>
      </div>

      {/* Trend */}
      <div className={`flex items-center gap-1 mb-4 ${trendColor}`}>
        {getTrendIcon()}
        <span className="text-sm font-semibold">
          {change_percent > 0 && trend !== 'stable' ? '+' : ''}{change_percent.toFixed(1)}%
        </span>
        <span className="text-xs text-gray-500">
          {title.includes('Cycle Time') ? 'of baseline' :
           title.includes('Total Savings') ? 'saved' :
           'vs previous'}
        </span>
      </div>

      {/* Mini Chart */}
      {miniChartData && miniChartData.length > 0 && (
        <div className="h-16 mb-3">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={miniChartData}>
              <Bar
                dataKey="value"
                fill={isGoodTrend() ? '#22c55e' : '#3b82f6'}
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Target */}
      {target && (
        <div className="text-xs text-gray-500 mb-2">
          Target: {formatKPIValue(target, unit)}
        </div>
      )}

      {/* Drill Down Link */}
      {onDrillDown && (
        <button
          onClick={onDrillDown}
          className="text-sm text-primary-600 hover:text-primary-700 font-medium hover:underline"
        >
          View Details →
        </button>
      )}
    </div>
  );
}
