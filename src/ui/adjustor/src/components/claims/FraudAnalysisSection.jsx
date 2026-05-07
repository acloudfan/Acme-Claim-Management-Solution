/**
 * FraudAnalysisSection - Display fraud signals and risk score
 */
import { AlertTriangle, ShieldAlert, AlertCircle } from 'lucide-react';
import Card from '../common/Card';
import Badge from '../common/Badge';
import { getFraudRiskLevel } from '../../utils/constants';

const FraudAnalysisSection = ({ fraudData }) => {
  // Don't render if no fraud data
  if (!fraudData || !fraudData.overall_risk_score || fraudData.overall_risk_score === 0) {
    return null;
  }

  const riskLevel = getFraudRiskLevel(fraudData.overall_risk_score);
  const signals = fraudData.signals || [];

  // Sort signals by severity (descending)
  const sortedSignals = [...signals].sort((a, b) =>
    (parseFloat(b.severity) || 0) - (parseFloat(a.severity) || 0)
  );

  return (
    <Card>
      <div className={`${riskLevel.bgClass} border-2 ${riskLevel.borderClass} rounded-lg p-6`}>
        {/* Header */}
        <div className="flex items-center gap-3 mb-4">
          <ShieldAlert className={`${riskLevel.textClass} w-8 h-8`} />
          <div className="flex-1">
            <h3 className={`text-lg font-bold ${riskLevel.textClass}`}>
              Fraud Signals Detected
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              This claim has been flagged for potential fraud indicators
            </p>
          </div>
        </div>

        {/* Risk Score */}
        <div className="mb-6 pb-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-700 mb-1">Overall Fraud Risk Score</p>
              <div className="flex items-center gap-3">
                <span className={`text-4xl font-bold ${riskLevel.textClass}`}>
                  {(fraudData.overall_risk_score * 100).toFixed(0)}%
                </span>
                <Badge variant={riskLevel.color} className="text-base px-3 py-1">
                  {riskLevel.label}
                </Badge>
              </div>
            </div>

            {/* Risk Score Meter */}
            <div className="hidden md:block">
              <div className="text-right mb-2">
                <span className="text-xs font-medium text-gray-600">Risk Level</span>
              </div>
              <div className="w-64 h-6 bg-gray-200 rounded-full overflow-hidden relative">
                {/* Background gradient */}
                <div className="absolute inset-0 bg-gradient-to-r from-green-400 via-amber-400 to-red-500"></div>
                {/* Score indicator */}
                <div
                  className="absolute top-0 bottom-0 w-1 bg-gray-900 shadow-lg"
                  style={{ left: `${fraudData.overall_risk_score * 100}%` }}
                >
                  <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-3 h-3 bg-gray-900 rounded-full"></div>
                </div>
              </div>
              <div className="flex justify-between text-xs text-gray-600 mt-1">
                <span>0%</span>
                <span>30%</span>
                <span>70%</span>
                <span>100%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Fraud Signals List */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <AlertCircle className={`${riskLevel.textClass} w-5 h-5`} />
            <h4 className="text-sm font-semibold text-gray-900">
              Detected Signals ({signals.length})
            </h4>
          </div>

          {signals.length === 0 ? (
            <p className="text-sm text-gray-600 italic">No specific signals detected</p>
          ) : (
            <div className="space-y-3">
              {sortedSignals.map((signal, idx) => {
                const severity = parseFloat(signal.severity) || 0;
                let severityColor = 'text-gray-700';
                let severityBg = 'bg-gray-100';
                let severityLabel = 'Low';

                if (severity >= 0.7) {
                  severityColor = 'text-red-700';
                  severityBg = 'bg-red-100';
                  severityLabel = 'High';
                } else if (severity >= 0.4) {
                  severityColor = 'text-amber-700';
                  severityBg = 'bg-amber-100';
                  severityLabel = 'Medium';
                }

                return (
                  <div
                    key={signal.id || idx}
                    className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 mt-1">
                        <AlertTriangle className={`w-5 h-5 ${severityColor}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        {/* Signal Type */}
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm font-semibold text-gray-900">
                            {signal.signal_type || 'Fraud Signal'}
                          </span>
                          <span className={`text-xs px-2 py-0.5 rounded-full ${severityBg} ${severityColor} font-medium`}>
                            {severityLabel} ({(severity * 100).toFixed(0)}%)
                          </span>
                        </div>

                        {/* Description */}
                        <p className="text-sm text-gray-700 mb-2">
                          {signal.description || 'No description available'}
                        </p>

                        {/* Evidence (if available) */}
                        {signal.evidence && Object.keys(signal.evidence).length > 0 && (
                          <details className="text-xs text-gray-600">
                            <summary className="cursor-pointer hover:text-gray-900 font-medium">
                              View Evidence
                            </summary>
                            <div className="mt-2 p-2 bg-gray-50 rounded border border-gray-200">
                              <pre className="whitespace-pre-wrap font-mono text-xs">
                                {JSON.stringify(signal.evidence, null, 2)}
                              </pre>
                            </div>
                          </details>
                        )}

                        {/* Timestamp */}
                        {signal.detection_timestamp && (
                          <p className="text-xs text-gray-500 mt-2">
                            Detected: {new Date(signal.detection_timestamp).toLocaleString()}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Adjustor Notes Section */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className={`${riskLevel.bgClass} border ${riskLevel.borderClass} rounded-lg p-4`}>
            <h4 className="text-sm font-semibold text-gray-900 mb-2">
              ⚠️ Review Guidelines
            </h4>
            <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside">
              <li>Carefully verify all damage images for authenticity</li>
              <li>Cross-reference vehicle details (VIN, make, model, color) with images</li>
              <li>Check for duplicate or AI-generated images</li>
              <li>Review claim history and patterns for this customer</li>
              <li>Consider routing to fraud investigation team if score is very high</li>
            </ul>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default FraudAnalysisSection;
