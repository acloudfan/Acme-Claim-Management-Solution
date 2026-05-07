/**
 * Radio button group component
 */

const RadioGroup = ({
  label,
  name,
  options,
  value,
  onChange,
  error,
  required = false,
  vertical = false,
  className = '',
}) => {
  return (
    <div className={`mb-4 ${className}`}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
          {required && <span className="text-error-600 ml-1">*</span>}
        </label>
      )}
      <div className={vertical ? 'flex flex-col gap-3' : 'flex gap-6'}>
        {options.map((option) => (
          <label
            key={option.value}
            className="flex items-center cursor-pointer"
          >
            <input
              type="radio"
              name={name}
              value={option.value}
              checked={value === option.value}
              onChange={(e) => onChange(e.target.value)}
              className="w-5 h-5 text-primary-600 focus:ring-primary-500 cursor-pointer"
            />
            <span className="ml-2 text-gray-700">{option.label}</span>
          </label>
        ))}
      </div>
      {error && (
        <p className="mt-1 text-sm text-error-600">{error}</p>
      )}
    </div>
  );
};

export default RadioGroup;
