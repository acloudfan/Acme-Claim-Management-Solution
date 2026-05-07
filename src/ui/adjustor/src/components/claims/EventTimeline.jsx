/**
 * EventTimeline component - displays claim event history with SLA metrics
 */
import { useState } from 'react';
import { formatDateTime } from '../../utils/formatters';
import { ChevronDown, ChevronUp, Clock, AlertTriangle } from 'lucide-react';
import Badge from '../common/Badge';

const EventTimeline = ({ events = [] }) => {
  const [expandedEvents, setExpandedEvents] = useState(new Set());
  const [showEventsList, setShowEventsList] = useState(true); // Default to expanded

  if (events.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No events recorded</p>
      </div>
    );
  }

  // Sort events in reverse chronological order (newest first)
  const sortedEvents = [...events].sort((a, b) => {
    const dateA = new Date(`${a.event_date}T${a.event_time || '00:00:00'}`);
    const dateB = new Date(`${b.event_date}T${b.event_time || '00:00:00'}`);
    return dateB - dateA; // Descending order (newest first)
  });

  const toggleExpand = (eventId) => {
    setExpandedEvents((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(eventId)) {
        newSet.delete(eventId);
      } else {
        newSet.add(eventId);
      }
      return newSet;
    });
  };

  const getActorColor = (actor) => {
    switch (actor?.toLowerCase()) {
      case 'customer':
        return 'bg-blue-500';
      case 'ai':
      case 'system':
        return 'bg-green-500';
      case 'adjustor':
        return 'bg-amber-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusBadgeVariant = (status) => {
    if (status?.includes('approved') || status?.includes('paid')) return 'success';
    if (status?.includes('pending') || status?.includes('review')) return 'warning';
    if (status?.includes('appealed')) return 'danger';
    return 'default';
  };

  // Format event date and time
  const formatEventDateTime = (event) => {
    if (!event.event_date) return 'Unknown date';

    const dateStr = event.event_date;
    const timeStr = event.event_time || '00:00:00';
    const dateTime = new Date(`${dateStr}T${timeStr}`);

    return dateTime.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  // Calculate SLA metrics
  const calculateSLAMetrics = () => {
    // Find FNOL event (claim_submitted or submit_claim)
    const fnolEvent = sortedEvents.find(e =>
      e.action === 'claim_submitted' ||
      e.action === 'submit_claim' ||
      e.action?.toLowerCase().includes('fnol')
    );

    if (!fnolEvent || !fnolEvent.event_date) {
      return null;
    }

    const fnolTimestamp = new Date(`${fnolEvent.event_date}T${fnolEvent.event_time || '00:00:00'}`);
    const now = new Date();

    // Time since FNOL (in hours)
    const timeSinceFNOL = (now - fnolTimestamp) / (1000 * 60 * 60); // milliseconds to hours

    // SLA: 48 hours from FNOL
    const SLA_THRESHOLD_HOURS = 48;
    const slaDeadline = new Date(fnolTimestamp.getTime() + SLA_THRESHOLD_HOURS * 60 * 60 * 1000);
    const timeRemaining = (slaDeadline - now) / (1000 * 60 * 60); // hours

    return {
      timeSinceFNOL,
      timeRemaining,
      slaDeadline,
      fnolTimestamp
    };
  };

  // Format time since FNOL
  const formatTimeSinceFNOL = (hours) => {
    if (hours < 0.5) return '0.5 hr';
    if (hours < 1) return `${hours.toFixed(1)} hr`;

    const days = Math.floor(hours / 24);
    const remainingHours = hours % 24;

    if (days === 0) {
      return `${remainingHours.toFixed(1)} hrs`;
    }

    return `${days} ${days === 1 ? 'day' : 'days'}, ${remainingHours.toFixed(1)} hrs`;
  };

  // Get SLA status and color
  const getSLAStatus = (hoursRemaining) => {
    if (hoursRemaining < 0) {
      return {
        status: 'BREACHED',
        color: 'bg-red-100 text-red-800 border-red-300',
        icon: '🔴'
      };
    } else if (hoursRemaining < 12) {
      return {
        status: 'At Risk',
        color: 'bg-red-50 text-red-700 border-red-200',
        icon: '🔴'
      };
    } else if (hoursRemaining < 24) {
      return {
        status: 'Warning',
        color: 'bg-amber-50 text-amber-700 border-amber-200',
        icon: '🟡'
      };
    } else {
      return {
        status: 'On Track',
        color: 'bg-green-50 text-green-700 border-green-200',
        icon: '🟢'
      };
    }
  };

  const slaMetrics = calculateSLAMetrics();

  return (
    <div className="space-y-4">
      {/* SLA Metrics Header */}
      {slaMetrics && (
        <div className="grid grid-cols-2 gap-4 mb-6">
          {/* Time Since FNOL */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="h-5 w-5 text-blue-600" />
              <h4 className="text-sm font-semibold text-blue-900">Time Since FNOL</h4>
            </div>
            <p className="text-2xl font-bold text-blue-900">
              {formatTimeSinceFNOL(slaMetrics.timeSinceFNOL)}
            </p>
            <p className="text-xs text-blue-600 mt-1">
              {slaMetrics.fnolTimestamp.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: 'numeric',
                minute: '2-digit',
                hour12: true
              })}
            </p>
          </div>

          {/* SLA Time Remaining */}
          <div className={`border rounded-lg p-4 ${getSLAStatus(slaMetrics.timeRemaining).color}`}>
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="h-5 w-5" />
              <h4 className="text-sm font-semibold">SLA Time Remaining</h4>
            </div>
            <p className="text-2xl font-bold">
              {slaMetrics.timeRemaining < 0 ? (
                <span>{getSLAStatus(slaMetrics.timeRemaining).icon} BREACHED</span>
              ) : (
                <>
                  {slaMetrics.timeRemaining.toFixed(1)} hrs
                </>
              )}
            </p>
            <p className="text-xs mt-1 flex items-center gap-1">
              <span>{getSLAStatus(slaMetrics.timeRemaining).icon}</span>
              <span>{getSLAStatus(slaMetrics.timeRemaining).status}</span>
            </p>
          </div>
        </div>
      )}

      {/* Toggle Button for Events List */}
      <button
        onClick={() => setShowEventsList(!showEventsList)}
        className="text-sm text-primary-600 hover:text-primary-700 font-medium mb-3"
      >
        {showEventsList ? 'Hide Events' : 'Show Events'}
      </button>

      {/* Event List */}
      {showEventsList && sortedEvents.map((event, index) => {
        const isExpanded = expandedEvents.has(event.event_id);
        const hasDetails = event.comments || event.metadata;

        return (
          <div key={event.event_id || index} className="relative">
            {/* Timeline Line */}
            {index < sortedEvents.length - 1 && (
              <div className="absolute left-3 top-10 bottom-0 w-0.5 bg-gray-200" />
            )}

            {/* Event Card */}
            <div className="flex gap-4">
              {/* Actor Indicator */}
              <div className="flex-shrink-0">
                <div className={`w-6 h-6 rounded-full ${getActorColor(event.action_by || event.actor)} flex items-center justify-center`}>
                  <div className="w-2 h-2 bg-white rounded-full" />
                </div>
              </div>

              {/* Event Content */}
              <div className="flex-1 bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-medium text-gray-900 capitalize">
                        {event.action_by || event.actor || 'System'}
                      </span>
                      <span className="text-sm text-gray-500">·</span>
                      <span className="text-sm text-gray-600">{event.action}</span>
                    </div>
                    <p className="text-xs text-gray-500">
                      {formatEventDateTime(event)}
                    </p>
                  </div>

                  {event.status && (
                    <Badge variant={getStatusBadgeVariant(event.status)}>
                      {event.status}
                    </Badge>
                  )}
                </div>

                {/* Comments/Details */}
                {hasDetails && (
                  <>
                    {isExpanded && (
                      <div className="mt-3 pt-3 border-t">
                        {event.comments && (
                          <div className="mb-3">
                            <p className="text-xs font-medium text-gray-700 mb-1">Comments:</p>
                            <p className="text-sm text-gray-600">{event.comments}</p>
                          </div>
                        )}

                        {event.metadata && (
                          <div>
                            <p className="text-xs font-medium text-gray-700 mb-1">Details:</p>
                            <pre className="text-xs text-gray-600 bg-gray-50 p-2 rounded overflow-x-auto">
                              {JSON.stringify(event.metadata, null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    )}

                    <button
                      onClick={() => toggleExpand(event.event_id)}
                      className="mt-2 flex items-center gap-1 text-xs text-primary-600 hover:text-primary-700 font-medium"
                    >
                      {isExpanded ? (
                        <>
                          <ChevronUp className="h-3 w-3" />
                          Show less
                        </>
                      ) : (
                        <>
                          <ChevronDown className="h-3 w-3" />
                          Show details
                        </>
                      )}
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default EventTimeline;
