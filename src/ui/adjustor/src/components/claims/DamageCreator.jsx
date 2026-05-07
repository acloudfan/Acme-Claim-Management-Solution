/**
 * DamageCreator component - modal for adding manual damages
 */
import { useState } from 'react';
import Modal from '../common/Modal';
import Input from '../common/Input';
import Textarea from '../common/Textarea';
import Button from '../common/Button';
import { formatCurrency } from '../../utils/formatters';
import { DAMAGE_TYPES, DAMAGE_TYPE_LABELS, SEVERITY } from '../../utils/constants';

const DamageCreator = ({ isOpen, onClose, onAdd, images = [] }) => {
  const [formData, setFormData] = useState({
    damage_type: '',
    location: '',
    description: '',
    severity: '',
    image_id: '',
    labor_hours: '',
    labor_rate: '',
    parts_cost: '',
    adjustor_note: '',
  });
  const [errors, setErrors] = useState({});

  const calculateTotal = () => {
    const hours = parseFloat(formData.labor_hours) || 0;
    const rate = parseFloat(formData.labor_rate) || 0;
    const parts = parseFloat(formData.parts_cost) || 0;
    return hours * rate + parts;
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.damage_type) {
      newErrors.damage_type = 'Damage type is required';
    }

    if (!formData.location || formData.location.length < 3) {
      newErrors.location = 'Location must be at least 3 characters';
    }

    if (!formData.description || formData.description.length < 10) {
      newErrors.description = 'Description must be at least 10 characters';
    }

    if (!formData.severity) {
      newErrors.severity = 'Severity is required';
    }

    if (!formData.labor_hours || parseFloat(formData.labor_hours) <= 0) {
      newErrors.labor_hours = 'Labor hours must be greater than 0';
    }

    if (!formData.labor_rate || parseFloat(formData.labor_rate) <= 0) {
      newErrors.labor_rate = 'Labor rate must be greater than 0';
    }

    if (!formData.parts_cost || parseFloat(formData.parts_cost) < 0) {
      newErrors.parts_cost = 'Parts cost must be 0 or greater';
    }

    if (!formData.adjustor_note || formData.adjustor_note.length < 10) {
      newErrors.adjustor_note = 'Adjustor note is required (minimum 10 characters)';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!validate()) return;

    const newDamage = {
      damage_id: `manual_${Date.now()}`,
      damage_type: formData.damage_type,
      location: formData.location.trim(),
      description: formData.description.trim(),
      severity: formData.severity,
      image_id: formData.image_id || null,
      labor_hours: parseFloat(formData.labor_hours),
      labor_rate: parseFloat(formData.labor_rate),
      parts_cost: parseFloat(formData.parts_cost),
      adjustor_note: formData.adjustor_note.trim(),
      source: 'manual',
      confidence: null,
      bounding_box: null,
    };

    onAdd(newDamage);
    handleClose();
  };

  const handleClose = () => {
    setFormData({
      damage_type: '',
      location: '',
      description: '',
      severity: '',
      image_id: '',
      labor_hours: '',
      labor_rate: '',
      parts_cost: '',
      adjustor_note: '',
    });
    setErrors({});
    onClose();
  };

  const total = calculateTotal();

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Add Manual Damage" size="lg">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Damage Type and Location */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Damage Type <span className="text-danger">*</span>
            </label>
            <select
              value={formData.damage_type}
              onChange={(e) => setFormData({ ...formData, damage_type: e.target.value })}
              className={`w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 ${
                errors.damage_type ? 'border-danger' : 'border-gray-300'
              }`}
            >
              <option value="">Select type...</option>
              {Object.values(DAMAGE_TYPES).map((type) => (
                <option key={type} value={type}>
                  {DAMAGE_TYPE_LABELS[type]}
                </option>
              ))}
            </select>
            {errors.damage_type && <p className="mt-1 text-sm text-danger">{errors.damage_type}</p>}
          </div>

          <Input
            label="Location"
            type="text"
            value={formData.location}
            onChange={(e) => setFormData({ ...formData, location: e.target.value })}
            placeholder="e.g., Front bumper, Driver door"
            error={errors.location}
            required
          />
        </div>

        {/* Description */}
        <Textarea
          label="Description"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          placeholder="Detailed description of the damage..."
          rows={3}
          error={errors.description}
          required
        />

        {/* Severity and Image */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Severity <span className="text-danger">*</span>
            </label>
            <select
              value={formData.severity}
              onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
              className={`w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 ${
                errors.severity ? 'border-danger' : 'border-gray-300'
              }`}
            >
              <option value="">Select severity...</option>
              <option value={SEVERITY.LIGHT}>Light</option>
              <option value={SEVERITY.MODERATE}>Moderate</option>
              <option value={SEVERITY.SEVERE}>Severe</option>
            </select>
            {errors.severity && <p className="mt-1 text-sm text-danger">{errors.severity}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Associated Image (Optional)
            </label>
            <select
              value={formData.image_id}
              onChange={(e) => setFormData({ ...formData, image_id: e.target.value })}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="">None</option>
              {images.map((img, idx) => (
                <option key={img.image_id} value={img.image_id}>
                  Image {idx + 1} {img.view_angle ? `- ${img.view_angle}` : ''}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Cost Inputs */}
        <div className="border-t pt-6">
          <h4 className="text-md font-semibold text-gray-900 mb-4">Cost Breakdown</h4>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Labor Hours"
              type="number"
              step="0.5"
              min="0"
              value={formData.labor_hours}
              onChange={(e) => setFormData({ ...formData, labor_hours: e.target.value })}
              error={errors.labor_hours}
              required
            />

            <Input
              label="Labor Rate ($/hr)"
              type="number"
              step="0.01"
              min="0"
              value={formData.labor_rate}
              onChange={(e) => setFormData({ ...formData, labor_rate: e.target.value })}
              error={errors.labor_rate}
              required
            />
          </div>

          <Input
            label="Parts Cost ($)"
            type="number"
            step="0.01"
            min="0"
            value={formData.parts_cost}
            onChange={(e) => setFormData({ ...formData, parts_cost: e.target.value })}
            error={errors.parts_cost}
            required
          />
        </div>

        {/* Adjustor Note */}
        <Textarea
          label="Adjustor Note"
          value={formData.adjustor_note}
          onChange={(e) => setFormData({ ...formData, adjustor_note: e.target.value })}
          placeholder="Explain why this damage was manually added..."
          rows={3}
          error={errors.adjustor_note}
          required
        />

        {/* Total Display */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <div className="flex justify-between items-center">
            <span className="text-lg font-medium text-gray-700">Total Cost:</span>
            <span className="text-2xl font-bold text-primary-700">
              {formatCurrency(total)}
            </span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t">
          <Button variant="secondary" onClick={handleClose} type="button">
            Cancel
          </Button>
          <Button variant="primary" type="submit">
            Add Damage
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default DamageCreator;
