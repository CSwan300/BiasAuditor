import React from 'react';
import RiskBanner from '../RiskBanner';
import AuditCard from './AuditCard';
import { AuditResponse } from '../../types';

// This fixes the TS2304: Cannot find name 'Props'
interface Props {
  data: AuditResponse;
  onReset: () => void;
  originalFile: File | null;
}

export const AuditResults: React.FC<Props> = ({ data, onReset, originalFile }) => {

  const handleDownloadPDF = async () => {
    if (!originalFile) {
      alert("Original file not found. Please try a new audit.");
      return;
    }

    try {
      const formData = new FormData();
      formData.append('file', originalFile);
      formData.append('protected_columns', JSON.stringify(data.metadata.protected_characteristics_found));
      formData.append('outcome_column', data.metadata.prediction_column);

      const response = await fetch(`http://127.0.0.1:8080/report/pdf`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('PDF generation failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Bias_Audit_Report.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
    } catch (error) {
      console.error("Export failed:", error);
      alert("Failed to generate PDF.");
    }
  };

  return (
    <div className="results-area">
      <RiskBanner risk={data.overall_risk} meta={data.metadata} />

      <div className="char-grid">
        {/* These explicit types fix the TS7006: Parameter 'audit' implicitly has any type */}
        {data.audits.map((audit, i: number) => (
          <AuditCard key={i} audit={audit} index={i} />
        ))}
      </div>

      <div className="results-footer">
        <button className="btn-secondary" onClick={onReset}>
          ↩ New Audit
        </button>
        <button className="btn-primary" onClick={handleDownloadPDF}>
          Download PDF Report
        </button>
      </div>
    </div>
  );
};