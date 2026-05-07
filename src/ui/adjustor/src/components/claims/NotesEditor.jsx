/**
 * NotesEditor component - two textareas for customer and internal notes
 */
import { useState, useEffect } from 'react';
import Textarea from '../common/Textarea';

const NotesEditor = ({
  customerNote,
  internalNote,
  onCustomerNoteChange,
  onInternalNoteChange,
  errors = {},
}) => {
  const CUSTOMER_NOTE_LIMIT = 1000;
  const INTERNAL_NOTE_LIMIT = 2000;

  const [customerCharCount, setCustomerCharCount] = useState(0);
  const [internalCharCount, setInternalCharCount] = useState(0);

  useEffect(() => {
    setCustomerCharCount(customerNote?.length || 0);
  }, [customerNote]);

  useEffect(() => {
    setInternalCharCount(internalNote?.length || 0);
  }, [internalNote]);

  const handleCustomerNoteChange = (e) => {
    const value = e.target.value;
    if (value.length <= CUSTOMER_NOTE_LIMIT) {
      onCustomerNoteChange(e);
    }
  };

  const handleInternalNoteChange = (e) => {
    const value = e.target.value;
    if (value.length <= INTERNAL_NOTE_LIMIT) {
      onInternalNoteChange(e);
    }
  };

  return (
    <div className="space-y-6">
      {/* Customer Note */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <label className="block text-sm font-medium text-gray-700">
            Customer Note
            <span className="text-danger ml-1">*</span>
          </label>
          <span className={`text-xs ${customerCharCount > CUSTOMER_NOTE_LIMIT * 0.9 ? 'text-danger' : 'text-gray-500'}`}>
            {customerCharCount} / {CUSTOMER_NOTE_LIMIT}
          </span>
        </div>
        <textarea
          value={customerNote}
          onChange={handleCustomerNoteChange}
          placeholder="Enter note that will be visible to the customer..."
          rows={4}
          className={`
            w-full px-4 py-3 border rounded-lg
            focus:ring-2 focus:ring-primary-500 focus:border-primary-500
            transition-colors
            ${errors.customerNote ? 'border-danger bg-red-50' : 'border-gray-300 bg-white'}
          `}
        />
        {errors.customerNote && (
          <p className="mt-1 text-sm text-danger">{errors.customerNote}</p>
        )}
        <p className="mt-1 text-xs text-gray-500">
          This note will be shared with the customer.
        </p>
      </div>

      {/* Internal Note */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <label className="block text-sm font-medium text-gray-700">
            Internal Note
            <span className="text-danger ml-1">*</span>
          </label>
          <span className={`text-xs ${internalCharCount > INTERNAL_NOTE_LIMIT * 0.9 ? 'text-danger' : 'text-gray-500'}`}>
            {internalCharCount} / {INTERNAL_NOTE_LIMIT}
          </span>
        </div>
        <textarea
          value={internalNote}
          onChange={handleInternalNoteChange}
          placeholder="Enter internal notes for records (not visible to customer)..."
          rows={4}
          className={`
            w-full px-4 py-3 border rounded-lg
            focus:ring-2 focus:ring-primary-500 focus:border-primary-500
            transition-colors
            ${errors.internalNote ? 'border-danger bg-red-50' : 'border-gray-300 bg-white'}
          `}
        />
        {errors.internalNote && (
          <p className="mt-1 text-sm text-danger">{errors.internalNote}</p>
        )}
        <p className="mt-1 text-xs text-gray-500">
          This note is for internal use only and will not be shared with the customer.
        </p>
      </div>
    </div>
  );
};

export default NotesEditor;
