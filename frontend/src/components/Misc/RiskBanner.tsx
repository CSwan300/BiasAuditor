import React from 'react';

interface Props {
  risk: any;
  meta: any;
}

export const RiskBanner: React.FC<Props> = ({ risk, meta }) => {
  const rawLabel = typeof risk === 'object' ? risk?.level : risk;
  const riskScore = typeof risk === 'object' ? (risk?.score ?? 0) : 0;

  const displayLabel = rawLabel?.toString().replace(/risk/i, '').trim().toUpperCase() || 'UNKNOWN';
  const levelClass = displayLabel.toLowerCase(); // 'high', 'moderate', 'low'

  const rowCount = meta?.total_rows || meta?.rows || 0;
  const targetCol = meta?.prediction_column || 'AUTO-DETECTED';

  return (
    <div className={`risk-banner ${levelClass}`}>
      <div className="risk-score-container">
        {/* Ring uses the dynamic level class for coloring */}
        <div className={`risk-score-ring ${levelClass}`}>
          {riskScore}%
        </div>

        <div className="risk-definition">
          <strong>Bias Intensity Score</strong>
          <p className="score-explanation">
            {`100% Score: Total Bias. One group gets everything; another group gets nothing.

            80% Score: Severe Disparity. The disadvantaged group is receiving benefits at only 1/5th the rate of the privileged group.

            0% Score: Perfect Fairness. Every group is receiving the outcome at the same rate.`}
          </p>
        </div>
      </div>

      <div className="risk-info">
        <h2>{displayLabel} RISK</h2>
        <p>
          {risk?.flagged_characteristics?.length > 0
            ? `Impacted Attributes: ${risk.flagged_characteristics.join(', ')}`
            : 'Audit complete. No significant disparities found.'}
        </p>
      </div>

      <div className="risk-meta">
        <div className="meta-item">
          ROWS <span className="meta-value">{rowCount.toLocaleString()}</span>
        </div>
        <div className="meta-item">
          TARGET <span className="meta-value">{targetCol.toUpperCase()}</span>
        </div>
      </div>
    </div>
  );
};

export default RiskBanner;