/**
 * Executive Dashboard Page (Enhanced with Phase 3 Components)
 * Main BI dashboard with KPIs, charts, queries, and filters
 */
import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  fetchKPIs,
  fetchTrendData,
  executeQuery,
  fetchClaimDetails
} from '../api/executive';
import { BarChart3, RefreshCw } from 'lucide-react';

// Dashboard Components
import KPICard from '../components/dashboard/KPICard';
import TrendChart from '../components/dashboard/TrendChart';
import QueryInterface from '../components/dashboard/QueryInterface';
import FilterSidebar from '../components/dashboard/FilterSidebar';
import DrillDownModal from '../components/dashboard/DrillDownModal';
import QueryResults from '../components/dashboard/QueryResults';
import SampleDataDistribution from '../components/dashboard/SampleDataDistribution';
import AssumptionsAndReferences from '../components/dashboard/AssumptionsAndReferences';
import ProcessingMixChart from '../components/dashboard/ProcessingMixChart';
import DemoDataDisclaimer from '../components/dashboard/DemoDataDisclaimer';
import NarrativeModal from '../components/dashboard/NarrativeModal';
import Spinner from '../components/common/Spinner';

import { KPI_NAMES, KPI_LABELS } from '../utils/constants';
import { NARRATIVES } from '../utils/narratives';

