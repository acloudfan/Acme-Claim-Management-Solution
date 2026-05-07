/**
 * Policy Detail Page - View policy details, vehicles, and claim history
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  FileText,
  Shield,
  DollarSign,
  Calendar,
  CreditCard,
  Car as CarIcon,
  Users,
  Settings,
  AlertCircle,
  Eye,
  Trash2
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { fetchPolicy, fetchCustomerClaims, deleteClaim } from '../api/customers';
import Layout from '../components/layout/Layout';
import VehicleCard from '../components/policies/VehicleCard';
import PolicyActionCard from '../components/policies/PolicyActionCard';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Spinner from '../components/common/Spinner';
import Badge from '../components/common/Badge';
import { getStatusLabel, getStatusVariant } from '../utils/statusMapping';

const PolicyPage = () => {
  const { policyNumber } = useParams();
  const navigate = useNavigate();
  const { customerId } = useAuth();
  const [policy, setPolicy] = useState(null);
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (customerId && policyNumber) {
      loadPolicyData();
    }
  }, [customerId, policyNumber]);

  const loadPolicyData = async () => {
    try {
      setLoading(true);
      setError('');

      // Fetch policy details
      const policyResponse = await fetchPolicy(customerId, policyNumber);
      setPolicy(policyResponse.data);

      // Fetch claims for this policy
      const claimsResponse = await fetchCustomerClaims(customerId);
      const policyClaims = (claimsResponse.data || []).filter(
        (claim) => claim.policy_number === policyNumber
      );
      setClaims(policyClaims);
    } catch (err) {
      console.error('Failed to load policy data:', err);
      setError('Failed to load policy information. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileNewClaim = () => {
    navigate(`/claims/new?policy=${policyNumber}`);
  };

  const handleViewClaim = (claim) => {
    // Navigate based on claim status:
    // - draft: Continue filing claim (NewClaimPage)
    // - customer_decision_pending: Go directly to estimate summary (ClaimDetailPage with Accept/Appeal)
    // - all others: View claim detail page
    if (claim.current_status === 'draft') {
      navigate(`/claims/${claim.claim_id}/edit`);
    } else if (claim.current_status === 'customer_decision_pending') {
      // Claims awaiting customer decision should go directly to estimate page
      navigate(`/claims/${claim.claim_id}`);
    } else {
      // For all other claims, show the claim detail page
      // TODO: Create proper claim summary/detail view for non-AI statuses
      navigate(`/claims/${claim.claim_id}`);
    }
  };

  const handleDeleteClaim = async (e, claim) => {
    e.stopPropagation();

    if (!window.confirm(`Are you sure you want to delete claim #${claim.claim_id}? This action cannot be undone.`)) {
      return;
    }

    try {
      await deleteClaim(customerId, claim.claim_id);
      // Reload claims after deletion
      await loadPolicyData();
    } catch (err) {
      console.error('Failed to delete claim:', err);
      alert('Failed to delete claim. Please try again.');
    }
  };

  const handlePayPremium = () => {
    // TODO: Navigate to payment page when implemented
    alert('Payment feature coming soon! This will allow you to pay premiums and manage renewals.');
  };

  const handleManageVehicles = () => {
    // TODO: Navigate to vehicle management page when implemented
    alert('Vehicle management coming soon! This will allow you to add or remove vehicles from your policy.');
  };

  const handleManageDrivers = () => {
    // TODO: Navigate to driver management page when implemented
    alert('Driver management coming soon! This will allow you to add or update drivers on your policy.');
  };

  const handleAdjustCoverage = () => {
    // TODO: Navigate to coverage adjustment page when implemented
    alert('Coverage adjustment coming soon! This will allow you to modify policy limits and add specialized coverage.');
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
  };

  const getStatusBadge = (status) => {
    return <Badge variant={getStatusVariant(status)}>{getStatusLabel(status)}</Badge>;
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <Spinner size="lg" />
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="p-4 bg-error-light text-error-dark rounded-lg">
          {error}
        </div>
      </Layout>
    );
  }

  if (!policy) {
    return (
      <Layout>
        <div className="text-center py-12">
          <p className="text-gray-600">Policy not found</p>
          <Button onClick={() => navigate('/')} className="mt-4">
            Back to Home
          </Button>
        </div>
      </Layout>
    );
  }

  // Filter pending claims (customer_decision_pending)
  const pendingClaims = claims.filter(
    (claim) => claim.current_status === 'customer_decision_pending'
  );

  return (
    <Layout>
      {/* Back Navigation */}
      <button
        onClick={() => navigate('/')}
        className="flex items-center gap-2 text-primary-600 hover:text-primary-700 mb-6 transition-colors"
      >
        <ArrowLeft className="h-5 w-5" />
        Back to Home
      </button>

      {/* Page Title */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Auto Policy: {policy.policy_number}
        </h1>
        <p className="text-gray-600">View your policy details and coverage information</p>
      </div>

      {/* Pending Actions Alert */}
      {pendingClaims.length > 0 && (
        <div className="mb-8 p-4 bg-warning-light border-l-4 border-warning rounded-lg">
          <div className="flex items-start">
            <AlertCircle className="h-5 w-5 text-warning-dark mt-0.5 mr-3" />
            <div className="flex-1">
              <h3 className="font-semibold text-warning-dark mb-2">
                Action Required
              </h3>
              <p className="text-sm text-gray-700 mb-3">
                You have {pendingClaims.length} claim{pendingClaims.length > 1 ? 's' : ''} awaiting your decision
              </p>
              {pendingClaims.map((claim) => (
                <div
                  key={claim.claim_id}
                  className="flex justify-between items-center bg-white p-3 rounded-lg mb-2 last:mb-0"
                >
                  <div>
                    <p className="font-medium text-gray-900">
                      Auto claim #{claim.claim_id}
                    </p>
                    <p className="text-sm text-gray-600">
                      AI estimate completed - Review and accept or appeal
                    </p>
                  </div>
                  <Button
                    size="sm"
                    onClick={() => handleViewClaim(claim)}
                  >
                    Review Now
                  </Button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Policy Actions */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-4">
          <AlertCircle className="h-6 w-6 text-primary-600" />
          <h2 className="text-2xl font-semibold text-gray-900">Quick Actions</h2>
        </div>
        <p className="text-gray-600 mb-6">
          Manage your policy, make changes, and file claims all in one place
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Primary Action - File Claim */}
          <PolicyActionCard
            icon={FileText}
            title="File a Claim"
            description="Report damage and get an instant AI-powered estimate with photo upload"
            onClick={handleFileNewClaim}
            primary={true}
          />

          {/* Secondary Actions */}
          <PolicyActionCard
            icon={CreditCard}
            title="Pay Premium & Renewals"
            description="Pay premiums on time to prevent policy cancellation and manage renewals"
            onClick={handlePayPremium}
          />

          <PolicyActionCard
            icon={CarIcon}
            title="Add/Remove Vehicles"
            description="Update your policy when replacing or adding vehicles for continuous coverage"
            onClick={handleManageVehicles}
          />

          <PolicyActionCard
            icon={Users}
            title="Update Drivers"
            description="Add all household drivers to your policy to prevent claim issues"
            onClick={handleManageDrivers}
          />

          <PolicyActionCard
            icon={Settings}
            title="Adjust Coverage"
            description="Change policy limits or add specialized coverage like gap insurance"
            onClick={handleAdjustCoverage}
          />
        </div>
      </div>

      {/* Policy Information Card */}
      <Card className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Shield className="h-6 w-6 text-primary-600" />
          Policy Information
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div>
            <p className="text-sm text-gray-500 mb-1">Policy Number</p>
            <p className="font-semibold text-gray-900">{policy.policy_number}</p>
          </div>

          <div>
            <p className="text-sm text-gray-500 mb-1">Policyholder</p>
            <p className="font-semibold text-gray-900">{policy.policyholder_name}</p>
          </div>

          <div>
            <p className="text-sm text-gray-500 mb-1">Insured Name</p>
            <p className="font-semibold text-gray-900">{policy.insured_name}</p>
          </div>

          <div>
            <p className="text-sm text-gray-500 mb-1 flex items-center gap-1">
              <Calendar className="h-4 w-4" />
              Effective Date
            </p>
            <p className="font-semibold text-gray-900">{formatDate(policy.start_date)}</p>
          </div>

          <div>
            <p className="text-sm text-gray-500 mb-1 flex items-center gap-1">
              <Calendar className="h-4 w-4" />
              Expiration Date
            </p>
            <p className="font-semibold text-gray-900">{formatDate(policy.end_date)}</p>
          </div>

          <div>
            <p className="text-sm text-gray-500 mb-1 flex items-center gap-1">
              <DollarSign className="h-4 w-4" />
              Annual Premium
            </p>
            <p className="font-semibold text-gray-900">{formatCurrency(policy.premium)}</p>
          </div>
        </div>

        {/* Coverage Details */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Coverage Details</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-primary-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Bodily Injury Limit</p>
              <p className="text-lg font-bold text-primary-700">{formatCurrency(policy.bodily_injury_limit)}</p>
            </div>
            <div className="p-4 bg-primary-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Property Damage Limit</p>
              <p className="text-lg font-bold text-primary-700">{formatCurrency(policy.property_damage_limit)}</p>
            </div>
            <div className="p-4 bg-primary-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Deductible</p>
              <p className="text-lg font-bold text-primary-700">{formatCurrency(policy.deductible)}</p>
            </div>
          </div>
        </div>
      </Card>

      {/* Covered Vehicles */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">Covered Vehicles</h2>
        {policy.vehicles && policy.vehicles.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {policy.vehicles.map((vehicle) => (
              <VehicleCard key={vehicle.vin} vehicle={vehicle} />
            ))}
          </div>
        ) : (
          <Card>
            <p className="text-gray-600 text-center py-4">No vehicles found for this policy</p>
          </Card>
        )}
      </div>

      {/* Claims History */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">Claims History</h2>
        {claims.length > 0 ? (
          <Card>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Claim ID</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Date Filed</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Loss Date</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Status</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">Loss Amount</th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {claims.map((claim) => (
                    <tr
                      key={claim.claim_id}
                      className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                    >
                      <td className="py-3 px-4 font-medium text-gray-900">#{claim.claim_id}</td>
                      <td className="py-3 px-4 text-gray-600">{formatDate(claim.fnol_date)}</td>
                      <td className="py-3 px-4 text-gray-600">{formatDate(claim.date_of_damage)}</td>
                      <td className="py-3 px-4">{getStatusBadge(claim.current_status)}</td>
                      <td className="py-3 px-4 text-right font-semibold text-gray-900">
                        {claim.claim_amount ? formatCurrency(claim.claim_amount) :
                         claim.damage_assessment?.total_estimated_cost ? formatCurrency(claim.damage_assessment.total_estimated_cost) : '-'}
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center justify-center gap-2">
                          <button
                            onClick={() => handleViewClaim(claim)}
                            className="p-2 text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded-lg transition-colors"
                            title="View claim details"
                          >
                            <Eye className="h-5 w-5" />
                          </button>
                          {claim.current_status === 'draft' && (
                            <button
                              onClick={(e) => handleDeleteClaim(e, claim)}
                              className="p-2 text-error-600 hover:text-error-700 hover:bg-error-50 rounded-lg transition-colors"
                              title="Delete draft claim"
                            >
                              <Trash2 className="h-5 w-5" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        ) : (
          <Card>
            <p className="text-gray-600 text-center py-4">No claims filed yet</p>
          </Card>
        )}
      </div>

    </Layout>
  );
};

export default PolicyPage;
