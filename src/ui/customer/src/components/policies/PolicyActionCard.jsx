/**
 * Policy Action Card - Shows available policy actions
 */
import { ChevronRight } from 'lucide-react';

const PolicyActionCard = ({ icon: Icon, title, description, onClick, primary = false }) => {
  return (
    <button
      onClick={onClick}
      className={`
        w-full text-left p-5 rounded-xl border-2 transition-all duration-200
        ${primary
          ? 'bg-primary-600 border-primary-600 text-white hover:bg-primary-700 hover:border-primary-700 hover:shadow-lg'
          : 'bg-white border-gray-200 hover:border-primary-300 hover:shadow-md'
        }
        transform hover:-translate-y-1
      `}
    >
      <div className="flex items-start gap-4">
        <div className={`
          p-3 rounded-lg flex-shrink-0
          ${primary ? 'bg-white/20' : 'bg-primary-50'}
        `}>
          <Icon className={`h-6 w-6 ${primary ? 'text-white' : 'text-primary-600'}`} />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className={`font-semibold text-lg mb-1 ${primary ? 'text-white' : 'text-gray-900'}`}>
            {title}
          </h3>
          <p className={`text-sm ${primary ? 'text-white/90' : 'text-gray-600'}`}>
            {description}
          </p>
        </div>
        <ChevronRight className={`h-5 w-5 flex-shrink-0 mt-1 ${primary ? 'text-white' : 'text-gray-400'}`} />
      </div>
    </button>
  );
};

export default PolicyActionCard;
