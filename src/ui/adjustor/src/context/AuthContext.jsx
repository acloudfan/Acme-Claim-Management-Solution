import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

// Mock adjustor data
const MOCK_ADJUSTORS = [
  { adjustor_id: 'ADJ-001', name: 'Sarah Johnson', email: 'sarah.johnson@acme-insurance.com', role: 'Senior Claims Adjustor' },
  { adjustor_id: 'ADJ-002', name: 'Michael Chen', email: 'michael.chen@acme-insurance.com', role: 'Claims Adjustor' },
  { adjustor_id: 'ADJ-003', name: 'Emily Rodriguez', email: 'emily.rodriguez@acme-insurance.com', role: 'Senior Claims Adjustor' }
];

const MOCK_PASSWORD = 'adjustor123';

export const AuthProvider = ({ children }) => {
  const [adjustorId, setAdjustorId] = useState(null);
  const [adjustor, setAdjustor] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load adjustor from localStorage on mount
  useEffect(() => {
    const storedAdjustorId = localStorage.getItem('adjustor_id');
    if (storedAdjustorId) {
      const foundAdjustor = MOCK_ADJUSTORS.find(adj => adj.adjustor_id === storedAdjustorId);
      if (foundAdjustor) {
        setAdjustorId(storedAdjustorId);
        setAdjustor(foundAdjustor);
      } else {
        // Invalid stored ID, clear it
        localStorage.removeItem('adjustor_id');
      }
    }
    setLoading(false);
  }, []);

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

    // Store in localStorage
    localStorage.setItem('adjustor_id', selectedAdjustorId);

    // Update state
    setAdjustorId(selectedAdjustorId);
    setAdjustor(foundAdjustor);

    return foundAdjustor;
  };

  const logout = () => {
    localStorage.removeItem('adjustor_id');
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
    availableAdjustors: MOCK_ADJUSTORS
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
