/**
 * Policy card component
 */
import { Car, Home, ChevronRight } from 'lucide-react';
import Card from '../common/Card';
import Badge from '../common/Badge';

const PolicyCard = ({ policy, onClick, fake = false }) => {
  const isAuto = policy?.policy_type === 'auto' || policy?.type === 'auto';
  const Icon = isAuto ? Car : Home;

  const handleClick = () => {
    if (!fake && onClick) {
      onClick(policy);
    }
  };

  return (
    <Card
      className={`transition-all duration-200 ${
        fake ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer hover:shadow-lg hover:-translate-y-1'
      }`}
      onClick={handleClick}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4">
          <div className={`p-3 rounded-lg ${isAuto ? 'bg-primary-100' : 'bg-gray-100'}`}>
            <Icon className={`h-8 w-8 ${isAuto ? 'text-primary-600' : 'text-gray-600'}`} />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              {isAuto ? 'Auto Insurance' : 'Home Insurance'}
            </h3>
            <p className="text-gray-600 text-sm mb-2">
              Policy: {policy?.policy_number || 'POL-Home-1234'}
            </p>
            {fake ? (
              <Badge variant="default">Demo Only</Badge>
            ) : (
              <Badge variant="success">{policy?.status || 'Active'}</Badge>
            )}
          </div>
        </div>
        {!fake && <ChevronRight className="h-6 w-6 text-gray-400" />}
      </div>

      {!fake && policy && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-500">Effective Date</p>
              <p className="font-medium text-gray-900">
                {new Date(policy.start_date).toLocaleDateString()}
              </p>
            </div>
            <div>
              <p className="text-gray-500">Expiration Date</p>
              <p className="font-medium text-gray-900">
                {new Date(policy.end_date).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
};

export default PolicyCard;
