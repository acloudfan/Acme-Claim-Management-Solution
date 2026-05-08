/**
 * Authentication Context
 * Manages customer authentication state
 */
import { createContext, useContext, useState, useEffect } from 'react';
import { fetchCustomer } from '../api/customers';

const AuthContext = createContext();

// Mock customer data (matches seed_data.py)
const MOCK_CUSTOMERS = [
  { customer_id: 100, name: 'John Doe', email: 'john.doe@example.com' },
  { customer_id: 101, name: 'Jane Smith', email: 'jane.smith@example.com' },
  { customer_id: 102, name: 'Bob Johnson', email: 'bob.johnson@example.com' },
  { customer_id: 103, name: 'Alice Williams', email: 'alice.williams@example.com' },
  { customer_id: 104, name: 'Charlie Brown', email: 'charlie.brown@example.com' }
];

const MOCK_PASSWORD = 'password';

export const AuthProvider = ({ children }) => {
  const [customerId, setCustomerId] = useState(null);
  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [hasCustomers, setHasCustomers] = useState(null);
  const [customerCount, setCustomerCount] = useState(0);

  useEffect(() => {
    // Check customer count on mount
    checkCustomerCount();

    // Load customer_id from localStorage on mount
    const storedId = localStorage.getItem('customer_id');
    if (storedId) {
      setCustomerId(parseInt(storedId));
      loadCustomer(storedId);
    } else {
      setLoading(false);
    }
  }, []);

  const checkCustomerCount = async () => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/customers`);
      const data = await response.json();
      setHasCustomers(data.has_customers);
      setCustomerCount(data.count);
    } catch (error) {
      console.error('Failed to check customer count:', error);
      // Assume customers exist if API call fails (fail open)
      setHasCustomers(true);
    }
  };

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
    availableCustomers: MOCK_CUSTOMERS,
    hasCustomers,
    customerCount
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
