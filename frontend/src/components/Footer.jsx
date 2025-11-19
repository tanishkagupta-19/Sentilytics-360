import React from 'react';

const Footer = () => (
  <footer className="bg-gray-900 text-gray-400 py-8">
    <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row justify-between items-center gap-4 text-sm">
      <p>© {new Date().getFullYear()} Sentilytics 360. All rights reserved.</p>
      <div className="flex items-center gap-4">
        <a href="#privacy" className="hover:text-white transition-colors">
          Privacy
        </a>
        <a href="#terms" className="hover:text-white transition-colors">
          Terms
        </a>
        <a href="mailto:support@sentilytics.ai" className="hover:text-white transition-colors">
          Contact
        </a>
      </div>
    </div>
  </footer>
);

export default Footer;

