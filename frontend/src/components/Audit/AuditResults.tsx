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
  const API_BASE_URL = "http://127.0.0.1:9999";

  const handleDownloadPDF = async () => {
    if (!originalFile) {
      alert("Source file missing. Please re-upload your dataset.");
      return;
    }

    try {
      const formData = new FormData();
      formData.append('file', originalFile);

      const safeThreshold = (threshold ?? 0.80).toString();
      const foundCols = data?.metadata?.protected_characteristics_found || [];
      formData.append('protected_columns', JSON.stringify(foundCols));

      const rawOutcome = data?.metadata?.prediction_column || "";
      const forbidden = ["not specified", "auto-detected", "null", "undefined"];
      const safeOutcome = forbidden.includes(rawOutcome.toLowerCase()) ? "" : rawOutcome;

      formData.append('outcome_column', safeOutcome);
      formData.append('org_name', "BiasAuditor Analysis");
      formData.append('fairness_threshold', safeThreshold);

      const response = await fetch(`${API_BASE_URL}/report/pdf`, {
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
      alert(`Failed to generate PDF: ${error instanceof Error ? error.message : 'Check backend connection'}`);
    }
  };

  return (
    <div className="results-area">
      <RiskBanner risk={data.overall_risk} meta={data.metadata} />

      <div className="char-grid">
        {(data.audits || []).map((audit: AuditResult, i: number) => (
          <AuditCard key={i} audit={audit} index={i} />
        ))}
      </div>

      {data.mitigations && data.mitigations.length > 0 && (
        <div className="mitigation-container">
          <h3 className="mitigation-title">Recommended Mitigations</h3>
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
        <button className="btn-secondary" onClick={onReset}>
          New Audit
        </button>
        <button className="btn-primary" onClick={handleDownloadPDF}>
          Download PDF Report
        </button>
      </div>
    </div>
  );
};