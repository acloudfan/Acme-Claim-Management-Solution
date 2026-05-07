/**
 * Header component with navigation
 */
import { useNavigate } from 'react-router-dom';
import { LogOut, User } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import Button from '../common/Button';

const Header = () => {
  const navigate = useNavigate();
  const { customer, logout, isAuthenticated } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!isAuthenticated()) {
    return null; // Don't show header on login page
  }

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div
            className="flex items-center cursor-pointer"
            onClick={() => navigate('/')}
          >
            <img
              src="/ACME-logo.png"
              alt="ACME Insurance"
              className="h-12 w-auto"
            />
          </div>

          {/* Right side - User info and logout */}
          <div className="flex items-center gap-4">
            {customer && (
              <div className="flex items-center gap-2 text-gray-700">
                <User className="h-5 w-5" />
                <span className="font-medium">
                  Welcome, {customer.fname || 'Customer'}!
                </span>
              </div>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="text-gray-600"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
