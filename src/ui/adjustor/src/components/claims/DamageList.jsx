/**
 * DamageList component - displays list of damages with costs
 */
import { useState } from 'react';
import { Edit2, ChevronDown, ChevronUp } from 'lucide-react';
import { formatCurrency } from '../../utils/formatters';
import { DAMAGE_TYPE_LABELS, SEVERITY_LABELS, SEVERITY_COLORS } from '../../utils/constants';
import Badge from '../common/Badge';

const DamageList = ({ damages, onEdit, editable = true }) => {
  const [expandedReasoning, setExpandedReasoning] = useState({});
  if (!damages || damages.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No damages detected or added.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {damages.map((damage, index) => {
        const total = damage.estimated_total_cost || 0;
        const laborRate = damage.labor_rate || 0;

        return (
          <div
            key={damage.damage_id || index}
            className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex justify-between items-start mb-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <h4 className="text-lg font-semibold text-gray-900">
                    {damage.damage_part || DAMAGE_TYPE_LABELS[damage.damage_type] || damage.damage_type}
                  </h4>
                  {damage.severity && (
                    <Badge variant="default">
                      <span className={SEVERITY_COLORS[damage.severity]}>
                        {SEVERITY_LABELS[damage.severity]}
                      </span>
                    </Badge>
                  )}
                  {damage.reviewed_by_adjustor && (
                    <Badge variant="success">Reviewed by Adjustor</Badge>
                  )}
                  {damage.estimate_type === 'human' && (
                    <Badge variant="info">Manual Entry</Badge>
                  )}
                </div>

                {damage.location && (
                  <p className="text-sm text-gray-600 mb-1">
                    <span className="font-medium">Location:</span> {damage.location}
                  </p>
                )}

                {damage.confidence && (
                  <p className="text-sm text-gray-600 mb-1">
                    <span className="font-medium">AI Confidence:</span> {Math.round(damage.confidence * 100)}%
                  </p>
                )}

                {damage.description && (
                  <p className="text-sm text-gray-600 mt-2">
                    {damage.description}
                  </p>
                )}

                {/* Damage Summary (Customer-friendly description from LLM) */}
                {damage.damage_summary && (
                  <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-xs font-medium text-blue-800 mb-1">AI Assessment Summary:</p>
                    <p className="text-sm text-blue-900">{damage.damage_summary}</p>
                  </div>
                )}

                {/* Additional Assessment Details */}
                {(damage.recommended_action || damage.reasoning || damage.car_side || damage.assessment_confidence) && (
                  <div className="mt-3 p-3 bg-gray-50 border border-gray-200 rounded-lg">
                    <p className="text-xs font-medium text-gray-700 mb-2">Additional Assessment Details:</p>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      {damage.recommended_action && (
                        <div>
                          <span className="text-gray-600">Recommended Action:</span>
                          <span className="ml-1 font-medium text-gray-900">{damage.recommended_action}</span>
                        </div>
                      )}
                      {damage.car_side && (
                        <div>
                          <span className="text-gray-600">Car Side:</span>
                          <span className="ml-1 font-medium text-gray-900">{damage.car_side}</span>
                        </div>
                      )}
                      {damage.assessment_confidence !== null && damage.assessment_confidence !== undefined && (
                        <div>
                          <span className="text-gray-600">Assessment Confidence:</span>
                          <span className="ml-1 font-medium text-gray-900">
                            {Math.round(damage.assessment_confidence * 100)}%
                          </span>
                        </div>
                      )}
                    </div>
                    {damage.reasoning && (
                      <div className="mt-2">
                        <button
                          onClick={() => setExpandedReasoning(prev => ({
                            ...prev,
                            [damage.damage_id]: !prev[damage.damage_id]
                          }))}
                          className="flex items-center gap-1 text-xs font-medium text-gray-700 hover:text-gray-900 transition-colors"
                        >
                          <span>Reasoning</span>
                          {expandedReasoning[damage.damage_id] ? (
                            <ChevronUp className="w-4 h-4" />
                          ) : (
                            <ChevronDown className="w-4 h-4" />
                          )}
                        </button>
                        {expandedReasoning[damage.damage_id] && (
                          <p className="text-sm text-gray-800 mt-2 leading-relaxed">
                            {damage.reasoning}
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {editable && onEdit && (
                <button
                  onClick={() => onEdit(damage)}
                  className="ml-4 p-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                  aria-label="Edit damage"
                >
                  <Edit2 className="h-5 w-5" />
                </button>
              )}
            </div>

            {/* AI Estimate Baseline */}
            {damage.ai_total_cost && (
              <div className="text-xs text-gray-500 mb-2 bg-gray-50 p-2 rounded">
                <span className="font-semibold">AI Estimated:</span>{' '}
                {damage.ai_labor_hours?.toFixed(1)}h × ${laborRate} + ${damage.ai_parts_cost} = ${damage.ai_total_cost.toFixed(2)}
              </div>
            )}

            {/* Cost Breakdown */}
            <div className="border-t pt-3 mt-3">
              <div className="grid grid-cols-3 gap-3 text-sm">
                <div>
                  <p className="text-gray-600">Labor Cost</p>
                  <p className="font-medium text-gray-900">
                    {damage.labor_hours && laborRate
                      ? formatCurrency((damage.labor_hours || 0) * laborRate)
                      : '-'}
                  </p>
                  <p className="text-xs text-gray-500">{damage.labor_hours?.toFixed(1)}h × ${laborRate}</p>
                </div>
                <div>
                  <p className="text-gray-600">Parts Cost</p>
                  <p className="font-medium text-gray-900">
                    {damage.estimated_parts_cost ? formatCurrency(damage.estimated_parts_cost) : '-'}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Current Total</p>
                  <p className="font-bold text-lg text-primary-700">
                    {formatCurrency(total)}
                  </p>
                  {damage.estimate_source === 'adjustor' && (
                    <p className="text-xs text-green-600 font-medium">Adjustor Revised</p>
                  )}
                </div>
              </div>

              {/* Show variance if adjustor modified */}
              {damage.reviewed_by_adjustor && damage.ai_total_cost && (
                <div className="mt-2 text-sm">
                  <span className="text-gray-600">Variance from AI: </span>
                  <span className={total - damage.ai_total_cost >= 0 ? 'text-red-600 font-medium' : 'text-green-600 font-medium'}>
                    {total - damage.ai_total_cost >= 0 ? '+' : ''}
                    {formatCurrency(total - damage.ai_total_cost)}
                  </span>
                </div>
              )}

              {damage.adjustor_note && (
                <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                  <p className="text-xs font-medium text-amber-800 mb-1">Adjustor Note:</p>
                  <p className="text-sm text-amber-900">{damage.adjustor_note}</p>
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default DamageList;
