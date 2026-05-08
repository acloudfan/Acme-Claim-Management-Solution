/**
 * LoginPage - Simple login (auto-login with no password for prototype)
 */
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const LoginPage = () => {
  const navigate = useNavigate();
  const { isAuthenticated, loading, apiServerDown } = useAuth();

  useEffect(() => {
    // Auto-redirect if already authenticated
    if (!loading && isAuthenticated()) {
      navigate('/dashboard');
    }
  }, [loading, isAuthenticated, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Admin Portal</h1>
          <p className="text-gray-600 mt-2">Configuration Management</p>
        </div>

        {apiServerDown ? (
          <div className="bg-red-50 border-2 border-red-300 text-red-900 px-4 py-4 rounded-md text-sm">
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
        ) : (
          <div className="text-center py-4">
            <p className="text-sm text-gray-500">
              No authentication required (prototype mode)
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Redirecting to dashboard...
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default LoginPage;
