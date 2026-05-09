/**
 * Login Page - Mock authentication with customer dropdown
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Card from '../components/common/Card';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import { LogIn } from 'lucide-react';

const LoginPage = () => {
  const navigate = useNavigate();
  const { login, isAuthenticated, availableCustomers, hasCustomers, customerCount, apiServerDown } = useAuth();
  const [selectedCustomerId, setSelectedCustomerId] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated()) {
      navigate('/', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!selectedCustomerId) {
      setError('Please select a customer');
      return;
    }
    if (!password) {
      setError('Please enter your password');
      return;
    }

    setLoading(true);

    try {
      await login(selectedCustomerId, password);
      navigate('/', { replace: true });
    } catch (err) {
      setError(err.message || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 px-4">
      <div className="w-full max-w-md">
        {/* Logo/Brand */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <img
              src="/ACME-logo.png"
              alt="ACME Insurance"
              className="h-20 w-auto"
              onError={(e) => {
                e.target.style.display = 'none';
              }}
            />
          </div>
          <p className="text-gray-600 text-sm">Customer Portal</p>
        </div>

        {/* Login Card */}
        <Card>
          <h2 className="text-2xl font-semibold text-gray-900 mb-6 text-center">
            Welcome Back
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Customer Dropdown */}
            <div>
              <label htmlFor="customer-select" className="block text-sm font-medium text-gray-700 mb-2">
                Customer Name
              </label>
              <select
                id="customer-select"
                value={selectedCustomerId}
                onChange={(e) => setSelectedCustomerId(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                disabled={loading || hasCustomers === false || apiServerDown}
              >
                <option value="">
                  {hasCustomers === false ? 'No customers available - seed database first' : 'Select your name...'}
                </option>
                {hasCustomers !== false && availableCustomers.map((customer) => (
                  <option key={customer.customer_id} value={customer.customer_id}>
                    {customer.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Password Input */}
            <Input
              label="Password"
              name="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              disabled={loading}
              required
            />

            {/* Error Message */}
            {error && (
              <div className="p-3 bg-error-light text-error-dark rounded-lg text-sm">
                {error}
              </div>
            )}

            {/* API Server Down Warning */}
            {apiServerDown && (
              <div className="p-4 bg-red-50 border-2 border-red-300 text-red-900 rounded-lg text-sm">
                <p className="font-bold mb-2 text-base">🔴 API Server Not Running</p>
                <p className="mb-3">The backend API server is not responding. Please start it to continue.</p>
                <div className="bg-red-100 p-3 rounded mt-2 font-mono text-xs space-y-2">
                  <div>
                    <p className="font-semibold mb-1">1. Start the API server:</p>
                    <p className="text-red-900">cd &lt;project-root&gt;</p>
                    <p className="text-red-900">./scripts/start-api-server.sh</p>
                  </div>
                  <div className="mt-2 pt-2 border-t border-red-200">
                    <p className="font-semibold mb-1">2. Verify it's running:</p>
                    <p className="text-red-900">curl http://localhost:8000/health</p>
                  </div>
                </div>
                <p className="mt-3 text-xs">
                  Once the server is running, refresh this page.
                </p>
              </div>
            )}

            {/* Database Seeding Warning */}
            {!apiServerDown && hasCustomers === false && (
              <div className="p-4 bg-red-50 border border-red-200 text-red-800 rounded-lg text-sm">
                <p className="font-semibold mb-2">⚠️ Database Not Seeded</p>
                <p className="mb-2">You MUST first seed the database with customer and policy data.</p>
                <div className="bg-red-100 p-2 rounded mt-2 font-mono text-xs">
                  <p className="font-semibold mb-1">Run this command:</p>
                  <p className="text-red-900">python scripts/seed-data.py --clean</p>
                </div>
                <p className="mt-2 text-xs">
                  Once seeded, you can start the API server without the --clean flag to retain the data.
                </p>
              </div>
            )}

            {/* Demo Info */}
            {!apiServerDown && hasCustomers !== false && (
              <div className="p-3 bg-blue-50 text-blue-800 rounded-lg text-sm">
                <p className="font-medium mb-1">Demo Credentials:</p>
                <p>Password: <code className="bg-blue-100 px-2 py-0.5 rounded">password</code></p>
                <p className="text-xs text-blue-600 mt-1">
                  (Select any customer and use this password)
                </p>
              </div>
            )}

            {/* Login Button */}
            <Button
              type="submit"
              variant="primary"
              className="w-full"
              loading={loading}
              disabled={loading || hasCustomers === false || apiServerDown}
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2 inline-block"></div>
                  Logging in...
                </>
              ) : (
                <>
                  <LogIn className="mr-2 h-5 w-5 inline" />
                  Login
                </>
              )}
            </Button>
          </form>
        </Card>

        {/* Footer note */}
        <p className="text-center text-gray-600 text-sm mt-6">
          © 2026 ACME Insurance. All rights reserved.
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
