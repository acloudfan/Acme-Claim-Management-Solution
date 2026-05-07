/**
 * DamageEditor component - modal for editing existing damage costs
 */
import { useState, useEffect } from 'react';
import Modal from '../common/Modal';
import Input from '../common/Input';
import Textarea from '../common/Textarea';
import Button from '../common/Button';
import { formatCurrency } from '../../utils/formatters';
import { AlertTriangle } from 'lucide-react';

const DamageEditor = ({ isOpen, onClose, damage, onSave }) => {
  const [formData, setFormData] = useState({
    labor_hours: '',
    parts_cost: '',
    adjustor_note: '',
  });
  const [errors, setErrors] = useState({});
  const [showWarning, setShowWarning] = useState(false);

  useEffect(() => {
    if (damage) {
      setFormData({
        labor_hours: damage.labor_hours || '',
        parts_cost: damage.estimated_parts_cost || '',
        adjustor_note: damage.adjustor_note || '',
      });
    }
  }, [damage]);

  const calculateTotal = () => {
    const hours = parseFloat(formData.labor_hours) || 0;
    const rate = parseFloat(damage?.labor_rate) || 0;
    const parts = parseFloat(formData.parts_cost) || 0;
    return hours * rate + parts;
  };

  const calculateChangePercentage = () => {
    if (!damage || !damage.ai_total_cost) return 0;
    const aiTotal = damage.ai_total_cost;
    const newTotal = calculateTotal();
    if (aiTotal === 0) return 0;
    return ((newTotal - aiTotal) / aiTotal) * 100;
  };

  const hasChanges = () => {
    if (!damage) return false;
    return (
      parseFloat(formData.labor_hours) !== parseFloat(damage.labor_hours) ||
      parseFloat(formData.parts_cost) !== parseFloat(damage.estimated_parts_cost)
    );
  };

  useEffect(() => {
    const changePercent = Math.abs(calculateChangePercentage());
    setShowWarning(changePercent > 50);
  }, [formData]);

  const validate = () => {
    const newErrors = {};

    const laborHours = parseFloat(formData.labor_hours);
    if (!formData.labor_hours || laborHours < 0) {
      newErrors.labor_hours = 'Labor hours must be a positive number';
    } else if (laborHours % 0.5 !== 0) {
      newErrors.labor_hours = 'Labor hours must be in 0.5 increments (e.g., 1.0, 1.5, 2.0)';
    }

    if (!formData.parts_cost || parseFloat(formData.parts_cost) < 0) {
      newErrors.parts_cost = 'Parts cost must be a positive number';
    }

    if (hasChanges() && !formData.adjustor_note.trim()) {
      newErrors.adjustor_note = 'Adjustor note is required when making changes';
    }

    if (formData.adjustor_note && formData.adjustor_note.length > 500) {
      newErrors.adjustor_note = 'Note must be 500 characters or less';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!validate()) return;

    const updatedDamage = {
      ...damage,
      labor_hours: parseFloat(formData.labor_hours),
      parts_cost: parseFloat(formData.parts_cost),
      adjustor_note: formData.adjustor_note.trim(),
    };

    onSave(updatedDamage);
    handleClose();
  };

  const handleClose = () => {
    setFormData({
      labor_hours: '',
      parts_cost: '',
      adjustor_note: '',
    });
    setErrors({});
    setShowWarning(false);
    onClose();
  };

  if (!damage) return null;

  const total = calculateTotal();
  const changePercent = calculateChangePercentage();

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Edit Damage Costs" size="lg">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* AI Baseline (read-only) */}
        {damage.ai_total_cost && (
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
            <h5 className="text-sm font-semibold mb-2 text-gray-700">AI Estimate (Baseline)</h5>
            <div className="space-y-1 text-sm text-gray-600">
              <p>Labor: {damage.ai_labor_hours?.toFixed(1)}h × ${damage.labor_rate || 0}/h = ${((damage.ai_labor_hours || 0) * (damage.labor_rate || 0)).toFixed(2)}</p>
              <p>Parts: ${damage.ai_parts_cost?.toFixed(2)}</p>
              <p className="text-base font-semibold text-gray-800 pt-1 border-t">Total: ${damage.ai_total_cost.toFixed(2)}</p>
            </div>
          </div>
        )}

        {/* Warning for large changes */}
        {showWarning && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-yellow-800">Large Cost Change Detected</p>
              <p className="text-sm text-yellow-700 mt-1">
                This represents a {Math.abs(changePercent).toFixed(1)}% change from the AI estimate.
                Please provide a detailed note explaining the adjustment.
              </p>
            </div>
          </div>
        )}

        {/* Form Fields */}
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

        <Textarea
          label="Adjustor Note"
          value={formData.adjustor_note}
          onChange={(e) => setFormData({ ...formData, adjustor_note: e.target.value })}
          placeholder="Explain the reason for cost adjustments..."
          rows={3}
          error={errors.adjustor_note}
          required={hasChanges()}
        />

        {/* Total Display */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <div className="flex justify-between items-center">
            <span className="text-lg font-medium text-gray-700">Revised Total:</span>
            <span className="text-2xl font-bold text-primary-700">
              {formatCurrency(total)}
            </span>
          </div>
          {damage.ai_total_cost && total !== damage.ai_total_cost && (
            <p className={`text-sm mt-2 ${changePercent > 0 ? 'text-red-600' : 'text-green-600'}`}>
              {changePercent > 0 ? '+' : ''}{changePercent.toFixed(1)}% change from AI estimate
              ({changePercent > 0 ? '+' : ''}{formatCurrency(total - damage.ai_total_cost)})
            </p>
          )}
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t">
          <Button variant="secondary" onClick={handleClose} type="button">
            Cancel
          </Button>
          <Button variant="primary" type="submit">
            Save Changes
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default DamageEditor;
