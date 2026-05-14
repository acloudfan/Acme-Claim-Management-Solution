/**
 * SampleDataDistribution Component
 * Displays sample data methodology and monthly distribution table
 */
import { useState } from 'react';
import { ChevronDown, ChevronRight, Info } from 'lucide-react';
import Card from '../common/Card';

export default function SampleDataDistribution({
  sampleSize = 4500,
  actualVolume = 450000,
  extrapolationFactor = 100,
  monthlyDistribution = []
}) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Calculate totals
  const avgAutoAdj = monthlyDistribution.length > 0
    ? (monthlyDistribution.reduce((sum, m) => sum + m.autoAdjPct, 0) / monthlyDistribution.length).toFixed(1)
    : 0;

  return (
    <Card id="sample-data-distribution" className="mt-8 border-t-2 border-blue-200 bg-white transition-all duration-300">
      {/* Header - Always Visible */}
      <div
        data-expandable-header
        className="flex items-center justify-between cursor-pointer p-6 hover:bg-gray-50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            {isExpanded ? (
              <ChevronDown className="w-5 h-5 text-gray-600" />
            ) : (
              <ChevronRight className="w-5 h-5 text-gray-600" />
            )}
            <span className="text-lg font-semibold text-gray-900">
              📊 Sample Data Distribution & Methodology
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 text-xs font-medium text-blue-700 bg-blue-100 rounded-full">
              {sampleSize.toLocaleString()} samples
            </span>
            <span className="px-3 py-1 text-xs font-medium text-green-700 bg-green-100 rounded-full">
              {extrapolationFactor}× extrapolation
            </span>
          </div>
        </div>
        <button className="text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors">
          {isExpanded ? 'Hide Details' : 'Show Details'}
        </button>
      </div>

      {/* Expandable Content */}
      {isExpanded && (
        <div className="px-6 pb-6 border-t border-gray-200">
          {/* Data Source Info */}
          <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-5">
            <h3 className="text-sm font-semibold text-blue-900 mb-3 flex items-center gap-2">
              <Info className="w-4 h-4" />
              Data Source & Methodology
            </h3>
            <div className="space-y-2 text-sm text-blue-900">
              <div className="flex items-start gap-2">
                <span className="font-semibold min-w-[140px]">Sample Size:</span>
                <span>{sampleSize.toLocaleString()} claims (1% of actual volume)</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="font-semibold min-w-[140px]">Actual Volume:</span>
                <span>{actualVolume.toLocaleString()} claims (Oct 2025 - Mar 2026)</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="font-semibold min-w-[140px]">Extrapolation:</span>
                <span>All dashboard metrics are multiplied by {extrapolationFactor}× to represent full operational volume</span>
              </div>
              <div className="flex items-start gap-2">
                <span className="font-semibold min-w-[140px]">Time Period:</span>
                <span>6 months (October 2025 - March 2026)</span>
              </div>
            </div>
          </div>

          {/* Processing Mix Distribution */}
          <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-5">
            <h3 className="text-sm font-semibold text-green-900 mb-3 flex items-center gap-2">
              <Info className="w-4 h-4" />
              Processing Path Distribution (6-Month Average)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="bg-white rounded-lg p-4 border border-green-200">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-gray-700 font-semibold">Traditional</span>
                  <span className="text-2xl font-bold text-gray-900">88%</span>
                </div>
                <p className="text-xs text-gray-600">
                  Not AI-eligible (internal damage) or customer declined AI processing
                </p>
              </div>
              <div className="bg-white rounded-lg p-4 border border-green-200">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-gray-700 font-semibold">AI Auto-Approved</span>
                  <span className="text-2xl font-bold text-success-700">8%</span>
                </div>
                <p className="text-xs text-gray-600">
                  Fully automated, zero human touchpoints (STP)
                </p>
              </div>
              <div className="bg-white rounded-lg p-4 border border-green-200">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-gray-700 font-semibold">AI + Human Review</span>
                  <span className="text-2xl font-bold text-primary-700">4%</span>
                </div>
                <p className="text-xs text-gray-600">
                  AI assessment with adjuster validation
                </p>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-green-200 text-xs text-green-900">
              <p className="mb-2">
                <strong>Auto-Adjudication Rate:</strong> 67% of AI-processed claims (8% auto / 12% total AI = 67%)
              </p>
              <p className="mb-2">
                <strong>AI Adoption Ceiling:</strong> 35% of claims are body damage (AI-eligible) × 50% customer opt-in = 17.5% maximum
              </p>
              <p>
                <strong>Auto-Approval Threshold:</strong> Fixed at $5,000 for all 6 months (consistent policy)
              </p>
            </div>
          </div>

          {/* Monthly Distribution Table */}
          {monthlyDistribution.length > 0 && (
            <div className="mt-6">
              <h3 className="text-sm font-semibold text-gray-900 mb-4">
                Monthly Sample Distribution
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm border border-gray-200 rounded-lg overflow-hidden">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="px-4 py-3 text-left font-semibold text-gray-700 border-b border-gray-200">
                        Month
                      </th>
                      <th className="px-4 py-3 text-right font-semibold text-gray-700 border-b border-gray-200">
                        Sample Claims
                      </th>
                      <th className="px-4 py-3 text-right font-semibold text-gray-700 border-b border-gray-200">
                        Auto-Adj %
                      </th>
                      <th className="px-4 py-3 text-right font-semibold text-gray-700 border-b border-gray-200">
                        AI Threshold
                      </th>
                      <th className="px-4 py-3 text-right font-semibold text-gray-700 border-b border-gray-200">
                        Extrapolated
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {monthlyDistribution.map((row, idx) => (
                      <tr key={idx} className="hover:bg-gray-50 transition-colors">
                        <td className="px-4 py-3 text-gray-900 font-medium">
                          {row.month}
                        </td>
                        <td className="px-4 py-3 text-right text-gray-700">
                          {row.claims.toLocaleString()}
                        </td>
                        <td className="px-4 py-3 text-right text-gray-700">
                          <span className={`inline-flex items-center px-2 py-1 rounded ${
                            row.autoAdjPct >= 50 ? 'bg-green-100 text-green-700' :
                            row.autoAdjPct >= 30 ? 'bg-yellow-100 text-yellow-700' :
                            'bg-red-100 text-red-700'
                          }`}>
                            {row.autoAdjPct}%
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right text-gray-700 font-mono">
                          ${row.threshold.toLocaleString()}
                        </td>
                        <td className="px-4 py-3 text-right text-gray-600 font-semibold">
                          {(row.claims * extrapolationFactor).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                    {/* Total Row */}
                    <tr className="bg-gray-100 font-semibold border-t-2 border-gray-300">
                      <td className="px-4 py-3 text-gray-900">
                        Total
                      </td>
                      <td className="px-4 py-3 text-right text-gray-900">
                        {sampleSize.toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-right text-gray-900">
                        {avgAutoAdj}% avg
                      </td>
                      <td className="px-4 py-3 text-right text-gray-500 text-xs">
                        Progressive
                      </td>
                      <td className="px-4 py-3 text-right text-gray-900">
                        {actualVolume.toLocaleString()}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Important Note */}
          <div className="mt-6 p-4 bg-yellow-50 border-l-4 border-yellow-400 rounded">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-yellow-900">
                <p className="font-semibold mb-1">Important Note</p>
                <p>
                  All KPIs, charts, and metrics displayed on this dashboard represent extrapolated values
                  (sample × {extrapolationFactor}). This approach allows for realistic business intelligence
                  insights while maintaining manageable data volumes for demonstration purposes.
                </p>
              </div>
            </div>
          </div>

          {/* AI Threshold Strategy Note */}
          <div className="mt-4 p-4 bg-blue-50 border-l-4 border-blue-400 rounded">
            <div className="flex items-start gap-3">
              <div className="text-2xl">💡</div>
              <div className="text-sm text-blue-900">
                <p className="font-semibold mb-1">AI Threshold Strategy</p>
                <p className="mb-2">
                  <strong>Simulation Baseline:</strong> This synthetic dataset uses a fixed auto-adjudication threshold of <strong>${monthlyDistribution[0]?.threshold.toLocaleString()}</strong>
                  to establish a consistent baseline for demonstrating AI performance and LAE savings potential.
                </p>
                <p className="text-xs bg-white border border-blue-200 rounded p-2 mt-2">
                  <strong>Production Strategy (if pilot results are promising):</strong> In actual deployment, the threshold will be progressively increased
                  to maximize LAE (Loss Adjustment Expense) savings. Higher thresholds = more AI-automated claims = greater operational cost reduction.
                  Threshold adjustments will be based on AI accuracy performance, business risk tolerance, and regulatory requirements.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
}
