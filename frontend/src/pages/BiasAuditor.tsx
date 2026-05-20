import React, { useState } from "react";
import { AuditResponse } from "../types";
import { Hero } from "../components/Hero";
import { AuditConfig } from "../components/Audit/AuditConfig";
import { AuditResults } from "../components/Audit/AuditResults";

export const BiasAuditor: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<AuditResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [currentFile, setCurrentFile] = useState<File | null>(null);
  const [lastThreshold, setLastThreshold] = useState(0.8);

  // Set to the port that successfully responded to Invoke-RestMethod
  const API_BASE_URL = "http://127.0.0.1:9999";

  const runAudit = async (file: File, threshold: number, outcomeCol: string) => {
    setLoading(true);
    setError(null);
    setResults(null);
    setCurrentFile(file);
    setLastThreshold(threshold);

    console.log(`🚀 Dispatching Request to ${API_BASE_URL}`, { threshold });

    const formData = new FormData();
    formData.append('file', file);
    formData.append('fairness_threshold', threshold.toString());
    formData.append('protected_columns', JSON.stringify([]));

    if (outcomeCol && outcomeCol.trim() !== "") {
      formData.append('outcome_column', outcomeCol.trim());
    }

    try {
      const response = await fetch(`${API_BASE_URL}/audit`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorDetail = await response.json().catch(() => ({ detail: "Analysis failed." }));
        throw new Error(errorDetail.detail || `Error ${response.status}`);
      }

      const data: AuditResponse = await response.json();
      console.log("✅ Analysis complete, loading results UI");
      setResults(data);
      window.scrollTo({ top: 0, behavior: 'smooth' });

    } catch (err: any) {
      console.error("❌ Connection failed:", err);
      setError(err.message || `Cannot connect to server on port 9999.`);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResults(null);
    setError(null);
    setCurrentFile(null);
  };

  return (
    <main className="fade-in">
      {!results && <Hero />}
      <section className="card-section" id="audit-container">
        {error && (
          <div className="error-banner">
            <p><strong>System Error:</strong> {error}</p>
            <button onClick={() => setError(null)} className="close-error">×</button>
          </div>
        )}

        {results ? (
          <AuditResults
            data={results}
            onReset={handleReset}
            originalFile={currentFile}
            threshold={lastThreshold}
          />
        ) : (
          <AuditConfig onRun={runAudit} loading={loading} />
        )}
      </section>

      {loading && (
        <div className="loading-overlay">
          <div className="spinner"></div>
          <p>Processing Dataset & Auditing Bias...</p>
        </div>
      )}
    </main>
  );
};