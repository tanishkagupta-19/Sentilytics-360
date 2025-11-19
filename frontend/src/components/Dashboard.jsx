import React, { useCallback, useEffect, useMemo, useState } from 'react';
import SentimentPie from './SentimentPie';
import TrendChart from './TrendChart';
import Loader from './Loader';
import EmptyState from './EmptyState';
import InsightsCards from './InsightsCards';

const dateRangeWindow = {
  '24h': 24 * 60 * 60 * 1000,
  '7d': 7 * 24 * 60 * 60 * 1000,
  '30d': 30 * 24 * 60 * 60 * 1000,
  all: Infinity,
};

const buildApiUrl = (base, path) => {
  const trimmed = base ? base.replace(/\/$/, '') : '';
  if (!trimmed) {
    return path;
  }
  return `${trimmed}${path}`;
};

const Dashboard = ({ apiBase, onBackToLanding }) => {
  const [query, setQuery] = useState(() => localStorage.getItem('sentilytics:lastQuery') || '');
  const [platformFilter, setPlatformFilter] = useState('all');
  const [dateRange, setDateRange] = useState('24h');
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const fetchAnalysis = useCallback(
    async (nextQuery) => {
      const activeQuery = (nextQuery ?? query).trim();
      if (!activeQuery) {
        setError('Please enter a keyword or hashtag to analyze.');
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const url = buildApiUrl(
          apiBase,
          `/api/sentiment?query=${encodeURIComponent(activeQuery)}`
        );
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error('API request failed');
        }
        const data = await response.json();
        setResult(data);
        localStorage.setItem('sentilytics:lastQuery', activeQuery);
      } catch (err) {
        setError(err.message || 'Unknown error');
      } finally {
        setLoading(false);
      }
    },
    [apiBase, query]
  );

  useEffect(() => {
    if (!autoRefresh || !query.trim()) return;
    const id = setInterval(() => fetchAnalysis(), 120000);
    return () => clearInterval(id);
  }, [autoRefresh, fetchAnalysis, query]);

  const filteredPosts = useMemo(() => {
    if (!result?.data) return [];
    const platform = platformFilter.toLowerCase();
    const windowMs = dateRangeWindow[dateRange] ?? Infinity;
    const now = Date.now();

    return result.data.filter((post) => {
      if (platform !== 'all') {
        const source = (post.source || '').toLowerCase();
        if (source !== platform) {
          return false;
        }
      }

      if (!post.created_at || windowMs === Infinity) {
        return true;
      }

      const created = new Date(post.created_at).getTime();
      if (Number.isNaN(created)) return true;
      return now - created <= windowMs;
    });
  }, [result, platformFilter, dateRange]);

  const filteredBreakdown = useMemo(() => {
    if (!filteredPosts.length) {
      return result?.sentiment_breakdown || null;
    }

    return filteredPosts.reduce((acc, post) => {
      const label = (post.sentiment || 'Unknown').toLowerCase();
      acc[label] = (acc[label] || 0) + 1;
      return acc;
    }, {});
  }, [filteredPosts, result]);

  const trendData = useMemo(() => {
    if (!filteredPosts.length) return [];
    const map = new Map();

    filteredPosts.forEach((post) => {
      const date = post.created_at ? new Date(post.created_at) : null;
      const key = date && !Number.isNaN(date.getTime())
        ? date.toISOString().slice(0, 10)
        : 'Unknown';
      if (!map.has(key)) {
        map.set(key, { positive: 0, negative: 0, neutral: 0, total: 0 });
      }
      const sentiment = (post.sentiment || 'neutral').toLowerCase();
      const entry = map.get(key);
      if (sentiment.includes('pos')) entry.positive += 1;
      else if (sentiment.includes('neg')) entry.negative += 1;
      else entry.neutral += 1;
      entry.total += 1;
    });

    return Array.from(map.entries())
      .sort((a, b) => (a[0] > b[0] ? 1 : -1))
      .map(([date, values]) => ({ date, ...values }));
  }, [filteredPosts]);

  const insights = useMemo(() => {
    if (!filteredPosts.length) return undefined;
    const lastEntry = trendData[trendData.length - 1];
    const dominantPlatform = filteredPosts.reduce((acc, post) => {
      const key = (post.source || 'Unknown').toLowerCase();
      acc[key] = (acc[key] || 0) + 1;
      return acc;
    }, {});

    const sortedPlatforms = Object.entries(dominantPlatform).sort((a, b) => b[1] - a[1]);
    const topPlatform = sortedPlatforms[0]?.[0] || 'twitter';

    return [
      {
        emoji: '📈',
        title: lastEntry?.positive > lastEntry?.negative
          ? 'Positive sentiment leading'
          : 'Negative sentiment leading',
        description: `Latest window shows ${lastEntry?.positive || 0} positive vs ${lastEntry?.negative || 0} negative signals.`,
      },
      {
        emoji: '🌐',
        title: `Most active platform: ${topPlatform}`,
        description: `${sortedPlatforms[0]?.[1] || 0} posts analyzed from ${topPlatform}.`,
      },
      {
        emoji: '⏱️',
        title: 'Auto refresh enabled',
        description: autoRefresh
          ? 'Streaming new posts every 2 minutes.'
          : 'Enable Auto Refresh to keep insights live.',
      },
    ];
  }, [filteredPosts, trendData, autoRefresh]);

  const totalPosts = filteredPosts.length || result?.total_results || 0;

  return (
    <main className="max-w-6xl mx-auto px-4 py-8">
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 mb-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-end">
          <div className="flex-1 w-full">
            <label className="text-sm font-medium text-gray-600 mb-2 block">Keyword / hashtag</label>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. generative ai, tesla, #fomc"
              className="w-full p-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
            />
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => fetchAnalysis()}
              className="px-6 py-3 rounded-xl bg-blue-600 text-white font-semibold hover:bg-blue-700 transition-colors"
            >
              Analyze
            </button>
            <button
              onClick={onBackToLanding}
              className="px-6 py-3 rounded-xl border border-gray-200 text-gray-600 font-semibold hover:bg-gray-50 transition-colors"
            >
              Back
            </button>
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <div>
            <label className="text-xs uppercase tracking-wide text-gray-500 mb-2 block">
              Platform
            </label>
            <select
              value={platformFilter}
              onChange={(e) => setPlatformFilter(e.target.value)}
              className="w-full rounded-xl border border-gray-200 p-2.5 text-sm"
            >
              <option value="all">All</option>
              <option value="twitter">Twitter</option>
              <option value="reddit">Reddit</option>
            </select>
          </div>
          <div>
            <label className="text-xs uppercase tracking-wide text-gray-500 mb-2 block">
              Date range
            </label>
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="w-full rounded-xl border border-gray-200 p-2.5 text-sm"
            >
              <option value="24h">Last 24 hours</option>
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="all">All time</option>
            </select>
          </div>
          <label className="flex items-center gap-3 text-sm font-semibold text-gray-700 cursor-pointer">
            <input
              type="checkbox"
              className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Live auto-refresh (2 min)
          </label>
        </div>
      </div>

      {loading && <Loader />}

      {error && (
        <div className="bg-white border border-red-200 text-red-700 rounded-2xl p-4 mb-6">
          {error}
        </div>
      )}

      {result && !filteredPosts.length && !loading && (
        <EmptyState
          title="No posts match your filters"
          description="Try widening the date window or switching platform filters to see more conversations."
          actionLabel="Reset filters"
          onAction={() => {
            setPlatformFilter('all');
            setDateRange('all');
          }}
        />
      )}

      {filteredPosts.length > 0 && (
        <div className="space-y-6">
          <div className="grid md:grid-cols-3 gap-4">
            <div className="rounded-2xl border border-gray-100 p-5 bg-white shadow-sm">
              <p className="text-sm text-gray-500">Total posts</p>
              <p className="text-3xl font-bold text-gray-900">{totalPosts}</p>
            </div>
            <div className="rounded-2xl border border-gray-100 p-5 bg-white shadow-sm">
              <p className="text-sm text-gray-500">Dominant sentiment</p>
              <p className="text-2xl font-bold text-gray-900">
                {(() => {
                  if (!filteredBreakdown) return 'N/A';
                  const sorted = Object.entries(filteredBreakdown).sort((a, b) => b[1] - a[1]);
                  return sorted[0]?.[0]?.toUpperCase() || 'N/A';
                })()}
              </p>
            </div>
            <div className="rounded-2xl border border-gray-100 p-5 bg-white shadow-sm">
              <p className="text-sm text-gray-500">Platforms</p>
              <p className="text-2xl font-bold text-gray-900">
                {new Set(filteredPosts.map((post) => post.source || 'Unknown')).size}
              </p>
            </div>
          </div>

          <div className="grid lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 rounded-2xl border border-gray-100 bg-white p-6">
              <div className="flex items-center justify-between mb-4">
                <p className="font-semibold text-gray-900">Sentiment distribution</p>
                <span className="text-xs text-gray-400">Filtered view</span>
              </div>
              <SentimentPie breakdown={filteredBreakdown} />
            </div>
            <div className="lg:col-span-2 rounded-2xl border border-gray-100 bg-white p-6">
              <div className="flex items-center justify-between mb-4">
                <p className="font-semibold text-gray-900">Timeline trends</p>
                <span className="text-xs text-gray-400">Positive vs Negative</span>
              </div>
              <TrendChart data={trendData} />
            </div>
          </div>

          <div className="grid lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 rounded-2xl border border-gray-100 bg-white p-6">
              <h4 className="text-lg font-semibold mb-4 text-gray-900">Posts</h4>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="bg-gray-50 text-gray-600 uppercase text-xs">
                    <tr>
                      <th className="px-4 py-3">Source</th>
                      <th className="px-4 py-3">Content</th>
                      <th className="px-4 py-3">Sentiment</th>
                      <th className="px-4 py-3">Score</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {filteredPosts.slice(0, 25).map((post, index) => (
                      <tr key={`${post.created_at}-${index}`} className="hover:bg-gray-50">
                        <td className="px-4 py-3 capitalize">{post.source || '-'}</td>
                        <td className="px-4 py-3 text-gray-700 max-w-lg">
                          <p className="truncate" title={post.text || '-'}>
                            {post.text || '-'}
                          </p>
                        </td>
                        <td className="px-4 py-3">
                          <span
                            className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                              (post.sentiment || '').toLowerCase().includes('pos')
                                ? 'bg-green-100 text-green-700'
                                : (post.sentiment || '').toLowerCase().includes('neg')
                                ? 'bg-red-100 text-red-700'
                                : 'bg-yellow-100 text-yellow-700'
                            }`}
                          >
                            {post.sentiment || '-'}
                          </span>
                        </td>
                        <td className="px-4 py-3">{post.sentiment_score?.toFixed?.(3) ?? '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {filteredPosts.length > 25 && (
                <p className="text-center text-xs text-gray-500 mt-4">
                  Showing 25 of {filteredPosts.length} posts (filters applied)
                </p>
              )}
            </div>
            <div className="lg:col-span-1 rounded-2xl border border-gray-100 bg-white p-6">
              <h4 className="text-lg font-semibold mb-4 text-gray-900">Insights</h4>
              <InsightsCards insights={insights} />
            </div>
          </div>
        </div>
      )}
    </main>
  );
};

export default Dashboard;

