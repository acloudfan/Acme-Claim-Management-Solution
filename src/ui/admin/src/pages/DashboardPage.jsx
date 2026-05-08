/**
 * DashboardPage - Main configuration editor (Enhanced UI version)
 */
import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { loadConfig as loadApiConfig, saveConfig, reloadConfig } from '../api/admin';
import { Settings, Code, RefreshCw } from 'lucide-react';
import Button from '../components/common/Button';
import Card from '../components/common/Card';
import Spinner from '../components/common/Spinner';
import ConfigSection from '../components/config/ConfigSection';
import ConfigSubsection from '../components/config/ConfigSubsection';
import ConfigField from '../components/config/ConfigField';
import { getConfig } from '../api/config';
import { getNestedValue, setNestedValue, validateConsistency } from '../utils/configHelpers';
import { VALIDATION_RANGES, FIELD_DESCRIPTIONS, FIELD_EXAMPLES } from '../utils/constants';

const DashboardPage = () => {
  const { adminId } = useAuth();
  const [config, setConfig] = useState(null);
  const [editedConfig, setEditedConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [reloading, setReloading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [reloadMessage, setReloadMessage] = useState(null);
  const [isDirty, setIsDirty] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});
  const [showJson, setShowJson] = useState(false);

  const portalConfig = getConfig();

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await loadApiConfig();
      setConfig(data.config);
      setEditedConfig(JSON.parse(JSON.stringify(data.config)));
      console.log('Configuration loaded:', data);
    } catch (err) {
      console.error('Failed to load configuration:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to load configuration');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccessMessage(null);
      setReloadMessage(null);

      // Step 1: Save configuration
      const result = await saveConfig(editedConfig);

      console.log('Configuration saved:', result);

      // Step 2: Automatically reload configuration in API server
      try {
        const reloadResult = await reloadConfig();
        console.log('Configuration reloaded:', reloadResult);

        // Success: both saved and reloaded
        setSuccessMessage(
          `✓ Configuration saved and activated! Backup created: ${result.backup_file}`
        );
        setConfig(JSON.parse(JSON.stringify(editedConfig)));
        setIsDirty(false);
      } catch (reloadErr) {
        // Saved but reload failed - show warning
        console.error('Failed to reload configuration:', reloadErr);
        setSuccessMessage(
          `Configuration saved (backup: ${result.backup_file}), but reload failed. Please reload manually or restart the API server.`
        );
        setConfig(JSON.parse(JSON.stringify(editedConfig)));
        setIsDirty(false);
      }
    } catch (err) {
      console.error('Failed to save configuration:', err);
      const errorData = err.response?.data;

      if (errorData?.errors) {
        // Validation errors
        const errorMessages = Object.entries(errorData.errors)
          .map(([field, message]) => `${field}: ${message}`)
          .join('\n');
        setError(`Validation failed:\n${errorMessages}`);
      } else {
        setError(errorData?.detail || err.message || 'Failed to save configuration');
      }
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    if (config) {
      setEditedConfig(JSON.parse(JSON.stringify(config)));
      setIsDirty(false);
      setError(null);
      setSuccessMessage(null);
      setReloadMessage(null);
    }
  };

  const handleReload = async () => {
    try {
      setReloading(true);
      setError(null);
      setReloadMessage(null);

      const result = await reloadConfig();

      setReloadMessage(
        `✓ Configuration reloaded successfully! Changes are now active in the API server.`
      );
      setSuccessMessage(null); // Clear the save message

      console.log('Configuration reloaded:', result);
    } catch (err) {
      console.error('Failed to reload configuration:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to reload configuration');
    } finally {
      setReloading(false);
    }
  };

  const handleFieldChange = (path, value) => {
    const newConfig = setNestedValue(editedConfig, path, value);
    setEditedConfig(newConfig);
    setIsDirty(true);
    setError(null);
    setSuccessMessage(null);

    // Real-time validation
    const consistencyErrors = validateConsistency(newConfig);
    setFieldErrors(consistencyErrors);
  };

  const openPortal = (url) => {
    if (url) {
      window.open(url, '_blank', 'width=1440,height=900');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">ACME Insurance : Admin Portal</h1>
              <p className="text-sm text-gray-600 mt-1">
                Manage the (a) Business rules applied to the AI Agents (b) Technical parameters such as Vision models, Model providers etc.
              </p>
            </div>
            <div className="text-sm text-gray-600">
              Admin: {adminId}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Content (80%) */}
          <div className="lg:col-span-3 space-y-6">
            {/* Action Buttons */}
            <Card>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Button
                    onClick={handleSave}
                    disabled={!isDirty || saving || Object.keys(fieldErrors).length > 0}
                    loading={saving}
                  >
                    {saving ? 'Saving & Reloading...' : 'Save Configuration'}
                  </Button>
                  <Button
                    variant="secondary"
                    onClick={handleReset}
                    disabled={!isDirty || saving}
                  >
                    Reset
                  </Button>
                </div>
                <div className="flex items-center gap-3">
                  {isDirty && (
                    <span className="text-sm text-warning-600 font-medium">
                      Unsaved changes
                    </span>
                  )}
                  {Object.keys(fieldErrors).length > 0 && (
                    <span className="text-sm text-red-600 font-medium">
                      {Object.keys(fieldErrors).length} validation error{Object.keys(fieldErrors).length > 1 ? 's' : ''}
                    </span>
                  )}
                </div>
              </div>
            </Card>

            {/* Messages */}
            {error && (
              <Card>
                {error.includes('backend API server is not responding') ? (
                  <div className="bg-red-50 border-2 border-red-300 text-red-900 p-4 rounded-md text-sm">
                    <p className="font-bold mb-2 text-base">🔴 API Server Not Running</p>
                    <p className="mb-3">The backend API server is not responding. Please start it to continue.</p>
                    <div className="bg-red-100 p-3 rounded mt-2 font-mono text-xs space-y-2">
                      <div>
                        <p className="font-semibold mb-1">1. Start the API server:</p>
                        <p className="text-red-900">cd /home/raj/workspace2026/Acme-Claim-Management-Solution</p>
                        <p className="text-red-900">python -m src.api.main</p>
                      </div>
                      <div className="mt-2 pt-2 border-t border-red-200">
                        <p className="font-semibold mb-1">2. Verify it's running:</p>
                        <p className="text-red-900">curl http://localhost:8000/health</p>
                      </div>
                    </div>
                    <p className="mt-3 text-xs">
                      Once the server is running, refresh this page.
                    </p>
                  </div>
                ) : (
                  <div className="bg-error-light border-l-4 border-error p-4">
                    <p className="text-sm text-error-dark whitespace-pre-wrap">{error}</p>
                  </div>
                )}
              </Card>
            )}

            {successMessage && (
              <Card>
                <div className="bg-success-light border-l-4 border-success p-4">
                  <p className="text-sm text-success-dark font-medium">{successMessage}</p>
                  {successMessage.includes('activated') && (
                    <p className="text-xs text-success-dark mt-2">
                      ℹ️ Changes are now active in the API server. No restart required!
                    </p>
                  )}
                  {successMessage.includes('reload failed') && (
                    <div className="mt-3">
                      <Button
                        onClick={handleReload}
                        disabled={reloading}
                        loading={reloading}
                        className="flex items-center gap-2"
                      >
                        <RefreshCw className="w-4 h-4" />
                        {reloading ? 'Reloading...' : 'Retry Reload'}
                      </Button>
                    </div>
                  )}
                </div>
              </Card>
            )}

            {/* Toggle: Form UI vs JSON */}
            <Card>
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">
                    Configuration Editor
                  </h2>
                  <p className="text-sm text-gray-600 mt-1">
                    {showJson ? 'Advanced JSON editor' : 'Visual form-based editor'}
                  </p>
                </div>
                <Button
                  variant="secondary"
                  onClick={() => setShowJson(!showJson)}
                  className="flex items-center gap-2"
                >
                  {showJson ? (
                    <>
                      <Settings className="w-4 h-4" />
                      Show Form UI
                    </>
                  ) : (
                    <>
                      <Code className="w-4 h-4" />
                      Show JSON
                    </>
                  )}
                </Button>
              </div>
            </Card>

            {/* Form-based UI (Default) */}
            {!showJson && editedConfig && (
              <>
                {/* Business Rules Section */}
                <ConfigSection
                  title="Business Rules"
                  icon={Settings}
                  description="Configure AI confidence thresholds, agent toggles, and fraud detection settings"
                  defaultExpanded={true}
                >
                  {/* Subsection 1: Confidence Thresholds */}
                  <ConfigSubsection
                    title="Confidence Thresholds"
                    description="AI confidence levels for claim triage and routing"
                  >
                    <ConfigField
                      label="High Confidence Threshold"
                      description={FIELD_DESCRIPTIONS['ai.confidence.high_threshold']}
                      example={FIELD_EXAMPLES['ai.confidence.high_threshold']}
                      value={getNestedValue(editedConfig, 'ai.confidence.high_threshold')}
                      onChange={(val) => handleFieldChange('ai.confidence.high_threshold', val)}
                      variant="number-slider"
                      min={0}
                      max={1}
                      step={0.05}
                      error={fieldErrors['ai.confidence.high_threshold']}
                      required
                    />

                    <ConfigField
                      label="Low Confidence Threshold"
                      description={FIELD_DESCRIPTIONS['ai.confidence.low_threshold']}
                      example={FIELD_EXAMPLES['ai.confidence.low_threshold']}
                      value={getNestedValue(editedConfig, 'ai.confidence.low_threshold')}
                      onChange={(val) => handleFieldChange('ai.confidence.low_threshold', val)}
                      variant="number-slider"
                      min={0}
                      max={1}
                      step={0.05}
                      error={fieldErrors['ai.confidence.low_threshold']}
                      required
                    />

                    <ConfigField
                      label="Fraud Risk Threshold"
                      description={FIELD_DESCRIPTIONS['ai.fraud.risk_threshold']}
                      example={FIELD_EXAMPLES['ai.fraud.risk_threshold']}
                      value={getNestedValue(editedConfig, 'ai.fraud.risk_threshold')}
                      onChange={(val) => handleFieldChange('ai.fraud.risk_threshold', val)}
                      variant="number-slider"
                      min={0}
                      max={1}
                      step={0.05}
                      required
                    />

                    <ConfigField
                      label="Human Review Amount Threshold"
                      description={FIELD_DESCRIPTIONS['ai.estimate.human_review_threshold']}
                      example={FIELD_EXAMPLES['ai.estimate.human_review_threshold']}
                      value={getNestedValue(editedConfig, 'ai.estimate.human_review_threshold')}
                      onChange={(val) => handleFieldChange('ai.estimate.human_review_threshold', val)}
                      variant="number"
                      min={0}
                      max={100000}
                      step={100}
                      required
                    />
                  </ConfigSubsection>

                  {/* Subsection 2: Agent Toggles */}
                  <ConfigSubsection
                    title="Agent Toggles"
                    description="Enable or disable AI agents for claim processing"
                  >
                    <ConfigField
                      label="YOLO Damage Detection"
                      description="Fine-tuned YOLO model for vehicle damage detection"
                      value={true}
                      onChange={() => {}}
                      variant="checkbox"
                      disabled={true}
                    />

                    <ConfigField
                      label="Enable Customer Chatbot"
                      description={FIELD_DESCRIPTIONS['agents.chatbot.enabled']}
                      value={getNestedValue(editedConfig, 'agents.chatbot.enabled')}
                      onChange={(val) => handleFieldChange('agents.chatbot.enabled', val)}
                      variant="checkbox"
                    />

                    <ConfigField
                      label="Enable Fraud Detector"
                      description={FIELD_DESCRIPTIONS['agents.fraud_detector.enabled']}
                      value={getNestedValue(editedConfig, 'agents.fraud_detector.enabled')}
                      onChange={(val) => handleFieldChange('agents.fraud_detector.enabled', val)}
                      variant="checkbox"
                    />

                    <ConfigField
                      label="Enable Damage Analyzer (Coming Soon)"
                      description="LLM-enhanced damage assessment - Not yet implemented. Agent will refine severity scores, estimate internal damage, and recommend repair strategies."
                      value={false}
                      onChange={() => {}}
                      variant="checkbox"
                      disabled={true}
                    />

                    <ConfigField
                      label="Enable Risk Estimator (Coming Soon)"
                      description="Actuarial risk analysis - Not yet implemented. Agent will analyze cost deviations, vehicle value risk, and claim velocity patterns."
                      value={false}
                      onChange={() => {}}
                      variant="checkbox"
                      disabled={true}
                    />
                  </ConfigSubsection>

                  {/* Subsection 3: Fraud Detection Settings (only shown when fraud detector enabled) */}
                  {getNestedValue(editedConfig, 'agents.fraud_detector.enabled') && (
                    <ConfigSubsection
                      title="Fraud Detection Settings"
                      description="Configure fraud detection risk thresholds and vision checks"
                    >
                      <ConfigField
                        label="High Risk Threshold"
                        description={FIELD_DESCRIPTIONS['agents.fraud_detector.high_risk_threshold']}
                        example={FIELD_EXAMPLES['agents.fraud_detector.high_risk_threshold']}
                        value={getNestedValue(editedConfig, 'agents.fraud_detector.high_risk_threshold')}
                        onChange={(val) => handleFieldChange('agents.fraud_detector.high_risk_threshold', val)}
                        variant="number-slider"
                        min={0}
                        max={1}
                        step={0.05}
                        error={fieldErrors['agents.fraud_detector.high_risk_threshold']}
                        required
                      />

                      <ConfigField
                        label="Medium Risk Threshold"
                        description={FIELD_DESCRIPTIONS['agents.fraud_detector.medium_risk_threshold']}
                        example={FIELD_EXAMPLES['agents.fraud_detector.medium_risk_threshold']}
                        value={getNestedValue(editedConfig, 'agents.fraud_detector.medium_risk_threshold')}
                        onChange={(val) => handleFieldChange('agents.fraud_detector.medium_risk_threshold', val)}
                        variant="number-slider"
                        min={0}
                        max={1}
                        step={0.05}
                        error={fieldErrors['agents.fraud_detector.medium_risk_threshold']}
                        required
                      />

                      <ConfigField
                        label="Color Verification"
                        description={FIELD_DESCRIPTIONS['agents.fraud_detector.phase1_vision.color_verification.enabled']}
                        value={getNestedValue(editedConfig, 'agents.fraud_detector.phase1_vision.color_verification.enabled')}
                        onChange={(val) => handleFieldChange('agents.fraud_detector.phase1_vision.color_verification.enabled', val)}
                        variant="checkbox"
                      />

                      <ConfigField
                        label="Make/Model Verification"
                        description={FIELD_DESCRIPTIONS['agents.fraud_detector.phase1_vision.make_model_verification.enabled']}
                        value={getNestedValue(editedConfig, 'agents.fraud_detector.phase1_vision.make_model_verification.enabled')}
                        onChange={(val) => handleFieldChange('agents.fraud_detector.phase1_vision.make_model_verification.enabled', val)}
                        variant="checkbox"
                      />

                      <ConfigField
                        label="AI Image Detection"
                        description={FIELD_DESCRIPTIONS['agents.fraud_detector.phase1_vision.ai_generated_detection.enabled']}
                        value={getNestedValue(editedConfig, 'agents.fraud_detector.phase1_vision.ai_generated_detection.enabled')}
                        onChange={(val) => handleFieldChange('agents.fraud_detector.phase1_vision.ai_generated_detection.enabled', val)}
                        variant="checkbox"
                      />

                      <ConfigField
                        label="Manipulation Detection"
                        description="Detect photo editing/manipulation with traditional image analysis tools (coming soon)"
                        value={false}
                        onChange={() => {}}
                        variant="checkbox"
                        disabled={true}
                      />
                    </ConfigSubsection>
                  )}

                  {/* Message when fraud detector is disabled */}
                  {!getNestedValue(editedConfig, 'agents.fraud_detector.enabled') && (
                    <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                      <p className="text-sm text-gray-600 italic">
                        💡 Fraud Detection Settings are hidden because the Fraud Detector agent is disabled.
                        Enable it above to configure fraud detection thresholds and vision checks.
                      </p>
                    </div>
                  )}
                </ConfigSection>
              </>
            )}

            {/* JSON Editor (Advanced Mode) */}
            {showJson && (
              <Card>
                <div className="space-y-4">
                  <h2 className="text-lg font-semibold text-gray-900">
                    Advanced JSON Editor
                  </h2>
                  <p className="text-sm text-gray-600">
                    Direct JSON editing for advanced users. Changes sync with form UI.
                  </p>

                  <textarea
                    value={JSON.stringify(editedConfig, null, 2)}
                    onChange={(e) => {
                      try {
                        const parsed = JSON.parse(e.target.value);
                        setEditedConfig(parsed);
                        setIsDirty(true);
                        const consistencyErrors = validateConsistency(parsed);
                        setFieldErrors(consistencyErrors);
                      } catch (err) {
                        // Invalid JSON - don't update
                      }
                    }}
                    className="w-full h-96 font-mono text-sm p-4 border rounded-lg focus:ring-2 focus:ring-primary-500"
                    style={{ fontFamily: 'monospace' }}
                  />

                  <p className="text-xs text-gray-500">
                    Tip: Edit the JSON above. The editor validates on save. Switch to Form UI for guided editing.
                  </p>
                </div>
              </Card>
            )}
          </div>

          {/* Sidebar (20%) - Portal Launcher */}
          <div className="lg:col-span-1">
            <Card>
              <div className="space-y-4">
                <h3 className="text-sm font-semibold text-gray-900">Quick Access</h3>

                <div className="space-y-2">
                  <Button
                    onClick={() => openPortal(portalConfig.portal_links.customer_portal_url)}
                    variant="secondary"
                    className="w-full justify-start"
                  >
                    🌐 Customer Portal
                  </Button>

                  <Button
                    onClick={() => openPortal(portalConfig.portal_links.adjustor_portal_url)}
                    variant="secondary"
                    className="w-full justify-start"
                  >
                    👤 Adjustor Portal
                  </Button>

                  <Button
                    onClick={() => openPortal(portalConfig.portal_links.executive_portal_url)}
                    variant="secondary"
                    className="w-full justify-start"
                    disabled={!portalConfig.portal_links.executive_portal_url}
                  >
                    📊 Executive Portal
                    {!portalConfig.portal_links.executive_portal_url && (
                      <span className="ml-2 text-xs">(Coming Soon)</span>
                    )}
                  </Button>
                </div>

                <div className="pt-4 border-t text-xs text-gray-500">
                  <p>Opens portals in new window</p>
                </div>
              </div>
            </Card>

            {/* Demo Scenarios Card */}
            <Card className="mt-4">
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">🎬</span>
                  <h3 className="text-sm font-semibold text-gray-900">Demo Scenarios</h3>
                </div>

                <div className="space-y-4 text-sm">
                  {/* Scenario 1: Happy Path */}
                  <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-start gap-2">
                      <span className="text-lg">✅</span>
                      <div>
                        <h4 className="font-semibold text-green-900 mb-1">Happy Path - Cx accepts AI estimate</h4>
                        <p className="text-green-800 text-xs leading-relaxed">
                          <strong>John Doe</strong> files a claim for his <strong>Toyota Corolla 2015</strong> that was rear-ended.
                        </p>
                        <ul className="mt-2 space-y-1 text-green-700 text-xs">
                          <li>• Has filed police report (not received yet)</li>
                          <li>• Claim processes smoothly through AI</li>
                          <li>• Auto-approved with estimate</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* Scenario 2: Customer Appeal */}
                  <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
                    <div className="flex items-start gap-2">
                      <span className="text-lg">⚠️</span>
                      <div>
                        <h4 className="font-semibold text-amber-900 mb-1">Human Review - Cx Appeals</h4>
                        <p className="text-amber-800 text-xs leading-relaxed">
                          <strong>Jane Smith</strong> files a claim for her <strong>BMW 1 Series (E87) 2006</strong>.
                        </p>
                        <ul className="mt-2 space-y-1 text-amber-700 text-xs">
                          <li>• AI generates initial damage estimate</li>
                          <li>• Customer appeals: "Radiator seems to be damaged beyond repair"</li>
                          <li>• Routed to adjustor for manual review</li>
                          <li>• Adjustor can add manual damages & revise estimate</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* Scenario 3: Fraud Detection - Make Mismatch */}
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                    <div className="flex items-start gap-2">
                      <span className="text-lg">🚨</span>
                      <div>
                        <h4 className="font-semibold text-red-900 mb-1">Fraud - Make Mismatch</h4>
                        <p className="text-red-800 text-xs leading-relaxed">
                          <strong>Bob Johnson</strong> owns a <strong>red Chevy Silverado 2012</strong>. He files a claim and uploads an image of a damaged <strong>red Ford F-150</strong>.
                        </p>
                        <ul className="mt-2 space-y-1 text-red-700 text-xs">
                          <li>• Fraud AI detects vehicle make mismatch (Chevy ≠ Ford)</li>
                          <li>• Flagged for human review with fraud signals</li>
                          <li>• Adjustor reviews fraud analysis</li>
                          <li>• Routes claim to traditional processing</li>
                        </ul>
                        <div className="mt-3 p-2 bg-red-100 border border-red-300 rounded">
                          <p className="text-xs font-semibold text-red-900 mb-1">🔬 Variation:</p>
                          <p className="text-xs text-red-800">
                            Switch OFF fraud detection in Admin Config and try again — claim will be auto-approved!
                            This demonstrates the fraud detection toggle.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Scenario 4: Fraud Detection - AI Generated Image */}
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                    <div className="flex items-start gap-2">
                      <span className="text-lg">🎨</span>
                      <div>
                        <h4 className="font-semibold text-red-900 mb-1">Fraud - AI Generated Damage</h4>
                        <p className="text-red-800 text-xs leading-relaxed">
                          <strong>Alice Williams</strong> owns a <strong>black Honda Accord 2022</strong>. She generates an AI image using her car's original photo, adding fake damage with an image model.
                        </p>
                        <ul className="mt-2 space-y-1 text-red-700 text-xs">
                          <li>• VLM analyzes images for AI generation artifacts</li>
                          <li>• Detects inconsistencies in lighting, textures, and damage patterns</li>
                          <li>• Flagged for fraud review with detailed analysis</li>
                          <li>• Routed to adjustor with AI detection signals</li>
                        </ul>
                        <div className="mt-3 p-2 bg-red-100 border border-red-300 rounded">
                          <p className="text-xs font-semibold text-red-900 mb-1">🔬 Detection Method:</p>
                          <p className="text-xs text-red-800">
                            Demo uses Vision Language Model (VLM) for AI generation analysis. Production systems combine VLM with static image forensics tools (metadata analysis, pixel-level artifact detection) for comprehensive fraud detection.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t text-xs text-gray-500">
                  <p className="mb-1">💡 <strong>Try it yourself:</strong></p>
                  <ol className="list-decimal list-inside space-y-1 text-gray-600">
                    <li>Open Customer Portal</li>
                    <li>Select a customer</li>
                    <li>File a claim & upload photos</li>
                    <li>Track progress in Adjustor Portal</li>
                  </ol>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
