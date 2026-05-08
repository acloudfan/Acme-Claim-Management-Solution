/**
 * ProcessingMixChart Component
 * Pie chart showing distribution of claim processing paths
 */
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { Info } from 'lucide-react';
import Card from '../common/Card';

export default function ProcessingMixChart({ summary, onShowNarrative }) {
  if (!summary) return null;

  // Calculate processing path distribution
  const data = [
    {
      name: 'Traditional Processing',
      value: summary.traditional_claims || 0,
      color: '#94a3b8', // gray
      description: 'Standard manual adjuster review'
    },
    {
      name: 'AI Auto-Approved',
      value: summary.ai_auto_approved_claims || 0,
      color: '#22c55e', // green
      description: 'Fully automated, no human touchpoints (STP)'
    },
    {
      name: 'AI + Human Review',
      value: summary.ai_human_reviewed_claims || 0,
      color: '#3b82f6', // blue
      description: 'AI processing with single human review'
    }
  ];

  const total = data.reduce((sum, item) => sum + item.value, 0);

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const percentage = ((data.value / total) * 100).toFixed(1);
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-900">{data.name}</p>
          <p className="text-sm text-gray-600">{data.description}</p>
          <p className="text-lg font-bold text-gray-900 mt-2">
            {data.value.toLocaleString()} claims
          </p>
          <p className="text-sm text-gray-600">{percentage}% of total</p>
        </div>
      );
    }
    return null;
  };

  // Custom label
  const renderLabel = (entry) => {
    const percentage = ((entry.value / total) * 100).toFixed(1);
    return `${percentage}%`;
  };

  return (
    <Card className="mb-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-semibold text-gray-900">AI Processed Claims</h3>
            {onShowNarrative && (
              <button
                onClick={onShowNarrative}
                className="p-1 hover:bg-gray-100 rounded transition-colors"
                aria-label="Show help"
              >
                <Info className="w-4 h-4 text-gray-400 hover:text-primary-600" />
              </button>
            )}
          </div>
          <p className="text-sm text-gray-600">Distribution of claim processing paths</p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-gray-900">
            {total.toLocaleString()}
          </div>
          <div className="text-sm text-gray-600">Total Claims</div>
        </div>
      </div>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={renderLabel}
              outerRadius={100}
              innerRadius={60}
              fill="#8884d8"
              dataKey="value"
              paddingAngle={2}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend
              verticalAlign="bottom"
              height={36}
              formatter={(value, entry) => {
                const item = data.find(d => d.name === value);
                const percentage = ((item.value / total) * 100).toFixed(1);
                return `${value} (${percentage}%)`;
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Statistics Grid */}
      <div className="mt-4 pt-4 border-t border-gray-200 grid grid-cols-3 gap-4">
        {data.map((item, index) => (
          <div key={index} className="text-center">
            <div
              className="w-3 h-3 rounded-full mx-auto mb-2"
              style={{ backgroundColor: item.color }}
            />
            <div className="text-2xl font-bold text-gray-900">
              {item.value.toLocaleString()}
            </div>
            <div className="text-xs text-gray-600 mt-1">{item.name}</div>
            <div className="text-sm font-semibold text-gray-700 mt-1">
              {((item.value / total) * 100).toFixed(1)}%
            </div>
          </div>
        ))}
      </div>

      {/* AI Adoption Insight */}
      <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-start gap-2">
          <div className="text-blue-600 font-semibold text-sm">💡 Insight:</div>
          <div className="text-sm text-blue-900">
            <span className="font-semibold">
              {(((summary.ai_auto_approved_claims + summary.ai_human_reviewed_claims) / total) * 100).toFixed(1)}%
            </span>
            {' '}of claims are AI-enabled, processing{' '}
            <span className="font-semibold">
              {(summary.ai_auto_approved_claims + summary.ai_human_reviewed_claims).toLocaleString()}
            </span>
            {' '}claims with AI assistance. This is limited by the 35% body damage eligibility constraint.
          </div>
        </div>
      </div>
    </Card>
  );
}
