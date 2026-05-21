import React from 'react';

const metrics = [
  { title: 'Disparate Impact', text: 'Compares selection rates. Below 80% signals potential adverse impact.' },
  { title: 'Equal Opportunity', text: 'Checks if True Positive Rates are equal across groups.' },
  { title: 'Statistical Significance', text: 'Uses Fisher/Chi-Squared to ensure results aren’t just noise.' }
];

export const MetricsReference = () => (
  <section className="about-section card-section">
    <div className="metrics-grid">
      {metrics.map(m => (
        <div key={m.title} className="metric-card">
          <div className="metric-icon">
            {/* Icons can be added here as SVG or CSS elements */}
          </div>
          <h4>{m.title}</h4>
          <p>{m.text}</p>
        </div>
      ))}
    </div>
  </section>
);