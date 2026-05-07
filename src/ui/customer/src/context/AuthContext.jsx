/**
 * Authentication Context
 * Manages customer authentication state
 */
import { createContext, useContext, useState, useEffect } from 'react';
import { fetchCustomer } from '../api/customers';

const AuthContext = createContext();

// Mock customer data (similar to adjustor portal pattern)
const MOCK_CUSTOMERS = [
  { customer_id: 100, name: 'Jane Doe', email: 'jane.doe@example.com' },
  { customer_id: 101, name: 'John Smith', email: 'john.smith@example.com' },
  { customer_id: 102, name: 'Alice Johnson', email: 'alice.johnson@example.com' }
];

const MOCK_PASSWORD = 'password123';

export const AuthProvider = ({ children }) => {
  const [customerId, setCustomerId] = useState(null);
  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load customer_id from localStorage on mount
    const storedId = localStorage.getItem('customer_id');
    if (storedId) {
      setCustomerId(parseInt(storedId));
      loadCustomer(storedId);
    } else {
      setLoading(false);
    }
  }, []);

  const loadCustomer = async (id) => {
    try {
      const response = await fetchCustomer(id, true);
      setCustomer(response.data);
    } catch (error) {
      console.error('Failed to fetch customer:', error);
      // If customer fetch fails, clear auth
      logout();
    } finally {
      setLoading(false);
    }
  };

  /**
   * Mock login - validates password and customer selection (dropdown pattern)
   * @param {number} selectedCustomerId - Customer ID from dropdown
   * @param {string} password - Password
   * @returns {Promise<boolean>} Success status
   */
  const login = async (selectedCustomerId, password) => {
    // Validate password
    if (password !== MOCK_PASSWORD) {
      throw new Error('Invalid password');
    }

    // Find customer in mock list
    const foundCustomer = MOCK_CUSTOMERS.find(c => c.customer_id === parseInt(selectedCustomerId));
    if (!foundCustomer) {
      throw new Error('Invalid customer selection');
    }

    // Store customer_id in localStorage
    localStorage.setItem('customer_id', selectedCustomerId.toString());
    setCustomerId(parseInt(selectedCustomerId));

    // Fetch customer data from API
    await loadCustomer(selectedCustomerId);

    return true;
  };

  /**
   * Logout - clear auth state
   */
  const logout = () => {
    localStorage.removeItem('customer_id');
    setCustomerId(null);
    setCustomer(null);
  };

  /**
   * Check if user is authenticated
   * @returns {boolean} Is authenticated
   */
  const isAuthenticated = () => {
    return customerId !== null;
  };

  const value = {
    customerId,
    customer,
    loading,
    login,
    logout,
    isAuthenticated,
    availableCustomers: MOCK_CUSTOMERS
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

/**
 * Hook to use auth context
 * @returns {Object} Auth context
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
