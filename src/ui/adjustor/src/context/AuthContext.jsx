import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

// Mock adjustor data (must match scripts/seed-data.py)
const MOCK_ADJUSTORS = [
  { adjustor_id: 'ADJ-001', name: 'Sarah Chen', email: 'sarah.chen@acme-insurance.com', role: 'Senior Adjustor' },
  { adjustor_id: 'ADJ-002', name: 'Michael Torres', email: 'michael.torres@acme-insurance.com', role: 'Collision Specialist' },
  { adjustor_id: 'ADJ-003', name: 'Emily Watson', email: 'emily.watson@acme-insurance.com', role: 'Claims Supervisor' }
];

const MOCK_PASSWORD = 'password';

export const AuthProvider = ({ children }) => {
  const [adjustorId, setAdjustorId] = useState(null);
  const [adjustor, setAdjustor] = useState(null);
  const [loading, setLoading] = useState(true);
  const [hasAdjustors, setHasAdjustors] = useState(null);
  const [adjustorCount, setAdjustorCount] = useState(0);

  // Load adjustor from sessionStorage on mount (not localStorage)
  useEffect(() => {
    // Check adjustor count on mount
    checkAdjustorCount();

    const storedAdjustorId = sessionStorage.getItem('adjustor_id');
    if (storedAdjustorId) {
      const foundAdjustor = MOCK_ADJUSTORS.find(adj => adj.adjustor_id === storedAdjustorId);
      if (foundAdjustor) {
        setAdjustorId(storedAdjustorId);
        setAdjustor(foundAdjustor);
      } else {
        // Invalid stored ID, clear it
        sessionStorage.removeItem('adjustor_id');
      }
    }
    setLoading(false);

    // Auto-logout when window/tab is closed
    const handleBeforeUnload = () => {
      sessionStorage.removeItem('adjustor_id');
    };
    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, []);

  const checkAdjustorCount = async () => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/adjustors/count`);
      const data = await response.json();
      setHasAdjustors(data.has_adjustors);
      setAdjustorCount(data.count);
    } catch (error) {
      console.error('Failed to check adjustor count:', error);
      // Assume adjustors exist if API call fails (fail open)
      setHasAdjustors(true);
    }
  };

  const login = async (selectedAdjustorId, password) => {
    // Validate password
    if (password !== MOCK_PASSWORD) {
      throw new Error('Invalid password');
    }

    // Find adjustor
    const foundAdjustor = MOCK_ADJUSTORS.find(adj => adj.adjustor_id === selectedAdjustorId);
    if (!foundAdjustor) {
      throw new Error('Invalid adjustor ID');
    }

    // Store in sessionStorage (cleared when browser closes)
    sessionStorage.setItem('adjustor_id', selectedAdjustorId);

    // Update state
    setAdjustorId(selectedAdjustorId);
    setAdjustor(foundAdjustor);

    return foundAdjustor;
  };

  const logout = () => {
    sessionStorage.removeItem('adjustor_id');
    setAdjustorId(null);
    setAdjustor(null);
  };

  const isAuthenticated = () => {
    return adjustorId !== null && adjustor !== null;
  };

  const value = {
    adjustorId,
    adjustor,
    loading,
    login,
    logout,
    isAuthenticated,
    availableAdjustors: MOCK_ADJUSTORS,
    hasAdjustors,
    adjustorCount
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
