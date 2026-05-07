/**
 * Main layout wrapper component
 */
import { useState, useEffect } from 'react';
import Header from './Header';
import Footer from './Footer';
import ChatWidget from '../ChatWidget';
import { getFeatureFlags } from '../../api/features';

const Layout = ({ children, currentContext }) => {
  // Get customer ID from localStorage
  const customerId = localStorage.getItem('customer_id');
  const [chatbotEnabled, setChatbotEnabled] = useState(true); // Default to true for backwards compatibility

  // Fetch feature flags on mount
  useEffect(() => {
    const fetchFeatureFlags = async () => {
      try {
        const flags = await getFeatureFlags();
        setChatbotEnabled(flags.chatbot_enabled);
      } catch (error) {
        console.error('Failed to fetch feature flags:', error);
        // On error, keep chatbot enabled (fail open)
        setChatbotEnabled(true);
      }
    };

    fetchFeatureFlags();
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
      <Footer />

      {/* Floating chat widget - appears on all pages when enabled */}
      {customerId && chatbotEnabled && (
        <ChatWidget
          customerId={parseInt(customerId)}
          currentContext={currentContext}
        />
      )}
    </div>
  );
};

export default Layout;
