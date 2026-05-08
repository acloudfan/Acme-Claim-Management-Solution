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
  const [apiServerDown, setApiServerDown] = useState(false);

  useEffect(() => {
    // Check API server health first
    checkApiServer();

    // Check sessionStorage for executive_id
    const storedId = sessionStorage.getItem('executive_id');
    const config = getConfig();

    if (storedId) {
      setExecutiveId(storedId);
      setIsAuthenticated(true);
    } else if (!config.auth.require_login) {
      // Auto-authenticate with default ID
      const defaultId = config.auth.default_executive_id;
      setExecutiveId(defaultId);
      sessionStorage.setItem('executive_id', defaultId);
      setIsAuthenticated(true);
    }

    // Auto-logout when window/tab is closed
    const handleBeforeUnload = () => {
      sessionStorage.removeItem('executive_id');
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

  const login = (id = null) => {
    const config = getConfig();
    const finalId = id || config.auth.default_executive_id;
    setExecutiveId(finalId);
    sessionStorage.setItem('executive_id', finalId);
    setIsAuthenticated(true);
  };

  const logout = () => {
    setExecutiveId(null);
    sessionStorage.removeItem('executive_id');
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ executiveId, isAuthenticated, login, logout, apiServerDown }}>
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
