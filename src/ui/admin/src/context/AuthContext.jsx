/**
 * Authentication Context for Admin Portal
 * No real authentication - just tracking for prototype
 */
import { createContext, useContext, useState, useEffect } from 'react';
import { getConfig } from '../api/config';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [adminId, setAdminId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [apiServerDown, setApiServerDown] = useState(false);

  useEffect(() => {
    // Check API server health first
    checkApiServer();

    // Check if admin is already logged in
    const storedAdminId = sessionStorage.getItem('admin_id');
    if (storedAdminId) {
      setAdminId(storedAdminId);
    } else {
      // Auto-login with default admin ID if no auth required
      const config = getConfig();
      if (!config.auth.require_login) {
        const defaultId = config.auth.default_admin_id;
        setAdminId(defaultId);
        sessionStorage.setItem('admin_id', defaultId);
      }
    }
    setLoading(false);

    // Auto-logout when window/tab is closed
    const handleBeforeUnload = () => {
      sessionStorage.removeItem('admin_id');
    };
    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, []);

  const checkApiServer = async () => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/health`, {
        signal: AbortSignal.timeout(5000)
      });

      if (!response.ok) {
        throw new Error(`API returned ${response.status}`);
      }

      setApiServerDown(false);
    } catch (error) {
      console.error('API server health check failed:', error);
      if (error.name === 'TypeError' || error.message.includes('Failed to fetch') || error.name === 'TimeoutError') {
        setApiServerDown(true);
      }
    }
  };

  const login = (id) => {
    setAdminId(id);
    sessionStorage.setItem('admin_id', id);
  };

  const logout = () => {
    setAdminId(null);
    sessionStorage.removeItem('admin_id');
  };

  const isAuthenticated = () => {
    return !!adminId;
  };

  return (
    <AuthContext.Provider
      value={{
        adminId,
        loading,
        login,
        logout,
        isAuthenticated,
        apiServerDown,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
