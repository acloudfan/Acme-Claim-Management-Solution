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
  const { isAuthenticated, login } = useAuth();

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
        </div>
      </div>
    </div>
  );
}
