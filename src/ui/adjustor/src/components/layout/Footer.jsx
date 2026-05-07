/**
 * Footer component for adjustor portal
 */

const Footer = () => {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex flex-col sm:flex-row justify-between items-center text-sm text-gray-600">
          <p>© 2026 ACME Insurance. All rights reserved.</p>
          <p className="mt-2 sm:mt-0">
            <span className="font-medium">Version 1.0.0</span> · AI-Powered Claims Adjustor Portal
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
