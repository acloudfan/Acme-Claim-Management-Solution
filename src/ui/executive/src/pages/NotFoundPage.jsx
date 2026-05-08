/**
 * 404 Not Found Page
 */
import { useNavigate } from 'react-router-dom';
import Button from '../components/common/Button';
import { Home } from 'lucide-react';

export default function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="text-center">
        <h1 className="text-9xl font-bold text-primary-500 mb-4">404</h1>
        <h2 className="text-3xl font-semibold text-gray-900 mb-4">
          Page Not Found
        </h2>
        <p className="text-gray-600 mb-8">
          The page you're looking for doesn't exist.
        </p>
        <Button
          variant="primary"
          onClick={() => navigate('/dashboard')}
          className="inline-flex items-center gap-2"
        >
          <Home className="w-5 h-5" />
          Back to Dashboard
        </Button>
      </div>
    </div>
  );
}
