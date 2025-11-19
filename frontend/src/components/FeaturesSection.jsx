import React from 'react';
import { FiTrendingUp, FiFilter, FiShare2, FiZap, FiDownload, FiShield } from 'react-icons/fi';

const features = [
  {
    icon: <FiTrendingUp />,
    title: 'Cross-platform intelligence',
    description: 'Blend Twitter and Reddit streams with unified normalization and enrichment.',
  },
  {
    icon: <FiZap />,
    title: 'AI signal detection',
    description: 'RoBERTa-powered sentiment scoring with contextual summaries for exec readouts.',
  },
  {
    icon: <FiFilter />,
    title: 'Precision filters',
    description: 'Slice by platform, sentiment, time horizon, and keyword clusters instantly.',
  },
  {
    icon: <FiShare2 />,
    title: 'Collaboration ready',
    description: 'Share live dashboards or embed insights via API + webhooks.',
  },
  {
    icon: <FiDownload />,
    title: 'One-click exports',
    description: 'Generate CSV, PDF, or slide-ready summaries with source links.',
  },
  {
    icon: <FiShield />,
    title: 'Enterprise-grade security',
    description: 'SOC2-aligned controls, audit logging, and RBAC baked in.',
  },
];

const FeaturesSection = () => (
  <section className="bg-white py-16">
    <div className="max-w-6xl mx-auto px-4">
      <div className="text-center max-w-3xl mx-auto mb-12">
        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-blue-600 mb-3">platform</p>
        <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">Purpose-built for insight teams</h2>
        <p className="text-gray-600">
          Everything analysts, marketing strategists, and research partners need to move from noise to decisions.
        </p>
      </div>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature) => (
          <div
            key={feature.title}
            className="rounded-2xl border border-gray-100 p-6 shadow-sm hover:shadow-md transition-shadow bg-gradient-to-br from-white to-gray-50"
          >
            <div className="text-2xl text-blue-600 mb-4">{feature.icon}</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
            <p className="text-gray-600 text-sm leading-relaxed">{feature.description}</p>
          </div>
        ))}
      </div>
    </div>
  </section>
);

export default FeaturesSection;

