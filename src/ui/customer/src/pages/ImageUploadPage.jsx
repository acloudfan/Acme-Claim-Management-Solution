/**
 * Image Upload Page - Upload damage photos with real-time AI analysis (Step 2 of 3)
 * Backend runs YOLO analysis automatically during upload and creates damage reports.
 * This page displays the detected damages immediately after each image upload.
 * The ClaimAnalysisPage handles final submission and estimate generation.
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Upload, FileText, CheckCircle, XCircle, Loader, Trash2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { fetchClaimDetail, fetchClaimImages, uploadClaimImage, deleteClaimImage } from '../api/customers';
import Layout from '../components/layout/Layout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import ProgressBar from '../components/common/ProgressBar';
import Spinner from '../components/common/Spinner';

const ImageUploadPage = () => {
  const { claimId } = useParams();
  const navigate = useNavigate();
  const { customerId } = useAuth();

  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [uploadedFiles, setUploadedFiles] = useState([]);

  useEffect(() => {
    if (customerId && claimId) {
      loadClaim();
    }
  }, [customerId, claimId]);

  const loadClaim = async () => {
    try {
      setLoading(true);

      // Fetch claim details
      const claimResponse = await fetchClaimDetail(customerId, claimId);
      const claimData = claimResponse.data;
      setClaim(claimData);

      // Fetch existing images for this claim
      const imagesResponse = await fetchClaimImages(customerId, claimId);
      const existingImages = imagesResponse.data;

      console.log('Existing images from API:', existingImages);

      if (existingImages && existingImages.length > 0) {
        // Create a map of damages by image_id for quick lookup
        const damagesByImageId = new Map();
        if (claimData.damage_assessment?.damages) {
          claimData.damage_assessment.damages.forEach(damage => {
            if (damage.image_id) {
              if (!damagesByImageId.has(damage.image_id)) {
                damagesByImageId.set(damage.image_id, []);
              }
              damagesByImageId.get(damage.image_id).push(damage);
            }
          });
        }

        // Convert images to uploadedFiles format
        const imageFiles = existingImages.map(img => ({
          name: img.image_id,
          imageId: img.image_id,
          status: 'existing',
          damages: damagesByImageId.get(img.image_id) || [],
          uploadedAt: img.uploaded_at
        }));

        console.log('Loaded existing images:', imageFiles);
        setUploadedFiles(imageFiles);
      }

      return claimData;
    } catch (err) {
      console.error('Failed to load claim:', err);
      setError('Failed to load claim information. Please try again.');
      return null;
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = async (e) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;

    // Validate file count
    if (uploadedFiles.length + files.length > 20) {
      setError('Maximum 20 images allowed per claim');
      return;
    }

    // Add files to state with pending status
    const newFiles = files.map((file) => ({
      file,
      name: file.name,
      status: 'pending', // pending, uploading, assessing, summarizing, analyzed, error
      progress: 0,
      error: null,
      damages: [],
    }));

    setUploadedFiles((prev) => [...prev, ...newFiles]);

    // Upload files one by one
    for (let i = 0; i < newFiles.length; i++) {
      await uploadFile(newFiles[i], uploadedFiles.length + i);
    }
  };

  const uploadFile = async (fileData, index) => {
    try {
      // Update status to uploading
      setUploadedFiles((prev) => {
        const updated = [...prev];
        updated[index] = { ...updated[index], status: 'uploading' };
        return updated;
      });

      const formData = new FormData();
      formData.append('file', fileData.file);

      // Upload image with progress tracking
      await uploadClaimImage(customerId, claimId, formData, (progressEvent) => {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        setUploadedFiles((prev) => {
          const updated = [...prev];
          updated[index] = { ...updated[index], progress };
          return updated;
        });
      });

      // Update status to assessing (backend runs YOLO automatically)
      setUploadedFiles((prev) => {
        const updated = [...prev];
        updated[index] = { ...updated[index], status: 'assessing', progress: 100 };
        return updated;
      });

      // Wait for YOLO analysis
      await new Promise((resolve) => setTimeout(resolve, 800));

      // Update status to summarizing (backend runs LLM damage assessment)
      setUploadedFiles((prev) => {
        const updated = [...prev];
        updated[index] = { ...updated[index], status: 'summarizing' };
        return updated;
      });

      // Wait for LLM summarization
      await new Promise((resolve) => setTimeout(resolve, 700));

      // Fetch claim details to get updated damages (don't use loadClaim as it replaces the array)
      const claimResponse = await fetchClaimDetail(customerId, claimId);
      const updatedClaim = claimResponse.data;

      // Find damages for this specific image
      // Note: image_id in damage record is the filename
      let imageDamages = [];
      if (updatedClaim?.damage_assessment?.damages) {
        imageDamages = updatedClaim.damage_assessment.damages.filter(
          (damage) => damage.image_id === fileData.name
        );
      }

      // Update status to analyzed with damage info
      setUploadedFiles((prev) => {
        const updated = [...prev];
        updated[index] = {
          ...updated[index],
          status: 'analyzed',
          damages: imageDamages,
          imageId: fileData.name // Store imageId for deletion
        };
        return updated;
      });

      console.log(`Image ${fileData.name} analyzed. Found ${imageDamages.length} damages.`);
    } catch (err) {
      console.error('Failed to upload image:', err);
      setUploadedFiles((prev) => {
        const updated = [...prev];
        updated[index] = {
          ...updated[index],
          status: 'error',
          error: err.response?.data?.detail || 'Upload failed',
        };
        return updated;
      });
    }
  };

  const handleRemoveFile = async (index) => {
    const fileData = uploadedFiles[index];

    // If it's an existing image (already on server), call delete API
    if (fileData.status === 'existing' || fileData.status === 'analyzed') {
      try {
        console.log(`Deleting image ${fileData.imageId || fileData.name} from server...`);
        await deleteClaimImage(customerId, claimId, fileData.imageId || fileData.name);
        console.log('Image deleted successfully');
      } catch (err) {
        console.error('Failed to delete image:', err);
        setError(`Failed to delete image: ${err.response?.data?.detail || err.message}`);
        return; // Don't remove from UI if server deletion failed
      }
    }

    // Remove from local state
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleContinueToAnalysis = () => {
    // Validation
    if (uploadedFiles.length === 0) {
      setError('Please upload at least one image before continuing');
      return;
    }

    const hasErrors = uploadedFiles.some((f) => f.status === 'error');
    if (hasErrors) {
      setError('Please remove or re-upload failed images before continuing');
      return;
    }

    const isUploading = uploadedFiles.some((f) => f.status === 'uploading');
    if (isUploading) {
      setError('Please wait for all images to finish uploading');
      return;
    }

    // Navigate to Claim Analysis Page (submission happens there)
    navigate(`/claims/${claimId}/submit`);
  };

  const handleBack = () => {
    navigate(-1);
  };

  const handleSaveDraft = () => {
    // Claim is already in draft state with uploaded images
    // Simply navigate back to policy page
    if (claim?.policy_number) {
      alert('Draft saved successfully! You can continue later from your policy page.');
      navigate(`/policy/${claim.policy_number}`);
    } else {
      navigate('/');
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

  if (!claim) {
    return (
      <Layout>
        <div className="text-center py-12">
          <p className="text-gray-600 mb-4">Claim not found</p>
          <Button onClick={() => navigate('/')}>Back to Home</Button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      {/* Back Navigation */}
      <button
        onClick={handleBack}
        className="flex items-center gap-2 text-primary-600 hover:text-primary-700 mb-6 transition-colors"
      >
        <ArrowLeft className="h-5 w-5" />
        Back
      </button>

      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-3">
          <div className="p-3 rounded-lg bg-primary-100">
            <FileText className="h-8 w-8 text-primary-600" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Upload Damage Photos</h1>
            <p className="text-gray-600">Claim #{claimId}</p>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <ProgressBar current={2} total={3} steps={['Loss Details', 'Upload Photos', 'Analysis & Review']} />

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-error-light border border-error-300 text-error-dark rounded-lg">
          {error}
        </div>
      )}

      {/* Upload Card */}
      <Card className="max-w-4xl mx-auto">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6">Upload Images</h2>

        {/* Mobile QR Code Section */}
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex flex-col md:flex-row items-center gap-4">
            <div className="flex-1">
              <h3 className="text-base font-semibold text-blue-900 mb-2">
                📱 Continue on Mobile Device
              </h3>
              <p className="text-sm text-blue-800 mb-2">
                You can continue filing this claim on your mobile device such as a phone or tablet. Just scan the QR code with your device's camera and continue from there.
              </p>
            </div>
            <div className="flex-shrink-0">
              <div className="bg-white p-3 rounded-lg border-2 border-blue-300 shadow-sm">
                <img
                  src="/qr-code-mobile.png"
                  alt="QR Code to continue on mobile"
                  className="w-32 h-32"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.parentElement.innerHTML = '<div class="w-32 h-32 bg-gray-200 flex items-center justify-center rounded"><span class="text-gray-500 text-xs">QR Code</span></div>';
                  }}
                />
              </div>
              <p className="text-xs text-center text-blue-600 mt-1">Scan to continue</p>
            </div>
          </div>
        </div>

        {/* Drag & Drop Zone - 50% smaller */}
        <label className="block mb-2">
          <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center cursor-pointer hover:border-primary-400 hover:bg-primary-50 transition-colors">
            <Upload className="w-8 h-8 mx-auto text-gray-400 mb-3" />
            <p className="text-base text-gray-700 mb-1">
              Drag & drop images here, or click to browse
            </p>
            <p className="text-xs text-gray-500">
              Supported: JPG, PNG, HEIC • Max size: 10MB per image • Max images: 20
            </p>
            <input
              type="file"
              accept="image/jpeg,image/png,image/heic"
              multiple
              onChange={handleFileSelect}
              className="hidden"
              disabled={uploadedFiles.length >= 20 || uploadedFiles.some(f => f.status === 'uploading')}
            />
          </div>
        </label>

        {/* Test Images Note */}
        <div className="mb-6 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800">
            <span className="font-semibold">💡 Test Images Available:</span> You can use sample damaged car images provided in the <code className="bg-yellow-100 px-1.5 py-0.5 rounded text-xs font-mono">images/</code> folder under project root for testing this feature.
          </p>
        </div>

        {/* Uploaded Files Grid */}
        {uploadedFiles.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Uploaded Images ({uploadedFiles.length})
            </h3>

            <div className="space-y-4 mb-6">
              {uploadedFiles.map((fileData, idx) => (
                <div key={idx} className="border border-gray-200 rounded-lg p-4 bg-white relative">
                  {/* Delete Button - Show for existing, analyzed, or error status */}
                  {(fileData.status === 'existing' || fileData.status === 'analyzed' || fileData.status === 'error') && (
                    <button
                      onClick={() => handleRemoveFile(idx)}
                      className="absolute top-2 right-2 p-2 bg-red-500 hover:bg-red-600 text-white rounded-full shadow-lg transition-colors z-10"
                      title="Delete image"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}

                  {/* Horizontal layout: Image on left, details on right */}
                  <div className="flex gap-4">
                    {/* Left side: Image with filename and status below */}
                    <div className="flex-shrink-0 w-56">
                      {/* Thumbnail */}
                      <div className="w-full h-40 bg-gray-100 rounded-lg flex items-center justify-center overflow-hidden mb-2">
                        {fileData.file ? (
                          <img
                            src={URL.createObjectURL(fileData.file)}
                            alt={fileData.name}
                            className="w-full h-full object-cover"
                          />
                        ) : fileData.status === 'existing' || fileData.status === 'analyzed' ? (
                          <img
                            src={`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/v1/customers/${customerId}/claims/${claimId}/images/${fileData.imageId || fileData.name}`}
                            alt={fileData.name}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              // Fallback to placeholder if image fails to load
                              e.target.style.display = 'none';
                              e.target.parentElement.innerHTML = '<div class="flex items-center justify-center w-full h-full bg-gray-200"><svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg></div>';
                            }}
                          />
                        ) : (
                          <div className="flex items-center justify-center w-full h-full bg-gray-200">
                            <FileText className="w-12 h-12 text-gray-400" />
                          </div>
                        )}
                      </div>

                      {/* Filename */}
                      <p className="text-sm font-medium text-gray-900 truncate mb-2">
                        {fileData.name}
                      </p>

                      {/* Status - under image */}
                      {fileData.status === 'pending' && (
                        <div className="flex items-center gap-2 text-gray-600 text-xs">
                          <div className="w-3 h-3 border-2 border-gray-300 border-t-primary-600 rounded-full animate-spin"></div>
                          Pending...
                        </div>
                      )}

                      {fileData.status === 'uploading' && (
                        <div className="flex items-center gap-2 text-blue-600 text-xs">
                          <Loader className="w-3 h-3 animate-spin" />
                          Uploading...
                        </div>
                      )}

                      {fileData.status === 'assessing' && (
                        <div className="flex items-center gap-2 text-yellow-600 text-xs">
                          <Loader className="w-3 h-3 animate-spin" />
                          Assessing damage...
                        </div>
                      )}

                      {fileData.status === 'summarizing' && (
                        <div className="flex items-center gap-2 text-purple-600 text-xs">
                          <Loader className="w-3 h-3 animate-spin" />
                          Summarizing findings...
                        </div>
                      )}

                      {(fileData.status === 'analyzed' || fileData.status === 'existing') && (
                        <div className="flex items-center gap-2 text-green-600 text-xs">
                          <CheckCircle className="w-3 h-3" />
                          {fileData.status === 'existing' ? 'Previously uploaded' : 'Analysis complete'}
                        </div>
                      )}

                      {fileData.status === 'error' && (
                        <div className="flex items-center gap-2 text-error-600 text-xs">
                          <XCircle className="w-3 h-3" />
                          {fileData.error}
                        </div>
                      )}
                    </div>

                    {/* Right side: Damage details */}
                    <div className="flex-1">
                      {(fileData.status === 'analyzed' || fileData.status === 'existing') && fileData.damages && fileData.damages.length > 0 ? (
                        <div>
                          {/* Damage count badge */}
                          <div className="inline-block px-3 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded-full mb-3">
                            {fileData.damages.length} damage{fileData.damages.length > 1 ? 's' : ''} detected
                          </div>

                          {/* Display damage summaries - New layout */}
                          <div className="space-y-3">
                            {fileData.damages.map((damage, idx) => (
                              <div key={idx} className="border border-blue-200 rounded-lg overflow-hidden">
                                {/* Damage header with blue background */}
                                <div className="bg-blue-100 px-3 py-2 border-b border-blue-200">
                                  <div className="font-semibold text-gray-900 text-sm">
                                    {damage.damage_part?.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                  </div>
                                </div>
                                {/* Summary content */}
                                <div className="bg-blue-50 px-3 py-2">
                                  {damage.damage_summary ? (
                                    <p className="text-xs text-gray-700 leading-relaxed">
                                      {damage.damage_summary}
                                    </p>
                                  ) : (
                                    <p className="text-xs text-gray-600">
                                      Severity: {(Number(damage.severity || 0) * 100).toFixed(0)}% •
                                      Est. ${Number(damage.estimated_total_cost || 0).toFixed(2)}
                                    </p>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ) : (fileData.status === 'analyzed' || fileData.status === 'existing') && (
                        <p className="text-xs text-gray-500">No vehicle/damage was detected!!</p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Info Box */}
        {uploadedFiles.length > 0 && (
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>What happens next?</strong> Our AI has analyzed each image and detected damage.
              Click "Continue to Estimate" to submit your claim and generate a complete repair estimate.
            </p>
          </div>
        )}

        {/* Form Actions */}
        <div className="flex justify-between items-center pt-6 border-t border-gray-200">
          <Button variant="secondary" onClick={handleBack}>
            ← Back
          </Button>
          <div className="flex gap-3">
            <Button variant="secondary" onClick={handleSaveDraft}>
              Save Draft
            </Button>
            <Button
              onClick={handleContinueToAnalysis}
              disabled={uploadedFiles.length === 0}
            >
              Continue to Estimate →
            </Button>
          </div>
        </div>
      </Card>
    </Layout>
  );
};

export default ImageUploadPage;
