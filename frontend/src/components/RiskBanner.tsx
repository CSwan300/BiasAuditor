import React from 'react';

interface Props {
  risk: any;
  meta: any;
}

const RiskBanner: React.FC<Props> = ({ risk, meta }) => {
  const riskLabel = typeof risk === 'object' ? risk?.level : risk;
  const riskScore = typeof risk === 'object' ? risk?.score : (riskLabel === 'High' ? 100 : 0);

  const level = riskLabel?.toLowerCase() || 'low';

  const rowCount = meta?.total_rows || meta?.rows || 0;
  const targetCol = meta?.prediction_column || meta?.outcome_column || 'N/A';

  return (
    <div className={`risk-banner ${level}`}>
      <div className={`risk-score-ring ${level}`}>{riskScore}%</div>
      <div className="risk-info">
        <h2>{riskLabel || 'Unknown'} Risk</h2>
        <p>
          {risk?.flagged_characteristics?.length > 0
            ? `Flagged: ${risk.flagged_characteristics.join(', ')}`
            : 'Audit complete. Check attribute details below.'}
        </p>
      </div>
      <div className="risk-meta">
        <div className="meta-item">
          Rows <span className="meta-value">{rowCount.toLocaleString()}</span>
        </div>
        <div className="meta-item">
          Target <span className="meta-value">{targetCol}</span>
        </div>
      </div>
    </div>
  );
};

export default RiskBanner;