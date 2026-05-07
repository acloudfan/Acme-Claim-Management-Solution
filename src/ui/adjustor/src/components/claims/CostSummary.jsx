/**
 * CostSummary component - displays original vs revised estimates
 */
import { formatCurrency } from '../../utils/formatters';
import { AlertTriangle } from 'lucide-react';
import Badge from '../common/Badge';

const CostSummary = ({ originalEstimate, revisedEstimate, damages = [], originalDamages = [] }) => {
  const difference = revisedEstimate - originalEstimate;
  const changePercent = originalEstimate > 0 ? (difference / originalEstimate) * 100 : 0;

  // Identify changes
  const addedDamages = damages.filter(d => d.estimate_type === 'human');
  const adjustedDamages = damages.filter(d => d.reviewed_by_adjustor);

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Cost Summary</h3>

      {/* Estimate Comparison */}
      <div className="space-y-4 mb-6">
        <div className="flex justify-between items-center pb-3 border-b">
          <span className="text-gray-600">Original AI Estimate</span>
          <span className="text-xl font-semibold text-gray-900">
            {formatCurrency(originalEstimate)}
          </span>
        </div>

        <div className="flex justify-between items-center pb-3 border-b">
          <span className="text-gray-600">Revised Estimate</span>
          <span className="text-xl font-semibold text-primary-700">
            {formatCurrency(revisedEstimate)}
          </span>
        </div>

        <div className="flex justify-between items-center pt-2">
          <span className="font-medium text-gray-900">Difference</span>
          <div className="text-right">
            <div className={`text-xl font-bold ${difference > 0 ? 'text-red-600' : difference < 0 ? 'text-green-600' : 'text-gray-900'}`}>
              {difference > 0 ? '+' : ''}{formatCurrency(Math.abs(difference))}
            </div>
            <div className={`text-sm ${Math.abs(changePercent) > 100 ? 'text-red-600 font-semibold' : 'text-gray-600'}`}>
              {changePercent > 0 ? '+' : ''}{changePercent.toFixed(1)}%
            </div>
          </div>
        </div>
      </div>

      {/* Warning for large changes */}
      {Math.abs(changePercent) > 100 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-800">Significant Cost Change</p>
            <p className="text-sm text-red-700 mt-1">
              The revised estimate differs by more than 100% from the AI estimate.
              Please ensure all adjustments are properly documented.
            </p>
          </div>
        </div>
      )}

      {/* Changes List */}
      {(addedDamages.length > 0 || adjustedDamages.length > 0) && (
        <div className="border-t pt-4">
          <h4 className="text-sm font-semibold text-gray-900 mb-3">Changes Made:</h4>

          <div className="space-y-2">
            {addedDamages.length > 0 && (
              <div className="flex items-start gap-2">
                <Badge variant="info" className="mt-0.5">+{addedDamages.length}</Badge>
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    Manual Damage{addedDamages.length > 1 ? 's' : ''} Added
                  </p>
                  <ul className="text-sm text-gray-600 mt-1 space-y-1">
                    {addedDamages.map((d, idx) => (
                      <li key={idx}>
                        • {d.damage_part} ({formatCurrency(d.estimated_total_cost || 0)})
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {adjustedDamages.length > 0 && (
              <div className="flex items-start gap-2">
                <Badge variant="warning" className="mt-0.5">{adjustedDamages.length}</Badge>
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    Cost{adjustedDamages.length > 1 ? 's' : ''} Adjusted
                  </p>
                  <ul className="text-sm text-gray-600 mt-1 space-y-1">
                    {adjustedDamages.map((d, idx) => {
                      const aiTotal = d.ai_total_cost || 0;
                      const adjustorTotal = d.adjustor_total_cost || d.estimated_total_cost || 0;
                      const diff = adjustorTotal - aiTotal;
                      return (
                        <li key={idx}>
                          • {d.damage_part} ({diff > 0 ? '+' : ''}{formatCurrency(diff)})
                        </li>
                      );
                    })}
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default CostSummary;
