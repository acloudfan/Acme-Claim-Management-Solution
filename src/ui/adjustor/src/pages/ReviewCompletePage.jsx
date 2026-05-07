/**
 * ReviewCompletePage - Final review submission page
 */
import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { completeReview } from '../api/claims';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import CostSummary from '../components/claims/CostSummary';
import NotesEditor from '../components/claims/NotesEditor';
import Modal from '../components/common/Modal';
import { ArrowLeft, CheckCircle } from 'lucide-react';

const ReviewCompletePage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { adjustor } = useAuth();

  const { claim, damages, originalDamages, revisedTotal, laborRateState, laborCost } = location.state || {};

  const [reviewDecision, setReviewDecision] = useState('');
  const [customerNote, setCustomerNote] = useState('');
  const [internalNote, setInternalNote] = useState('');
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  if (!claim) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">No claim data available</p>
        <Button onClick={() => navigate('/claims/queue')}>Return to Queue</Button>
      </div>
    );
  }

  const originalTotal = parseFloat(claim.ai_estimate_total) || 0;

  const validate = () => {
    const newErrors = {};

    if (!reviewDecision) {
      newErrors.reviewDecision = 'Please select a review decision';
    }

    if (!customerNote || customerNote.trim().length < 10) {
      newErrors.customerNote = 'Customer note must be at least 10 characters';
    }

    if (!internalNote || internalNote.trim().length < 10) {
      newErrors.internalNote = 'Internal note must be at least 10 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;

    // Show confirmation modal for large changes
    const changePercent = Math.abs(((revisedTotal - originalTotal) / originalTotal) * 100);
    if (changePercent > 100 && !showConfirmModal) {
      setShowConfirmModal(true);
      return;
    }

    try {
      setLoading(true);

      // Prepare damage updates - include all damages with their current values
      const damageUpdates = damages.map((damage) => {
        const update = {
          damage_id: damage.damage_id,
          labor_hours: parseFloat(damage.labor_hours) || 0,
          parts_cost: parseFloat(damage.parts_cost) || 0,
          adjustor_note: damage.adjustor_note || null,
        };

        // If this is a manual damage (string ID), include additional fields
        if (typeof damage.damage_id === 'string' && damage.damage_id.startsWith('manual_')) {
          update.damage_part = damage.damage_part || damage.location;
          update.damage_type = damage.damage_type;
          update.location = damage.location;
          update.description = damage.description;
          update.severity = damage.severity;
          update.image_id = damage.image_id || null;
        }

        return update;
      });

      const reviewData = {
        action: reviewDecision,
        customer_note: customerNote.trim(),
        internal_note: internalNote.trim(),
        revised_estimate_total: parseFloat(revisedTotal) || 0,
        adjustor_id: adjustor.adjustor_id,
        damages: damageUpdates,
        labor_rate_state: laborRateState || null,
        state_avg_labor_cost: parseFloat(laborCost) || null,
      };

      console.log('Submitting review data:', reviewData);

      const result = await completeReview(claim.claim_id, reviewData);

      console.log('Review completed successfully:', result);

      // Success - redirect to queue
      navigate('/claims/queue', {
        state: {
          message: `Claim #${claim.claim_id} review completed successfully`,
        },
      });
    } catch (err) {
      console.error('Failed to complete review:', err);
      console.error('Error details:', err.response?.data);
      setErrors({
        submit: err.response?.data?.detail || 'Failed to submit review. Please try again.',
      });
    } finally {
      setLoading(false);
      setShowConfirmModal(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" onClick={() => navigate(-1)} size="sm">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Review
        </Button>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Complete Review - Claim #{claim.claim_id}</h1>
          <p className="text-gray-600 mt-1">Submit your final decision and notes</p>
        </div>
      </div>

      {/* Cost Summary */}
      <CostSummary
        originalEstimate={originalTotal}
        revisedEstimate={revisedTotal}
        damages={damages}
        originalDamages={originalDamages}
      />

      {/* Review Decision */}
      <Card title="Review Decision">
        <div className="space-y-4">
          <p className="text-sm text-gray-600 mb-4">
            Choose your decision based on the review and cost analysis:
          </p>

          <div className="space-y-3">
            <label className="flex items-start p-4 border-2 rounded-lg cursor-pointer transition-colors hover:bg-gray-50">
              <input
                type="radio"
                name="reviewDecision"
                value="denied_appeal"
                checked={reviewDecision === 'denied_appeal'}
                onChange={(e) => setReviewDecision(e.target.value)}
                className="mt-1 h-4 w-4 text-primary-600 focus:ring-primary-500"
              />
              <div className="ml-3">
                <span className="block text-sm font-medium text-gray-900">Deny Appeal</span>
                <span className="block text-sm text-gray-600 mt-1">
                  Uphold the original AI estimate. Customer's appeal is not justified.
                </span>
              </div>
            </label>

            <label className="flex items-start p-4 border-2 rounded-lg cursor-pointer transition-colors hover:bg-gray-50">
              <input
                type="radio"
                name="reviewDecision"
                value="revised_estimate"
                checked={reviewDecision === 'revised_estimate'}
                onChange={(e) => setReviewDecision(e.target.value)}
                className="mt-1 h-4 w-4 text-primary-600 focus:ring-primary-500"
              />
              <div className="ml-3">
                <span className="block text-sm font-medium text-gray-900">Revise Estimate</span>
                <span className="block text-sm text-gray-600 mt-1">
                  Update the estimate based on adjustor review. Return to customer with revised amount.
                </span>
              </div>
            </label>

            <label className="flex items-start p-4 border-2 rounded-lg cursor-pointer transition-colors hover:bg-gray-50 border-orange-200 hover:bg-orange-50">
              <input
                type="radio"
                name="reviewDecision"
                value="route_to_traditional"
                checked={reviewDecision === 'route_to_traditional'}
                onChange={(e) => setReviewDecision(e.target.value)}
                className="mt-1 h-4 w-4 text-orange-600 focus:ring-orange-500"
              />
              <div className="ml-3">
                <span className="block text-sm font-medium text-gray-900">Route to Traditional Processing</span>
                <span className="block text-sm text-gray-600 mt-1">
                  Damage requires in-person inspection or cannot be accurately assessed remotely. Customer will be contacted to schedule physical inspection.
                </span>
              </div>
            </label>
          </div>

          {errors.reviewDecision && (
            <p className="text-sm text-danger mt-2">{errors.reviewDecision}</p>
          )}
        </div>
      </Card>

      {/* Notes */}
      <Card title="Review Notes">
        <NotesEditor
          customerNote={customerNote}
          internalNote={internalNote}
          onCustomerNoteChange={(e) => setCustomerNote(e.target.value)}
          onInternalNoteChange={(e) => setInternalNote(e.target.value)}
          errors={errors}
        />
      </Card>

      {/* Submit Error */}
      {errors.submit && (
        <Card className="bg-red-50 border-red-200">
          <p className="text-sm text-danger">{errors.submit}</p>
        </Card>
      )}

      {/* Actions */}
      <Card>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={() => navigate(-1)} disabled={loading}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleSubmit} loading={loading}>
            <CheckCircle className="h-5 w-5 mr-2" />
            Submit Review
          </Button>
        </div>
      </Card>

      {/* Confirmation Modal */}
      <Modal
        isOpen={showConfirmModal}
        onClose={() => setShowConfirmModal(false)}
        title="Confirm Large Cost Change"
        size="md"
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-700">
            The revised estimate differs by more than 100% from the original AI estimate.
          </p>
          <p className="text-sm text-gray-700">
            Please confirm that all adjustments have been properly documented and reviewed.
          </p>

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-sm font-medium text-yellow-800">Cost Change Summary:</p>
            <ul className="text-sm text-yellow-700 mt-2 space-y-1">
              <li>Original: ${originalTotal.toFixed(2)}</li>
              <li>Revised: ${revisedTotal.toFixed(2)}</li>
              <li>
                Difference: {revisedTotal > originalTotal ? '+' : ''}$
                {(revisedTotal - originalTotal).toFixed(2)} (
                {((revisedTotal - originalTotal) / originalTotal * 100).toFixed(1)}%)
              </li>
            </ul>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Button variant="secondary" onClick={() => setShowConfirmModal(false)}>
              Go Back
            </Button>
            <Button variant="primary" onClick={handleSubmit} loading={loading}>
              Confirm & Submit
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default ReviewCompletePage;