export default function DashboardPage() {
  const { isAuthenticated, executiveId } = useAuth();

  // State
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [kpiData, setKpiData] = useState(null);
  const [trendData, setTrendData] = useState({});
  const [queryResults, setQueryResults] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Filters
  const [timePeriod, setTimePeriod] = useState('all');  // Show all 6 months by default
  const [customDateRange, setCustomDateRange] = useState(null);

  // Drill-down
  const [drillDownOpen, setDrillDownOpen] = useState(false);
  const [drillDownData, setDrillDownData] = useState(null);

  // Narrative modal
  const [narrativeOpen, setNarrativeOpen] = useState(false);
  const [currentNarrative, setCurrentNarrative] = useState(null);

  // Loading states
  const [queryLoading, setQueryLoading] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);

  /**
   * Load all dashboard data
   */
  const loadDashboardData = async (period = timePeriod, customRange = null) => {
    try {
      setLoading(true);
      setError(null);

      // Fetch KPIs
      const startDate = customRange?.start || null;
      const endDate = customRange?.end || null;
      const kpis = await fetchKPIs(period, startDate, endDate);
      setKpiData(kpis);
      setLastUpdated(new Date().toLocaleTimeString());

      // Fetch trend data for all 4 KPIs (full 6 months: Oct 2025 - Mar 2026)
      const trends = {};
      for (const kpiName of Object.keys(KPI_NAMES)) {
        const kpiId = KPI_NAMES[kpiName];
        try {
          const trendResult = await fetchTrendData(
            kpiId,
            'monthly',
            startDate || '2025-10-01',  // Default to Oct 2025
            endDate || '2026-03-31'     // Through Mar 2026
          );
          trends[kpiId] = trendResult.data_points;
        } catch (err) {
          console.error(`Error fetching trend for ${kpiId}:`, err);
          trends[kpiId] = [];
        }
      }
      setTrendData(trends);

      console.log('Dashboard data loaded:', { kpis, trends });
    } catch (err) {
      console.error('Error loading dashboard:', err);
      setError('Failed to load dashboard data. Make sure the API server is running.');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle time period change
   */
  const handlePeriodChange = (period, customRange = null) => {
    setTimePeriod(period);
    setCustomDateRange(customRange);
    loadDashboardData(period, customRange);
  };

  /**
   * Handle query submission
   */
  const handleQuerySubmit = async (queryType, presetId, customQuery) => {
    try {
      setQueryLoading(true);
      setQueryResults(null);

      const timeRange = {
        start_date: customDateRange?.start || '2025-10-01',  // Full 6 months
        end_date: customDateRange?.end || '2026-03-31'
      };

      const result = await executeQuery(queryType, presetId, timeRange, customQuery);
      setQueryResults(result);

      console.log('Query results:', result);
    } catch (err) {
      console.error('Error executing query:', err);
      alert('Failed to execute query. Please try again.');
    } finally {
      setQueryLoading(false);
    }
  };

  /**
   * Handle drill-down
   */
  const handleDrillDown = async (claimId) => {
    try {
      const details = await fetchClaimDetails(claimId);
      setDrillDownData(details);
      setDrillDownOpen(true);
    } catch (err) {
      console.error('Error fetching claim details:', err);
      alert('Failed to load claim details');
    }
  };

  /**
   * Handle KPI drill-down - scroll to corresponding chart
   */
  const handleKPIDrillDown = (kpiKey) => {
    const chartId = `chart-${kpiKey}`;
    const chartElement = document.getElementById(chartId);
    if (chartElement) {
      chartElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
      // Add highlight effect
      chartElement.classList.add('ring-2', 'ring-primary-500', 'ring-offset-2');
      setTimeout(() => {
        chartElement.classList.remove('ring-2', 'ring-primary-500', 'ring-offset-2');
      }, 2000);
    }
  };

  /**
   * Handle export
   */
  const handleExport = async (format) => {
    setExportLoading(true);
    try {
      // Placeholder: Export not implemented yet
      alert(`Export as ${format.toUpperCase()} will be available in Phase 5`);
    } catch (err) {
      console.error('Export error:', err);
    } finally {
      setExportLoading(false);
    }
  };

  /**
   * Handle narrative display
   */
  const handleShowNarrative = (narrativeKey) => {
    const narrative = NARRATIVES[narrativeKey];
    if (narrative) {
      setCurrentNarrative(narrative);
      setNarrativeOpen(true);
    }
  };

  // Load data on mount
  useEffect(() => {
    if (isAuthenticated) {
      loadDashboardData();
    }
  }, [isAuthenticated]);

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <p className="text-gray-600">Please log in to view the dashboard</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-[1920px] mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary-500 rounded-lg flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  ACME Claims : Executive Portal
                </h1>
                <p className="text-sm text-gray-600">Business Intelligence Dashboard</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              {lastUpdated && (
                <span className="text-sm text-gray-600">
                  Last updated: {lastUpdated}
                </span>
              )}
              <button
                onClick={() => loadDashboardData()}
                disabled={loading}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-primary-600 bg-primary-50 rounded-lg hover:bg-primary-100 disabled:opacity-50 transition-colors"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                Refresh Data
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-[1920px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading && (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <Spinner size="lg" />
              <p className="mt-4 text-gray-600">Loading dashboard...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-error-50 border border-error-200 rounded-lg p-6 mb-6">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0">
                <svg className="w-6 h-6 text-error-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="flex-1">
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
                    Once the server is running, click the Retry button below.
                  </p>
                  <button
                    onClick={() => loadDashboardData()}
                    className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium"
                  >
                    Retry
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {!loading && !error && kpiData && (
          <div className="flex gap-6">
            {/* Main Dashboard (70%) */}
            <div className="flex-1 space-y-6">
              {/* Demo Data Disclaimer */}
              <DemoDataDisclaimer />

              {/* AI Processed Claims Pie Chart */}
              {kpiData?.summary && (
                <ProcessingMixChart
                  summary={kpiData.summary}
                  onShowNarrative={() => handleShowNarrative('AI_PROCESSED_CLAIMS')}
                />
              )}

              {/* KPI Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {Object.entries(kpiData.kpis).map(([key, kpi]) => {
                  const miniData = trendData[key]?.map(point => ({
                    value: point.value
                  })) || [];

                  // Map KPI key to narrative key
                  const narrativeKeyMap = {
                    [KPI_NAMES.CYCLE_TIME_SAVINGS]: 'CYCLE_TIME_SAVINGS',
                    [KPI_NAMES.TOTAL_SAVINGS]: 'TOTAL_SAVINGS',
                    [KPI_NAMES.AUTO_ADJUDICATION]: 'AUTO_ADJUDICATION_RATE'
                  };

                  return (
                    <KPICard
                      key={key}
                      title={KPI_LABELS[key] || key}
                      kpi={kpi}
                      miniChartData={miniData}
                      onDrillDown={() => handleKPIDrillDown(key)}
                      onShowNarrative={() => handleShowNarrative(narrativeKeyMap[key])}
                    />
                  );
                })}
              </div>

              {/* Trend Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div id={`chart-${KPI_NAMES.CYCLE_TIME_SAVINGS}`} className="transition-all duration-300">
                  <TrendChart
                    title="Cycle Time Savings Trend"
                    subtitle="Days saved per AI-enabled claim vs traditional processing baseline"
                    data={trendData[KPI_NAMES.CYCLE_TIME_SAVINGS] || []}
                    yAxisLabel="Days Saved"
                    color="blue"
                    onShowNarrative={() => handleShowNarrative('TREND_CHART_CYCLE_TIME')}
                  />
                </div>
                <div id={`chart-${KPI_NAMES.TOTAL_SAVINGS}`} className="transition-all duration-300">
                  <TrendChart
                    title="Total Savings Trend"
                    subtitle="Cumulative operational cost savings from AI processing"
                    data={trendData[KPI_NAMES.TOTAL_SAVINGS] || []}
                    yAxisLabel="Savings ($)"
                    color="green"
                    onShowNarrative={() => handleShowNarrative('TREND_CHART_TOTAL_SAVINGS')}
                  />
                </div>
                <div id={`chart-${KPI_NAMES.AUTO_ADJUDICATION}`} className="transition-all duration-300">
                  <TrendChart
                    title="Auto-Adjudication Rate"
                    subtitle="Percentage of AI-enabled claims processed automatically without human intervention"
                    data={trendData[KPI_NAMES.AUTO_ADJUDICATION] || []}
                    yAxisLabel="Percentage (%)"
                    color="purple"
                    onShowNarrative={() => handleShowNarrative('TREND_CHART_AUTO_ADJ')}
                  />
                </div>
              </div>

              {/* Query Interface */}
              <QueryInterface
                onQuerySubmit={handleQuerySubmit}
                loading={queryLoading}
                onShowNarrative={() => handleShowNarrative('QUERY_INTERFACE')}
              />

              {/* Query Results */}
              {queryResults && (
                <QueryResults queryData={queryResults} />
              )}

              {/* Sample Data Distribution - Bottom of Dashboard */}
              <SampleDataDistribution
                sampleSize={4500}
                actualVolume={450000}
                extrapolationFactor={100}
                monthlyDistribution={[
                  { month: 'Oct 2025', claims: 750, autoAdjPct: 2.9, threshold: 4000, fraudPct: 60.0 },
                  { month: 'Nov 2025', claims: 750, autoAdjPct: 6.5, threshold: 4500, fraudPct: 100.0 },
                  { month: 'Dec 2025', claims: 750, autoAdjPct: 15.5, threshold: 5000, fraudPct: 55.0 },
                  { month: 'Jan 2026', claims: 750, autoAdjPct: 42.8, threshold: 5500, fraudPct: 73.9 },
                  { month: 'Feb 2026', claims: 750, autoAdjPct: 47.3, threshold: 6000, fraudPct: 80.9 },
                  { month: 'Mar 2026', claims: 750, autoAdjPct: 59.6, threshold: 6500, fraudPct: 80.0 },
                ]}
              />

              {/* Assumptions and References - Bottom of Dashboard */}
              <AssumptionsAndReferences />
            </div>

            {/* Sidebar (30%) */}
            <div className="w-80 flex-shrink-0 space-y-6 no-print">
              <FilterSidebar
                currentPeriod={timePeriod}
                onPeriodChange={handlePeriodChange}
                onExport={handleExport}
                summary={kpiData?.summary}
                exportLoading={exportLoading}
              />
            </div>
          </div>
        )}
      </main>

      {/* Drill Down Modal */}
      <DrillDownModal
        isOpen={drillDownOpen}
        onClose={() => setDrillDownOpen(false)}
        claimDetails={drillDownData}
      />

      {/* Narrative Help Modal */}
      <NarrativeModal
        isOpen={narrativeOpen}
        onClose={() => setNarrativeOpen(false)}
        narrative={currentNarrative}
      />
    </div>
  );
}
