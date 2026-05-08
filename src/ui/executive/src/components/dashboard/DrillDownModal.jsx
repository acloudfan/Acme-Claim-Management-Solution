/**
 * Drill Down Modal Component
 * Shows claim-level details when drilling down from charts
 */
import { X, CheckCircle, XCircle, Calendar, DollarSign } from 'lucide-react';
import Modal from '../common/Modal';
import Badge from '../common/Badge';
import { formatCurrency, formatDate } from '../../utils/formatters';

export default function DrillDownModal({ isOpen, onClose, claimDetails }) {
  if (!claimDetails) return null;

  const {
    claim_id,
    customer_name,
    policy_number,
    vehicle,
    fnol_date,
    claim_closed_date,
    cycle_time_days,
    processing_path,
    cost_estimated,
    cost_actual,
    cost_accuracy_percent,
    within_tolerance,
    fraud_detected,
    damages = [],
    events = []
  } = claimDetails;

  // Processing path badge color
  const getPathColor = (path) => {
    if (path === 'ai_auto_approved') return 'success';
    if (path === 'ai_human_reviewed') return 'warning';
    return 'default';
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} maxWidth="2xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-200">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            Claim Details
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Claim ID: #{claim_id}
          </p>
        </div>
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <X className="w-6 h-6 text-gray-500" />
        </button>
      </div>

      {/* Content */}
      <div className="space-y-6">
        {/* Customer & Vehicle Info */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600 mb-1">Customer</p>
            <p className="text-lg font-semibold text-gray-900">{customer_name}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Policy</p>
            <p className="text-lg font-semibold text-gray-900">{policy_number}</p>
          </div>
          <div className="col-span-2">
            <p className="text-sm text-gray-600 mb-1">Vehicle</p>
            <p className="text-lg font-semibold text-gray-900">{vehicle}</p>
          </div>
        </div>

        {/* Processing Path */}
        <div>
          <p className="text-sm text-gray-600 mb-2">Processing Path</p>
          <Badge variant={getPathColor(processing_path)}>
            {processing_path.replace(/_/g, ' ').toUpperCase()}
          </Badge>
        </div>

        {/* Timeline */}
        <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-gray-500" />
            <div>
              <p className="text-xs text-gray-600">FNOL Date</p>
              <p className="font-semibold text-gray-900">{formatDate(fnol_date)}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-gray-500" />
            <div>
              <p className="text-xs text-gray-600">Closed Date</p>
              <p className="font-semibold text-gray-900">
                {claim_closed_date ? formatDate(claim_closed_date) : 'Open'}
              </p>
            </div>
          </div>
          <div className="col-span-2">
            <p className="text-xs text-gray-600">Cycle Time</p>
            <p className="text-2xl font-bold text-primary-600">
              {cycle_time_days.toFixed(1)} days
            </p>
          </div>
        </div>

        {/* Cost Information */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Cost Analysis</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Estimated Cost</span>
              <span className="text-lg font-semibold text-gray-900">
                {formatCurrency(cost_estimated)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Actual Cost</span>
              <span className="text-lg font-semibold text-gray-900">
                {formatCurrency(cost_actual)}
              </span>
            </div>
            <div className="flex justify-between items-center pt-3 border-t border-gray-200">
              <span className="text-gray-600">Accuracy</span>
              <div className="flex items-center gap-2">
                <span className={`text-lg font-semibold ${
                  within_tolerance ? 'text-success-600' : 'text-warning-600'
                }`}>
                  {cost_accuracy_percent.toFixed(1)}%
                </span>
                {within_tolerance ? (
                  <CheckCircle className="w-5 h-5 text-success-600" />
                ) : (
                  <XCircle className="w-5 h-5 text-warning-600" />
                )}
              </div>
            </div>
            <p className="text-sm text-gray-600">
              {within_tolerance
                ? '✓ Within ±10% tolerance'
                : '⚠ Outside tolerance range'}
            </p>
          </div>
        </div>

        {/* Fraud Detection */}
        {fraud_detected && (
          <div className="p-4 bg-error-50 border border-error-200 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <XCircle className="w-5 h-5 text-error-600" />
              <span className="font-semibold text-error-900">Fraud Detected</span>
            </div>
            <p className="text-sm text-error-700">
              This claim was flagged for potential fraud by the AI detection system.
            </p>
          </div>
        )}

        {/* Damages */}
        {damages && damages.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              Damages ({damages.length})
            </h3>
            <div className="space-y-2">
              {damages.map((damage, index) => (
                <div
                  key={index}
                  className="flex justify-between items-center p-3 bg-gray-50 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-900">{damage.part}</p>
                    <p className="text-sm text-gray-600 capitalize">
                      Severity: {damage.severity}
                    </p>
                  </div>
                  <span className="font-semibold text-gray-900">
                    {formatCurrency(damage.cost)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Timeline Events */}
        {events && events.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Timeline</h3>
            <div className="space-y-2">
              {events.map((event, index) => (
                <div
                  key={index}
                  className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg"
                >
                  <div className="w-2 h-2 mt-2 rounded-full bg-primary-500"></div>
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{event.status}</p>
                    <p className="text-sm text-gray-600">
                      {formatDate(event.date)} • {event.action_by}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="mt-6 pt-4 border-t border-gray-200 flex justify-end gap-3">
        <button
          onClick={onClose}
          className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
        >
          Close
        </button>
        <button
          onClick={() => {
            // Link to full claim view in Claims Portal
            window.open(`http://localhost:5173/claims/${claim_id}`, '_blank');
          }}
          className="px-4 py-2 text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors"
        >
          View Full Claim →
        </button>
      </div>
    </Modal>
  );
}
