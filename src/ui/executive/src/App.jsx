/**
 * Main App component with routing
 */
import { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { loadConfig } from './api/config';
import { AuthProvider } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import NotFoundPage from './pages/NotFoundPage';
import Spinner from './components/common/Spinner';

function App() {
  const [configLoaded, setConfigLoaded] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Load configuration on mount
    loadConfig()
      .then(() => {
        console.log('Config loaded successfully');
        setConfigLoaded(true);
      })
      .catch((err) => {
        console.error('Failed to load config:', err);
        setError('Failed to load configuration');
        // Still mark as loaded to allow app to run with defaults
        setConfigLoaded(true);
      });
  }, []);

  if (!configLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    console.warn('Running with default configuration');
  }

  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
