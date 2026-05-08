/**
 * Login Page (Minimal - No Auth Required)
 */
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Button from '../components/common/Button';
import { BarChart3 } from 'lucide-react';

export default function LoginPage() {
  const navigate = useNavigate();
  const { isAuthenticated, login, apiServerDown } = useAuth();

  useEffect(() => {
    // Auto-redirect if already authenticated
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const handleEnter = () => {
    login(); // Use default executive ID
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 md:p-12 max-w-md w-full">
        <div className="text-center">
          {/* Logo */}
          <div className="inline-flex items-center justify-center w-20 h-20 bg-primary-500 rounded-full mb-6">
            <BarChart3 className="w-10 h-10 text-white" />
          </div>

          {/* Title */}
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            ACME Claims
          </h1>
          <p className="text-xl text-primary-600 font-semibold mb-2">
            Executive Portal
          </p>
          <p className="text-gray-600 mb-8">
            Business Intelligence Dashboard
          </p>

          {/* API Server Down Warning */}
          {apiServerDown ? (
            <div className="bg-red-50 border-2 border-red-300 text-red-900 px-4 py-4 rounded-md text-sm text-left">
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
            <>
              {/* Enter Button */}
              <Button
                variant="primary"
                size="lg"
                onClick={handleEnter}
                className="w-full"
              >
                Enter Portal
              </Button>

              {/* Info Text */}
              <p className="text-sm text-gray-500 mt-6">
                No authentication required for prototype
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
