/**
 * NarrativeModal Component
 * Displays contextual help narratives for dashboard components
 * All narratives include AI-generated disclaimer
 */
import { X, AlertTriangle } from 'lucide-react';
import Modal from '../common/Modal';

export default function NarrativeModal({ isOpen, onClose, narrative }) {
  if (!narrative) return null;

  // Convert markdown-style bold to JSX
  const renderContent = (text) => {
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={index}>{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  // Parse content into sections
  const sections = narrative.content.split('\n\n').map((section, idx) => {
    const lines = section.split('\n');
    return (
      <div key={idx} className="mb-4">
        {lines.map((line, lineIdx) => {
          // Check if it's a header (starts with **)
          if (line.startsWith('**') && line.includes(':')) {
            const headerText = line.replace(/\*\*/g, '');
            return (
              <h4 key={lineIdx} className="text-base font-semibold text-gray-900 mb-2 mt-4">
                {headerText}
              </h4>
            );
          }
          // Check if it's a list item
          if (line.startsWith('- ')) {
            return (
              <li key={lineIdx} className="ml-4 text-sm text-gray-700 leading-relaxed">
                {renderContent(line.substring(2))}
              </li>
            );
          }
          // Regular paragraph
          if (line.trim()) {
            return (
              <p key={lineIdx} className="text-sm text-gray-700 leading-relaxed">
                {renderContent(line)}
              </p>
            );
          }
          return null;
        })}
      </div>
    );
  });

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      {/* AI Generated Disclaimer */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 mb-4 flex items-center gap-2">
        <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0" />
        <span className="text-sm font-semibold text-amber-900">
          AI Generated Summary
        </span>
      </div>

      {/* Header */}
      <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{narrative.icon}</span>
          <h2 className="text-xl font-bold text-gray-900">{narrative.title}</h2>
        </div>
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          aria-label="Close"
        >
          <X className="w-5 h-5 text-gray-500" />
        </button>
      </div>

      {/* Content */}
      <div className="max-h-[60vh] overflow-y-auto pr-2">
        <div className="prose prose-sm max-w-none">
          {sections}
        </div>
      </div>

      {/* Footer */}
      <div className="mt-6 pt-4 border-t border-gray-200 flex justify-end">
        <button
          onClick={onClose}
          className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
        >
          Got it
        </button>
      </div>
    </Modal>
  );
}
