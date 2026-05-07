/**
 * Vehicle Selection Card - For claim filing vehicle selection
 */
import { Car, Check } from 'lucide-react';

const VehicleSelectionCard = ({ vehicle, selected, onClick }) => {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`
        w-full text-left p-5 rounded-xl border-2 transition-all duration-200
        ${selected
          ? 'border-primary-600 bg-primary-50 shadow-md'
          : 'border-gray-200 bg-white hover:border-primary-300 hover:shadow-sm'
        }
      `}
    >
      <div className="flex items-start gap-4">
        <div className={`
          p-3 rounded-lg flex-shrink-0
          ${selected ? 'bg-primary-600' : 'bg-gray-100'}
        `}>
          <Car className={`h-6 w-6 ${selected ? 'text-white' : 'text-gray-600'}`} />
        </div>

        <div className="flex-1 min-w-0">
          <h3 className={`font-semibold text-lg mb-1 ${selected ? 'text-primary-900' : 'text-gray-900'}`}>
            {vehicle.year} {vehicle.make} {vehicle.model}
          </h3>
          <div className="space-y-1">
            <p className="text-sm text-gray-600">
              VIN: {vehicle.vin}
            </p>
            {vehicle.color && (
              <p className="text-sm text-gray-600">
                Color: {vehicle.color}
              </p>
            )}
          </div>
        </div>

        {selected && (
          <div className="flex-shrink-0">
            <div className="bg-primary-600 rounded-full p-1">
              <Check className="h-5 w-5 text-white" />
            </div>
          </div>
        )}
      </div>
    </button>
  );
};

export default VehicleSelectionCard;
