import React from 'react';

const defaultInsights = [
  {
    emoji: '🚀',
    title: 'Positive sentiment trending up',
    description: 'Product launch buzz driving uplift vs last 7d.',
  },
  {
    emoji: '⚠️',
    title: 'Watch emerging negative cohort',
    description: 'Privacy concerns resurfacing in Reddit threads.',
  },
  {
    emoji: '📣',
    title: 'Top advocacy channel',
    description: 'Twitter mentions converting at 1.8x Reddit reach.',
  },
];

const InsightsCards = ({ insights = defaultInsights }) => (
  <div className="space-y-4">
    {insights.map((insight) => (
      <div
        key={insight.title}
        className="flex items-start gap-3 rounded-2xl border border-gray-100 p-4 bg-white shadow-sm"
      >
        <span className="text-2xl">{insight.emoji}</span>
        <div>
          <p className="font-semibold text-gray-900">{insight.title}</p>
          <p className="text-sm text-gray-500">{insight.description}</p>
        </div>
      </div>
    ))}
  </div>
);

export default InsightsCards;

