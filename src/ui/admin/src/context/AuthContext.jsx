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

  useEffect(() => {
    // Check if admin is already logged in
    const storedAdminId = localStorage.getItem('admin_id');
    if (storedAdminId) {
      setAdminId(storedAdminId);
    } else {
      // Auto-login with default admin ID if no auth required
      const config = getConfig();
      if (!config.auth.require_login) {
        const defaultId = config.auth.default_admin_id;
        setAdminId(defaultId);
        localStorage.setItem('admin_id', defaultId);
      }
    }
    setLoading(false);
  }, []);

  const login = (id) => {
    setAdminId(id);
    localStorage.setItem('admin_id', id);
  };

  const logout = () => {
    setAdminId(null);
    localStorage.removeItem('admin_id');
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
