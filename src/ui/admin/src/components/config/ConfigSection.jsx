import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import Card from '../common/Card';

/**
 * ConfigSection - Collapsible section wrapper for configuration groups
 *
 * Provides expand/collapse functionality with smooth animations.
 * Each section contains multiple subsections of related fields.
 */
const ConfigSection = ({
  title,
  icon: Icon = null,
  children,
  defaultExpanded = true,
  description = null
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  return (
    <Card className="overflow-hidden">
      {/* Section header (clickable) */}
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-6 text-left hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          {Icon && <Icon className="w-6 h-6 text-blue-600" />}
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
            {description && (
              <p className="text-sm text-gray-600 mt-1">{description}</p>
            )}
          </div>
        </div>
        <div className="text-gray-400">
          {isExpanded ? (
            <ChevronUp className="w-5 h-5" />
          ) : (
            <ChevronDown className="w-5 h-5" />
          )}
        </div>
      </button>

      {/* Section content (collapsible) */}
      {isExpanded && (
        <div className="px-6 pb-6 space-y-6 border-t border-gray-200">
          <div className="pt-6 space-y-6">
            {children}
          </div>
        </div>
      )}
    </Card>
  );
};

export default ConfigSection;
