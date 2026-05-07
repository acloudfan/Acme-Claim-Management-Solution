import React from 'react';

/**
 * ConfigSubsection - Wrapper for grouping related configuration fields
 *
 * Creates a visual subsection within a ConfigSection with a title and
 * light background to group related fields together.
 */
const ConfigSubsection = ({ title, children, description = null }) => {
  return (
    <div className="bg-gray-50 rounded-lg p-4 space-y-4">
      {/* Subsection header */}
      <div className="border-b border-gray-200 pb-2">
        <h4 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
          {title}
        </h4>
        {description && (
          <p className="text-sm text-gray-600 mt-1">{description}</p>
        )}
      </div>

      {/* Fields */}
      <div className="space-y-6">
        {children}
      </div>
    </div>
  );
};

export default ConfigSubsection;
