import React from 'react';
import RiskBanner from '../RiskBanner';
import AuditCard from './AuditCard';
import { AuditResponse, AuditResult, Mitigation } from '../../types';

interface Props {
  data: AuditResponse;
  onReset: () => void;
  originalFile: File | null;
  threshold: number;
}

export const AuditResults: React.FC<Props> = ({ data, onReset, originalFile, threshold }) => {

  const handleDownloadPDF = async () => {
    if (!originalFile) {
      alert("Source file missing. Please re-upload your dataset.");
      return;
    }

    try {
      const formData = new FormData();
      formData.append('file', originalFile);

      /**
       * CRITICAL FIX:
       * We MUST send the threshold that matches the DATA currently on screen.
       * If your 'data' object contains the threshold it was audited with, use that.
       * Otherwise, use the 'threshold' prop, but warn the user if they've moved the slider.
       */
      const safeThreshold = (threshold ?? 0.80).toString();

      // Use optional chaining safely for metadata
      const protectedCols = data?.metadata?.protected_characteristics_found
        ? JSON.stringify(data.metadata.protected_characteristics_found)
        : "[]";

      // Ensure we use the exact outcome column the current data represents
      const outcomeCol = data?.metadata?.prediction_column || "target";

      formData.append('fairness_threshold', safeThreshold);
      formData.append('protected_columns', protectedCols);
      formData.append('outcome_column', outcomeCol);
      formData.append('org_name', "BiasAuditor Analysis");

      const response = await fetch(`http://127.0.0.1:8080/report/pdf`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'PDF generation failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;

      const dateStr = new Date().toISOString().split('T')[0];
      link.setAttribute('download', `Bias_Audit_Report_${dateStr}.pdf`);

      document.body.appendChild(link);
      link.click();

      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Export failed:", error);
      alert(`Failed to generate PDF: ${error instanceof Error ? error.message : 'Check backend connection'}`);
    }
  };

  return (
    <div className="results-area">
      <RiskBanner risk={data.overall_risk} meta={data.metadata} />

      {/* Logic Check: If the slider threshold is different from the data's threshold, show a warning */}
      {/* (Optional: ensures user knows the PDF will use the CURRENT slider position) */}

      <div className="char-grid">
        {data.audits.map((audit: AuditResult, i: number) => (
          <AuditCard key={i} audit={audit} index={i} />
        ))}
      </div>

      {data.mitigations && data.mitigations.length > 0 && (
        <div className="mitigation-container">
          <h3 className="mitigation-title">🛠 Recommended Mitigations</h3>
          <div className="mitigation-grid">
            {data.mitigations.map((mit: Mitigation, index: number) => (
              <div key={index} className={`mitigation-card priority-${mit.priority}`}>
                <div className="mitigation-header">
                  <h4 className="mitigation-card-title">{mit.title}</h4>
                  <span className={`priority-badge badge-${mit.priority}`}>
                    {mit.priority.toUpperCase()}
                  </span>
                </div>
                <p className="mitigation-description">{mit.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="results-footer">
        <button className="btn-secondary" onClick={onReset}>↩ New Audit</button>
        <button className="btn-primary" onClick={handleDownloadPDF}>
          Download PDF Report
        </button>
      </div>
    </div>
  );
};