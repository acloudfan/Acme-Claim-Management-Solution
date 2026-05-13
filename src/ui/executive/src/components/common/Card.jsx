/**
 * Card component for content containers
 */

const Card = ({ children, className = '', title, actions, padding = true, onClick, id }) => {
  return (
    <div
      id={id}
      className={`bg-white rounded-xl card-shadow border border-gray-200 ${padding ? 'p-6' : ''} ${className}`}
      onClick={onClick}
    >
      {(title || actions) && (
        <div className="flex justify-between items-center mb-4">
          {title && <h3 className="text-xl font-semibold text-gray-900">{title}</h3>}
          {actions && <div className="flex gap-2">{actions}</div>}
        </div>
      )}
      {children}
    </div>
  );
};

export default Card;
