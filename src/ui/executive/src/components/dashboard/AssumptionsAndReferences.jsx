/**
 * AssumptionsAndReferences Component
 * Displays LAE (Loss Adjustment Expense) assumptions, industry benchmarks, and references
 */
import { useState } from 'react';
import { ChevronDown, ChevronRight, Info, ExternalLink } from 'lucide-react';
import Card from '../common/Card';

export default function AssumptionsAndReferences() {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <Card className="mt-8 border-t-2 border-gray-300 bg-gray-50">
      {/* Header - Always Visible */}
      <div
        className="flex items-center justify-between cursor-pointer p-6 hover:bg-gray-100 transition-colors"
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
              📋 Assumptions, Benchmarks & References
            </span>
          </div>
        </div>
        <button className="text-sm font-medium text-gray-600 hover:text-gray-800 transition-colors">
          {isExpanded ? 'Hide Details' : 'Show Details'}
        </button>
      </div>

      {/* Expandable Content */}
      {isExpanded && (
        <div className="px-6 pb-6 border-t border-gray-300">

          {/* LAE Assumptions */}
          <div className="mt-6">
            <h3 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Info className="w-4 h-4 text-blue-600" />
              LAE Assumptions (Loss Adjustment Expense - Claims Processing Cost)
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm border border-gray-200 rounded-lg overflow-hidden">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-4 py-3 text-left font-semibold text-gray-700 border-b border-gray-200">
                      Processing Type
                    </th>
                    <th className="px-4 py-3 text-right font-semibold text-gray-700 border-b border-gray-200">
                      LAE per Claim
                    </th>
                    <th className="px-4 py-3 text-right font-semibold text-gray-700 border-b border-gray-200">
                      Savings vs Traditional
                    </th>
                    <th className="px-4 py-3 text-left font-semibold text-gray-700 border-b border-gray-200">
                      Description
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  <tr className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-900 font-medium">
                      Traditional Processing
                    </td>
                    <td className="px-4 py-3 text-right text-gray-700 font-mono">
                      $357.50
                    </td>
                    <td className="px-4 py-3 text-right text-gray-500">
                      —
                    </td>
                    <td className="px-4 py-3 text-gray-600 text-xs">
                      Manual adjuster review, photos, shop visits, rental coordination (Acme current state: 10% above industry avg)
                    </td>
                  </tr>
                  <tr className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-900 font-medium">
                      AI Auto-Approved
                    </td>
                    <td className="px-4 py-3 text-right text-green-700 font-mono font-semibold">
                      $35.75
                    </td>
                    <td className="px-4 py-3 text-right">
                      <span className="inline-flex items-center px-2 py-1 rounded bg-green-100 text-green-700 font-semibold">
                        90% cheaper
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-600 text-xs">
                      Fully automated, AI-driven, zero human touchpoints (STP)
                    </td>
                  </tr>
                  <tr className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-900 font-medium">
                      AI + Human Review
                    </td>
                    <td className="px-4 py-3 text-right text-green-700 font-mono font-semibold">
                      $107.25
                    </td>
                    <td className="px-4 py-3 text-right">
                      <span className="inline-flex items-center px-2 py-1 rounded bg-green-100 text-green-700 font-semibold">
                        70% cheaper
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-600 text-xs">
                      AI processing with single human review (appeals, high-value, low confidence)
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* AI Eligibility Constraints */}
          <div className="mt-6">
            <h3 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Info className="w-4 h-4 text-blue-600" />
              AI Eligibility Constraints
            </h3>
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="text-sm text-gray-900 space-y-2">
                <p className="font-semibold">
                  Only body damage claims are eligible for AI auto-adjudication
                </p>
                <p className="text-gray-700">
                  Internal damage requires physical inspection and is NOT eligible for AI processing.
                  Based on industry data, only <strong>35% of all auto insurance claims are for body work</strong>,
                  which limits the maximum AI adoption rate.
                </p>
                <div className="mt-3 grid grid-cols-3 gap-3 text-center">
                  <div className="p-3 bg-white rounded border border-blue-300">
                    <div className="text-2xl font-bold text-blue-900">35%</div>
                    <div className="text-xs text-blue-700 mt-1">AI-Eligible Claims</div>
                    <div className="text-xs text-gray-600">(Body damage only)</div>
                  </div>
                  <div className="p-3 bg-white rounded border border-blue-300">
                    <div className="text-2xl font-bold text-blue-900">50%</div>
                    <div className="text-xs text-blue-700 mt-1">Customer Opt-In</div>
                    <div className="text-xs text-gray-600">(Pilot target)</div>
                  </div>
                  <div className="p-3 bg-white rounded border border-blue-300">
                    <div className="text-2xl font-bold text-blue-900">17.5%</div>
                    <div className="text-xs text-blue-700 mt-1">Max AI Usage</div>
                    <div className="text-xs text-gray-600">(35% × 50%)</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Industry Benchmarks */}
          <div className="mt-6">
            <h3 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Info className="w-4 h-4 text-blue-600" />
              Industry Benchmarks
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-4 bg-white border border-gray-200 rounded-lg">
                <div className="text-xs text-gray-600 mb-1">Body Damage Claims</div>
                <div className="text-2xl font-bold text-gray-900">35%</div>
                <div className="text-xs text-gray-500 mt-1">AI-eligible claims only</div>
              </div>
              <div className="p-4 bg-white border border-gray-200 rounded-lg">
                <div className="text-xs text-gray-600 mb-1">Average Cycle Time</div>
                <div className="text-2xl font-bold text-gray-900">19.3 days</div>
                <div className="text-xs text-gray-500 mt-1">Traditional processing</div>
              </div>
              <div className="p-4 bg-white border border-gray-200 rounded-lg">
                <div className="text-xs text-gray-600 mb-1">Fraudulent Claims Rate</div>
                <div className="text-2xl font-bold text-gray-900">15%</div>
                <div className="text-xs text-gray-500 mt-1">Of auto-adjudicated claims</div>
              </div>
              <div className="p-4 bg-white border border-gray-200 rounded-lg">
                <div className="text-xs text-gray-600 mb-1">Average Claim Loss</div>
                <div className="text-2xl font-bold text-gray-900">$6,000</div>
                <div className="text-xs text-gray-500 mt-1">Repair/settlement payout</div>
              </div>
            </div>
          </div>

          {/* Acme's Production Scale */}
          <div className="mt-6">
            <h3 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Info className="w-4 h-4 text-blue-600" />
              Acme's Production Scale
            </h3>
            <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <div className="flex items-center justify-center mb-4">
                <div className="p-6 bg-white border-2 border-purple-400 rounded-lg shadow-sm">
                  <div className="text-xs text-purple-700 mb-2 text-center">ACME's Annual Auto Claims</div>
                  <div className="text-4xl font-bold text-purple-900 text-center">~900K</div>
                  <div className="text-sm text-purple-600 mt-2 text-center">claims/year (~75K/month)</div>
                </div>
              </div>
              <div className="p-3 bg-white border border-purple-300 rounded text-xs text-gray-700">
                <p className="mb-2">
                  <strong>Pilot Scale:</strong> This dashboard shows a 6-month pilot with 4,500 sample claims (750/month = 1% of production volume).
                  All financial projections extrapolate this 1% sample to full production scale (100×).
                </p>
                <p>
                  <strong>At Scale Impact:</strong> With 11.6% AI adoption, Acme would process ~8,700 AI-enabled claims/month at production scale,
                  generating ~$2.6M in monthly LAE savings ($31.3M annual).
                </p>
              </div>
            </div>
          </div>

          {/* Actual Averages from Data */}
          <div className="mt-6">
            <h3 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Info className="w-4 h-4 text-blue-600" />
              Actual Averages (Oct 2025 - Mar 2026)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="text-xs text-blue-700 mb-1">Traditional LAE</div>
                <div className="text-2xl font-bold text-blue-900">$357.71</div>
                <div className="text-xs text-blue-600 mt-1">n = 3,956 claims</div>
              </div>
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="text-xs text-green-700 mb-1">AI Auto-Approved LAE</div>
                <div className="text-2xl font-bold text-green-900">$35.84</div>
                <div className="text-xs text-green-600 mt-1">n = 359 claims</div>
              </div>
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="text-xs text-green-700 mb-1">AI + Review LAE</div>
                <div className="text-2xl font-bold text-green-900">$107.50</div>
                <div className="text-xs text-green-600 mt-1">n = 185 claims</div>
              </div>
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="text-xs text-green-700 mb-1">AI Average LAE</div>
                <div className="text-2xl font-bold text-green-900">$48.52</div>
                <div className="text-xs text-green-600 mt-1">Weighted average</div>
              </div>
            </div>
          </div>

          {/* References */}
          <div className="mt-6">
            <h3 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <ExternalLink className="w-4 h-4 text-blue-600" />
              References & Sources
            </h3>
            <div className="space-y-3 bg-white p-4 rounded-lg border border-gray-200">
              <div className="text-sm">
                <div className="font-semibold text-gray-900 mb-1">
                  [1] Body Damage Claims Rate (35%)
                </div>
                <a
                  href="https://www.autobodynews.com/news/2025-data-points-to-fewer-claims-more-collision-repair-complexity-in-2026"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 hover:underline break-all text-xs"
                >
                  https://www.autobodynews.com/news/2025-data-points-to-fewer-claims-more-collision-repair-complexity-in-2026
                </a>
                <div className="text-xs text-gray-600 mt-1">
                  Auto Body News - Only 35% of claims are body work (AI-eligible)
                </div>
              </div>

              <div className="text-sm">
                <div className="font-semibold text-gray-900 mb-1">
                  [2] Fraudulent Auto Claims Rate (15%)
                </div>
                <a
                  href="https://www.insurancejournal.com/news/national/2015/02/04/356392.htm"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 hover:underline break-all text-xs"
                >
                  https://www.insurancejournal.com/news/national/2015/02/04/356392.htm
                </a>
                <div className="text-xs text-gray-600 mt-1">
                  Insurance Journal - National fraud statistics
                </div>
              </div>

              <div className="text-sm">
                <div className="font-semibold text-gray-900 mb-1">
                  [3] Average Cycle Time (19.3 days)
                </div>
                <a
                  href="https://www.autobodynews.com/news/auto-insurance-customer-satisfaction-strained-by-higher-deductibles-more-total-losses"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 hover:underline break-all text-xs"
                >
                  https://www.autobodynews.com/news/auto-insurance-customer-satisfaction-strained-by-higher-deductibles-more-total-losses
                </a>
                <div className="text-xs text-gray-600 mt-1">
                  Auto Body News - Industry cycle time analysis
                </div>
              </div>

              <div className="text-sm">
                <div className="font-semibold text-gray-900 mb-1">
                  [4] LAE Benchmarks ($20-$450)
                </div>
                <div className="text-xs text-gray-600">
                  Industry average: $325. Acme current state: $357.50 (~10% above industry avg per SOW v5)
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Based on insurance industry LAE (Loss Adjustment Expense) studies. LAE = operational cost to process claims (adjustor labor, inspection, admin overhead, fraud investigation, customer service). Excludes claim payouts (indemnity).
                </div>
              </div>

              <div className="text-sm">
                <div className="font-semibold text-gray-900 mb-1">
                  [5] AI LAE Reduction Factors (70-90%)
                </div>
                <div className="text-xs text-gray-600">
                  Derived from LAE analysis: AI automation reduces Loss Adjustment Expense by eliminating manual touchpoints
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  STP: 0.10 × traditional ($357.50 → $35.75), With review: 0.30 × traditional ($357.50 → $107.25)
                </div>
              </div>
            </div>
          </div>

          {/* Methodology Note */}
          <div className="mt-6 p-4 bg-yellow-50 border-l-4 border-yellow-400 rounded">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-yellow-900">
                <p className="font-semibold mb-1">Methodology Note</p>
                <p className="mb-2">
                  All KPIs, charts, and savings calculations are based on a 1% sample of actual claims
                  (4,500 sample claims representing 450,000 actual claims) with 100× extrapolation.
                </p>
                <p className="mb-2">
                  <strong>AI Eligibility:</strong> Only 35% of claims (body damage) are eligible for AI processing.
                  Internal damage requires physical inspection and cannot be auto-adjudicated by AI.
                  Of eligible claims, 50% of customers opt-in to AI processing (Pilot target), resulting in a maximum
                  AI adoption rate of 17.5% (35% × 50%) of total claims.
                </p>
                <p>
                  <strong>LAE (Loss Adjustment Expense)</strong> represents the internal cost to process a claim and does not
                  include the claim payout amount (average $6,000 per claim). <strong>LAE savings</strong> are
                  calculated by comparing AI processing LAE against Acme's current baseline of $357.50/claim (~10% above $325 industry average per SOW v5).
                </p>
              </div>
            </div>
          </div>

        </div>
      )}
    </Card>
  );
}
