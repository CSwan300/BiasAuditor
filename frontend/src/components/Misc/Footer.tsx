import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <div className="footer-grid">
          <div className="footer-info">
            <p className="footer-tagline">Open Source Algorithmic Fairness Audit Tool</p>
          </div>
          <div className="footer-meta">
            <span>&copy; {new Date().getFullYear()} BiasAuditor Project</span>
            <span className="divider">|</span>
            <span>v2.0.0 Stable</span>
          </div>
        </div>
      </div>
    </footer>
  );
};