import React from 'react';

const Loader = ({ message = 'Processing your query...' }) => (
  <div className="bg-white p-6 rounded-xl shadow-md border border-gray-100 flex items-center gap-4 animate-pulse">
    <div className="w-12 h-12 rounded-full border-4 border-blue-100 border-t-blue-600 animate-spin" />
    <div>
      <p className="text-sm font-semibold text-gray-800">{message}</p>
      <p className="text-xs text-gray-500">This might take a few seconds.</p>
    </div>
  </div>
);

export default Loader;

