import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/layout/ProtectedRoute';
import Layout from './components/layout/Layout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ClaimQueuePage from './pages/ClaimQueuePage';
import ClaimDetailPage from './pages/ClaimDetailPage';
import ReviewCompletePage from './pages/ReviewCompletePage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Layout>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />

            {/* Protected routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/claims/queue"
              element={
                <ProtectedRoute>
                  <ClaimQueuePage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/claims/:claimId/review"
              element={
                <ProtectedRoute>
                  <ClaimDetailPage />
                </ProtectedRoute>
              }
            />

            <Route
              path="/claims/:claimId/review/complete"
              element={
                <ProtectedRoute>
                  <ReviewCompletePage />
                </ProtectedRoute>
              }
            />

            {/* Default redirect */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Layout>
      </Router>
    </AuthProvider>
  );
}

export default App;
