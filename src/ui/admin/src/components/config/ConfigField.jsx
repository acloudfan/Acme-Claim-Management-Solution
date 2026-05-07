import React from 'react';
import { AlertCircle } from 'lucide-react';
import Input from '../common/Input';

/**
 * ConfigField - Universal field component for configuration editing
 *
 * Supports multiple variants:
 * - number-slider: Number input + range slider for thresholds
 * - checkbox: Toggle switch for enable/disable options
 * - select: Dropdown for enumerated choices
 * - text: Text input for string values
 * - number: Number input without slider
 */
const ConfigField = ({
  label,
  description,
  example,
  value,
  onChange,
  variant = 'text',
  min = 0,
  max = 1,
  step = 0.01,
  options = [],
  error = null,
  required = false,
  disabled = false,
  path = ''
}) => {
  const handleNumberSliderChange = (newValue, source = 'input') => {
    const numValue = parseFloat(newValue);
    if (!isNaN(numValue)) {
      onChange(Math.max(min, Math.min(max, numValue)));
    }
  };

  const handleCheckboxChange = (e) => {
    onChange(e.target.checked);
  };

  const handleSelectChange = (e) => {
    onChange(e.target.value);
  };

  const handleTextChange = (e) => {
    onChange(e.target.value);
  };

  const renderField = () => {
    switch (variant) {
      case 'number-slider':
        return (
          <div className="space-y-2">
            <div className="flex items-center gap-4">
              {/* Number input */}
              <input
                type="number"
                value={value || min}
                onChange={(e) => handleNumberSliderChange(e.target.value, 'input')}
                min={min}
                max={max}
                step={step}
                disabled={disabled}
                className={`w-24 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  error ? 'border-red-500' : 'border-gray-300'
                } ${disabled ? 'bg-gray-100 cursor-not-allowed' : ''}`}
              />

              {/* Range slider */}
              <div className="flex-1 flex items-center gap-2">
                <span className="text-sm text-gray-500">{min}</span>
                <input
                  type="range"
                  value={value || min}
                  onChange={(e) => handleNumberSliderChange(e.target.value, 'slider')}
                  min={min}
                  max={max}
                  step={step}
                  disabled={disabled}
                  className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                  style={{
                    background: disabled
                      ? '#e5e7eb'
                      : `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${((value - min) / (max - min)) * 100}%, #e5e7eb ${((value - min) / (max - min)) * 100}%, #e5e7eb 100%)`
                  }}
                />
                <span className="text-sm text-gray-500">{max}</span>
              </div>
            </div>
          </div>
        );

      case 'checkbox':
        return (
          <div className="flex items-center">
            <button
              type="button"
              role="switch"
              aria-checked={value || false}
              onClick={() => !disabled && onChange(!value)}
              disabled={disabled}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
                value ? 'bg-blue-600' : 'bg-gray-300'
              } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  value ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
            <span className="ml-3 text-sm text-gray-700">
              {value ? 'Enabled' : 'Disabled'}
            </span>
          </div>
        );

      case 'select':
        return (
          <select
            value={value || ''}
            onChange={handleSelectChange}
            disabled={disabled}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              error ? 'border-red-500' : 'border-gray-300'
            } ${disabled ? 'bg-gray-100 cursor-not-allowed' : ''}`}
          >
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );

      case 'number':
        return (
          <input
            type="number"
            value={value || ''}
            onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
            min={min}
            max={max}
            step={step}
            disabled={disabled}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              error ? 'border-red-500' : 'border-gray-300'
            } ${disabled ? 'bg-gray-100 cursor-not-allowed' : ''}`}
          />
        );

      case 'text':
      default:
        return (
          <input
            type="text"
            value={value || ''}
            onChange={handleTextChange}
            disabled={disabled}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              error ? 'border-red-500' : 'border-gray-300'
            } ${disabled ? 'bg-gray-100 cursor-not-allowed' : ''}`}
          />
        );
    }
  };

  return (
    <div className="space-y-2">
      {/* Label */}
      <label className="block text-sm font-medium text-gray-700">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>

      {/* Field input */}
      {renderField()}

      {/* Description */}
      {description && (
        <p className="text-sm text-gray-600">{description}</p>
      )}

      {/* Example */}
      {example && !error && (
        <p className="text-xs text-gray-500 italic">Example: {example}</p>
      )}

      {/* Error message */}
      {error && (
        <div className="flex items-start gap-2 text-red-600 text-sm">
          <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};

export default ConfigField;
