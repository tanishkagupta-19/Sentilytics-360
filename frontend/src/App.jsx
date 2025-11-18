import React, { useState } from 'react';

// This is the main application component.
const App = () => {
  // Use state to manage which view is currently displayed.
  const [view, setView] = useState('landing'); // 'landing' or 'dashboard'

  // Header component used on both pages for consistency.
  const Header = () => (
    <header className="bg-white p-4 shadow-md sticky top-0 z-50">
      <div className="container mx-auto flex justify-between items-center">
        {/* Logo and title */}
        <div className="flex items-center space-x-2">
          {/* Using an inline SVG for the logo */}
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-8 h-8 text-blue-600">
            <path fillRule="evenodd" d="M11.47 2.47a.75.75 0 011.06 0l7.5 7.5a.75.75 0 11-1.06 1.06L12 4.061 5.03 11.03a.75.75 0 11-1.06-1.06l7.5-7.5zM11.25 4.5v7.35l-3.277 3.278a.75.75 0 01-1.06-1.06l4.5-4.5a.75.75 0 011.06 0l4.5 4.5a.75.75 0 01-1.06 1.06L12.75 11.85V4.5h-1.5z" clipRule="evenodd" />
            <path d="M12.75 18a.75.75 0 01-.75-.75V15a.75.75 0 011.5 0v2.25c0 .414-.336.75-.75.75zM8.25 18a.75.75 0 01-.75-.75V15a.75.75 0 011.5 0v2.25c0 .414-.336.75-.75.75zM17.25 18a.75.75 0 01-.75-.75V15a.75.75 0 011.5 0v2.25c0 .414-.336.75-.75.75zM12 21a.75.75 0 01-.75-.75V18a.75.75 0 011.5 0v2.25c0 .414-.336.75-.75.75z" />
          </svg>
          <h1 className="text-xl font-bold text-gray-900">Sentilytics 360</h1>
        </div>
        
        {/* Navigation buttons */}
        <nav className="space-x-4 flex">
          <button className="px-4 py-2 rounded-lg font-semibold text-blue-600 hover:text-blue-800 transition-colors duration-300">
            Get Started
          </button>
        </nav>
      </div>
    </header>
  );

  // Landing page component.
  const LandingPage = () => (
    <div className="min-h-screen bg-gray-50 font-sans text-gray-800 flex flex-col">
      <Header />
      
      {/* Hero Section */}
      <section className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4 py-16">
        <h2 className="text-4xl md:text-5xl lg:text-6xl font-extrabold text-gray-900 mb-4 tracking-tight">
          AI-Powered Social Sentiment Analytics
        </h2>
        <p className="text-base md:text-lg text-gray-600 max-w-2xl mb-8 leading-relaxed">
          Unlock the power of public opinion with real-time sentiment analysis across Twitter and Reddit. Transform social media conversations into actionable insights.
        </p>
        <div className="flex flex-col md:flex-row gap-4 mb-16">
          <button 
            onClick={() => setView('dashboard')}
            className="px-8 py-4 rounded-full font-semibold text-white bg-blue-600 hover:bg-blue-700 transition-colors duration-300 transform hover:scale-105 shadow-lg">
            Start Analyzing
          </button>
          <button 
            className="px-8 py-4 rounded-full font-semibold text-blue-600 bg-white border-2 border-blue-600 hover:bg-blue-50 transition-colors duration-300 transform hover:scale-105 shadow-lg">
            View Demo
          </button>
        </div>
        {/* This is the image inserted after the buttons */}
        <img
          src="/Gemini_Generated_Image_8flb7p8flb7p8flb.png"
          alt="AI-Powered Social Sentiment Analytics Dashboard"
          className="rounded-2xl shadow-2xl w-full max-w-2xl h-96 "
        />
      </section>

      {/* Features Section */}
      <section className="bg-white py-16 px-4">
        <div className="container mx-auto text-center">
          <h3 className="text-3xl font-bold text-gray-900 mb-12">
            Comprehensive Sentiment Intelligence
          </h3>
          <p className="text-gray-600 max-w-2xl mx-auto mb-12">Everything you need to understand and analyze public sentiment across social media platforms</p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature cards using inline SVG icons */}
            <div className="flex flex-col items-center text-center p-6 bg-gray-50 rounded-2xl border border-gray-200 shadow-sm">
              <span className="text-4xl mb-4">🌍</span>
              <h4 className="text-xl font-semibold mb-2">Multi-Platform Analysis</h4>
              <p className="text-gray-600 text-sm">Analyze sentiment from Twitter and Reddit in real-time with advanced scraping technology.</p>
            </div>
            <div className="flex flex-col items-center text-center p-6 bg-gray-50 rounded-2xl border border-gray-200 shadow-sm">
              <span className="text-4xl mb-4">💡</span>
              <h4 className="text-xl font-semibold mb-2">AI-Powered Insights</h4>
              <p className="text-gray-600 text-sm">Leverage VADER and DistilBERT models for accurate sentiment classification and trend analysis.</p>
            </div>
            <div className="flex flex-col items-center text-center p-6 bg-gray-50 rounded-2xl border border-gray-200 shadow-sm">
              <span className="text-4xl mb-4">📊</span>
              <h4 className="text-xl font-semibold mb-2">Interactive Dashboards</h4>
              <p className="text-gray-600 text-sm">Visualize sentiment trends with dynamic charts, word clouds, and comprehensive analytics.</p>
            </div>
            <div className="flex flex-col items-center text-center p-6 bg-gray-50 rounded-2xl border border-gray-200 shadow-sm">
              <span className="text-4xl mb-4">🔍</span>
              <h4 className="text-xl font-semibold mb-2">Advanced Filtering</h4>
              <p className="text-gray-600 text-sm">Filter by platform, keyword, date range, and sentiment for precise insights.</p>
            </div>
            <div className="flex flex-col items-center text-center p-6 bg-gray-50 rounded-2xl border border-gray-200 shadow-sm">
              <span className="text-4xl mb-4">📁</span>
              <h4 className="text-xl font-semibold mb-2">Export & Reports</h4>
              <p className="text-gray-600 text-sm">Export insights as CSV or PDF with automated AI-generated summary reports.</p>
            </div>
            <div className="flex flex-col items-center text-center p-6 bg-gray-50 rounded-2xl border border-gray-200 shadow-sm">
              <span className="text-4xl mb-4">📈</span>
              <h4 className="text-xl font-semibold mb-2">Real-Time Trends</h4>
              <p className="text-gray-600 text-sm">Monitor sentiment trends over time with live data updates and predictive analytics.</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-white py-16 px-4 text-center">
        <h3 className="text-3xl font-bold text-gray-900 mb-4">
          Ready to Transform Social Data into Insights?
        </h3>
        <p className="text-gray-600 max-w-2xl mx-auto mb-8">
          Join thousands of analysts, marketers, and researchers who trust Sentilytics 360 for their sentiment analysis needs.
        </p>
        <button 
          onClick={() => setView('dashboard')}
          className="px-8 py-4 rounded-full font-semibold text-white bg-blue-600 hover:bg-blue-700 transition-colors duration-300 transform hover:scale-105 shadow-lg">
          Start Your Analysis Today
        </button>
      </section>
      
      {/* Footer */}
      <footer className="bg-gray-100 py-6 text-center text-gray-500 text-sm">
        © 2024 Sentilytics 360. Empowering insights through sentiment analysis.
      </footer>
    </div>
  );

  // Dashboard component.
  const DashboardPage = () => {
    // A simple mock data object for the dashboard metrics
    const metrics = [
      { label: 'Total Posts Analyzed', value: '15,847', change: '+12.3%', trend: 'up' },
      { label: 'Positive Sentiment', value: '65%', change: '+5.2%', trend: 'up' },
      { label: 'Engagement Rate', value: '8.4%', change: '+2.1%', trend: 'up' },
      { label: 'Neutral Sentiment', value: '25%', change: '-1.8%', trend: 'down' },
      { label: 'Active Users', value: '2,543', change: '+8.7%', trend: 'up' },
      { label: 'Negative Sentiment', value: '10%', change: '-3.4%', trend: 'down' },
    ];
    
    // Using a simple mock for the chart data
    const sentimentData = [
      { label: 'Positive', percentage: 65, color: 'bg-green-500' },
      { label: 'Neutral', percentage: 25, color: 'bg-yellow-500' },
      { label: 'Negative', percentage: 10, color: 'bg-red-500' },
    ];

    return (
      <div className="min-h-screen bg-gray-100 font-sans text-gray-800">
        <header className="bg-white p-4 shadow-md sticky top-0 z-50">
          <div className="container mx-auto flex justify-between items-center">
            <div className="flex items-center space-x-2 cursor-pointer" onClick={() => setView('landing')}>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-8 h-8 text-blue-600">
                <path fillRule="evenodd" d="M11.47 2.47a.75.75 0 011.06 0l7.5 7.5a.75.75 0 11-1.06 1.06L12 4.061 5.03 11.03a.75.75 0 11-1.06-1.06l7.5-7.5zM11.25 4.5v7.35l-3.277 3.278a.75.75 0 01-1.06-1.06l4.5-4.5a.75.75 0 011.06 0l4.5 4.5a.75.75 0 01-1.06 1.06L12.75 11.85V4.5h-1.5z" clipRule="evenodd" />
                <path d="M12.75 18a.75.75 0 01-.75-.75V15a.75.75 0 011.5 0v2.25c0 .414-.336.75-.75.75zM8.25 18a.75.75 0 01-.75-.75V15a.75.75 0 011.5 0v2.25c0 .414-.336.75-.75.75zM17.25 18a.75.75 0 01-.75-.75V15a.75.75 0 011.5 0v2.25c0 .414-.336.75-.75.75zM12 21a.75.75 0 01-.75-.75V18a.75.75 0 011.5 0v2.25c0 .414-.336.75-.75.75z" />
              </svg>
              <h1 className="text-xl font-bold text-gray-900">Sentilytics 360</h1>
            </div>
            <nav className="space-x-4 flex">
              <button className="px-4 py-2 rounded-full font-semibold text-blue-600 bg-white border border-blue-600 hover:bg-blue-50 transition-colors duration-300">
                Export CSV
              </button>
              <button className="px-4 py-2 rounded-full font-semibold text-white bg-blue-600 hover:bg-blue-700 transition-colors duration-300">
                Export PDF
              </button>
            </nav>
          </div>
        </header>
        <main className="container mx-auto py-8 px-4">
          {/* Search & Filter Section */}
          <div className="bg-white p-6 rounded-xl shadow-md border border-gray-200 mb-8">
            <h2 className="text-xl font-bold mb-4">Search & Filters</h2>
            <div className="flex flex-col md:flex-row items-center gap-4">
              <div className="flex-1 w-full">
                <input
                  type="text"
                  placeholder="Enter keywords or hashtags to analyze sentiment across social platforms"
                  className="w-full p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
                />
              </div>
              <div className="flex flex-wrap items-center gap-4 w-full md:w-auto">
                <select className="p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option>All Platforms</option>
                  <option>Twitter</option>
                  <option>Reddit</option>
                </select>
                <select className="p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option>Last 7 Days</option>
                  <option>Last 24 Hours</option>
                  <option>Last 30 Days</option>
                </select>
                <select className="p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option>All Sentiment</option>
                  <option>Positive</option>
                  <option>Neutral</option>
                  <option>Negative</option>
                </select>
                <button className="px-6 py-3 rounded-lg font-semibold text-white bg-blue-600 hover:bg-blue-700 transition-colors duration-300">
                  Analyze
                </button>
              </div>
            </div>
          </div>
          
          {/* Metrics & Insights Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-1 gap-6">
            <div className="lg:col-span-2 space-y-6">
              {/* Key Metrics Section */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {metrics.map((metric, index) => (
                  <div key={index} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <p className="text-gray-500 text-sm">{metric.label}</p>
                    <div className="flex items-end justify-between mt-1">
                      <p className="text-3xl font-bold text-gray-900">{metric.value}</p>
                      <span className={`text-sm font-medium ${metric.trend === 'up' ? 'text-green-500' : 'text-red-500'}`}>
                        {metric.change}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Sentiment Distribution & Key Insights */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Sentiment Distribution Card */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                  <h3 className="text-xl font-bold mb-4">Sentiment Distribution</h3>
                  {/* Placeholder for Pie Chart. In a real app, you would use a library like Recharts. */}
                  <div className="h-64 flex items-center justify-center">
                    <div className="relative w-48 h-48">
                      <div className="absolute inset-0 rounded-full bg-green-500" style={{ clipPath: 'polygon(50% 0%, 50% 65%, 100% 65%, 100% 0%)' }}></div>
                      <div className="absolute inset-0 rounded-full bg-yellow-500" style={{ clipPath: 'polygon(50% 65%, 50% 85%, 100% 85%, 100% 65%)' }}></div>
                      <div className="absolute inset-0 rounded-full bg-red-500" style={{ clipPath: 'polygon(50% 85%, 50% 100%, 100% 100%, 100% 85%)' }}></div>
                      <div className="absolute inset-0 rounded-full bg-white scale-75"></div>
                    </div>
                  </div>
                  <div className="flex justify-center gap-4 mt-4">
                    {sentimentData.map((item, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <span className={`h-3 w-3 rounded-full ${item.color}`}></span>
                        <p className="text-gray-600">{item.label} ({item.percentage}%)</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Key Insights Card */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                  <h3 className="text-xl font-bold mb-4">Key Insights</h3>
                  <div className="space-y-4 text-gray-700">
                    <div className="flex items-start gap-2">
                      <span>🚀</span>
                      <div>
                        <p className="font-semibold">Positive sentiment trending up 23%</p>
                        <p className="text-sm text-gray-500">Driven by product launch discussions</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-2">
                      <span>📉</span>
                      <div>
                        <p className="font-semibold">Negative sentiment down 15%</p>
                        <p className="text-sm text-gray-500">Fewer complaints about pricing</p>
                      </div>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-2">AI Summary</h4>
                      <p className="text-sm text-gray-500 leading-relaxed">Overall sentiment towards "AI technology" has been predominantly positive (65%) over the past week. Major drivers include excitement around new product features and improved user experiences. Negative sentiment primarily stems from concerns about job displacement and privacy issues.</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Trends Over Time Card */}
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <h3 className="text-xl font-bold mb-4">Trends Over Time</h3>
                {/* Placeholder for Line Chart. In a real app, you would use a library like Recharts. */}
                <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
                  <p className="text-gray-400">Placeholder for a Line Chart showing trends over time.</p>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    );
  };

  // Main rendering logic based on the `view` state
  return (
    <>
      {view === 'landing' ? <LandingPage /> : <DashboardPage />}
    </>
  );
};

export default App;