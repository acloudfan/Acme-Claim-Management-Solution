/**
 * Main App component with routing
 */
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import HomePage from './pages/HomePage';
import PolicyPage from './pages/PolicyPage';
import NewClaimPage from './pages/NewClaimPage';
import ImageUploadPage from './pages/ImageUploadPage';
import ClaimAnalysisPage from './pages/ClaimAnalysisPage';
import ClaimDetailPage from './pages/ClaimDetailPage';

// Protected Route wrapper
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return isAuthenticated() ? children : <Navigate to="/login" replace />;
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <HomePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/policy/:policyNumber"
            element={
              <ProtectedRoute>
                <PolicyPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/claims/new"
            element={
              <ProtectedRoute>
                <NewClaimPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/claims/:claimId/edit"
            element={
              <ProtectedRoute>
                <NewClaimPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/claims/:claimId/upload"
            element={
              <ProtectedRoute>
                <ImageUploadPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/claims/:claimId/submit"
            element={
              <ProtectedRoute>
                <ClaimAnalysisPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/claims/:claimId"
            element={
              <ProtectedRoute>
                <ClaimDetailPage />
              </ProtectedRoute>
            }
          />
          {/* Redirect any unknown routes to home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
