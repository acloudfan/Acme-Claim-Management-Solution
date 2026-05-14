/**
 * NotesEditor component - two textareas for customer and internal notes
 */
import { useState, useEffect } from 'react';
import Textarea from '../common/Textarea';
import { Star } from 'lucide-react';

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

  // AI Feedback ratings (dummy state - not saved)
  const [damageSummaryRating, setDamageSummaryRating] = useState(0);
  const [repairEstimateRating, setRepairEstimateRating] = useState(0);
  const [fraudDetectionRating, setFraudDetectionRating] = useState(0);
  const [aiComments, setAiComments] = useState('');

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

      {/* AI Feedback Section */}
      <div className="border-t pt-6 mt-6">
        <div className="mb-3">
          <h3 className="text-sm font-medium text-gray-700 mb-1">AI Performance Feedback (Optional)</h3>
          <p className="text-xs text-gray-500">
            Rate AI outputs to help improve system accuracy (1 = Poor, 5 = Excellent)
          </p>
        </div>

        <div className="bg-gray-50 rounded-lg p-4 space-y-3">
          {/* AI Damage Summary Rating */}
          <RatingControl
            label="AI Damage Summary"
            rating={damageSummaryRating}
            onRatingChange={setDamageSummaryRating}
          />

          {/* AI Repair Estimate Rating */}
          <RatingControl
            label="AI Repair Estimate"
            rating={repairEstimateRating}
            onRatingChange={setRepairEstimateRating}
          />

          {/* Fraud Detection Rating */}
          <RatingControl
            label="Fraud Detection"
            rating={fraudDetectionRating}
            onRatingChange={setFraudDetectionRating}
          />

          {/* AI Comments */}
          <div className="pt-2">
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Additional Comments
            </label>
            <textarea
              value={aiComments}
              onChange={(e) => setAiComments(e.target.value)}
              placeholder="Any observations about AI performance? (optional)"
              rows={2}
              maxLength={500}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-1 focus:ring-primary-500 focus:border-primary-500"
            />
            <p className="text-xs text-gray-400 mt-1">{aiComments.length}/500 characters</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Rating Control Component
const RatingControl = ({ label, rating, onRatingChange }) => {
  return (
    <div className="flex items-center justify-between py-2">
      <label className="text-xs font-medium text-gray-600 min-w-[140px]">
        {label}
      </label>

      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            onClick={() => onRatingChange(star)}
            className="transition-all duration-150 hover:scale-110 focus:outline-none focus:ring-1 focus:ring-primary-400 rounded p-0.5"
          >
            <Star
              className={`w-5 h-5 ${
                star <= rating
                  ? 'fill-yellow-400 text-yellow-400'
                  : 'text-gray-300 hover:text-gray-400'
              }`}
            />
          </button>
        ))}
        {rating > 0 && (
          <span className="text-xs text-gray-500 ml-2 min-w-[30px]">
            {rating}/5
          </span>
        )}
        {rating > 0 && (
          <button
            type="button"
            onClick={() => onRatingChange(0)}
            className="ml-1 text-xs text-gray-400 hover:text-gray-600"
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
};

export default NotesEditor;
