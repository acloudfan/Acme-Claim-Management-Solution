/**
 * Home Page - Customer dashboard with policies and pending actions
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { fetchCustomerPolicies, fetchCustomerClaims } from '../api/customers';
import Layout from '../components/layout/Layout';
import PolicyCard from '../components/policies/PolicyCard';
import Spinner from '../components/common/Spinner';
import Button from '../components/common/Button';

const HomePage = () => {
  const navigate = useNavigate();
  const { customer, customerId } = useAuth();
  const [policies, setPolicies] = useState([]);
  const [pendingClaims, setPendingClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (customerId) {
      loadData();
    }
  }, [customerId]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');

      // Fetch policies
      const policiesResponse = await fetchCustomerPolicies(customerId);
      setPolicies(policiesResponse.data || []);

      // Fetch claims with pending status
      const claimsResponse = await fetchCustomerClaims(customerId, {
        status: 'customer_decision_pending',
      });
      setPendingClaims(claimsResponse.data || []);
    } catch (err) {
      console.error('Failed to load data:', err);
      setError('Failed to load your information. Please try refreshing the page.');
    } finally {
      setLoading(false);
    }
  };

  const handlePolicyClick = (policy) => {
    navigate(`/policy/${policy.policy_number}`);
  };

  const handleViewClaim = (claim) => {
    // Navigate based on claim status:
    // - draft: Continue filing claim (NewClaimPage)
    // - customer_decision_pending: Go directly to estimate summary with Accept/Appeal buttons
    // - all others: View claim detail page
    if (claim.current_status === 'draft') {
      navigate(`/claims/${claim.claim_id}/edit`);
    } else if (claim.current_status === 'customer_decision_pending') {
      // Claims awaiting customer decision should go directly to estimate summary page
      navigate(`/claims/${claim.claim_id}`);
    } else {
      // For all other submitted claims, show the claim detail page
      navigate(`/claims/${claim.claim_id}`);
    }
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

  // Find auto policy
  const autoPolicy = policies.find((p) => p.policy_type === 'auto');

  // Fake home policy (hardcoded)
  const fakeHomePolicy = {
    policy_number: 'POL-Home-1234',
    type: 'home',
    status: 'Active',
  };

  return (
    <Layout>
      {/* Welcome Banner */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Welcome back, {customer?.fname || 'Customer'}! 👋
        </h1>
        <p className="text-gray-600">
          Manage your policies and track your claims
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-error-light text-error-dark rounded-lg">
          {error}
        </div>
      )}

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
                  className="flex justify-between items-center bg-white p-3 rounded-lg mb-2"
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
                    Review Now →
                  </Button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Policies Section */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">
          Your Policies
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Fake Home Policy */}
          <PolicyCard policy={fakeHomePolicy} fake={true} />

          {/* Real Auto Policy */}
          {autoPolicy ? (
            <PolicyCard
              policy={autoPolicy}
              onClick={handlePolicyClick}
            />
          ) : (
            <div className="p-6 bg-gray-50 border-2 border-dashed border-gray-300 rounded-xl text-center">
              <p className="text-gray-600">No auto policy found</p>
            </div>
          )}
        </div>
      </div>

    </Layout>
  );
};

export default HomePage;
