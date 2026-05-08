/**
 * Filter Sidebar Component
 * Time period filtering, export options, and quick stats
 */
import { useState } from 'react';
import { Calendar, Download, TrendingUp } from 'lucide-react';
import Card from '../common/Card';
import Button from '../common/Button';
import { TIME_PERIODS, EXPORT_FORMATS } from '../../utils/constants';
import { formatNumber, formatCurrency, formatPercent } from '../../utils/formatters';

export default function FilterSidebar({
  currentPeriod,
  onPeriodChange,
  onExport,
  summary,
  exportLoading = false
}) {
  const [customStartDate, setCustomStartDate] = useState('');
  const [customEndDate, setCustomEndDate] = useState('');

  const handlePeriodChange = (period) => {
    if (period === 'custom') {
      onPeriodChange(period, { start: customStartDate, end: customEndDate });
    } else {
      onPeriodChange(period);
    }
  };

  const handleCustomDateApply = () => {
    if (customStartDate && customEndDate) {
      onPeriodChange('custom', { start: customStartDate, end: customEndDate });
    }
  };

  const handleExport = async (format) => {
    if (onExport) {
      await onExport(format);
    }
  };

  return (
    <div className="space-y-6">
      {/* Time Period Filter */}
      <Card>
        <div className="flex items-center gap-2 mb-4">
          <Calendar className="w-5 h-5 text-primary-600" />
          <h3 className="font-semibold text-gray-900">Time Period</h3>
        </div>

        <div className="space-y-2">
          {TIME_PERIODS.map((period) => (
            <div key={period.value}>
              <label className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
                <input
                  type="radio"
                  name="time-period"
                  value={period.value}
                  checked={currentPeriod === period.value}
                  onChange={(e) => handlePeriodChange(e.target.value)}
                  className="w-4 h-4 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm font-medium text-gray-700">
                  {period.label}
                </span>
              </label>

              {/* Custom Date Range Inputs */}
              {period.value === 'custom' && currentPeriod === 'custom' && (
                <div className="ml-7 mt-2 space-y-2">
                  <input
                    type="date"
                    value={customStartDate}
                    onChange={(e) => setCustomStartDate(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    placeholder="Start Date"
                  />
                  <input
                    type="date"
                    value={customEndDate}
                    onChange={(e) => setCustomEndDate(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    placeholder="End Date"
                  />
                  <Button
                    size="sm"
                    onClick={handleCustomDateApply}
                    disabled={!customStartDate || !customEndDate}
                    className="w-full"
                  >
                    Apply
                  </Button>
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>

      {/* Quick Stats */}
      {summary && (
        <Card>
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-primary-600" />
            <h3 className="font-semibold text-gray-900">Quick Stats</h3>
          </div>

          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Total Claims</span>
              <span className="text-lg font-bold text-gray-900">
                {formatNumber(summary.total_claims)}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">AI-Enabled</span>
              <span className="text-lg font-bold text-gray-900">
                {formatNumber(summary.ai_enabled_claims)}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">AI Adoption</span>
              <span className="text-lg font-bold text-primary-600">
                {formatPercent(summary.ai_adoption_rate)}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Total Savings</span>
              <span className="text-lg font-bold text-success-600">
                {formatCurrency(summary.total_savings)}
              </span>
            </div>

            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Accuracy</span>
              <span className="text-lg font-bold text-gray-900">
                {formatPercent(summary.accuracy_within_tolerance)}
              </span>
            </div>
          </div>
        </Card>
      )}

      {/* Extrapolation Card */}
      {summary && (
        <Card className="bg-gradient-to-br from-primary-50 to-primary-100 border-primary-200">
          <h3 className="font-semibold text-gray-900 mb-3">Extrapolation</h3>

          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-700">Current Sample:</span>
              <span className="font-semibold text-gray-900">
                {summary.total_claims} claims
              </span>
            </div>

            <div className="flex justify-between">
              <span className="text-gray-700">Projected Q:</span>
              <span className="font-semibold text-gray-900">
                {formatNumber(summary.total_claims * 100)} claims
              </span>
            </div>

            <div className="pt-2 mt-2 border-t border-primary-200">
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Est. Savings/Q:</span>
                <span className="text-xl font-bold text-success-600">
                  {formatCurrency(summary.total_savings * 100)}
                </span>
              </div>
            </div>
          </div>

          <p className="mt-3 text-xs text-gray-600">
            * Extrapolated from {summary.total_claims} sample claims
          </p>
        </Card>
      )}

      {/* Export Options - Moved to Bottom */}
      <Card>
        <div className="flex items-center gap-2 mb-4">
          <Download className="w-5 h-5 text-primary-600" />
          <h3 className="font-semibold text-gray-900">Export Options</h3>
        </div>

        <div className="space-y-2">
          {EXPORT_FORMATS.map((format) => (
            <Button
              key={format.value}
              variant="ghost"
              size="sm"
              onClick={() => handleExport(format.value)}
              disabled={exportLoading}
              className="w-full justify-start"
            >
              <span className="mr-2">{format.icon}</span>
              {format.label}
            </Button>
          ))}
        </div>

        <p className="mt-4 text-xs text-gray-500">
          💡 Export functionality coming in Phase 5
        </p>
      </Card>
    </div>
  );
}
