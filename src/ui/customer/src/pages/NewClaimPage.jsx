/**
 * New Claim Page - Multi-step claim filing workflow
 * Step 1: Loss event details form
 * Step 2: Image upload (future phase)
 */
import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, useParams } from 'react-router-dom';
import { ArrowLeft, FileText, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { fetchPolicy, createClaim, fetchClaimDetail } from '../api/customers';
import Layout from '../components/layout/Layout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import Textarea from '../components/common/Textarea';
import RadioGroup from '../components/common/RadioGroup';
import ProgressBar from '../components/common/ProgressBar';
import Spinner from '../components/common/Spinner';
import FileUpload from '../components/common/FileUpload';
import VehicleSelectionCard from '../components/claims/VehicleSelectionCard';

const NewClaimPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { claimId } = useParams(); // For editing existing claims
  const { customerId } = useAuth();

  const policyNumber = searchParams.get('policy');
  const [isEditMode, setIsEditMode] = useState(false);

  const [policy, setPolicy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Vehicle selection state
  const [selectedVehicle, setSelectedVehicle] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    lossDescription: '',
    lossDate: '',
    isDrivable: '',
    hasPhotos: '',
    hasPoliceReport: '',
  });

  const [formErrors, setFormErrors] = useState({});

  useEffect(() => {
    if (customerId) {
      if (claimId) {
        // Edit mode: load existing claim
        loadExistingClaim();
      } else if (policyNumber) {
        // Create mode: load policy
        loadPolicy();
      }
    }
  }, [customerId, policyNumber, claimId]);

  const loadPolicy = async () => {
    try {
      setLoading(true);
      const response = await fetchPolicy(customerId, policyNumber);
      setPolicy(response.data);
    } catch (err) {
      console.error('Failed to load policy:', err);
      setError('Failed to load policy information. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const loadExistingClaim = async () => {
    try {
      setLoading(true);
      setIsEditMode(true);

      // Load claim data
      const claimResponse = await fetchClaimDetail(customerId, claimId);
      const claim = claimResponse.data;

      // Load policy for the claim
      const policyResponse = await fetchPolicy(customerId, claim.policy_number);
      setPolicy(policyResponse.data);

      // Find and set the vehicle
      const vehicle = policyResponse.data.vehicles.find(v => v.vin === claim.vin);
      if (vehicle) {
        setSelectedVehicle(vehicle);
      }

      // Populate form with existing data
      setFormData({
        lossDescription: claim.incident_description || '',  // Load from backend
        lossDate: claim.date_of_damage,
        isDrivable: claim.is_drivable ? 'yes' : 'no',
        hasPhotos: 'yes', // Assume yes since they're editing
        hasPoliceReport: 'no', // Not stored in backend, default to no
      });

    } catch (err) {
      console.error('Failed to load claim:', err);
      setError('Failed to load claim information. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field when user starts typing
    if (formErrors[field]) {
      setFormErrors((prev) => ({ ...prev, [field]: '' }));
    }
  };

  const handleVehicleSelect = (vehicle) => {
    setSelectedVehicle(vehicle);
  };

  const validateForm = () => {
    console.log('*** validateForm CALLED ***');
    console.log('selectedVehicle:', selectedVehicle);
    console.log('formData:', formData);

    const errors = {};

    if (!selectedVehicle) {
      console.log('ERROR: No vehicle selected');
      setError('Please select a vehicle to continue');
      return false;
    }

    if (!formData.lossDescription.trim()) {
      errors.lossDescription = 'Please describe what happened';
    }

    if (!formData.lossDate) {
      errors.lossDate = 'Please select the date of damage';
    } else {
      const selectedDate = new Date(formData.lossDate);
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      if (selectedDate > today) {
        errors.lossDate = 'Date cannot be in the future';
      }
    }

    if (!formData.isDrivable) {
      errors.isDrivable = 'Please indicate if your vehicle is drivable';
    }

    if (!formData.hasPhotos) {
      errors.hasPhotos = 'Please indicate if you can provide damage photos';
    }

    if (!formData.hasPoliceReport) {
      errors.hasPoliceReport = 'Please indicate if you filed a police report';
    }

    console.log('Validation errors:', errors);
    console.log('Validation result:', Object.keys(errors).length === 0);

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleCancel = () => {
    const targetPolicy = policy?.policy_number || policyNumber;
    if (targetPolicy) {
      navigate(`/policy/${targetPolicy}`);
    } else {
      navigate('/');
    }
  };

  const handleSaveDraft = async () => {
    console.log('*** handleSaveDraft CALLED ***');

    if (!validateForm()) {
      console.log('*** Validation failed for Save Draft ***');
      return;
    }

    try {
      setSubmitting(true);
      setError('');

      // Only create claim if not in edit mode (claim doesn't exist yet)
      if (!isEditMode) {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const fnolDate = `${year}-${month}-${day}`;

        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        const fnolTime = `${hours}:${minutes}:${seconds}`;

        const claimData = {
          vin: selectedVehicle.vin,
          policy_number: policyNumber,
          fnol_date: fnolDate,
          fnol_time: fnolTime,
          date_of_damage: formData.lossDate,
          is_drivable: formData.isDrivable === 'yes',
          incident_description: formData.lossDescription,  // Include description
        };

        console.log('Creating draft claim:', claimData);
        await createClaim(customerId, claimData);
      }

      // Navigate back to policy page
      const targetPolicy = policy?.policy_number || policyNumber;
      console.log('Draft saved, navigating to:', `/policy/${targetPolicy}`);
      alert('Draft saved successfully! You can continue later from your policy page.');
      navigate(`/policy/${targetPolicy}`);

    } catch (err) {
      console.error('Failed to save draft:', err);
      setError(err.response?.data?.detail || 'Failed to save draft. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleContinue = async () => {
    console.log('*** handleContinue CALLED ***');

    if (!validateForm()) {
      console.log('*** Validation failed ***');
      return;
    }

    console.log('*** Validation passed ***');

    try {
      setSubmitting(true);
      setError('');

      let currentClaimId = claimId;
      let currentPolicyNumber = policy?.policy_number || policyNumber;

      console.log('handleContinue - isEditMode:', isEditMode);
      console.log('handleContinue - claimId:', currentClaimId);
      console.log('handleContinue - policyNumber:', currentPolicyNumber);

      // Only create new claim if not in edit mode
      if (!isEditMode) {
        // Get today's date and time (using local timezone to avoid future date issues)
        const now = new Date();

        // Format date as YYYY-MM-DD in local timezone
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const fnolDate = `${year}-${month}-${day}`;

        // Format time as HH:MM:SS
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        const fnolTime = `${hours}:${minutes}:${seconds}`;

        // Create draft claim with selected vehicle
        const claimData = {
          vin: selectedVehicle.vin,
          policy_number: policyNumber,
          fnol_date: fnolDate,
          fnol_time: fnolTime,
          date_of_damage: formData.lossDate,
          is_drivable: formData.isDrivable === 'yes',
          incident_description: formData.lossDescription,  // Include description
        };

        console.log('Creating claim with data:', claimData);

        const response = await createClaim(customerId, claimData);
        console.log('Claim created successfully:', response.data);
        const claim = response.data;
        currentClaimId = claim.claim_id;
        currentPolicyNumber = claim.policy_number;
      }

      // If customer cannot provide photos, submit claim immediately for traditional review
      if (formData.hasPhotos === 'no') {
        await submitClaim(customerId, currentClaimId);
        alert(
          `Claim #${currentClaimId} has been submitted for traditional review.\n\n` +
          `An adjustor will contact you within 24-48 hours to schedule an inspection.`
        );
        navigate(`/policy/${currentPolicyNumber}`);
      } else {
        // Navigate to Step 2 (Image Upload)
        // Claim is saved in draft state, ready for image upload
        console.log('Navigating to upload page:', `/claims/${currentClaimId}/upload`);
        navigate(`/claims/${currentClaimId}/upload`);
      }

      console.log('handleContinue completed successfully');

    } catch (err) {
      console.error('Failed to create claim:', err);

      // Handle different error response formats
      let errorMessage = 'Failed to create claim. Please try again.';

      if (err.response?.data?.detail) {
        // FastAPI validation errors can be string or array
        const detail = err.response.data.detail;
        if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (Array.isArray(detail)) {
          // Format validation errors
          errorMessage = detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join(', ');
        } else if (typeof detail === 'object') {
          errorMessage = JSON.stringify(detail);
        }
      } else if (err.message) {
        errorMessage = err.message;
      }

      setError(errorMessage);
    } finally {
      setSubmitting(false);
    }
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

  if (!policy) {
    return (
      <Layout>
        <div className="text-center py-12">
          <p className="text-gray-600 mb-4">Policy not found</p>
          <Button onClick={() => navigate('/')}>Back to Home</Button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      {/* Back Navigation */}
      <button
        onClick={handleCancel}
        className="flex items-center gap-2 text-primary-600 hover:text-primary-700 mb-6 transition-colors"
      >
        <ArrowLeft className="h-5 w-5" />
        Back to Policy
      </button>

      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-3">
          <div className="p-3 rounded-lg bg-primary-100">
            <FileText className="h-8 w-8 text-primary-600" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {isEditMode ? `Edit Claim #${claimId}` : 'File New Claim'}
            </h1>
            <p className="text-gray-600">Policy: {policy?.policy_number || policyNumber}</p>
          </div>
        </div>
      </div>

      {/* Progress Bar - Dynamic based on vehicle selection and photo availability */}
      <ProgressBar
        current={selectedVehicle ? 2 : 1}
        total={formData.hasPhotos === 'yes' ? 5 : 4}
        steps={
          formData.hasPhotos === 'yes'
            ? ['Start Claim', 'Select Vehicle', 'Damage Details', 'Upload Images', 'Submit']
            : ['Start Claim', 'Select Vehicle', 'Damage Details', 'Submit']
        }
      />

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-error-light border border-error-300 text-error-dark rounded-lg flex items-start gap-3">
          <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
          <p>{error}</p>
        </div>
      )}

      {/* Vehicle Selection Card */}
      <Card className="max-w-4xl mx-auto mb-8">
        <h2 className="text-2xl font-semibold text-gray-900 mb-2">
          Select Vehicle
        </h2>
        <p className="text-gray-600 mb-6">
          Which vehicle was involved in the incident?
        </p>

        {policy.vehicles && policy.vehicles.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {policy.vehicles.map((vehicle) => (
              <VehicleSelectionCard
                key={vehicle.vin}
                vehicle={vehicle}
                selected={selectedVehicle?.vin === vehicle.vin}
                onClick={() => handleVehicleSelect(vehicle)}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-600">
            No vehicles found on this policy. Please contact support.
          </div>
        )}
      </Card>

      {/* Form Card - Only show after vehicle is selected */}
      {selectedVehicle && (
        <Card className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            Damage Details
          </h2>

          {/* Selected Vehicle Information */}
          <div className="mb-6 p-4 bg-primary-50 border border-primary-200 rounded-lg">
            <p className="text-sm font-medium text-gray-700 mb-1">Filing claim for:</p>
            <p className="text-lg font-semibold text-gray-900">
              {selectedVehicle.year} {selectedVehicle.make} {selectedVehicle.model}
            </p>
            <p className="text-sm text-gray-600">VIN: {selectedVehicle.vin}</p>
          </div>

        {/* Loss Description */}
        <Textarea
          label="Describe what happened"
          value={formData.lossDescription}
          onChange={(e) => handleInputChange('lossDescription', e.target.value)}
          placeholder="Please provide details about the incident (e.g., rear-ended at intersection, backed into a pole, etc.)"
          error={formErrors.lossDescription}
          required
          rows={4}
        />

        {/* Loss Date */}
        <Input
          type="date"
          label="When did the damage occur?"
          value={formData.lossDate}
          onChange={(e) => handleInputChange('lossDate', e.target.value)}
          error={formErrors.lossDate}
          required
          max={new Date().toISOString().split('T')[0]}
        />

        {/* Is Drivable */}
        <RadioGroup
          label="Is your vehicle drivable?"
          name="isDrivable"
          value={formData.isDrivable}
          onChange={(value) => handleInputChange('isDrivable', value)}
          options={[
            { value: 'yes', label: 'Yes' },
            { value: 'no', label: 'No' },
          ]}
          error={formErrors.isDrivable}
          required
        />

        {/* Police Report */}
        <RadioGroup
          label="Did you file a police report?"
          name="hasPoliceReport"
          value={formData.hasPoliceReport}
          onChange={(value) => handleInputChange('hasPoliceReport', value)}
          options={[
            { value: 'yes', label: 'Yes' },
            { value: 'no', label: 'No' },
          ]}
          error={formErrors.hasPoliceReport}
          required
        />

        {/* Police Report Upload (mockup) */}
        {formData.hasPoliceReport === 'yes' && (
          <FileUpload
            label="Upload Police Report"
            accept=".pdf,.jpg,.jpeg,.png"
          />
        )}

        {/* Can Provide Photos */}
        <RadioGroup
          label="Can you provide photos of the damage?"
          name="hasPhotos"
          value={formData.hasPhotos}
          onChange={(value) => handleInputChange('hasPhotos', value)}
          options={[
            { value: 'yes', label: 'Yes, I can provide photos now' },
            { value: 'no', label: 'No, I cannot provide photos' },
          ]}
          error={formErrors.hasPhotos}
          required
          vertical={true}
        />

        {/* Info message based on photo availability */}
        {formData.hasPhotos === 'no' && (
          <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>Note:</strong> Your claim will be processed through our traditional claim review process.
              An adjustor will contact you within 24-48 hours to schedule an inspection.
            </p>
          </div>
        )}

        {formData.hasPhotos === 'yes' && (
          <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-sm text-green-800">
              <strong>Great!</strong> You'll be able to upload photos in the next step and receive an instant AI-powered damage assessment.
            </p>
          </div>
        )}

          {/* Form Actions */}
          <div className="flex justify-between items-center pt-6 border-t border-gray-200">
            <Button
              variant="secondary"
              onClick={handleCancel}
              disabled={submitting}
            >
              Cancel
            </Button>
            <div className="flex gap-3">
              <Button
                variant="secondary"
                onClick={handleSaveDraft}
                disabled={submitting}
              >
                Save Draft
              </Button>
              <Button
                onClick={handleContinue}
                disabled={submitting}
              >
                {submitting
                  ? 'Submitting...'
                  : formData.hasPhotos === 'no'
                  ? 'Submit Claim for Review'
                  : formData.hasPhotos === 'yes'
                  ? 'Continue to Upload Photos →'
                  : 'Continue'}
              </Button>
            </div>
          </div>
        </Card>
      )}
    </Layout>
  );
};

export default NewClaimPage;
