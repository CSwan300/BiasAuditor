// @ts-ignore
import React, { useEffect, useState } from 'react';
import { AuditResult } from '../../types';

interface Props {
  audit: AuditResult;
  index: number;
}

const AuditCard: React.FC<Props> = ({ audit, index }) => {
  const [animate, setAnimate] = useState(false);
  const maxRate = Math.max(...audit.groups.map(g => g.rate), 0.001);

  useEffect(() => {
    setTimeout(() => setAnimate(true), 100);
  }, []);

  return (
    <div className="char-card" style={{ animationDelay: `${index * 0.1}s` }}>
      <div className="card-header">
        <span className="char-name">{audit.characteristic}</span>
        <span className={`flag-badge ${audit.disparity.flag ? 'flagged' : 'ok'}`}>
          {audit.disparity.flag ? '⚑ Flagged' : '✓ OK'}
        </span>
      </div>
      <div className="card-body">
        {audit.groups.map(g => {
          const widthPct = (g.rate / maxRate) * 100;
          const isLowest = g.group === audit.disparity.lowest_group;

          return (
            <div className="group-row" key={g.group}>
              <div className="group-meta">
                <span className="group-label">{g.group}</span>
                <span className="group-rate">{(g.rate * 100).toFixed(1)}%</span>
              </div>
              <div className="bar-track">
                <div
                  className={`bar-fill ${isLowest && audit.disparity.flag ? 'flagged-bar' : ''}`}
                  style={{ width: animate ? `${widthPct}%` : '0%' }}
                />
              </div>
            </div>
          );
        })}

        <div className="disparity-stats">
          <div className="stat-block">
            <div className="stat-label">Ratio (DIR)</div>
            <div className={`stat-value ${audit.disparity.disparate_impact_ratio < 0.8 ? 'bad' : 'good'}`}>
              {audit.disparity.disparate_impact_ratio.toFixed(3)}
            </div>
          </div>
          <div className="stat-block">
            <div className="stat-label">Max Gap</div>
            <div className="stat-value">{(audit.disparity.max_disparity * 100).toFixed(1)}%</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuditCard;