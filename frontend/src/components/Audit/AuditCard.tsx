import React, { useEffect, useState } from 'react';
import { AuditResult } from '../../types';

interface Props {
  audit: AuditResult;
  index: number;
}

const AuditCard: React.FC<Props> = ({ audit, index }) => {
  const [animate, setAnimate] = useState(false);

  // DESTRICTURING: Ensure we grab the flag and groups correctly
  const {
    flag,
    disparate_impact_ratio,
    max_disparity,
    lowest_group
  } = audit.disparity;

  // Rates from backend are now 0-100 (e.g., 42.1)
  const maxRate = Math.max(...audit.groups.map(g => g.rate), 1);

  useEffect(() => {
    const timer = setTimeout(() => setAnimate(true), 100);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className={`char-card ${flag ? 'flagged' : ''}`} style={{ animationDelay: `${index * 0.1}s` }}>
      <div className="card-header">
        <span className="char-name">{audit.characteristic}</span>

        {/* CRITICAL FIX: The badge MUST use the backend 'flag' */}
        <span className={`flag-badge ${flag ? 'flagged' : 'ok'}`}>
          {flag ? '⚑ Flagged' : '✓ OK'}
        </span>
      </div>

      <div className="card-body">
        {audit.groups.map(g => {
          // Relative width calculation for the bars
          const widthPct = (g.rate / maxRate) * 100;
          const isLowest = g.group === lowest_group;

          return (
            <div className="group-row" key={g.group}>
              <div className="group-meta">
                <span className="group-label">{g.group}</span>
                {/* Displaying the rate directly as a percentage */}
                <span className="group-rate">{g.rate.toFixed(1)}%</span>
              </div>
              <div className="bar-track">
                <div
                  className={`bar-fill ${isLowest && flag ? 'flagged-bar' : ''}`}
                  style={{ width: animate ? `${widthPct}%` : '0%' }}
                />
              </div>
            </div>
          );
        })}

        <div className="disparity-stats">
          <div className="stat-block">
            <div className="stat-label">Ratio (DIR)</div>
            {/* Color the text red (bad) only if the backend flagged this attribute */}
            <div className={`stat-value ${flag ? 'bad' : 'good'}`}>
              {disparate_impact_ratio.toFixed(3)}
            </div>
          </div>

          <div className="stat-block">
            <div className="stat-label">Max Gap</div>
            {/* Backend sends whole number (e.g., 24.2), simply append % */}
            <div className="stat-value">
              {max_disparity.toFixed(1)}%
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuditCard;