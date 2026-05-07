/**
 * Claim Details Card - Display non-editable claim information
 * Shows vehicle info, policy summary, event details, and incident description
 */
import { Car, FileText, Calendar, MessageSquare } from 'lucide-react';
import Card from '../common/Card';

const ClaimDetailsCard = ({ claim, vehicle, policy }) => {
  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  // Format time
  const formatTime = (timeString) => {
    if (!timeString) return 'N/A';
    // timeString format: "HH:MM:SS"
    const [hours, minutes] = timeString.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
  };

  return (
    <Card className="claim-details-card">
      <h2 className="text-2xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
        <FileText className="h-6 w-6 text-primary-600" />
        Claim Details
      </h2>

      <div className="space-y-6">
        {/* Vehicle Information */}
        {vehicle && (
          <div className="details-section">
            <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <Car className="h-5 w-5 text-gray-600" />
              Vehicle Information
            </h3>
            <ul className="space-y-2 ml-7 text-gray-700">
              <li className="flex items-start">
                <span className="font-medium mr-2">•</span>
                <div className="flex-1">
                  <span className="font-semibold text-gray-600 mr-2">Vehicle:</span>
                  <span>{vehicle.year} {vehicle.make} {vehicle.model}</span>
                </div>
              </li>
              <li className="flex items-start">
                <span className="font-medium mr-2">•</span>
                <div className="flex-1">
                  <span className="font-semibold text-gray-600 mr-2">VIN:</span>
                  <span>{vehicle.vin}</span>
                </div>
              </li>
              <li className="flex items-start">
                <span className="font-medium mr-2">•</span>
                <div className="flex-1">
                  <span className="font-semibold text-gray-600 mr-2">Color:</span>
                  <span>{vehicle.color}</span>
                </div>
              </li>
            </ul>
          </div>
        )}

        {/* Policy Summary */}
        {policy && (
          <div className="details-section">
            <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <FileText className="h-5 w-5 text-gray-600" />
              Policy Summary
            </h3>
            <ul className="space-y-2 ml-7 text-gray-700">
              <li className="flex items-start">
                <span className="font-medium mr-2">•</span>
                <div className="flex-1">
                  <span className="font-semibold text-gray-600 mr-2">Policy Number:</span>
                  <span>{policy.policy_number}</span>
                </div>
              </li>
              {policy.collision_deductible !== undefined && (
                <li className="flex items-start">
                  <span className="font-medium mr-2">•</span>
                  <div className="flex-1">
                    <span className="font-semibold text-gray-600 mr-2">Collision Deductible:</span>
                    <span>${policy.collision_deductible.toLocaleString()}</span>
                  </div>
                </li>
              )}
              {policy.liability_limit !== undefined && (
                <li className="flex items-start">
                  <span className="font-medium mr-2">•</span>
                  <div className="flex-1">
                    <span className="font-semibold text-gray-600 mr-2">Liability Coverage:</span>
                    <span>${policy.liability_limit.toLocaleString()}</span>
                  </div>
                </li>
              )}
            </ul>
          </div>
        )}

        {/* Event Details */}
        {claim && (
          <div className="details-section">
            <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <Calendar className="h-5 w-5 text-gray-600" />
              Event Details
            </h3>
            <ul className="space-y-2 ml-7 text-gray-700">
              <li className="flex items-start">
                <span className="font-medium mr-2">•</span>
                <div className="flex-1">
                  <span className="font-semibold text-gray-600 mr-2">Date of Incident:</span>
                  <span>{formatDate(claim.date_of_damage)}</span>
                </div>
              </li>
              <li className="flex items-start">
                <span className="font-medium mr-2">•</span>
                <div className="flex-1">
                  <span className="font-semibold text-gray-600 mr-2">Reported:</span>
                  <span>{formatDate(claim.fnol_date)} at {formatTime(claim.fnol_time)}</span>
                </div>
              </li>
              <li className="flex items-start">
                <span className="font-medium mr-2">•</span>
                <div className="flex-1">
                  <span className="font-semibold text-gray-600 mr-2">Vehicle Drivable:</span>
                  <span>{claim.is_drivable ? 'Yes' : 'No'}</span>
                </div>
              </li>
            </ul>
          </div>
        )}

        {/* Your Description */}
        {claim?.incident_description && (
          <div className="details-section">
            <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-gray-600" />
              Your Description
            </h3>
            <div className="ml-7">
              <p className="text-gray-700 italic bg-gray-50 p-4 rounded-lg border border-gray-200">
                {claim.incident_description}
              </p>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};

export default ClaimDetailsCard;
