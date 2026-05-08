import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const LoginPage = () => {
  const navigate = useNavigate();
  const { login, isAuthenticated, availableAdjustors, hasAdjustors, adjustorCount, apiServerDown } = useAuth();

  const [selectedAdjustorId, setSelectedAdjustorId] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated()) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!selectedAdjustorId) {
      setError('Please select an adjustor ID');
      return;
    }
    if (!password) {
      setError('Please enter your password');
      return;
    }

    setLoading(true);

    try {
      await login(selectedAdjustorId, password);
      navigate('/dashboard', { replace: true });
    } catch (err) {
      setError(err.message || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-900 via-primary-800 to-primary-700 px-4">
      <div className="w-full max-w-md">
        {/* Login Card */}
        <div className="bg-white rounded-lg shadow-xl p-8">
          {/* Logo */}
          <div className="flex justify-center mb-6">
            <img
              src="/assets/ACME-logo.png"
              alt="ACME Insurance"
              className="h-20 w-auto"
              onError={(e) => {
                e.target.style.display = 'none';
              }}
            />
          </div>

          {/* Title */}
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-gray-900">ACME Insurance</h1>
            <p className="text-sm text-gray-600 mt-1">Adjustor Portal</p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* API Server Down Warning */}
            {apiServerDown && (
              <div className="bg-red-50 border-2 border-red-300 text-red-900 px-4 py-3 rounded-md text-sm">
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
                  Once the server is running, refresh this page.
                </p>
              </div>
            )}

            {/* Database Seeding Warning */}
            {!apiServerDown && hasAdjustors === false && (
              <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-md text-sm">
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

            {/* Adjustor ID Dropdown */}
            <div>
              <label htmlFor="adjustor-id" className="block text-sm font-medium text-gray-700 mb-2">
                Adjustor ID
              </label>
              <select
                id="adjustor-id"
                value={selectedAdjustorId}
                onChange={(e) => setSelectedAdjustorId(e.target.value)}
                className="input"
                disabled={loading || hasAdjustors === false || apiServerDown}
              >
                <option value="">
                  {hasAdjustors === false ? 'No adjustors available - seed database first' : 'Select your ID...'}
                </option>
                {hasAdjustors !== false && availableAdjustors.map((adj) => (
                  <option key={adj.adjustor_id} value={adj.adjustor_id}>
                    {adj.adjustor_id} - {adj.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Password Input */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input"
                placeholder="Enter your password"
                disabled={loading}
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
                {error}
              </div>
            )}

            {/* Login Button */}
            <button
              type="submit"
              disabled={loading || hasAdjustors === false || apiServerDown}
              className="btn btn-primary w-full flex items-center justify-center"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Logging in...
                </>
              ) : (
                'Login'
              )}
            </button>
          </form>

          {/* Version Info */}
          <div className="mt-8 text-center text-xs text-gray-500">
            <p>Version 1.0.0</p>
            <p className="mt-1">AI-Powered Claims Adjustor Portal</p>
            {!apiServerDown && hasAdjustors !== false && (
              <p className="mt-3 text-gray-400">Demo: Use password "password"</p>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-6 text-center text-sm text-white/80">
          <p>© 2026 ACME Insurance. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
