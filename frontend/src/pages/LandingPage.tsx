import { useState, useRef } from 'react';
import { AuditResponse } from '../types';
import RiskBanner from '../components/RiskBanner';
import AuditCard from '../components/AuditCard';

const API_BASE = window.location.protocol + "//" + window.location.hostname + ":8000";

export const LandingPage = () => {
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
      setError('Could not reach the API server. Ensure backend is on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setResults(null);
    setFile(null);
    setError(null);
  };

  return (
    <main>
      {!results ? (
        <section className="upload-section">
          <div className="section-label">Dataset Upload</div>
          <div
            id="drop-zone"
            className={file ? 'has-file' : ''}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
            }}
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
            accept=".csv,.xlsx,.xls"
          />

          {file && (
            <div className="file-selected-bar visible">
              <span className="file-icon">📄</span>
              <span className="file-name">{file.name}</span>
              <span className="file-size">{(file.size / 1024).toFixed(1)} KB</span>
            </div>
          )}

          {error && <div id="error-box" className="visible">{error}</div>}

          {file && !loading && (
            <button onClick={runAudit} id="audit-btn" className="visible">
              ⚡ Run Bias Audit
            </button>
          )}
        </section>
      ) : (
        <div id="results" className="visible">
          <div className="section-label">Audit Results</div>
          <RiskBanner risk={results.overall_risk} meta={results.metadata} />

          <div className="section-label">Protected Characteristic Analysis</div>
          <div className="char-grid">
            {results.audits.map((audit, i) => (
              <AuditCard key={audit.characteristic} audit={audit} index={i} />
            ))}
          </div>

          <button onClick={reset} id="reset-btn">
            ↩ Upload New Dataset
          </button>
        </div>
      )}

      {loading && (
        <div id="loading" className="visible">
          <div className="spinner"></div>
          <div className="loading-label">Analysing dataset…</div>
        </div>
      )}
    </main>
  );
};