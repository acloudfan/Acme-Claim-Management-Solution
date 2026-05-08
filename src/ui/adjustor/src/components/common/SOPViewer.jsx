/**
 * SOP Viewer Modal - Display Standard Operating Procedures
 * Shows the damage triage SOP document in a modal
 */
import { X, FileText } from 'lucide-react';
import { useEffect, useState } from 'react';
import Modal from './Modal';

const SOPViewer = ({ isOpen, onClose }) => {
  const [sopContent, setSopContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen) {
      loadSOPContent();
    }
  }, [isOpen]);

  const loadSOPContent = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch the SOP markdown file from the public directory
      const response = await fetch('/sop_damage_triage.md');

      if (!response.ok) {
        throw new Error('Failed to load SOP document');
      }

      const content = await response.text();
      setSopContent(content);
    } catch (err) {
      console.error('Failed to load SOP:', err);
      setError('Failed to load SOP document. Please check if the file exists.');
    } finally {
      setLoading(false);
    }
  };

  // Simple markdown-to-HTML converter for basic formatting
  const renderMarkdown = (markdown) => {
    if (!markdown) return '';

    let html = markdown;

    // Headers
    html = html.replace(/^### (.*$)/gim, '<h3 class="text-lg font-semibold text-gray-900 mt-6 mb-3">$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2 class="text-xl font-bold text-gray-900 mt-8 mb-4">$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold text-gray-900 mb-6">$1</h1>');

    // Bold
    html = html.replace(/\*\*(.*?)\*\*/gim, '<strong class="font-semibold">$1</strong>');

    // Italic
    html = html.replace(/\*(.*?)\*/gim, '<em class="italic">$1</em>');

    // Code blocks (triple backticks)
    html = html.replace(/```([\s\S]*?)```/gim, '<pre class="bg-gray-100 p-4 rounded-lg overflow-x-auto my-4"><code class="text-sm">$1</code></pre>');

    // Inline code
    html = html.replace(/`([^`]+)`/gim, '<code class="bg-gray-100 px-2 py-1 rounded text-sm font-mono">$1</code>');

    // Links
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/gim, '<a href="$2" class="text-primary-600 hover:text-primary-700 underline">$1</a>');

    // Horizontal rules
    html = html.replace(/^---$/gim, '<hr class="my-8 border-gray-300" />');

    // Lists (unordered)
    html = html.replace(/^\s*[-*]\s+(.*)$/gim, '<li class="ml-6 mb-2">$1</li>');
    html = html.replace(/(<li.*<\/li>)/gims, '<ul class="list-disc mb-4">$1</ul>');

    // Lists (ordered)
    html = html.replace(/^\s*\d+\.\s+(.*)$/gim, '<li class="ml-6 mb-2">$1</li>');

    // Blockquotes
    html = html.replace(/^&gt; (.*$)/gim, '<blockquote class="border-l-4 border-blue-500 bg-blue-50 pl-4 py-2 my-4 italic text-gray-700">$1</blockquote>');
    html = html.replace(/^> (.*$)/gim, '<blockquote class="border-l-4 border-blue-500 bg-blue-50 pl-4 py-2 my-4 italic text-gray-700">$1</blockquote>');

    // Tables (basic support)
    html = html.replace(/\|(.+)\|/g, (match) => {
      const cells = match.split('|').filter(cell => cell.trim());
      const cellsHtml = cells.map(cell => `<td class="border border-gray-300 px-4 py-2">${cell.trim()}</td>`).join('');
      return `<tr>${cellsHtml}</tr>`;
    });
    html = html.replace(/(<tr>.*<\/tr>)/gims, '<table class="w-full my-4 border-collapse">$1</table>');

    // Paragraphs (lines separated by double newline)
    html = html.replace(/\n\n/g, '</p><p class="mb-4">');
    html = '<p class="mb-4">' + html + '</p>';

    return html;
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <div className="bg-white rounded-lg shadow-xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 sticky top-0 bg-white rounded-t-lg z-10">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary-100 rounded-lg">
              <FileText className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Standard Operating Procedures</h2>
              <p className="text-sm text-gray-600">Damage Triage Guidelines</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Close SOP viewer"
          >
            <X className="w-6 h-6 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
          )}

          {error && (
            <div className="bg-error-light border border-error text-error-dark p-4 rounded-lg">
              <p className="font-medium">Error Loading SOP</p>
              <p className="text-sm mt-1">{error}</p>
            </div>
          )}

          {!loading && !error && sopContent && (
            <div
              className="prose prose-sm max-w-none sop-content"
              dangerouslySetInnerHTML={{ __html: renderMarkdown(sopContent) }}
            />
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-lg">
          <div className="flex items-center justify-between">
            <p className="text-xs text-gray-600">
              This document provides guidance for claim triage and assessment.
            </p>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </Modal>
  );
};

export default SOPViewer;
