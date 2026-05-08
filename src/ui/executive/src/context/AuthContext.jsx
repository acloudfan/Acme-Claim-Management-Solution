/**
 * Authentication Context (No-Auth Mode)
 * Provides minimal auth state for prototype
 */
import React, { createContext, useContext, useState, useEffect } from 'react';
import { getConfig } from '../api/config';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [executiveId, setExecutiveId] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check localStorage for executive_id
    const storedId = localStorage.getItem('executive_id');
    const config = getConfig();

    if (storedId) {
      setExecutiveId(storedId);
      setIsAuthenticated(true);
    } else if (!config.auth.require_login) {
      // Auto-authenticate with default ID
      const defaultId = config.auth.default_executive_id;
      setExecutiveId(defaultId);
      localStorage.setItem('executive_id', defaultId);
      setIsAuthenticated(true);
    }
  }, []);

  const login = (id = null) => {
    const config = getConfig();
    const finalId = id || config.auth.default_executive_id;
    setExecutiveId(finalId);
    localStorage.setItem('executive_id', finalId);
    setIsAuthenticated(true);
  };

  const logout = () => {
    setExecutiveId(null);
    localStorage.removeItem('executive_id');
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ executiveId, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
