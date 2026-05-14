/**
 * Trend Chart Component
 * Bar + Line hybrid chart using Recharts
 */
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { Info } from 'lucide-react';
import { CHART_COLORS } from '../../utils/constants';

export default function TrendChart({
  title,
  subtitle,
  data = [],
  xAxisKey = 'period_label',
  yAxisKey = 'value',
  yAxisLabel,
  showLine = false,  // Changed default: line duplicates bar data
  showBar = true,
  color = 'blue',
  height = 300,
  onShowNarrative
}) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
        <div className="h-64 flex items-center justify-center text-gray-500">
          No data available
        </div>
      </div>
    );
  }

  const chartColor = CHART_COLORS[color] || CHART_COLORS.blue;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="mb-4 flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
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
          {subtitle && (
            <p className="text-sm text-gray-600 mt-1">{subtitle}</p>
          )}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />

          <XAxis
            dataKey={xAxisKey}
            tick={{ fill: '#6b7280', fontSize: 12 }}
            axisLine={{ stroke: '#d1d5db' }}
          />

          <YAxis
            label={yAxisLabel ? { value: yAxisLabel, angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#6b7280', fontSize: 12 } } : undefined}
            tick={{ fill: '#6b7280', fontSize: 12 }}
            axisLine={{ stroke: '#d1d5db' }}
          />

          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
            }}
            formatter={(value) => [value.toFixed(2), 'Value']}
          />

          <Legend
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="circle"
          />

          {showBar && (
            <Bar
              dataKey={yAxisKey}
              fill={chartColor}
              name="Value"
              radius={[8, 8, 0, 0]}
              opacity={0.8}
            />
          )}

          {showLine && (
            <Line
              type="monotone"
              dataKey={yAxisKey}
              stroke="#ef4444"
              strokeWidth={2}
              name="Trend"
              dot={{ fill: '#ef4444', r: 4 }}
              activeDot={{ r: 6 }}
            />
          )}
        </ComposedChart>
      </ResponsiveContainer>

      {/* Data Summary */}
      {data.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-xs text-gray-600">Data Points</p>
              <p className="text-lg font-semibold text-gray-900">{data.length}</p>
            </div>
            <div>
              <p className="text-xs text-gray-600">Average</p>
              <p className="text-lg font-semibold text-gray-900">
                {(data.reduce((sum, d) => sum + d[yAxisKey], 0) / data.length).toFixed(1)}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-600">Latest</p>
              <p className="text-lg font-semibold text-gray-900">
                {data[data.length - 1][yAxisKey].toFixed(1)}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
