/**
 * Vehicle card component showing vehicle details
 */
import { Car } from 'lucide-react';
import Card from '../common/Card';

const VehicleCard = ({ vehicle }) => {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <div className="flex items-start gap-4">
        <div className="p-3 rounded-lg bg-primary-100">
          <Car className="h-8 w-8 text-primary-600" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">
            {vehicle.year} {vehicle.make} {vehicle.model}
          </h3>
          <div className="space-y-1 text-sm text-gray-600">
            <p>VIN: {vehicle.vin}</p>
            {vehicle.color && <p>Color: {vehicle.color}</p>}
          </div>
        </div>
      </div>
    </Card>
  );
};

export default VehicleCard;
