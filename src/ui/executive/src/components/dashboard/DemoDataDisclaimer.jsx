/**
 * DemoDataDisclaimer Component
 * Displays prominent disclaimer about synthetic data at the top of dashboard
 */
import { Info } from 'lucide-react';

export default function DemoDataDisclaimer() {
  const handleLearnMoreClick = () => {
    const element = document.getElementById('sample-data-distribution');
    if (element) {
      // First, try to expand the section by clicking the header
      const header = element.querySelector('[data-expandable-header]');
      if (header) {
        header.click();
      }

      // Wait a moment for expansion animation, then scroll
      setTimeout(() => {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
        // Add highlight effect
        element.classList.add('ring-2', 'ring-blue-500', 'ring-offset-2');
        setTimeout(() => {
          element.classList.remove('ring-2', 'ring-blue-500', 'ring-offset-2');
        }, 2000);
      }, 100);
    }
  };

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">
          <Info className="w-5 h-5 text-blue-600" />
        </div>
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-blue-900 mb-1">
            Demo Dashboard - Synthetic Data
          </h3>
          <p className="text-sm text-blue-800 leading-relaxed">
            This dashboard is for <strong>demo purposes only</strong> and doesn't use real data.
            The synthetic dataset contains <strong>750 samples per month</strong> over 6 months (Oct 2025 - Mar 2026),
            representing approximately <strong>1% of average monthly auto-claims</strong> in North America.
            Data is generated using industry averages such as cycle times, cost structures, and fraud rates.
            All metrics are <strong>extrapolated by a factor of 100x</strong> to simulate realistic production volumes.{' '}
            <button
              onClick={handleLearnMoreClick}
              className="text-blue-700 font-semibold hover:text-blue-800 hover:underline focus:outline-none"
            >
              Read more about the synthetic data →
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
