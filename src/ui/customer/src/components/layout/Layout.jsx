/**
 * Main layout wrapper component
 */
import Header from './Header';
import Footer from './Footer';
import ChatWidget from '../ChatWidget';

const Layout = ({ children, currentContext }) => {
  // Get customer ID from localStorage
  const customerId = localStorage.getItem('customer_id');

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
      <Footer />

      {/* Floating chat widget - appears on all pages */}
      {customerId && (
        <ChatWidget
          customerId={parseInt(customerId)}
          currentContext={currentContext}
        />
      )}
    </div>
  );
};

export default Layout;
