/**
 * Main layout component wrapping all pages
 */
import { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { FileText } from 'lucide-react';
import Header from './Header';
import Footer from './Footer';
import SOPViewer from '../common/SOPViewer';

const Layout = ({ children }) => {
  const location = useLocation();
  const [showSOP, setShowSOP] = useState(false);

  // Don't show header/footer on login page
  const isLoginPage = location.pathname === '/login';

  if (isLoginPage) {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
      <Footer />

      {/* Floating SOP Button - Positioned in bottom-right */}
      <button
        onClick={() => setShowSOP(true)}
        className="fixed bottom-6 right-6 p-4 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-all hover:scale-110 focus:outline-none focus:ring-4 focus:ring-blue-300 z-50"
        aria-label="View Standard Operating Procedures"
        title="View SOP - Damage Triage Guidelines"
      >
        <FileText className="w-6 h-6" stroke="white" strokeWidth={2} />
      </button>

      {/* SOP Viewer Modal */}
      <SOPViewer isOpen={showSOP} onClose={() => setShowSOP(false)} />
    </div>
  );
};

export default Layout;
