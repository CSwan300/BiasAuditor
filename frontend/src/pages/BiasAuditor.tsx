import React, { useReducer } from "react";
import { AuditResponse } from "../types";
import { Hero } from "../components/Hero";
import { AuditConfig } from "../components/Audit/AuditConfig";
import { AuditResults } from "../components/Audit/AuditResults";

// 1. Define a clear state structure
interface AuditState {
  loading: boolean;
  results: AuditResponse | null;
  error: string | null;
  currentFile: File | null;
  lastThreshold: number;
}

type AuditAction =
  | { type: 'START_AUDIT'; file: File; threshold: number }
  | { type: 'AUDIT_SUCCESS'; payload: AuditResponse }
  | { type: 'AUDIT_FAILURE'; error: string }
  | { type: 'RESET' }
  | { type: 'CLEAR_ERROR' };

const initialState: AuditState = {
  loading: false,
  results: null,
  error: null,
  currentFile: null,
  lastThreshold: 0.8,
};

function auditReducer(state: AuditState, action: AuditAction): AuditState {
  switch (action.type) {
    case 'START_AUDIT':
      return { ...state, loading: true, error: null, results: null, currentFile: action.file, lastThreshold: action.threshold };
    case 'AUDIT_SUCCESS':
      return { ...state, loading: false, results: action.payload };
    case 'AUDIT_FAILURE':
      return { ...state, loading: false, error: action.error };
    case 'RESET':
      return { ...initialState };
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    default:
      return state;
  }
}

export const BiasAuditor: React.FC = () => {
  const [state, dispatch] = useReducer(auditReducer, initialState);
  const { loading, results, error, currentFile, lastThreshold } = state;

  // Use environment variables for the FastAPI URL
  // i cant be bothered to set it up atm but you would if it was to be launced in prod

  const API_BASE_URL =  "http://127.0.0.1:9999";

  const runAudit = async (file: File, threshold: number, outcomeCol: string) => {
    dispatch({ type: 'START_AUDIT', file, threshold });

    const formData = new FormData();
    formData.append('file', file);
    formData.append('fairness_threshold', threshold.toString());
    formData.append('protected_columns', JSON.stringify([]));

    if (outcomeCol?.trim()) {
      formData.append('outcome_column', outcomeCol.trim());
    }

    try {
      const response = await fetch(`${API_BASE_URL}/audit`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorDetail = await response.json().catch(() => ({ detail: "Analysis failed." }));
        throw new Error(errorDetail.detail || `Server Error: ${response.status}`);
      }

      const data: AuditResponse = await response.json();
      dispatch({ type: 'AUDIT_SUCCESS', payload: data });
      window.scrollTo({ top: 0, behavior: 'smooth' });

    } catch (err) {
      const message = err instanceof Error ? err.message : "An unexpected error occurred";
      dispatch({ type: 'AUDIT_FAILURE', error: message });
    }
  };

  return (
    <main className="fade-in">
      {!results && <Hero />}

      <section className="card-section" id="audit-container">
        {error && (
          <div className="error-banner" role="alert">
            <p><strong>System Error:</strong> {error}</p>
            <button
              onClick={() => dispatch({ type: 'CLEAR_ERROR' })}
              className="close-error"
              aria-label="Dismiss error"
            >
              ×
            </button>
          </div>
        )}

        {results ? (
          <AuditResults
            data={results}
            onReset={() => dispatch({ type: 'RESET' })}
            originalFile={currentFile}
            threshold={lastThreshold}
          />
        ) : (
          <AuditConfig onRun={runAudit} loading={loading} />
        )}
      </section>

      {loading && (
        <div className="loading-overlay" aria-busy="true">
          <div className="spinner"></div>
          <p>Processing Dataset & Auditing Bias...</p>
        </div>
      )}
    </main>
  );
};