import React from 'react';

const CTASection = ({ onStart }) => (
  <section className="bg-blue-600 text-white">
    <div className="max-w-5xl mx-auto px-4 py-16 text-center">
      <p className="text-xs uppercase tracking-[0.4em] text-blue-100 mb-4">next steps</p>
      <h3 className="text-3xl font-bold mb-4">Ready to ship real-time sentiment to your stakeholders?</h3>
      <p className="text-blue-100 max-w-2xl mx-auto mb-8">
        Spin up a workspace, connect your Twitter + Reddit credentials, and ship your first insight report in under 5 minutes.
      </p>
      <button
        onClick={onStart}
        className="px-8 py-3 rounded-full font-semibold bg-white text-blue-700 hover:text-blue-900 transition-transform transform hover:scale-[1.02]"
      >
        Launch Sentilytics 360
      </button>
    </div>
  </section>
);

export default CTASection;

