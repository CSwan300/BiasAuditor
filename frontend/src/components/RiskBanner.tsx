import React from 'react';
import { AuditResponse } from '../types';

interface Props {
  // Use 'any' temporarily or update your AuditResponse type to match the backend
  risk: any;
  meta: any;
}

const RiskBanner: React.FC<Props> = ({ risk, meta }) => {
  // 1. Defensive Extraction: Check if risk is an object or a string
  // Based on your auditor.py, 'risk' is likely the string "High" or "Low"
  const riskLabel = typeof risk === 'object' ? risk?.level : risk;
  const riskScore = typeof risk === 'object' ? risk?.score : (riskLabel === 'High' ? 100 : 0);

  // 2. Safe Lowercase: This prevents the 'undefined' crash
  const level = riskLabel?.toLowerCase() || 'low';

  // 3. Metadata fallbacks
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