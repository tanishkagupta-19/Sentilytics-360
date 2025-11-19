import React from 'react';

const EmptyState = ({ title, description, actionLabel, onAction }) => (
  <div className="bg-white border border-gray-200 rounded-2xl p-10 text-center shadow-sm">
    <p className="text-5xl mb-4">🛰️</p>
    <h4 className="text-xl font-semibold text-gray-900 mb-2">{title}</h4>
    <p className="text-gray-600 mb-6 max-w-xl mx-auto">{description}</p>
    {actionLabel && (
      <button
        onClick={onAction}
        className="px-6 py-3 rounded-full bg-blue-600 text-white font-semibold hover:bg-blue-700 transition-colors"
      >
        {actionLabel}
      </button>
    )}
  </div>
);

export default EmptyState;

