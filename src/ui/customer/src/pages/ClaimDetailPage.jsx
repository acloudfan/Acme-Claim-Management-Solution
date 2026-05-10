/**
 * Claim Detail Page - View AI assessment and accept/appeal estimate
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, AlertCircle, CheckCircle, FileText, Info, AlertTriangle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { fetchClaimDetail, acceptEstimate, fetchClaimEvents, appealEstimate, fetchPolicy } from '../api/customers';
import Layout from '../components/layout/Layout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Spinner from '../components/common/Spinner';
import Badge from '../components/common/Badge';
import Modal from '../components/common/Modal';
import Textarea from '../components/common/Textarea';
import ClaimDetailsCard from '../components/claims/ClaimDetailsCard';
import { getStatusLabel, getStatusVariant } from '../utils/statusMapping';

const ClaimDetailPage = () => {
  const { claimId } = useParams();
  const navigate = useNavigate();
  const { customerId } = useAuth();

  const [claim, setClaim] = useState(null);
  const [policy, setPolicy] = useState(null);
  const [vehicle, setVehicle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAcceptModal, setShowAcceptModal] = useState(false);
  const [accepting, setAccepting] = useState(false);
  const [acceptanceDate, setAcceptanceDate] = useState(null);
  const [showAppealModal, setShowAppealModal] = useState(false);
  const [appealReason, setAppealReason] = useState('');
  const [appealing, setAppealing] = useState(false);
  const [isSecondAppeal, setIsSecondAppeal] = useState(false);
  const [appealDate, setAppealDate] = useState(null);

  useEffect(() => {
    if (customerId && claimId) {
      loadClaim();
    }
  }, [customerId, claimId]);

  const loadClaim = async () => {
    try {
      setLoading(true);
      const response = await fetchClaimDetail(customerId, claimId);
      const claimData = response.data;
      setClaim(claimData);
      console.log('Loaded claim:', claimData);

      // Fetch policy and vehicle data
      if (claimData.policy_number) {
        try {
          const policyResponse = await fetchPolicy(customerId, claimData.policy_number);
          const policyData = policyResponse.data;
          setPolicy(policyData);

          // Find the vehicle that matches this claim's VIN
          const matchedVehicle = policyData.vehicles?.find(v => v.vin === claimData.vin);
          if (matchedVehicle) {
            setVehicle(matchedVehicle);
          }
        } catch (policyErr) {
          console.error('Failed to load policy:', policyErr);
          // Don't fail the entire page load if policy fetch fails
        }
      }

      // Fetch events for payment processing and appeal detection
      if (response.data.current_status === 'sent_for_payment' ||
          response.data.current_status === 'customer_decision_pending' ||
          response.data.current_status === 'human_review_pending') {
        try {
          const eventsResponse = await fetchClaimEvents(customerId, claimId);
          const events = eventsResponse.data.events || [];

          // Find the accept_estimate event (for payment processing)
          const acceptEvent = events.find(event => event.action === 'accept_estimate');
          if (acceptEvent) {
            // Combine event_date and event_time to create a full datetime
            const dateTimeString = `${acceptEvent.event_date}T${acceptEvent.event_time}`;
            setAcceptanceDate(new Date(dateTimeString));
          }

          // Find the appeal_estimate event (for human review banner)
          const appealEvent = events.find(event => event.action === 'appeal_estimate');
          if (appealEvent) {
            const dateTimeString = `${appealEvent.event_date}T${appealEvent.event_time}`;
            setAppealDate(new Date(dateTimeString));
          }

          // Check if human review was completed (indicates second appeal scenario)
          const hasHumanReview = events.some(
            event => event.action === 'revised_estimate' ||
                     event.status === 'human_review_completed'
          );
          setIsSecondAppeal(hasHumanReview);
        } catch (eventsErr) {
          console.error('Failed to load events:', eventsErr);
          // Don't fail the entire page load if events fail
        }
      }
    } catch (err) {
      console.error('Failed to load claim:', err);
      setError('Failed to load claim details. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate('/');
  };

  const handleAcceptEstimate = () => {
    setShowAcceptModal(true);
  };

  const handleConfirmAccept = async () => {
    try {
      setAccepting(true);
      await acceptEstimate(customerId, claimId);

      // Close modal
      setShowAcceptModal(false);

      // Reload claim to get updated status and show payment processing banner
      await loadClaim();
    } catch (err) {
      console.error('Failed to accept estimate:', err);
      alert('Failed to accept estimate. Please try again or contact support.');
    } finally {
      setAccepting(false);
    }
  };

  const handleCancelAccept = () => {
    setShowAcceptModal(false);
  };

  const handleAppealEstimate = () => {
    setAppealReason('');
    setShowAppealModal(true);
  };

  const handleConfirmAppeal = async () => {
    // Validate reason for first appeal
    if (!isSecondAppeal && !appealReason.trim()) {
      alert('Please provide a reason for your appeal.');
      return;
    }

    try {
      setAppealing(true);
      await appealEstimate(customerId, claimId, appealReason.trim() || 'Customer appealed');

      // Close modal
      setShowAppealModal(false);

      // Reload claim to get updated status and show appropriate banner
      await loadClaim();
    } catch (err) {
      console.error('Failed to appeal estimate:', err);
      alert('Failed to submit appeal. Please try again or contact support.');
    } finally {
      setAppealing(false);
    }
  };

  const handleCancelAppeal = () => {
    setShowAppealModal(false);
    setAppealReason('');
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <Spinner size="lg" />
        </div>
      </Layout>
    );
  }

  if (error || !claim) {
    return (
      <Layout>
        <div className="text-center py-12">
          <AlertCircle className="h-12 w-12 text-error-600 mx-auto mb-4" />
          <p className="text-gray-600 mb-4">{error || 'Claim not found'}</p>
          <Button onClick={handleBack}>Back to Home</Button>
        </div>
      </Layout>
    );
  }

  const damages = claim.damage_assessment?.damages || [];
  const totalCost = claim.damage_assessment?.total_estimated_cost || 0;
  const damageCount = damages.length;
  const isHumanReviewPending = claim.current_status === 'human_review_pending';
  const isPaymentProcessing = claim.current_status === 'sent_for_payment';
  const isRoutedToTraditional = claim.current_status === 'routed_to_traditional';

  // Check if claim was reviewed by adjustor
  const hasAdjustorReview = damages.some(d => d.reviewed_by_adjustor);

  // Determine if appeal was denied (no cost change) or accepted (cost revised)
  const aiTotal = damages.reduce((sum, d) => sum + parseFloat(d.ai_total_cost || 0), 0);
  const currentTotal = damages.reduce((sum, d) => sum + parseFloat(d.estimated_total_cost || 0), 0);
  const appealDenied = hasAdjustorReview && Math.abs(aiTotal - currentTotal) < 0.01;
  const appealAccepted = hasAdjustorReview && Math.abs(aiTotal - currentTotal) >= 0.01;

  // Get adjustor note (take first damage with note)
  const adjustorNote = damages.find(d => d.adjustor_note)?.adjustor_note ||
    'Our adjustor has reviewed your appeal and provided a decision.';

  // Debug logging
  console.log('Adjustor Review Debug:', {
    hasAdjustorReview,
    claimStatus: claim.current_status,
    showBanner: hasAdjustorReview && claim.current_status === 'customer_decision_pending',
    aiTotal,
    currentTotal,
    appealAccepted,
    appealDenied,
    damagesWithReview: damages.filter(d => d.reviewed_by_adjustor),
    adjustorNote
  });

  // Group damages by image_id
  const damagesByImage = damages.reduce((acc, damage) => {
    if (!acc[damage.image_id]) {
      acc[damage.image_id] = [];
    }
    acc[damage.image_id].push(damage);
    return acc;
  }, {});

  // Get annotated image URL with bounding boxes
  const getAnnotatedImageUrl = (imageId) => {
    return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/v1/customers/${customerId}/claims/${claimId}/images/${imageId}?annotated=yes`;
  };

  // Build context for chatbot
  const chatContext = claim ? {
    page: 'claim_detail',
    claim_id: claim.claim_id,
    claim_data: {
      status: claim.current_status,
      total_cost: currentTotal,
      damages: damages.map(d => ({
        part: d.damage_part,
        severity: d.severity,
        cost: parseFloat(d.estimated_total_cost || 0)
      }))
    }
  } : null;

  return (
    <Layout currentContext={chatContext}>
      {/* Back Navigation */}
      <button
        onClick={handleBack}
        className="flex items-center gap-2 text-primary-600 hover:text-primary-700 mb-6 transition-colors"
      >
        <ArrowLeft className="h-5 w-5" />
        Back to Home
      </button>

      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-lg bg-primary-100">
              <FileText className="h-8 w-8 text-primary-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Claim #{claimId}</h1>
              <p className="text-gray-600">Status: {getStatusLabel(claim.current_status)}</p>
            </div>
          </div>
          <Badge variant={getStatusVariant(claim.current_status)}>
            {getStatusLabel(claim.current_status)}
          </Badge>
        </div>
      </div>

      {/* Human Review Notice */}
      {isHumanReviewPending && (
        <div className="mb-6 p-6 bg-yellow-50 border-l-4 border-yellow-400 rounded-lg">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-6 w-6 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-lg font-semibold text-yellow-900 mb-2">
                {damageCount === 0 ? 'Claim Submitted for Human Review' : 'Human Review Required'}
              </h3>
              <p className="text-yellow-800 mb-2">
                {damageCount === 0 ? (
                  'No damage was detected in the uploaded images. A human adjuster will review your claim and assess the damage.'
                ) : appealDate ? (
                  <>
                    Human Review Required because you appealed the AI estimate on{' '}
                    {appealDate.toLocaleDateString('en-US', {
                      month: 'long',
                      day: 'numeric',
                      year: 'numeric'
                    })}.
                  </>
                ) : (
                  'Our AI has completed the initial analysis, but the confidence level is below our threshold. A human adjuster will review your claim to ensure accuracy.'
                )}
              </p>
              <p className="text-sm text-yellow-700">
                You will be notified via email once the review is complete. This typically takes 1-2 business days.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Payment Processing Notice */}
      {isPaymentProcessing && (
        <div className="mb-6 p-6 bg-green-50 border-l-4 border-green-400 rounded-lg">
          <div className="flex items-start gap-3">
            <CheckCircle className="h-6 w-6 text-green-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-lg font-semibold text-green-900 mb-2">
                You Accepted Estimate - Payment Processing
              </h3>
              <p className="text-green-800 mb-2">
                {acceptanceDate ? (
                  <>
                    You accepted this estimate on {acceptanceDate.toLocaleDateString('en-US', {
                      month: 'long',
                      day: 'numeric',
                      year: 'numeric'
                    })} at {acceptanceDate.toLocaleTimeString('en-US', {
                      hour: 'numeric',
                      minute: '2-digit'
                    })}. Your payment is being processed.
                  </>
                ) : (
                  'You accepted this estimate. Your payment is being processed.'
                )}
              </p>
              <p className="text-sm text-green-700 mb-2">
                <strong>Payment Timeline:</strong> Payment is usually issued within 5-10 business days of acceptance.
              </p>
              <p className="text-sm text-green-700">
                <strong>Delivery:</strong> Please note that there may be a delay in receiving the funds as payments are sent through the US Postal Service. Allow 5-7 business days for mail delivery.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Traditional Processing Notice */}
      {isRoutedToTraditional && (
        <div className="mb-6 p-6 bg-orange-50 border-l-4 border-orange-400 rounded-lg">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-6 w-6 text-orange-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-lg font-semibold text-orange-900 mb-2">
                Claim Routed to Traditional Processing
              </h3>
              <p className="text-orange-800 mb-2">
                Your claim has been routed to our traditional claim processing. A dedicated adjuster will handle your claim and may contact you to schedule a physical inspection if needed.
              </p>
              <p className="text-sm text-orange-700 mb-2">
                <strong>Processing Timeline:</strong> Traditional claims typically take 5-10 business days to complete. You will be notified via email once your claim has been assessed.
              </p>
              <p className="text-sm text-orange-700">
                <strong>What to expect:</strong> An adjuster may reach out to schedule an in-person inspection of your vehicle. You will receive a detailed estimate once the assessment is complete.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Adjustor Review Complete Notice */}
      {hasAdjustorReview && claim.current_status === 'customer_decision_pending' && (
        <div className={`mb-6 p-6 border-l-4 rounded-lg ${
          appealAccepted ? 'bg-blue-50 border-blue-400' : 'bg-yellow-50 border-yellow-400'
        }`}>
          <div className="flex items-start gap-3">
            {appealAccepted ? (
              <CheckCircle className="h-6 w-6 text-blue-600 flex-shrink-0 mt-0.5" />
            ) : (
              <AlertTriangle className="h-6 w-6 text-yellow-600 flex-shrink-0 mt-0.5" />
            )}
            <div className="flex-1">
              <h3 className={`text-lg font-semibold mb-2 ${
                appealAccepted ? 'text-blue-900' : 'text-yellow-900'
              }`}>
                {appealAccepted ? 'Appeal Accepted - Estimate Revised' : 'Appeal Denied - Original Estimate Confirmed'}
              </h3>
              <div className={`mb-3 p-3 rounded ${
                appealAccepted ? 'bg-blue-100' : 'bg-yellow-100'
              }`}>
                <p className={`text-sm font-medium mb-1 ${
                  appealAccepted ? 'text-blue-800' : 'text-yellow-800'
                }`}>
                  Adjustor's Note:
                </p>
                <p className={`text-sm ${
                  appealAccepted ? 'text-blue-900' : 'text-yellow-900'
                }`}>
                  {adjustorNote}
                </p>
              </div>

              {appealAccepted && (
                <p className="text-sm text-blue-800 mb-2">
                  <strong>Revised Estimate:</strong> ${currentTotal.toFixed(2)}{' '}
                  (Changed from AI estimate of ${aiTotal.toFixed(2)})
                </p>
              )}

              {appealDenied && (
                <p className="text-sm text-yellow-800 mb-2">
                  <strong>Original Estimate Confirmed:</strong> ${currentTotal.toFixed(2)}
                </p>
              )}

              <div className="mt-3 p-3 bg-white border border-gray-200 rounded">
                <p className="text-sm text-gray-700">
                  <strong>💡 Reminder:</strong> You can appeal this decision if the actual repair cost
                  exceeds this estimate. After repairs are completed, if the final invoice shows a higher
                  amount, you have the right to submit a supplemental claim with supporting documentation
                  (itemized invoice from the repair shop).
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* AI Damage Assessment */}
      {damageCount > 0 && (
        <Card className="mb-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">AI Damage Assessment</h2>

          {/* Vehicle Information */}
          {vehicle && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
              <div className="flex items-center gap-2 text-gray-700">
                <span className="font-semibold text-gray-900">Vehicle:</span>
                <span className="text-base">
                  {vehicle.year} {vehicle.make} {vehicle.model}
                  {vehicle.color && <span className="text-gray-600"> ({vehicle.color})</span>}
                </span>
              </div>
            </div>
          )}

          {/* Summary */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
            <div className="grid grid-cols-2 gap-6">
              <div>
                <p className="text-sm text-gray-600 mb-1">Total Estimated Cost</p>
                <p className="text-3xl font-bold text-primary-600">
                  ${Number(totalCost).toFixed(2)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Damages Detected</p>
                <p className="text-3xl font-bold text-gray-900">
                  {damageCount} {damageCount === 1 ? 'damage' : 'damages'} across {Object.keys(damagesByImage).length} {Object.keys(damagesByImage).length === 1 ? 'image' : 'images'}
                </p>
              </div>
            </div>
          </div>

        {/* Damages Grouped by Image */}
        {damages.length > 0 ? (
          <div className="space-y-8 mb-6">
            {Object.entries(damagesByImage).map(([imageId, imageDamages]) => (
              <div key={imageId} className="border-t-4 border-primary-200 pt-6 first:border-t-0 first:pt-0">
                {/* Image Header */}
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  Image: {imageId}
                </h3>

                {/* Annotated Image with Bounding Boxes */}
                <div className="mb-4 rounded-lg overflow-hidden border border-gray-300 bg-gray-50">
                  <img
                    src={getAnnotatedImageUrl(imageId)}
                    alt={`Damage analysis for ${imageId}`}
                    className="w-1/2 mx-auto"
                    onError={(e) => {
                      console.error('Failed to load annotated image:', imageId);
                      e.target.style.display = 'none';
                      e.target.parentElement.innerHTML = '<div class="p-8 text-center text-gray-500"><p>Annotated image not available</p></div>';
                    }}
                  />
                </div>

                {/* Damages from this image */}
                <div className="mb-3">
                  <h4 className="text-lg font-semibold text-gray-700 mb-1">
                    Damages detected in this image ({imageDamages.length}):
                  </h4>
                  {claim.state_avg_labor_cost && claim.labor_rate_state && (
                    <p className="text-sm text-gray-600 italic">
                      Note: Average labor cost of ${Number(claim.state_avg_labor_cost).toFixed(2)}/hour used for the state of {claim.labor_rate_state}
                    </p>
                  )}
                </div>

                <div className="space-y-3">
                  {imageDamages.map((damage) => (
                    <div key={damage.damage_id} className="border border-gray-200 rounded-lg p-4 bg-white">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex-1">
                          <h5 className="text-lg font-semibold text-gray-900">
                            {damage.damage_part?.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </h5>
                          {damage.reviewed_by_adjustor && (
                            <div className="mt-1 inline-flex items-center text-xs text-green-600">
                              <CheckCircle className="h-3 w-3 mr-1" />
                              Reviewed by adjustor
                            </div>
                          )}
                        </div>
                        <span className="text-xl font-bold text-primary-600">
                          ${Number(damage.estimated_total_cost || 0).toFixed(2)}
                        </span>
                      </div>

                      {/* Damage assessment summary */}
                      {damage.damage_summary && (
                        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                          <p className="text-sm text-gray-700 leading-relaxed">
                            {damage.damage_summary}
                          </p>
                        </div>
                      )}

                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Severity:</span>
                          <span className="ml-2 font-medium">
                            {(Number(damage.severity || 0) * 100).toFixed(0)}%
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">Labor Hours:</span>
                          <span className="ml-2 font-medium">{damage.labor_hours}h</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Labor Cost:</span>
                          <span className="ml-2 font-medium">
                            ${Number((damage.labor_hours || 0) * (claim.state_avg_labor_cost || 0)).toFixed(2)}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-600">Parts Cost:</span>
                          <span className="ml-2 font-medium">
                            ${Number(damage.estimated_parts_cost || 0).toFixed(2)}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <AlertCircle className="h-12 w-12 mx-auto mb-2" />
            <p>No damages detected</p>
          </div>
        )}

        {/* Action Buttons */}
        {damages.length > 0 && !isHumanReviewPending && !isPaymentProcessing && !isRoutedToTraditional && (
          <div className="flex gap-4 pt-6 border-t border-gray-200">
            <Button
              onClick={handleAcceptEstimate}
              className="flex-1"
            >
              <CheckCircle className="h-5 w-5 mr-2 inline" />
              Accept Estimate
            </Button>
            <Button
              onClick={handleAppealEstimate}
              variant="secondary"
              className="flex-1"
            >
              <AlertCircle className="h-5 w-5 mr-2 inline" />
              Appeal Estimate
            </Button>
          </div>
        )}
        </Card>
      )}

      {/* Claim Details Card - NEW */}
      <ClaimDetailsCard
        claim={claim}
        vehicle={vehicle}
        policy={policy}
      />

      {/* Info Box */}
      {!isHumanReviewPending && !isPaymentProcessing && !isRoutedToTraditional && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            <strong>What happens next?</strong> Review the AI damage assessment above. You can either
            accept the estimate to proceed with payment, or appeal if you believe the estimate needs
            human review.
          </p>
        </div>
      )}

      {/* Accept Estimate Confirmation Modal */}
      <Modal
        isOpen={showAcceptModal}
        onClose={handleCancelAccept}
        title="Accept Estimate"
        size="lg"
      >
        <div className="space-y-6">
          {/* Estimate Summary */}
          <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
            <p className="text-sm text-gray-700 mb-2">You are accepting an estimate of:</p>
            <p className="text-3xl font-bold text-primary-600">
              ${Number(totalCost).toFixed(2)}
            </p>
          </div>

          {/* Important Information */}
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <Info className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-gray-900 mb-1">Important Information</p>
                <p className="text-sm text-gray-700">
                  Please review the following before accepting:
                </p>
              </div>
            </div>

            <div className="space-y-3 ml-8">
              <div className="flex items-start gap-2">
                <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-gray-700">
                  <strong>Payment Processing:</strong> Payment will be issued to you within 5-10 business days after acceptance.
                </p>
              </div>

              <div className="flex items-start gap-2">
                <AlertCircle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-gray-700">
                  <strong>Claim Data:</strong> Once accepted, you will not be able to change the claim details or uploaded images.
                </p>
              </div>

              <div className="flex items-start gap-2">
                <Info className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-gray-700">
                  <strong>Additional Loss Funds:</strong> If the actual cost of repair exceeds this AI-estimated amount, you will have the ability to appeal for additional loss funds.
                </p>
              </div>
            </div>
          </div>

          {/* Confirmation Text */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <p className="text-sm text-gray-700 text-center">
              By clicking "Confirm & Accept", you acknowledge that you have read and understood the above information.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4">
            <Button
              onClick={handleCancelAccept}
              variant="secondary"
              className="flex-1"
              disabled={accepting}
            >
              Cancel
            </Button>
            <Button
              onClick={handleConfirmAccept}
              className="flex-1"
              disabled={accepting}
            >
              {accepting ? (
                <>
                  <Spinner size="sm" className="mr-2" />
                  Processing...
                </>
              ) : (
                <>
                  <CheckCircle className="h-5 w-5 mr-2 inline" />
                  Confirm & Accept
                </>
              )}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Appeal Estimate Modal */}
      <Modal
        isOpen={showAppealModal}
        onClose={handleCancelAppeal}
        title={isSecondAppeal ? "Appeal to Traditional Processing" : "Appeal Estimate"}
        size="lg"
      >
        <div className="space-y-6">
          {/* Second Appeal Warning */}
          {isSecondAppeal ? (
            <>
              {/* Warning Banner */}
              <div className="bg-yellow-50 border-l-4 border-yellow-400 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <AlertCircle className="h-6 w-6 text-yellow-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-yellow-900 mb-2">
                      Traditional Processing May Take Longer
                    </h4>
                    <p className="text-sm text-yellow-800">
                      This is your second appeal. Your claim will be sent to our traditional claim process,
                      which may take longer to complete. A dedicated adjuster will handle your claim.
                    </p>
                  </div>
                </div>
              </div>

              {/* Important Information */}
              <div className="space-y-3">
                <div className="flex items-start gap-2">
                  <Info className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-gray-700">
                    <strong>You can still accept the current estimate:</strong> If you accept now, you'll
                    receive payment within 5-10 business days.
                  </p>
                </div>

                <div className="flex items-start gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-gray-700">
                    <strong>Additional funds available:</strong> If the actual cost of repair exceeds this
                    estimate, you can appeal for additional loss funds through our extra fund appeal process.
                  </p>
                </div>
              </div>

              {/* Reason (optional for second appeal) */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Reason for Appeal (Optional)
                </label>
                <Textarea
                  value={appealReason}
                  onChange={(e) => setAppealReason(e.target.value)}
                  placeholder="e.g., I need a physical inspection by an adjuster..."
                  rows={4}
                  maxLength={500}
                />
                <p className="text-xs text-gray-500 mt-1">
                  {appealReason.length}/500 characters
                </p>
              </div>
            </>
          ) : (
            <>
              {/* First Appeal - Reason Required */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-800">
                  Your appeal will be reviewed by a human adjuster who will assess your claim
                  and provide a revised estimate within 1-2 business days.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Reason for Appeal <span className="text-red-600">*</span>
                </label>
                <Textarea
                  value={appealReason}
                  onChange={(e) => setAppealReason(e.target.value)}
                  placeholder="e.g., Estimate seems too low, missing damage, incorrect parts identified..."
                  rows={5}
                  maxLength={500}
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  {appealReason.length}/500 characters
                </p>
              </div>
            </>
          )}

          {/* Action Buttons */}
          <div className="flex gap-4">
            <Button
              onClick={handleCancelAppeal}
              variant="secondary"
              className="flex-1"
              disabled={appealing}
            >
              Cancel
            </Button>
            <Button
              onClick={handleConfirmAppeal}
              className="flex-1"
              disabled={appealing}
            >
              {appealing ? (
                <>
                  <Spinner size="sm" className="mr-2" />
                  Processing...
                </>
              ) : (
                <>
                  <AlertCircle className="h-5 w-5 mr-2 inline" />
                  {isSecondAppeal ? 'Route to Traditional' : 'Submit Appeal'}
                </>
              )}
            </Button>
          </div>
        </div>
      </Modal>
    </Layout>
  );
};

export default ClaimDetailPage;
