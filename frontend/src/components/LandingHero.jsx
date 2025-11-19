import React from 'react';
import CountUp from 'react-countup';

const LandingHero = ({ onGetStarted, onViewDemo, stats }) => {
  const fallbackStats = {
    analyzed: 15847,
    positive: 65,
    sources: 2,
  };
  const mergedStats = { ...fallbackStats, ...(stats || {}) };

  return (
    <section className="bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-16 md:py-24 grid md:grid-cols-2 gap-12 items-center">
        <div>
          <p className="uppercase text-xs font-semibold tracking-[0.2em] text-blue-600 mb-4">
            Real-time data ops
          </p>
          <h1 className="text-4xl md:text-5xl font-black text-gray-900 leading-tight mb-6">
            Understand every conversation in <span className="text-blue-600">seconds</span>.
          </h1>
          <p className="text-lg text-gray-600 mb-8">
            Sentilytics 360 transforms live Twitter + Reddit chatter into actionable sentiment trends, key drivers, and executive-ready summaries.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 mb-10">
            <button
              onClick={onGetStarted}
              className="px-8 py-4 rounded-full font-semibold text-white bg-blue-600 hover:bg-blue-700 transition-colors duration-300 transform hover:scale-[1.02] shadow-lg shadow-blue-500/40"
            >
              Launch Dashboard
            </button>
            <button
              onClick={onViewDemo}
              className="px-8 py-4 rounded-full font-semibold text-blue-600 bg-white border-2 border-blue-100 hover:border-blue-300 transition-all duration-300"
            >
              Watch 2-min Demo
            </button>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="p-5 rounded-2xl bg-white shadow-sm border border-gray-100 text-center">
              <p className="text-sm text-gray-500 mb-1">Posts analyzed</p>
              <p className="text-2xl font-bold text-gray-900">
                <CountUp end={mergedStats.analyzed} separator="," duration={2} />
              </p>
            </div>
            <div className="p-5 rounded-2xl bg-white shadow-sm border border-gray-100 text-center">
              <p className="text-sm text-gray-500 mb-1">Positive sentiment</p>
              <p className="text-2xl font-bold text-green-600">
                <CountUp end={mergedStats.positive} duration={2} />%
              </p>
            </div>
            <div className="p-5 rounded-2xl bg-white shadow-sm border border-gray-100 text-center">
              <p className="text-sm text-gray-500 mb-1">Sources connected</p>
              <p className="text-2xl font-bold text-blue-600">
                <CountUp end={mergedStats.sources} duration={2} />
              </p>
            </div>
          </div>
        </div>

        <div className="relative">
          <div className="aspect-[4/3] rounded-3xl bg-gradient-to-br from-blue-100 via-white to-purple-100 p-6 shadow-2xl">
            <div className="bg-white rounded-2xl h-full shadow-lg border border-gray-100 p-6 flex flex-col gap-4">
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold text-gray-700">Live Sentiment</p>
                <span className="text-xs text-green-500 font-semibold">LIVE</span>
              </div>
              <div className="grid grid-cols-3 gap-4 text-center">
                {['Positive', 'Neutral', 'Negative'].map((label, idx) => (
                  <div key={label} className="rounded-xl bg-gray-50 p-3">
                    <p className="text-xs text-gray-500 mb-1">{label}</p>
                    <p className={`text-xl font-bold ${idx === 0 ? 'text-green-600' : idx === 1 ? 'text-yellow-600' : 'text-red-500'}`}>
                      {mergedStats.sentiment?.[label.toLowerCase()] ?? ['65%', '25%', '10%'][idx]}
                    </p>
                  </div>
                ))}
              </div>
              <div className="flex-1 rounded-xl bg-gray-50 flex flex-col justify-center items-center text-gray-400 text-sm">
                <p>Realtime trends visualization</p>
                <p className="text-xs">Connect data sources to unlock insights</p>
              </div>
            </div>
          </div>
          <div className="absolute -bottom-6 -left-6 bg-white shadow-xl border border-gray-100 rounded-2xl p-4 w-40">
            <p className="text-xs text-gray-500">Keyword velocity</p>
            <p className="text-2xl font-bold text-gray-900">+23%</p>
            <p className="text-[11px] text-gray-400">vs last 24h</p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default LandingHero;

