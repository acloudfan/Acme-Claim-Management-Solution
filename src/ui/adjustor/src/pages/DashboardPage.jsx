/**
 * DashboardPage - Main dashboard for adjustor
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { fetchPendingClaims, fetchAdjustorStatistics } from '../api/adjustors';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import Spinner from '../components/common/Spinner';
import Button from '../components/common/Button';
import { formatCurrency, formatDate, getRelativeTime } from '../utils/formatters';
import { STATUS_LABELS, STATUS_COLORS, REVIEW_REASON_LABELS } from '../utils/constants';
import { ClipboardList, Clock, CheckCircle, TrendingUp } from 'lucide-react';

const DashboardPage = () => {
  const { adjustor } = useAuth();
  const navigate = useNavigate();

  const [statistics, setStatistics] = useState(null);
  const [recentClaims, setRecentClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, [adjustor]);

  const loadDashboardData = async () => {
    if (!adjustor) return;

    try {
      setLoading(true);
      setError(null);

      // Fetch statistics and recent claims in parallel
      const [statsData, claimsData] = await Promise.all([
        fetchAdjustorStatistics(adjustor.adjustor_id),
        fetchPendingClaims(adjustor.adjustor_id, { limit: 5, sort_by: 'created_at', sort_order: 'desc' })
      ]);

      setStatistics(statsData);
      setRecentClaims(claimsData.claims || []);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError('Failed to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleViewClaim = (claim) => {
    navigate(`/claims/${claim.claim_id}/review`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">{error}</p>
        <Button onClick={loadDashboardData}>Retry</Button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Welcome back, {adjustor?.name?.split(' ')[0]}</h1>
        <p className="text-gray-600 mt-1">Here's an overview of your workload</p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Pending Reviews</p>
              <p className="text-3xl font-bold text-primary-700">
                {statistics?.pending_reviews || 0}
              </p>
            </div>
            <div className="bg-primary-100 p-3 rounded-lg">
              <ClipboardList className="h-8 w-8 text-primary-600" />
            </div>
          </div>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Completed Today</p>
              <p className="text-3xl font-bold text-green-700">
                {statistics?.completed_today || 0}
              </p>
            </div>
            <div className="bg-green-100 p-3 rounded-lg">
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </div>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">This Week</p>
              <p className="text-3xl font-bold text-blue-700">
                {statistics?.completed_this_week || 0}
              </p>
            </div>
            <div className="bg-blue-100 p-3 rounded-lg">
              <TrendingUp className="h-8 w-8 text-blue-600" />
            </div>
          </div>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Avg. Review Time</p>
              <p className="text-3xl font-bold text-amber-700">
                {statistics?.avg_review_time_minutes ? `${Math.round(statistics.avg_review_time_minutes)}m` : '-'}
              </p>
            </div>
            <div className="bg-amber-100 p-3 rounded-lg">
              <Clock className="h-8 w-8 text-amber-600" />
            </div>
          </div>
        </Card>
      </div>

      {/* Recent Pending Claims */}
      <Card title="Recent Pending Claims" className="overflow-hidden">
        {recentClaims.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <ClipboardList className="h-12 w-12 mx-auto mb-3 text-gray-400" />
            <p>No pending claims at the moment</p>
            <p className="text-sm mt-1">Great job staying on top of your queue!</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Claim ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Customer
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    FNOL Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Reason
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    AI Estimate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Age
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {recentClaims.map((claim) => (
                  <tr
                    key={claim.claim_id}
                    className="hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => handleViewClaim(claim)}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm font-medium text-primary-600">
                        #{claim.claim_id}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{claim.customer_name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {claim.fnol_date ? new Date(claim.fnol_date).toLocaleDateString('en-US', { month: '2-digit', day: '2-digit', year: '2-digit' }) : '-'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Badge variant={claim.reason_for_review === 'customer_appeal' ? 'warning' : 'default'}>
                        {claim.reason_for_review === 'customer_appeal' ? 'Appeal' : 'Low Confidence'}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm font-semibold text-gray-900">
                        {formatCurrency(claim.ai_estimate_total || 0)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-600">
                        {claim.time_in_queue || '-'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Button
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleViewClaim(claim);
                        }}
                      >
                        Review
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {recentClaims.length > 0 && (
          <div className="border-t mt-4 pt-4">
            <Button variant="secondary" onClick={() => navigate('/claims/queue')} className="w-full">
              View All Pending Claims
            </Button>
          </div>
        )}
      </Card>

      {/* Quick Actions */}
      <Card title="Quick Actions">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Button variant="primary" onClick={() => navigate('/claims/queue')} className="w-full">
            <ClipboardList className="h-5 w-5 mr-2" />
            View Full Queue
          </Button>
          <Button variant="secondary" onClick={() => navigate('/statistics')} className="w-full" disabled>
            <TrendingUp className="h-5 w-5 mr-2" />
            My Statistics
          </Button>
          <Button variant="secondary" onClick={() => navigate('/help')} className="w-full" disabled>
            Help & Guidelines
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default DashboardPage;
