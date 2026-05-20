import React, { useState, useRef } from 'react';
import { AuditResponse } from '../types';
import RiskBanner from './RiskBanner';
import AuditCard from './AuditCard';

const API_BASE = 'http://localhost:8000';

export const BiasAuditor: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<AuditResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = (f: File) => {
    const ext = f.name.split('.').pop()?.toLowerCase();
    if (!['csv', 'xlsx', 'xls'].includes(ext || '')) {
      setError('Unsupported file type. Please upload a CSV or Excel file.');
      return;
    }
    setFile(f);
    setError(null);
  };

  const runAudit = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_BASE}/audit`, { method: 'POST', body: formData });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Audit failed');
      setResults(data);
    } catch (err: any) {
      setError(err.message || 'Could not reach server');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header>
        <div className="logo-mark"><span className="logo-icon">⚖</span></div>
        <div className="header-text">
          <h1>Bias Auditor</h1>
          <p>Fairness & Disparity Analysis Tool</p>
        </div>
        <div className="header-badge">v1.0.0</div>
      </header>

      <main>
        {!results && (
          <section className="upload-section">
            <div className="section-label">Dataset Upload</div>
            <div
              id="drop-zone"
              onDragOver={(e) => e.preventDefault()}
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="upload-icon">🗂</div>
              <div className="upload-title">Drop your dataset here</div>
              <p className="upload-sub">Drag & drop a file, or <span>browse</span></p>
            </div>
            <input
              type="file"
              ref={fileInputRef}
              onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
              style={{ display: 'none' }}
            />

            {file && (
              <div className="file-selected-bar visible">
                <span className="file-icon">📄</span>
                <span className="file-name">{file.name}</span>
                <button onClick={runAudit} id="audit-btn" className="visible" disabled={loading}>
                   {loading ? 'Processing...' : '⚡ Run Bias Audit'}
                </button>
              </div>
            )}
          </section>
        )}

        {loading && (
          <div id="loading" className="visible">
            <div className="spinner"></div>
            <div className="loading-label">Analysing dataset…</div>
          </div>
        )}

        {error && <div id="error-box" className="visible">⚠ {error}</div>}

        {results && (
          <div id="results" className="visible">
            <RiskBanner risk={results.overall_risk} meta={results.metadata} />

            <div className="section-label">Protected Characteristic Analysis</div>
            <div className="char-grid">
              {results.audits.map((audit, i) => (
                <AuditCard key={audit.characteristic} audit={audit} index={i} />
              ))}
            </div>

            <button onClick={() => setResults(null)} id="reset-btn">
              ↩ Upload New Dataset
            </button>
          </div>
        )}
      </main>
    </div>
  );
};