import React, { useState, useEffect } from 'react';

type Theme = 'dark' | 'light';

export const Header: React.FC = () => {
  const [theme, setTheme] = useState<Theme>(() => {
    if (typeof window !== 'undefined') {
      return (localStorage.getItem('bias-auditor-theme') as Theme) ?? 'dark';
    }
    return 'dark';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('bias-auditor-theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(t => (t === 'dark' ? 'light' : 'dark'));

  return (
    <header className="site-header">
      <div className="header-inner">
        <div className="logo">
          <span className="logo-icon">⚖</span>
          <span className="logo-text">Bias<strong>Auditor</strong></span>
          <span className="version-badge">v2.0</span>
        </div>

        <nav className="header-nav">
          {/* Nav links go here */}
        </nav>

        <button
          className="theme-toggle"
          onClick={toggleTheme}
          aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
          <span className="theme-toggle__track">
            <span className="theme-toggle__thumb" />
          </span>
          <span className="theme-toggle__icon theme-toggle__icon--sun" aria-hidden="true">☀</span>
          <span className="theme-toggle__icon theme-toggle__icon--moon" aria-hidden="true">☽</span>
        </button>
      </div>
    </header>
  );
};