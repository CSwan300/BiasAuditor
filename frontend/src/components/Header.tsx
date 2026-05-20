import React from 'react';

const Header: React.FC = () => {
  return (
    <header>
      <div className="logo-mark">
        <span className="logo-icon">⚖</span>
      </div>
      <div className="header-text">
        <h1>Bias Auditor</h1>
        <p>Fairness & Disparity Analysis Tool</p>
      </div>
      <div className="header-badge">v1.0.0</div>
    </header>
  );
};

export default Header;