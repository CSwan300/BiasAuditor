import {useState} from "react";
import {AuditResponse} from "../types";
import {Hero} from "../components/Hero";
import { AuditConfig } from "../components/Audit/AuditConfig";
import { AuditResults } from "../components/Audit/AuditResults";
import { MetricsReference } from "../components/MetricsReference";

export const BiasAuditor: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<AuditResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  // NEW: State to hold the actual file object for the PDF export
  const [currentFile, setCurrentFile] = useState<File | null>(null);

  const API_BASE_URL = "http://127.0.0.1:8080";

  const runAudit = async (file: File, threshold: number, outcomeCol: string) => {
    setLoading(true);
    setError(null);
    setCurrentFile(file); // SAVE THE FILE HERE

    const formData = new FormData();
    formData.append('file', file);
    formData.append('fairness_threshold', (threshold / 100).toString());

    if (outcomeCol.trim()) {
      formData.append('outcome_column', outcomeCol.trim());
    }

    try {
      const res = await fetch(`${API_BASE_URL}/audit`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "The audit failed to process.");
      }

      const data: AuditResponse = await res.json();
      setResults(data);
      window.scrollTo({ top: 0, behavior: 'smooth' });

    } catch (err: any) {
      setError(err.message || "Connection failed.");
    } finally {
      setLoading(false);
    }
  };

  const resetAudit = () => {
    setResults(null);
    setError(null);
    setCurrentFile(null); // Clear file on reset
  };

  return (
    <main className="fade-in">
      {!results && <Hero />}

      <section className="upload-section card-section" id="audit">
        <div className="section-header">
          <h2>{results ? "Audit Analysis" : "Configure Audit"}</h2>
          {results && (
            <span className="timestamp">
              Generated: {new Date(results.metadata.timestamp).toLocaleString()}
            </span>
          )}
        </div>

        {error && (
          <div className="error-banner">
            <p>{error}</p>
            <button onClick={() => setError(null)}>×</button>
          </div>
        )}

        {results ? (
          /* PASS THE FILE TO RESULTS */
          <AuditResults
            data={results}
            onReset={resetAudit}
            originalFile={currentFile}
          />
        ) : (
          <AuditConfig onRun={runAudit} loading={loading} />
        )}
      </section>

      {!results && !loading && <MetricsReference />}
    </main>
  );
};