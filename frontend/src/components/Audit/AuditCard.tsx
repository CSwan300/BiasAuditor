import React, { useEffect, useState } from 'react';
import { AuditResult } from '../../types';

interface Props {
  audit: AuditResult;
  index: number;
}

const AuditCard: React.FC<Props> = ({ audit, index }) => {
  const [animate, setAnimate] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setAnimate(true), 100);
    return () => clearTimeout(timer);
  }, []);

  // Safety fallback for missing disparity data
  const disparity = audit.disparity || {
    flag: false,
    disparate_impact_ratio: 0,
    max_disparity: 0,
    lowest_group: ""
  };

  const groups = audit.groups || [];
  const maxRate = Math.max(...groups.map(g => g.rate || 0), 1);

  return (
    <div className={`char-card ${disparity.flag ? 'flagged' : ''}`} style={{ animationDelay: `${index * 0.1}s` }}>
      <div className="card-header">
        <span className="char-name">{audit.characteristic}</span>
        <span className={`flag-badge ${disparity.flag ? 'flagged' : 'ok'}`}>
          {disparity.flag ? '⚑ Flagged' : '✓ OK'}
        </span>
      </div>

      <div className="card-body">
        {groups.map((g, i) => {
          const widthPct = ((g.rate || 0) / maxRate) * 100;
          return (
            <div className="group-row" key={i}>
              <div className="group-meta">
                <span className="group-label">{g.group}</span>
                <span className="group-rate">{(g.rate ?? 0).toFixed(1)}%</span>
              </div>
              <div className="bar-track">
                <div
                  className={`bar-fill ${g.group === disparity.lowest_group && disparity.flag ? 'flagged-bar' : ''}`}
                  style={{ width: animate ? `${widthPct}%` : '0%' }}
                />
              </div>
            </div>
          );
        })}

        <div className="disparity-stats">
          <div className="stat-block">
            <div className="stat-label">Ratio (DIR)</div>
            <div className={`stat-value ${disparity.flag ? 'bad' : 'good'}`}>
              {(disparity.disparate_impact_ratio ?? 0).toFixed(3)}
            </div>
          </div>
          <div className="stat-block">
            <div className="stat-label">Max Gap</div>
            <div className="stat-value">{(disparity.max_disparity ?? 0).toFixed(1)}%</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuditCard;