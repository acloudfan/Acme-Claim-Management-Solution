/**
 * Progress bar component for multi-step workflows
 */

const ProgressBar = ({ current, total, steps, showPercentage = true }) => {
  const percentage = (current / total) * 100;

  return (
    <div className="w-full mb-6">
      {steps && (
        <div className="flex justify-between mb-2">
          {steps.map((step, idx) => (
            <div
              key={idx}
              className={`text-sm font-medium ${
                idx + 1 <= current ? 'text-primary-600' : 'text-gray-400'
              }`}
            >
              {step}
            </div>
          ))}
        </div>
      )}

      <div className="relative w-full bg-gray-200 rounded-full h-3">
        <div
          className="absolute top-0 left-0 h-3 bg-primary-600 rounded-full transition-all duration-300"
          style={{ width: `${percentage}%` }}
        />
      </div>

      {showPercentage && (
        <div className="text-right text-sm text-gray-600 mt-2">
          {Math.round(percentage)}%
        </div>
      )}
    </div>
  );
};

export default ProgressBar;
