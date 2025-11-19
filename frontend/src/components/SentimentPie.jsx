import React from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';

const COLORS = {
  Positive: '#16a34a',
  Neutral: '#fbbf24',
  Negative: '#dc2626',
};

const SentimentPie = ({ breakdown }) => {
  if (!breakdown || Object.keys(breakdown).length === 0) {
    return (
      <p className="text-sm text-gray-500 text-center py-10">
        Run an analysis to unlock sentiment distribution.
      </p>
    );
  }

  const formatted = Object.entries(breakdown).map(([label, value]) => ({
    name: label.charAt(0).toUpperCase() + label.slice(1),
    value,
  }));

  return (
    <ResponsiveContainer width="100%" height={250}>
      <PieChart>
        <Pie
          data={formatted}
          dataKey="value"
          innerRadius={60}
          outerRadius={90}
          paddingAngle={2}
        >
          {formatted.map((entry) => (
            <Cell key={entry.name} fill={COLORS[entry.name] || '#3b82f6'} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  );
};

export default SentimentPie;

