/**
 * Claim Analysis Page - Auto-submit claim and show AI analysis progress (Step 3 of 3)
 * This page automatically submits the claim and polls for analysis completion.
 * User is automatically redirected to Claim Detail Page when analysis is complete.
 */
import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { CheckCircle, Loader, Clock, AlertCircle, ImageOff, RefreshCw } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { submitClaim, fetchClaimDetail, generateEstimate, requestHumanReview } from '../api/customers';
import Layout from '../components/layout/Layout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import ProgressBar from '../components/common/ProgressBar';
import Spinner from '../components/common/Spinner';

const ClaimAnalysisPage = () => {
  const { claimId } = useParams();
  const navigate = useNavigate();
  const { customerId } = useAuth();

  const [error, setError] = useState('');
  const [noDamagesDetected, setNoDamagesDetected] = useState(false);
  const [submittingHumanReview, setSubmittingHumanReview] = useState(false);
  const [analysisSteps, setAnalysisSteps] = useState([
    { id: 1, label: 'Images uploaded', status: 'completed' },
    { id: 2, label: 'Running damage detection', status: 'in_progress' },
    { id: 3, label: 'Calculating repair costs', status: 'pending' },
    { id: 4, label: 'Generating estimate report', status: 'pending' },
  ]);

  const submissionStarted = useRef(false);

  useEffect(() => {
    if (customerId && claimId && !submissionStarted.current) {
      submissionStarted.current = true;
      submitAndAnalyze();
    }
  }, [customerId, claimId]);

  const submitAndAnalyze = async () => {
    try {
      // 1. First, get claim details to check if damages exist
      console.log('Fetching claim details to check for damages...');
      const claimResponse = await fetchClaimDetail(customerId, claimId);
      const claim = claimResponse.data;

      console.log('Claim status:', claim.current_status);
      console.log('Claim data:', claim);

      // Get unique image IDs from damages
      // Each damage has an image_id field (this is the filename)
      let imageIds = [];
      if (claim.damage_assessment?.damages) {
        // Extract unique image IDs from all damages
        // Filter out any null/undefined values
        const ids = claim.damage_assessment.damages
          .map(d => d.image_id)
          .filter(id => id != null && id !== '');
        imageIds = Array.from(new Set(ids));
      }

      console.log('Extracted image IDs from damages:', imageIds);

      if (imageIds.length === 0) {
        // No damages detected - show user choice screen
        // DO NOT submit claim to FNOL yet - keep it in draft so user can upload more images
        console.log('No damages detected in uploaded images - keeping claim in draft state');
        setNoDamagesDetected(true);
        updateStepStatus(2, 'completed');
        return;
      }

      // 2. Damages found! Now submit the claim (draft -> FNOL)
      console.log('Damages found, submitting claim to FNOL...');
      await submitClaim(customerId, claimId);
      console.log('Claim submitted to FNOL');

      console.log('Generating estimate with image IDs:', imageIds);

      // 3. Trigger AI damage estimate generation
      updateStepStatus(2, 'completed'); // Damage detection already done in Phase 4
      updateStepStatus(3, 'in_progress');

      try {
        const estimateResponse = await generateEstimate(claimId, {
          claim_id: parseInt(claimId), // Include claim_id in body (API requirement)
          image_ids: imageIds,
          state: 'CA' // Default state for labor rates
        });
        console.log('Estimate generation response:', estimateResponse);
      } catch (estimateError) {
        console.error('Failed to generate estimate:', estimateError);
        console.error('Error response:', estimateError.response?.data);
        setError(`Failed to generate estimate: ${estimateError.response?.data?.detail || estimateError.message}`);
        return;
      }

      console.log('Estimate generation completed successfully');

      // 4. Start polling for estimate completion
      let pollCount = 0;
      const maxPolls = 30; // 60 seconds max (30 * 2s)

      const pollInterval = setInterval(async () => {
        try {
          pollCount++;
          const response = await fetchClaimDetail(customerId, claimId);
          const claim = response.data;

          console.log(`[Poll ${pollCount}/${maxPolls}] Current status:`, claim.current_status);
          console.log('[Poll] Active estimate ID:', claim.active_estimate_id);

          // Update progress steps based on claim status
          if (claim.current_status === 'FNOL' || claim.current_status === 'image_uploaded') {
            // Still processing
            console.log('[Poll] Still in FNOL/image_uploaded state, waiting...');
          } else if (claim.current_status === 'loss_estimated_ai' || claim.current_status === 'customer_decision_pending') {
            // Estimate complete with high confidence!
            console.log('[Poll] Estimate complete! Status:', claim.current_status);
            updateStepStatus(3, 'completed');
            updateStepStatus(4, 'completed');

            clearInterval(pollInterval);

            console.log('Analysis complete! Redirecting to claim detail page...');

            // Wait a moment to show completion state
            setTimeout(() => {
              navigate(`/claims/${claimId}`);
            }, 1000);
          } else if (claim.current_status === 'human_review_pending') {
            // Low confidence - routed to human review
            console.log('[Poll] Low confidence detected, routed to human review');
            updateStepStatus(3, 'completed');
            updateStepStatus(4, 'completed');

            clearInterval(pollInterval);

            console.log('Routed to human review. Redirecting to claim detail page...');

            // Wait a moment to show completion state
            setTimeout(() => {
              navigate(`/claims/${claimId}`);
            }, 1000);
          } else if (claim.current_status === 'error') {
            console.error('[Poll] Claim status is error');
            clearInterval(pollInterval);
            setError('Analysis failed. Please try again or contact support.');
          } else {
            console.log('[Poll] Unexpected status:', claim.current_status);
          }

          // Timeout after max polls
          if (pollCount >= maxPolls) {
            console.error('[Poll] Timed out after', maxPolls, 'polls');
            clearInterval(pollInterval);
            setError('Analysis is taking longer than expected. Please refresh the page or contact support.');
          }
        } catch (pollError) {
          console.error('Polling error:', pollError);
          // Continue polling - don't break on network hiccups
        }
      }, 2000); // Poll every 2 seconds

      // Cleanup interval on unmount
      return () => clearInterval(pollInterval);
    } catch (err) {
      console.error('Failed to submit and analyze claim:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to submit claim. Please try again.');
    }
  };

  const updateStepStatus = (stepId, status) => {
    setAnalysisSteps((prev) =>
      prev.map((step) => (step.id === stepId ? { ...step, status } : step))
    );
  };

  const handleRetry = () => {
    setError('');
    setAnalysisSteps([
      { id: 1, label: 'Images uploaded', status: 'completed' },
      { id: 2, label: 'Running damage detection', status: 'in_progress' },
      { id: 3, label: 'Calculating repair costs', status: 'pending' },
      { id: 4, label: 'Generating estimate report', status: 'pending' },
    ]);
    submitAndAnalyze();
  };

  const handleTryNewImages = () => {
    // Navigate back to image upload page
    navigate(`/claims/${claimId}/upload`);
  };

  const handleSubmitForHumanReview = async () => {
    try {
      setSubmittingHumanReview(true);
      console.log('Submitting claim for human review...');

      await requestHumanReview(customerId, claimId);

      console.log('Claim submitted for human review successfully');

      // Wait a moment to show success message
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Navigate to claim detail page
      navigate(`/claims/${claimId}`);
    } catch (err) {
      console.error('Failed to submit for human review:', err);
      setError(err.response?.data?.detail || 'Failed to submit claim for human review. Please try again.');
      setSubmittingHumanReview(false);
    }
  };

  const getStepIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'in_progress':
        return <Loader className="w-5 h-5 text-primary-600 animate-spin" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-gray-400" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  return (
    <Layout>
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-3">
          <div className="p-3 rounded-lg bg-primary-100">
            <Loader className="h-8 w-8 text-primary-600 animate-spin" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analyzing Your Claim...</h1>
            <p className="text-gray-600">Claim #{claimId}</p>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <ProgressBar current={3} total={3} steps={['Loss Details', 'Upload Photos', 'Analysis & Review']} />

      {/* No Damages Detected - User Choice */}
      {noDamagesDetected && !submittingHumanReview && (
        <Card className="max-w-2xl mx-auto text-center">
          {/* Icon */}
          <div className="mb-6">
            <div className="w-20 h-20 mx-auto rounded-full bg-yellow-100 flex items-center justify-center">
              <ImageOff className="w-10 h-10 text-yellow-600" />
            </div>
          </div>

          {/* Main Message */}
          <h2 className="text-2xl font-semibold text-gray-900 mb-3">
            No Damage Detected
          </h2>
          <p className="text-gray-600 mb-2">
            Our AI was unable to detect any damage in the uploaded images.
          </p>
          <p className="text-sm text-gray-500 mb-8">
            This could happen if the damage is not visible in the photos, or if better quality images are needed.
          </p>

          {/* Options */}
          <div className="space-y-4">
            <Button
              onClick={handleTryNewImages}
              className="w-full"
              size="lg"
            >
              <RefreshCw className="w-5 h-5 mr-2 inline" />
              Try Uploading New Images
            </Button>

            <Button
              onClick={handleSubmitForHumanReview}
              variant="secondary"
              className="w-full"
              size="lg"
            >
              <AlertCircle className="w-5 h-5 mr-2 inline" />
              Submit for Human Review
            </Button>
          </div>

          {/* Info Box */}
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg text-left">
            <p className="text-sm text-blue-800">
              <strong>What should I do?</strong>
              <br />
              • If you have better photos showing the damage, try uploading new images
              <br />
              • If you prefer a human adjuster to assess the damage, submit for human review
            </p>
          </div>
        </Card>
      )}

      {/* Submitting for Human Review */}
      {submittingHumanReview && (
        <Card className="max-w-2xl mx-auto text-center">
          <div className="mb-6">
            <Spinner size="xl" className="mx-auto" />
          </div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-3">
            Submitting Claim for Human Review
          </h2>
          <p className="text-gray-600">
            Your claim is being routed to a human adjuster for assessment...
          </p>
        </Card>
      )}

      {/* Error Message */}
      {error && !noDamagesDetected && (
        <div className="mb-6 p-4 bg-error-light border border-error-300 text-error-dark rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="font-semibold mb-2">Analysis Failed</p>
            <p className="text-sm mb-3">{error}</p>
            <Button variant="secondary" size="sm" onClick={handleRetry}>
              Try Again
            </Button>
          </div>
        </div>
      )}

      {/* Analysis Card */}
      {!error && !noDamagesDetected && !submittingHumanReview && (
        <Card className="max-w-2xl mx-auto text-center">
          {/* Spinner */}
          <div className="mb-6">
            <Spinner size="xl" className="mx-auto" />
          </div>

          {/* Main Message */}
          <h2 className="text-2xl font-semibold text-gray-900 mb-3">
            Processing Your Claim
          </h2>
          <p className="text-gray-600 mb-2">
            Our AI is analyzing your damage photos and generating a detailed estimate.
          </p>
          <p className="text-sm text-gray-500 mb-8">
            This typically takes 10-30 seconds...
          </p>

          {/* Progress Steps */}
          <div className="bg-gray-50 rounded-lg p-6 text-left">
            <h3 className="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide">
              Analysis Progress
            </h3>
            <div className="space-y-4">
              {analysisSteps.map((step) => (
                <div key={step.id} className="flex items-center gap-3">
                  {getStepIcon(step.status)}
                  <span
                    className={`text-base ${
                      step.status === 'completed'
                        ? 'text-green-700 font-medium'
                        : step.status === 'in_progress'
                        ? 'text-primary-700 font-medium'
                        : 'text-gray-500'
                    }`}
                  >
                    {step.label}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Info Box */}
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg text-left">
            <p className="text-sm text-blue-800">
              <strong>Please wait...</strong> You will be automatically redirected to your claim details
              once the analysis is complete. Do not close this page.
            </p>
          </div>
        </Card>
      )}
    </Layout>
  );
};

export default ClaimAnalysisPage;
