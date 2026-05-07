/**
 * File upload component (mockup - non-functional)
 */
import { Upload, File, X } from 'lucide-react';
import { useState } from 'react';

const FileUpload = ({
  label,
  accept = '.pdf,.jpg,.jpeg,.png',
  required = false,
  className = '',
}) => {
  const [fileName, setFileName] = useState('');

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setFileName(file.name);
    }
  };

  const handleRemove = () => {
    setFileName('');
  };

  return (
    <div className={`mb-4 ${className}`}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
          {required && <span className="text-error-600 ml-1">*</span>}
        </label>
      )}

      {!fileName ? (
        <label className="block">
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer hover:border-primary-400 hover:bg-primary-50 transition-colors">
            <Upload className="w-8 h-8 mx-auto text-gray-400 mb-2" />
            <p className="text-sm text-gray-600 mb-1">
              Click to upload or drag and drop
            </p>
            <p className="text-xs text-gray-500">
              PDF, JPG, PNG (Max 10MB)
            </p>
            <input
              type="file"
              accept={accept}
              onChange={handleFileChange}
              className="hidden"
            />
          </div>
        </label>
      ) : (
        <div className="border border-gray-300 rounded-lg p-4 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <File className="w-5 h-5 text-primary-600" />
              <span className="text-sm font-medium text-gray-700">
                {fileName}
              </span>
            </div>
            <button
              type="button"
              onClick={handleRemove}
              className="text-gray-400 hover:text-error-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}

      <p className="mt-2 text-xs text-gray-500">
        Note: This is a mockup. File upload functionality will be implemented in a future phase.
      </p>
    </div>
  );
};

export default FileUpload;
