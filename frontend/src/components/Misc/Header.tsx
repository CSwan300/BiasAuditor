import React from 'react';

export const Header: React.FC = () => {
  return (
    <header className="site-header">
      <div className="header-inner">
        <div className="logo">
          <span className="logo-icon">⚖</span>
          <span className="logo-text">Bias<strong>Auditor</strong></span>
          <span className="version-badge">v2.0</span>
        </div>
        <nav className="header-nav">
            {/*ill add these later lol */}
          {/*<a href="#audit" className="nav-link">Audit</a>*/}
          {/*<a href="#docs" className="nav-link">Documentation</a>*/}
          {/*<a href="https://github.com" className="nav-link">GitHub</a>*/}
        </nav>
      </div>
    </header>
  );
};