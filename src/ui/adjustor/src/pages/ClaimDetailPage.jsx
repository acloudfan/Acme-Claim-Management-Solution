/**
 * ClaimDetailPage - Claim review page with 70/30 split-screen layout
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { fetchClaimDetails, fetchClaimImages, fetchClaimImage, fetchAnnotatedImage, fetchClaimEvents, fetchFraudSignals } from '../api/claims';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import Button from '../components/common/Button';
import Spinner from '../components/common/Spinner';
import ImageViewer from '../components/claims/ImageViewer';
import DamageList from '../components/claims/DamageList';
import DamageEditor from '../components/claims/DamageEditor';
import DamageCreator from '../components/claims/DamageCreator';
import EventTimeline from '../components/claims/EventTimeline';
import ChatBotPlaceholder from '../components/claims/ChatBotPlaceholder';
import FraudAnalysisSection from '../components/claims/FraudAnalysisSection';
import { formatCurrency, formatDateTime } from '../utils/formatters';
import { STATUS_LABELS, STATUS_COLORS, REVIEW_REASON_LABELS, REVIEW_REASONS } from '../utils/constants';
import { ArrowLeft, Plus } from 'lucide-react';

const ClaimDetailPage = () => {
  const { claimId } = useParams();
  const navigate = useNavigate();
  const { adjustor } = useAuth();

  const [claim, setClaim] = useState(null);
  const [images, setImages] = useState([]);
  const [events, setEvents] = useState([]);
  const [damages, setDamages] = useState([]);
  const [originalDamages, setOriginalDamages] = useState([]);
  const [fraudData, setFraudData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [imageUrls, setImageUrls] = useState({}); // Store blob URLs for cleanup

  // Labor rate state
  const [laborRateState, setLaborRateState] = useState('');
  const [laborCost, setLaborCost] = useState(0);

  // Modal states
  const [editingDamage, setEditingDamage] = useState(null);
  const [showDamageEditor, setShowDamageEditor] = useState(false);
  const [showDamageCreator, setShowDamageCreator] = useState(false);

  useEffect(() => {
    loadClaimData();

    // Cleanup blob URLs on unmount
    return () => {
      Object.values(imageUrls).forEach(urls => {
        if (urls.original) URL.revokeObjectURL(urls.original);
        if (urls.annotated) URL.revokeObjectURL(urls.annotated);
      });
    };
  }, [claimId]);

  const loadClaimData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch claim details from API
      const client = (await import('../api/client')).getApiClient();

      // First, get claim basic info to find customer_id
      const claimsResponse = await client.get(`/adjustors/${adjustor.adjustor_id}/claims/pending`);
      const claimInfo = claimsResponse.data.claims.find(c => c.claim_id === parseInt(claimId));

      if (!claimInfo) {
        throw new Error('Claim not found');
      }

      // Fetch detailed claim data using customer endpoint
      const [claimData, imagesResponse, eventsData, fraudResponse] = await Promise.all([
        fetchClaimDetails(claimInfo.customer_id, claimId),
        fetchClaimImages(claimInfo.customer_id, claimId),
        fetchClaimEvents(claimInfo.customer_id, claimId),
        fetchFraudSignals(claimId),
      ]);

      // Parse vehicle info from queue response (format: "2022 Honda Accord Silver")
      const vehicleParts = claimInfo.vehicle?.split(' ') || [];
      const vehicleYear = vehicleParts[0] || '';
      const vehicleMake = vehicleParts[1] || '';
      const vehicleModel = vehicleParts.slice(2, -1).join(' ') || '';
      const vehicleColor = vehicleParts[vehicleParts.length - 1] || '';

      // Merge claim data with queue info for complete picture
      const mergedClaim = {
        claim_id: claimData.claim_id,
        customer_id: claimInfo.customer_id,
        customer_name: claimInfo.customer_name,
        customer_email: 'customer@email.com', // Not in API response
        customer_phone: '(555) 123-4567', // Not in API response
        vehicle_year: vehicleYear,
        vehicle_make: vehicleMake,
        vehicle_model: vehicleModel,
        vehicle_color: vehicleColor,
        vin: claimData.vin,
        policy_number: claimData.policy_number,
        status: claimData.current_status,
        review_reason: claimInfo.reason_for_review,
        fnol_date: `${claimData.fnol_date}T${claimData.fnol_time || '00:00:00'}`,
        damage_date: claimData.date_of_damage,
        vehicle_drivable: claimData.is_drivable,
        ai_estimate_total: claimData.damage_assessment?.total_estimated_cost || 0,
        created_at: claimData.fnol_date,
        appeal_count: claimData.appeal_count || 0,
        first_appeal_reason: claimData.first_appeal_reason,
        first_appeal_date: claimData.first_appeal_date,
        second_appeal_reason: claimData.second_appeal_reason,
        second_appeal_date: claimData.second_appeal_date,
      };

      // Parse damages from API response
      const apiDamages = claimData.damage_assessment?.damages || [];
      const laborRate = parseFloat(claimData.state_avg_labor_cost) || 0;
      const claimDamages = apiDamages.map((dmg, idx) => {
        const laborHours = parseFloat(dmg.labor_hours) || 0;
        const partsCost = parseFloat(dmg.estimated_parts_cost) || 0;
        const laborCost = laborHours * laborRate;
        const totalCost = laborCost + partsCost;

        return {
          damage_id: dmg.damage_id,
          damage_type: dmg.damage_part || 'unknown',
          damage_part: dmg.damage_part || 'Unknown',
          location: dmg.damage_part || 'Unknown',
          description: `${dmg.damage_part} detected by AI`,
          severity: parseFloat(dmg.severity) > 0.7 ? 'severe' : parseFloat(dmg.severity) > 0.4 ? 'moderate' : 'light',
          confidence: dmg.damage_confidence,
          image_id: dmg.image_id,
          labor_hours: laborHours,
          labor_rate: laborRate,
          parts_cost: partsCost,
          estimated_parts_cost: partsCost,
          estimated_total_cost: totalCost,
          source: 'ai',
          bounding_box: dmg.bounding_box,
          // LLM Assessment fields
          damage_summary: dmg.damage_summary,
          internal_damage_probability: dmg.internal_damage_probability,
          recommended_action: dmg.recommended_action,
          reasoning: dmg.reasoning,
          car_side: dmg.car_side,
          assessment_confidence: dmg.assessment_confidence,
        };
      });

      // Parse images from API response and fetch image blobs via API
      const apiImages = Array.isArray(imagesResponse) ? imagesResponse : (imagesResponse.images || []);

      // Fetch original and annotated images via API client (includes auth headers)
      const imagePromises = apiImages.map(async (img, idx) => {
        try {
          // Fetch original image
          const originalBlob = await fetchClaimImage(claimInfo.customer_id, claimId, img.image_id);
          const originalUrl = URL.createObjectURL(originalBlob);

          // Try to fetch annotated image (may not exist)
          let annotatedUrl = null;
          try {
            const annotatedBlob = await fetchAnnotatedImage(claimInfo.customer_id, claimId, img.image_id);
            annotatedUrl = URL.createObjectURL(annotatedBlob);
          } catch (err) {
            console.log('No annotated image available for:', img.image_id);
          }

          // Store URLs for cleanup
          setImageUrls(prev => ({
            ...prev,
            [img.image_id]: { original: originalUrl, annotated: annotatedUrl }
          }));

          return {
            image_id: img.image_id,
            image_url: originalUrl,
            annotated_url: annotatedUrl,
            view_angle: `Image ${idx + 1}`,
            uploaded_at: img.uploaded_at,
          };
        } catch (err) {
          console.error('Failed to load image:', img.image_id, err);
          return {
            image_id: img.image_id,
            image_url: null,
            annotated_url: null,
            view_angle: `Image ${idx + 1}`,
            uploaded_at: img.uploaded_at,
          };
        }
      });

      const claimImages = await Promise.all(imagePromises);

      setClaim(mergedClaim);
      setImages(claimImages);
      setDamages(claimDamages);
      setOriginalDamages(JSON.parse(JSON.stringify(claimDamages)));
      setEvents(eventsData.events || []);
      setFraudData(fraudResponse);

      // Set labor rate state
      setLaborRateState(claimData.labor_rate_state || '');
      setLaborCost(parseFloat(claimData.state_avg_labor_cost) || 0);
    } catch (err) {
      console.error('Failed to load claim data:', err);
      setError('Failed to load claim data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleEditDamage = (damage) => {
    setEditingDamage(damage);
    setShowDamageEditor(true);
  };

  const handleSaveDamage = (updatedDamage) => {
    setDamages((prev) =>
      prev.map((d) => (d.damage_id === updatedDamage.damage_id ? updatedDamage : d))
    );
  };

  const handleAddDamage = (newDamage) => {
    setDamages((prev) => [...prev, newDamage]);
  };

  const handleLaborRateChange = (newRate) => {
    const rateFloat = parseFloat(newRate) || 0;
    setLaborCost(rateFloat);

    // Update all damages with new labor rate and recalculate totals
    setDamages((prev) =>
      prev.map((d) => {
        const laborCost = (d.labor_hours || 0) * rateFloat;
        const partsCost = d.parts_cost || d.estimated_parts_cost || 0;
        const totalCost = laborCost + partsCost;

        return {
          ...d,
          labor_rate: rateFloat,
          estimated_total_cost: totalCost,
        };
      })
    );
  };

  const calculateTotal = () => {
    return damages.reduce((sum, d) => {
      return sum + (d.labor_hours || 0) * (d.labor_rate || 0) + (d.parts_cost || 0);
    }, 0);
  };

  const handleCompleteReview = () => {
    navigate(`/claims/${claimId}/review/complete`, {
      state: {
        claim,
        damages,
        originalDamages,
        revisedTotal: calculateTotal(),
        laborRateState,
        laborCost,
      },
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">{error}</p>
        <Button onClick={loadClaimData}>Retry</Button>
      </div>
    );
  }

  const revisedTotal = calculateTotal();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate('/claims/queue')} size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Queue
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Claim #{claim.claim_id} - Review</h1>
            <div className="flex items-center gap-2 mt-1">
              <Badge variant="warning">
                {REVIEW_REASON_LABELS[claim.review_reason] || claim.review_reason}
              </Badge>
              <span className={`badge ${STATUS_COLORS[claim.status]}`}>
                {STATUS_LABELS[claim.status]}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Split-Screen Layout: 70% Left Panel / 30% Right Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-[70%_30%] gap-6">
        {/* LEFT PANEL (70%) - Scrollable */}
        <div className="space-y-6">
          {/* Section 1: Claim Overview */}
          <Card title="Claim Overview">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Customer Info */}
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-3">Customer Information</h4>
                <dl className="space-y-2 text-sm">
                  <div>
                    <dt className="text-gray-600">Name</dt>
                    <dd className="font-medium text-gray-900">{claim.customer_name}</dd>
                  </div>
                  <div>
                    <dt className="text-gray-600">Email</dt>
                    <dd className="font-medium text-gray-900">{claim.customer_email}</dd>
                  </div>
                  <div>
                    <dt className="text-gray-600">Phone</dt>
                    <dd className="font-medium text-gray-900">{claim.customer_phone}</dd>
                  </div>
                </dl>
              </div>

              {/* Vehicle Info */}
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-3">Vehicle Information</h4>
                <dl className="space-y-2 text-sm">
                  <div>
                    <dt className="text-gray-600">Vehicle</dt>
                    <dd className="font-medium text-gray-900">
                      {claim.vehicle_year} {claim.vehicle_make} {claim.vehicle_model}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-gray-600">Color</dt>
                    <dd className="font-medium text-gray-900">{claim.vehicle_color}</dd>
                  </div>
                  <div>
                    <dt className="text-gray-600">VIN</dt>
                    <dd className="font-medium text-gray-900 font-mono text-xs">{claim.vin}</dd>
                  </div>
                </dl>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t">
              <dl className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <dt className="text-gray-600">Policy Number</dt>
                  <dd className="font-medium text-gray-900">{claim.policy_number}</dd>
                </div>
                <div>
                  <dt className="text-gray-600">FNOL Date</dt>
                  <dd className="font-medium text-gray-900">{formatDateTime(claim.fnol_date)}</dd>
                </div>
                <div>
                  <dt className="text-gray-600">Damage Date</dt>
                  <dd className="font-medium text-gray-900">{claim.damage_date}</dd>
                </div>
                <div>
                  <dt className="text-gray-600">Vehicle Drivable</dt>
                  <dd className="font-medium text-gray-900">{claim.vehicle_drivable ? 'Yes' : 'No'}</dd>
                </div>
              </dl>
            </div>
          </Card>

          {/* Section 2: AI Estimate Summary */}
          <Card title="AI Estimate Summary">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-gray-600">AI Estimate Total</p>
                <p className="text-2xl font-bold text-primary-700">{formatCurrency(claim.ai_estimate_total)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Damages Detected</p>
                <p className="text-2xl font-bold text-gray-900">{originalDamages.length}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Average Confidence</p>
                <p className="text-2xl font-bold text-gray-900">
                  {originalDamages.length > 0
                    ? Math.round(
                        (originalDamages.reduce((sum, d) => sum + (d.confidence || 0), 0) /
                          originalDamages.length) *
                          100
                      )
                    : 0}
                  %
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Current Total</p>
                <p className="text-2xl font-bold text-green-700">{formatCurrency(revisedTotal)}</p>
              </div>
            </div>
          </Card>

          {/* Section 2.6: Fraud Analysis (if fraud signals exist) */}
          {claim.review_reason === REVIEW_REASONS.FRAUD_SIGNALS && fraudData && (
            <FraudAnalysisSection fraudData={fraudData} />
          )}

          {/* Section 2.5: Customer Appeal (if exists) */}
          {(claim.first_appeal_reason || claim.second_appeal_reason) && (
            <Card title="Customer Appeal">
              <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-r-lg">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0">
                    <svg className="h-6 w-6 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <div className="space-y-3">
                      {claim.first_appeal_reason && (
                        <div>
                          <p className="text-sm font-medium text-yellow-800 mb-2">
                            {claim.first_appeal_date && new Date(claim.first_appeal_date).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
                          </p>
                          <p className="text-sm text-yellow-900 italic bg-yellow-100 p-3 rounded border border-yellow-200">
                            {claim.first_appeal_reason}
                          </p>
                        </div>
                      )}
                      {claim.second_appeal_reason && (
                        <div>
                          <p className="text-sm font-medium text-yellow-800 mb-2">
                            {claim.second_appeal_date && new Date(claim.second_appeal_date).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
                          </p>
                          <p className="text-sm text-yellow-900 italic bg-yellow-100 p-3 rounded border border-yellow-200">
                            {claim.second_appeal_reason}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          )}

          {/* Section 3: Damage Images */}
          <Card title="Damage Images">
            <ImageViewer images={images} damages={damages} />
          </Card>

          {/* Section 3.5: Labor Rate Configuration */}
          <Card title="Labor Rate Configuration">
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* State */}
                <div>
                  <label htmlFor="labor-state" className="block text-sm font-medium text-gray-700 mb-2">
                    State
                  </label>
                  <input
                    id="labor-state"
                    type="text"
                    value={laborRateState}
                    onChange={(e) => setLaborRateState(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="e.g., CA"
                  />
                </div>

                {/* Labor Cost */}
                <div>
                  <label htmlFor="labor-cost" className="block text-sm font-medium text-gray-700 mb-2">
                    Average Labor Cost ($/hour)
                  </label>
                  <input
                    id="labor-cost"
                    type="number"
                    step="0.01"
                    value={laborCost}
                    onChange={(e) => handleLaborRateChange(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="e.g., 156.00"
                  />
                </div>
              </div>

              <p className="text-sm text-gray-600 mt-3 italic">
                Note: Changing labor rate will recalculate all damage estimates
              </p>
            </div>
          </Card>

          {/* Section 4: Damages List */}
          <Card
            title="Damages"
            actions={
              <button
                onClick={() => setShowDamageCreator(true)}
                className="px-3 py-1.5 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-md transition-all duration-200 inline-flex items-center"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Manual Damage
              </button>
            }
          >
            <DamageList damages={damages} onEdit={handleEditDamage} editable={true} />

            <div className="mt-6 pt-6 border-t">
              <div className="flex justify-between items-center">
                <span className="text-lg font-semibold text-gray-700">Revised Total:</span>
                <span className="text-3xl font-bold text-primary-700">{formatCurrency(revisedTotal)}</span>
              </div>
              {revisedTotal !== claim.ai_estimate_total && (
                <p className="text-sm text-gray-600 mt-2 text-right">
                  Change:{' '}
                  <span
                    className={
                      revisedTotal > claim.ai_estimate_total ? 'text-red-600 font-medium' : 'text-green-600 font-medium'
                    }
                  >
                    {revisedTotal > claim.ai_estimate_total ? '+' : ''}
                    {formatCurrency(revisedTotal - claim.ai_estimate_total)}
                  </span>
                </p>
              )}
            </div>
          </Card>

          {/* Section 5: Event Timeline */}
          <Card title="Event Timeline">
            <EventTimeline events={events} />
          </Card>

          {/* Section 6: Review Actions */}
          <Card title="Your Decision">
            <div className="flex justify-end gap-3">
              <button
                onClick={handleCompleteReview}
                className="px-8 py-4 text-lg font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-lg transition-all duration-200"
              >
                Complete Review →
              </button>
            </div>
          </Card>
        </div>

        {/* RIGHT PANEL (30%) - Fixed Chatbot Placeholder */}
        <div className="lg:sticky lg:top-6 lg:h-[calc(100vh-8rem)] lg:overflow-y-auto">
          <ChatBotPlaceholder />
        </div>
      </div>

      {/* Modals */}
      <DamageEditor
        isOpen={showDamageEditor}
        onClose={() => {
          setShowDamageEditor(false);
          setEditingDamage(null);
        }}
        damage={editingDamage}
        onSave={handleSaveDamage}
      />

      <DamageCreator
        isOpen={showDamageCreator}
        onClose={() => setShowDamageCreator(false)}
        onAdd={handleAddDamage}
        images={images}
        laborRate={laborCost}
      />
    </div>
  );
};

export default ClaimDetailPage;
