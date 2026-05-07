import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const LoginPage = () => {
  const navigate = useNavigate();
  const { login, isAuthenticated, availableAdjustors } = useAuth();

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
                disabled={loading}
              >
                <option value="">Select your ID...</option>
                {availableAdjustors.map((adj) => (
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
              disabled={loading}
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
            <p className="mt-3 text-gray-400">Demo: Use password "adjustor123"</p>
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
