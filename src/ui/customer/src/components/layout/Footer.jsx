/**
 * Footer component
 */

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="text-center text-gray-600 text-sm">
          <p>&copy; {currentYear} Insurance Claims Portal. All rights reserved.</p>
          <p className="mt-1 text-gray-500">
            AI-Powered Auto Insurance Claims Management (Prototype)
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
