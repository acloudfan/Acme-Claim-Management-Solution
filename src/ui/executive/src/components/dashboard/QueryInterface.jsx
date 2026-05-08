/**
 * Query Interface Component
 * Hybrid dropdown (presets) + optional free-text for custom queries
 */
import { useState } from 'react';
import { Search, Loader2, Info } from 'lucide-react';
import Button from '../common/Button';
import Card from '../common/Card';
import { PRESET_QUERIES } from '../../api/executive';

export default function QueryInterface({ onQuerySubmit, loading = false, onShowNarrative }) {
  const [selectedPreset, setSelectedPreset] = useState('');
  const [customQuery, setCustomQuery] = useState('');
  const [queryType, setQueryType] = useState('preset');

  const handleSubmit = (e) => {
    e.preventDefault();

    if (queryType === 'preset' && selectedPreset) {
      onQuerySubmit('preset', selectedPreset, null);
    } else if (queryType === 'custom' && customQuery.trim()) {
      onQuerySubmit('custom', null, customQuery);
    }
  };

  const handlePresetChange = (e) => {
    setSelectedPreset(e.target.value);
    if (e.target.value) {
      setQueryType('preset');
      setCustomQuery('');
    }
  };

  const handleCustomQueryChange = (e) => {
    setCustomQuery(e.target.value);
    if (e.target.value.trim()) {
      setQueryType('custom');
      setSelectedPreset('');
    }
  };

  return (
    <Card className="mb-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Search className="w-5 h-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">
            Ask a Question or Select a Preset Query
          </h3>
          {onShowNarrative && (
            <button
              onClick={onShowNarrative}
              className="p-1 hover:bg-gray-100 rounded transition-colors"
              aria-label="Show help"
            >
              <Info className="w-4 h-4 text-gray-400 hover:text-primary-600" />
            </button>
          )}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Preset Query Dropdown */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Preset Query
          </label>
          <select
            value={selectedPreset}
            onChange={handlePresetChange}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
            disabled={loading}
          >
            <option value="">Choose a query...</option>
            {PRESET_QUERIES.map((query) => (
              <option key={query.id} value={query.id}>
                {query.label}
              </option>
            ))}
          </select>
          {selectedPreset && (
            <p className="mt-2 text-sm text-gray-600">
              {PRESET_QUERIES.find(q => q.id === selectedPreset)?.description}
            </p>
          )}
        </div>

        {/* OR Divider */}
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">OR</span>
          </div>
        </div>

        {/* Custom Query Input (Disabled in MVP) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Custom Query (Coming Soon)
          </label>
          <input
            type="text"
            value={customQuery}
            onChange={handleCustomQueryChange}
            placeholder="Type your question here... (e.g., 'What was the average cycle time in February?')"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors disabled:bg-gray-100 disabled:cursor-not-allowed"
            disabled={true} // MVP: Disabled, future enhancement
          />
          <p className="mt-2 text-xs text-gray-500">
            💡 Natural language queries will be available in a future release
          </p>
        </div>

        {/* Submit Button */}
        <Button
          type="submit"
          variant="primary"
          disabled={loading || (!selectedPreset && !customQuery.trim())}
          loading={loading}
          className="w-full"
        >
          {loading ? 'Generating Report...' : 'Generate Report'}
        </Button>
      </form>
    </Card>
  );
}
