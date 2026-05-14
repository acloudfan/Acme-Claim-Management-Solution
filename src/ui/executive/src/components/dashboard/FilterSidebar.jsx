/**
 * Filter Sidebar Component
 * Time period filtering, export options, and quick stats
 */
import { useState } from 'react';
import { Calendar, Download, TrendingUp, ChevronDown, ChevronRight } from 'lucide-react';
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
  const [isProjectionsExpanded, setIsProjectionsExpanded] = useState(false);
  const [isExportExpanded, setIsExportExpanded] = useState(false);

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
            {/* Total Claims: 4,500 (750/month × 6 months from Oct 2025 - Mar 2026) */}
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Total Claims</span>
              <span className="text-lg font-bold text-gray-900">
                {formatNumber(summary.total_claims)}
              </span>
            </div>

            {/* AI-Enabled: 523 claims (12% of total: 8% auto-approved, 4% human-reviewed) */}
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">AI-Enabled</span>
              <span className="text-lg font-bold text-gray-900">
                {formatNumber(summary.ai_enabled_claims)}
              </span>
            </div>

            {/* AI Adoption: (523 / 4,500) × 100 = 11.6%
                Includes: 359 auto-approved (69%) + 164 human-reviewed (31%) = 523 total AI */}
            <div className="flex flex-col">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">AI Adoption</span>
                <span className="text-lg font-bold text-primary-600">
                  {formatPercent(summary.ai_adoption_rate)}
                </span>
              </div>
              <div className="text-xs text-gray-500 mt-0.5">
                {formatNumber(summary.ai_auto_approved_claims)} auto + {formatNumber(summary.ai_human_reviewed_claims)} review
              </div>
            </div>

            {/* Total Savings: (523 × $357.50 baseline) - $30,431 actual cost = $156,542
                Actual cost includes: 359 auto-approved @ $35.77 + 164 human-reviewed @ $107.26 */}
            <div className="border-l-4 border-success-400 pl-3 py-2 bg-success-50 rounded">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-gray-600 font-medium">Total Savings</span>
                <span className="text-lg font-bold text-success-600">
                  {formatCurrency(summary.total_savings)}
                </span>
              </div>
              <div className="text-xs text-gray-600 space-y-0.5">
                <div className="flex justify-between">
                  <span>Baseline cost (if traditional):</span>
                  <span className="font-mono">{formatNumber(summary.ai_enabled_claims)} × $357.50 = {formatCurrency(summary.ai_enabled_claims * 357.50)}</span>
                </div>
                <div className="flex justify-between">
                  <span>Actual AI cost (auto + review):</span>
                  <span className="font-mono">- {formatCurrency(summary.ai_enabled_claims * 357.50 - summary.total_savings)}</span>
                </div>
                <div className="flex justify-between pt-1 border-t border-success-200">
                  <span className="font-semibold">Savings:</span>
                  <span className="font-mono font-semibold">{formatCurrency(summary.total_savings)}</span>
                </div>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Extrapolation Card - Collapsible */}
      {summary && (
        <Card className="bg-gradient-to-br from-primary-50 to-primary-100 border-primary-200">
          <div
            className="flex items-center justify-between cursor-pointer"
            onClick={() => setIsProjectionsExpanded(!isProjectionsExpanded)}
          >
            <h3 className="font-semibold text-gray-900 flex items-center gap-2">
              {isProjectionsExpanded ? (
                <ChevronDown className="w-4 h-4 text-gray-600" />
              ) : (
                <ChevronRight className="w-4 h-4 text-gray-600" />
              )}
              Annual Projections
            </h3>
            <span className="text-xs text-gray-600">
              {isProjectionsExpanded ? 'Hide' : 'Show'}
            </span>
          </div>

          {isProjectionsExpanded && (
            <div className="space-y-3 text-sm mt-3">
            <div className="flex justify-between">
              <span className="text-gray-700">Sample Period:</span>
              <span className="font-semibold text-gray-900">6 months</span>
            </div>

            <div className="flex justify-between">
              <span className="text-gray-700">Sample Size:</span>
              <span className="font-semibold text-gray-900">
                {formatNumber(summary.total_claims)} claims
              </span>
            </div>

            <div className="flex justify-between">
              <span className="text-gray-700">Production Scale:</span>
              <span className="font-semibold text-gray-900">
                75K claims/month
              </span>
            </div>

            <div className="pt-3 mt-3 border-t border-primary-200 space-y-3">
              <div className="p-3 bg-white rounded-lg border border-success-300">
                <div className="flex justify-between items-start mb-1">
                  <div className="flex flex-col">
                    <span className="text-gray-800 font-medium">Annual Savings:</span>
                    <span className="text-xs text-gray-600">At production scale (100×)</span>
                  </div>
                  <span className="text-2xl font-bold text-success-700">
                    {formatCurrency(summary.total_savings * 100 * 2)}
                  </span>
                </div>
                <p className="text-xs text-gray-600 text-right">
                  12% AI adoption (8% auto, 4% review)
                </p>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2 bg-white rounded border border-primary-200">
                  <div className="text-gray-600 mb-1">Quarterly</div>
                  <div className="font-bold text-gray-900">
                    {formatCurrency(summary.total_savings * 100 * 0.5)}
                  </div>
                </div>
                <div className="p-2 bg-white rounded border border-primary-200">
                  <div className="text-gray-600 mb-1">Monthly</div>
                  <div className="font-bold text-gray-900">
                    {formatCurrency(summary.total_savings * 100 / 6)}
                  </div>
                </div>
              </div>
            </div>

            <p className="pt-3 border-t border-primary-200 text-xs text-gray-600">
              <strong>Scale Factor:</strong> 100× (750 sample = 1% of 75K production claims/month)<br/>
              <strong>Calculation:</strong> 6-month savings × 100 = Extrapolated 6-month; ×2 = Annual
            </p>
          </div>
          )}
        </Card>
      )}

      {/* Export Options - Collapsible */}
      <Card>
        <div
          className="flex items-center justify-between cursor-pointer"
          onClick={() => setIsExportExpanded(!isExportExpanded)}
        >
          <div className="flex items-center gap-2">
            {isExportExpanded ? (
              <ChevronDown className="w-4 h-4 text-gray-600" />
            ) : (
              <ChevronRight className="w-4 h-4 text-gray-600" />
            )}
            <Download className="w-5 h-5 text-primary-600" />
            <h3 className="font-semibold text-gray-900">Export Options</h3>
          </div>
          <span className="text-xs text-gray-600">
            {isExportExpanded ? 'Hide' : 'Show'}
          </span>
        </div>

        {isExportExpanded && (
          <>
            <div className="space-y-2 mt-4">
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
          </>
        )}
      </Card>
    </div>
  );
}
