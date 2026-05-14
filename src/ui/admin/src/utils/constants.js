/**
 * Admin Portal Constants
 */

// Available LLM Providers
export const LLM_PROVIDERS = [
  { value: 'anthropic', label: 'Anthropic' },
  { value: 'openai', label: 'OpenAI' },
  { value: 'bedrock', label: 'AWS Bedrock' }
];

// Bedrock Model Options
export const BEDROCK_MODELS = [
  { value: 'anthropic.claude-3-5-sonnet-20241022-v2:0', label: 'Claude 3.5 Sonnet v2' },
  { value: 'anthropic.claude-3-opus-20240229-v1:0', label: 'Claude 3 Opus' },
  { value: 'anthropic.claude-3-sonnet-20240229-v1:0', label: 'Claude 3 Sonnet' },
  { value: 'anthropic.claude-3-haiku-20240307-v1:0', label: 'Claude 3 Haiku' }
];

// Validation Ranges
export const VALIDATION_RANGES = {
  'ai.confidence.high_threshold': { min: 0, max: 1, step: 0.05 },
  'ai.confidence.low_threshold': { min: 0, max: 1, step: 0.05 },
  'ai.fraud.risk_threshold': { min: 0, max: 1, step: 0.05 },
  'ai.estimate.human_review_threshold': { min: 0, max: 100000, step: 100 },
  'agents.fraud_detector.high_risk_threshold': { min: 0, max: 1, step: 0.05 },
  'agents.fraud_detector.medium_risk_threshold': { min: 0, max: 1, step: 0.05 },
  'llm.providers.bedrock.timeout_s': { min: 1, max: 600, step: 1 },
  'llm.providers.bedrock.max_tokens': { min: 1, max: 100000, step: 100 },
  'llm.providers.bedrock.temperature': { min: 0, max: 2, step: 0.1 },
  'database.pool_size': { min: 1, max: 100, step: 1 },
  'database.max_overflow': { min: 0, max: 100, step: 1 },
  'storage.max_upload_size_mb': { min: 1, max: 100, step: 1 },
  'storage.max_images_per_claim': { min: 1, max: 100, step: 1 },
  'api.port': { min: 1, max: 65535, step: 1 }
};

// Field Descriptions
export const FIELD_DESCRIPTIONS = {
  // AI Confidence
  'ai.confidence.high_threshold': 'Minimum confidence to auto-present estimate to customer',
  'ai.confidence.low_threshold': 'Below this, route to traditional claim process',
  'ai.fraud.risk_threshold': 'Above this, flag claim for human review',
  'ai.estimate.human_review_threshold': 'Dollar threshold for mandatory human review',

  // Agent Toggles
  'agents.fraud_detector.enabled': 'Run fraud detection on all claims',
  'agents.risk_estimator.enabled': 'Analyze claims for actuarial risk (NOT IMPLEMENTED - Coming Soon)',
  'agents.damage_analyzer.enabled': 'Agent generates damage summary, refines severity scores, estimates internal damage, and recommends repair strategies',
  'agents.damage_analyzer.enhance_all_damages': 'Apply analyzer to all damage reports vs. low-confidence only (NOT IMPLEMENTED - Coming Soon)',
  'agents.chatbot.enabled': 'Customer-facing chatbot in portal',

  // Fraud Detection
  'agents.fraud_detector.high_risk_threshold': '≥0.7 = HIGH RISK (recommend reject)',
  'agents.fraud_detector.medium_risk_threshold': '0.4-0.7 = MEDIUM RISK (human review)',
  'agents.fraud_detector.phase1_vision.color_verification.enabled': 'Check if image color matches vehicle record',
  'agents.fraud_detector.phase1_vision.make_model_verification.enabled': 'Verify vehicle make/model in images',
  'agents.fraud_detector.phase1_vision.ai_generated_detection.enabled': 'Detect AI-generated images',
  'agents.fraud_detector.phase1_vision.manipulation_detection.enabled': 'Detect photo editing/manipulation',

  // LLM Settings
  'llm.default_provider': 'LLM provider (anthropic, openai, or bedrock)',
  'llm.default_vision_model': 'Model used for image analysis',
  'llm.providers.bedrock.aws_region': 'AWS region for Bedrock',
  'llm.providers.bedrock.default_model': 'Model ID (dropdown of available models)',
  'llm.providers.bedrock.timeout_s': 'LLM API request timeout',
  'llm.providers.bedrock.max_tokens': 'Maximum response tokens',
  'llm.providers.bedrock.temperature': 'Sampling temperature (lower = more deterministic)',

  // Database
  'database.pool_size': 'Connection pool size',
  'database.max_overflow': 'Additional connections beyond pool',
  'database.echo': 'Log all SQL queries (debug mode)',

  // Storage
  'storage.images_root_folder': 'Directory for claim images',
  'storage.max_upload_size_mb': 'Per-image size limit',
  'storage.max_images_per_claim': 'Maximum images allowed per claim',

  // API
  'api.debug': 'Enable debug logging and CORS',
  'api.host': 'API server host (0.0.0.0 for all interfaces)',
  'api.port': 'API server port'
};

// Field Examples
export const FIELD_EXAMPLES = {
  'ai.confidence.high_threshold': '0.55 means 55% confidence',
  'ai.confidence.low_threshold': '0.35 means 35% confidence',
  'ai.fraud.risk_threshold': '0.1 means 10% risk',
  'ai.estimate.human_review_threshold': 'Claims over $5,000 require review',
  'agents.fraud_detector.high_risk_threshold': '0.7 = clear high risk, skip Phase 3',
  'agents.fraud_detector.medium_risk_threshold': '0.4-0.7 = borderline, run Phase 3',
  'llm.providers.bedrock.timeout_s': '60 seconds default',
  'llm.providers.bedrock.max_tokens': '4096 tokens',
  'llm.providers.bedrock.temperature': '0.2 for consistent results',
  'database.pool_size': '5 connections',
  'database.max_overflow': '10 additional connections',
  'storage.max_upload_size_mb': '10 MB per image',
  'storage.max_images_per_claim': '20 images maximum',
  'api.port': '8000 default'
};
