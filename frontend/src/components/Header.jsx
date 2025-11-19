import React from 'react';

const Header = ({
  onLogoClick,
  ctaLabel = 'Get Started',
  onCtaClick,
  secondaryLabel,
  onSecondaryClick,
  showBackButton = false,
}) => {
  return (
    <header className="bg-white/90 backdrop-blur border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <button
          onClick={onLogoClick}
          className="flex items-center space-x-2 focus:outline-none"
        >
          <span className="inline-flex items-center justify-center w-10 h-10 rounded-xl bg-blue-100 text-blue-600 font-semibold">
            S360
          </span>
          <div className="text-left">
            <p className="text-lg font-bold text-gray-900">Sentilytics 360</p>
            <p className="text-xs text-gray-500">Social sentiment intelligence</p>
          </div>
        </button>

        <div className="flex items-center gap-3">
          {secondaryLabel && (
            <button
              onClick={onSecondaryClick}
              className="hidden sm:inline-flex px-4 py-2 rounded-full border border-gray-200 text-sm font-semibold text-gray-600 hover:bg-gray-50 transition-colors"
            >
              {secondaryLabel}
            </button>
          )}
          <button
            onClick={onCtaClick}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-blue-600 text-white text-sm font-semibold shadow-lg shadow-blue-600/30 hover:bg-blue-700 transition-transform transform hover:-translate-y-0.5"
          >
            {showBackButton && (
              <span aria-hidden className="text-lg">
                ←
              </span>
            )}
            {ctaLabel}
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;

