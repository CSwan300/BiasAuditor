import React from 'react';
import { AuditResponse } from '../types';

interface Props {
  risk: AuditResponse['overall_risk'];
  meta: AuditResponse['metadata'];
}

const RiskBanner: React.FC<Props> = ({ risk, meta }) => {
  const level = risk.level.toLowerCase();

  return (
    <div className={`risk-banner ${level}`}>
      <div className={`risk-score-ring ${level}`}>{risk.score}%</div>
      <div className="risk-info">
        <h2>{risk.level} Risk</h2>
        <p>
          {risk.flagged_characteristics.length > 0
            ? `Flagged: ${risk.flagged_characteristics.join(', ')}`
            : 'No significant disparity detected.'}
        </p>
      </div>
      <div className="risk-meta">
        <div className="meta-item">Rows <span className="meta-value">{meta.total_rows.toLocaleString()}</span></div>
        <div className="meta-item">Target <span className="meta-value">{meta.prediction_column}</span></div>
      </div>
    </div>
  );
};

export default RiskBanner;