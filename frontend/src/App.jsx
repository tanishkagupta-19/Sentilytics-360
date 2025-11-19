import React, { useState } from 'react';
import { Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
// REMOVED 'ExternalLink' from imports below to fix the warning
import { Search, Download, Share2, MessageCircle, ThumbsUp, Users, TrendingUp, Activity } from 'lucide-react';

// --- Configuration ---
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const COLORS = ['#10B981', '#F59E0B', '#EF4444']; // Green, Yellow, Red

// Common English stop words to ignore in keyword analysis
const STOP_WORDS = new Set([
  'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
  'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there',
  'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no',
  'just', 'him', 'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then',
  'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well',
  'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us', 'is', 'are', 'was', 'were', 'has', 'had'
]);

const App = () => {
  const [view, setView] = useState('landing'); 

  // --- 1. Header Component ---
  const Header = () => (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="container mx-auto px-4 h-16 flex justify-between items-center">
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setView('landing')}>
          <div className="bg-blue-600 p-2 rounded-lg">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-xl font-bold text-gray-900 tracking-tight">Sentilytics 360</h1>
        </div>
        <nav className="flex items-center space-x-4">
          <button className="p-2 text-gray-500 hover:text-blue-600 transition-colors">
            <Share2 className="w-5 h-5" />
          </button>
          <button className="flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-semibold text-blue-600 bg-blue-50 hover:bg-blue-100 transition-colors">
            <Download className="w-4 h-4" />
            <span>Export Report</span>
          </button>
        </nav>
      </div>
    </header>
  );

  // --- 2. Landing Page ---
  const LandingPage = () => (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white font-sans">
      <Header />
      <section className="container mx-auto px-4 pt-20 pb-32 text-center">
        <div className="inline-flex items-center px-4 py-2 rounded-full bg-blue-100 text-blue-700 text-sm font-medium mb-8">
          <span className="flex h-2 w-2 rounded-full bg-blue-600 mr-2"></span>
          Now analyzing X (Twitter) & Reddit in real-time
        </div>
        <h2 className="text-5xl md:text-6xl font-extrabold text-gray-900 mb-6 tracking-tight leading-tight">
          Social Sentiment <br/>
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
            Intelligence Platform
          </span>
        </h2>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-10 leading-relaxed">
          Transform millions of social conversations into actionable insights. 
          Track brand health, monitor crises, and understand your audience with AI-powered analytics.
        </p>
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <button 
            onClick={() => setView('dashboard')}
            className="px-8 py-4 rounded-xl font-bold text-white bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-600/20 transition-all transform hover:-translate-y-1">
            Launch Dashboard
          </button>
          <button className="px-8 py-4 rounded-xl font-bold text-gray-700 bg-white border border-gray-200 hover:bg-gray-50 shadow-sm transition-all">
            View Live Demo
          </button>
        </div>
      </section>
    </div>
  );

  // --- 3. Dashboard Page ---
  const DashboardPage = () => {
    const [query, setQuery] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    // Stats State
    const [stats, setStats] = useState({
      total: 0,
      positive: 0,
      neutral: 0,
      negative: 0,
      engagement: 'N/A',
      activeUsers: 'N/A',
      dominantPlatform: 'N/A',
      topKeyword: 'N/A',
      insightTitle: 'AI Analysis Ready',
      insightDesc: 'Enter a keyword to generate real-time sentiment insights.'
    });

    // Posts State
    const [posts, setPosts] = useState([]);

    // Pie Chart Data
    const pieData = [
      { name: 'Positive', value: stats.positive },
      { name: 'Neutral', value: stats.neutral },
      { name: 'Negative', value: stats.negative },
    ];

    const handleAnalyze = async () => {
      if (!query.trim()) return;
      setLoading(true);
      setError(null);
      setPosts([]); 

      try {
        const response = await fetch(`${API_URL}/api/sentiment?query=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('Analysis failed');
        
        const data = await response.json();
        
        // --- Process Stats ---
        const total = data.total_results || 0;
        const breakdown = data.sentiment_breakdown || {};
        
        const posCount = breakdown.positive || breakdown.Positive || 0;
        const neuCount = breakdown.neutral || breakdown.Neutral || 0;
        const negCount = breakdown.negative || breakdown.Negative || 0;
        
        const posPct = total ? Math.round((posCount / total) * 100) : 0;
        const neuPct = total ? Math.round((neuCount / total) * 100) : 0;
        const negPct = total ? Math.round((negCount / total) * 100) : 0;

        const postList = data.data || [];

        // --- Calculate Dominant Platform ---
        let twitterCount = 0;
        let redditCount = 0;
        
        postList.forEach(post => {
            const src = (post.source || "").toLowerCase();
            if (src.includes("twitter")) twitterCount++;
            else if (src.includes("reddit")) redditCount++;
        });

        let dominant = "N/A";
        if (total > 0) {
            if (twitterCount >= redditCount) dominant = "Twitter (X)";
            else dominant = "Reddit";
        }

        // --- Calculate Top Keyword (Frequency Analysis) ---
        let extractedKeyword = "N/A";
        if (postList.length > 0) {
            const wordCounts = {};
            const searchTerms = query.toLowerCase().split(/\s+/);

            postList.forEach(post => {
                if (!post.text) return;
                const words = post.text.toLowerCase()
                    .replace(/[^\w\s]/g, '') 
                    .split(/\s+/);

                words.forEach(word => {
                    if (word.length > 3 && !STOP_WORDS.has(word) && !searchTerms.includes(word)) {
                        wordCounts[word] = (wordCounts[word] || 0) + 1;
                    }
                });
            });

            let maxCount = 0;
            for (const [word, count] of Object.entries(wordCounts)) {
                if (count > maxCount) {
                    maxCount = count;
                    extractedKeyword = word;
                }
            }
        }

        // --- Generate Dynamic Insight (Honest Logic) ---
        let newInsightTitle = "Mixed Reactions";
        let newInsightDesc = `Opinions on "${query}" are balanced. Neutral sentiment is at ${neuPct}%, indicating a lack of strong consensus on ${dominant}.`;

        if (total > 0) {
            if (posPct > 55) {
                newInsightTitle = "Positive Trend Detected";
                newInsightDesc = `Community sentiment is overwhelmingly positive (${posPct}%). This trend is primarily driven by discussions on ${dominant}.`;
            } else if (negPct > 50) {
                newInsightTitle = "Negative Sentiment Alert";
                newInsightDesc = `Significant negative feedback detected (${negPct}%). Users on ${dominant} are expressing dissatisfaction regarding "${query}".`;
            } else if (posPct > negPct) {
                newInsightTitle = "Generally Favorable";
                newInsightDesc = `While reactions are mixed, positive sentiment (${posPct}%) currently outweighs negative sentiment (${negPct}%).`;
            }
        } else {
            newInsightTitle = "No Data Found";
            newInsightDesc = "Try a different keyword or check your internet connection.";
        }

        setStats({
          total: total.toLocaleString(),
          positive: posPct,
          neutral: neuPct,
          negative: negPct,
          engagement: '8.4%', 
          activeUsers: Math.round(total * 0.4).toLocaleString(),
          dominantPlatform: dominant,
          topKeyword: extractedKeyword,
          insightTitle: newInsightTitle, // Dynamic
          insightDesc: newInsightDesc   // Dynamic
        });

        if (postList && Array.isArray(postList)) {
            setPosts(postList);
        }

      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    // Helper to get sentiment color for the list
    const getSentimentColor = (sentiment) => {
        const s = String(sentiment).toLowerCase();
        if (s.includes('pos')) return 'text-green-600 bg-green-50 border-green-200';
        if (s.includes('neg')) return 'text-red-600 bg-red-50 border-red-200';
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    };

    return (
      <div className="min-h-screen bg-gray-50 font-sans text-gray-800">
        <Header />
        
        <main className="container mx-auto py-8 px-4">
          {/* Search Section */}
          <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-200 mb-8 flex flex-col md:flex-row gap-4 items-center">
            <div className="relative flex-1 w-full">
              <Search className="absolute left-4 top-3.5 text-gray-400 w-5 h-5" />
              <input 
                type="text" 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Analyze a brand, topic, or hashtag (e.g. 'Tesla', 'Bitcoin')" 
                className="w-full pl-12 pr-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all"
              />
            </div>
            <button 
              onClick={handleAnalyze}
              disabled={loading}
              className="px-8 py-3 rounded-xl font-bold text-white bg-blue-600 hover:bg-blue-700 transition-colors disabled:opacity-70 whitespace-nowrap">
              {loading ? 'Analyzing...' : 'Analyze Sentiment'}
            </button>
          </div>

          {error && (
            <div className="mb-8 p-4 bg-red-50 text-red-600 rounded-xl border border-red-100 flex items-center">
              <Activity className="w-5 h-5 mr-2" />
              {error}
            </div>
          )}

          {/* Metric Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {/* Card 1 */}
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
              <div className="flex justify-between items-start mb-4">
                <p className="text-gray-500 font-medium">Total Posts Analyzed</p>
                <MessageCircle className="w-5 h-5 text-blue-500" />
              </div>
              <h3 className="text-4xl font-bold text-gray-900">{stats.total}</h3>
              <p className="text-sm text-green-600 mt-2 flex items-center font-medium">
                <TrendingUp className="w-4 h-4 mr-1" /> +12.3% this week
              </p>
            </div>

            {/* Card 2 */}
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
              <div className="flex justify-between items-start mb-4">
                <p className="text-gray-500 font-medium">Positive Sentiment</p>
                <ThumbsUp className="w-5 h-5 text-green-500" />
              </div>
              <h3 className="text-4xl font-bold text-gray-900">{stats.positive}%</h3>
              <div className="w-full bg-gray-100 rounded-full h-2 mt-4">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: `${stats.positive}%` }}></div>
              </div>
            </div>

            {/* Card 3 */}
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
              <div className="flex justify-between items-start mb-4">
                <p className="text-gray-500 font-medium">Estimated Reach</p>
                <Users className="w-5 h-5 text-purple-500" />
              </div>
              <h3 className="text-4xl font-bold text-gray-900">{stats.activeUsers}</h3>
              <p className="text-sm text-gray-400 mt-2">Unique accounts</p>
            </div>
          </div>

          {/* Charts & Insights Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
            
            {/* Sentiment Distribution */}
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 lg:col-span-1">
              <h3 className="text-lg font-bold text-gray-900 mb-6">Sentiment Distribution</h3>
              <div className="h-64 flex items-center justify-center">
                {stats.total !== 0 && stats.total !== "0" ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={pieData}
                        innerRadius={60}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {pieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="text-gray-400 text-sm flex flex-col items-center">
                    <Activity className="w-8 h-8 mb-2 opacity-20" />
                    No data to display
                  </div>
                )}
              </div>
              <div className="flex justify-center gap-4 mt-4 text-sm">
                <div className="flex items-center"><div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>Pos</div>
                <div className="flex items-center"><div className="w-3 h-3 rounded-full bg-yellow-500 mr-2"></div>Neu</div>
                <div className="flex items-center"><div className="w-3 h-3 rounded-full bg-red-500 mr-2"></div>Neg</div>
              </div>
            </div>

            {/* Key Insights */}
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 lg:col-span-2">
              <h3 className="text-lg font-bold text-gray-900 mb-6">AI Key Insights</h3>
              <div className="space-y-6">
                <div className="flex gap-4 p-4 bg-blue-50 rounded-xl border border-blue-100">
                  <div className="bg-white p-2 rounded-full h-fit shadow-sm">
                    <TrendingUp className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    {/* FIXED: Now shows the REAL Insight Title */}
                    <h4 className="font-bold text-gray-900">{stats.insightTitle}</h4>
                    {/* FIXED: Now shows the REAL Insight Description */}
                    <p className="text-gray-600 text-sm mt-1">
                      {stats.insightDesc}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="p-4 border border-gray-100 rounded-xl">
                    <h5 className="text-gray-500 text-sm font-medium mb-1">Dominant Platform</h5>
                    <p className="font-bold text-gray-900">{stats.dominantPlatform}</p>
                  </div>
                  <div className="p-4 border border-gray-100 rounded-xl">
                    <h5 className="text-gray-500 text-sm font-medium mb-1">Top Keyword</h5>
                    <p className="font-bold text-gray-900 capitalize">{stats.topKeyword}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* --- RECENT MENTIONS TABLE --- */}
          {posts.length > 0 && (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
                <div className="p-6 border-b border-gray-100 flex justify-between items-center">
                    <h3 className="text-lg font-bold text-gray-900">Analyzed Posts</h3>
                    <span className="text-sm text-gray-500">Showing top {Math.min(posts.length, 50)} results</span>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Source</th>
                                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Sentiment</th>
                                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider w-1/2">Content</th>
                                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {posts.slice(0, 50).map((post, index) => (
                                <tr key={index} className="hover:bg-gray-50 transition-colors">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                            post.source === 'Twitter' 
                                            ? 'bg-blue-100 text-blue-800' 
                                            : 'bg-orange-100 text-orange-800'
                                        }`}>
                                            {post.source}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getSentimentColor(post.sentiment)}`}>
                                            {post.sentiment}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <p className="text-sm text-gray-900 line-clamp-2" title={post.text}>
                                            {post.text}
                                        </p>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {post.created_at ? new Date(post.created_at).toLocaleDateString() : 'Just now'}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
          )}

        </main>
      </div>
    );
  };

  return <>{view === 'landing' ? <LandingPage /> : <DashboardPage />}</>;
};

export default App;