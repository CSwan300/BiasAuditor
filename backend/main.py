import io
import json
import traceback
import pandas as pd
from typing import Optional
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool

# Internal Modules
from backend.modules.auditor import BiasAuditor
from backend.modules.reporting import build_pdf_response

app = FastAPI()

# 1. CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- HELPER LOGIC ---

def get_clean_df(file: UploadFile) -> pd.DataFrame:
    """Resets the file pointer and returns a Pandas DataFrame."""
    file.file.seek(0)
    content = file.file.read()
    if not content:
        raise ValueError("The uploaded file is empty.")
    return pd.read_csv(io.BytesIO(content))


def process_audit_logic(df: pd.DataFrame, threshold_str: str, p_cols_raw: Optional[str], outcome_col: Optional[str]):
    """
    Unified processing logic to ensure the UI and PDF always match.
    Fixes the 'Not Specified' KeyError by properly handling None targets.
    """
    # 1. Normalize Threshold
    try:
        val = float(str(threshold_str).replace('%', '').strip())
        threshold = val / 100 if val > 1 else val
    except (ValueError, AttributeError):
        threshold = 0.8

    # 2. Parse Protected Columns
    p_cols = []
    if p_cols_raw and str(p_cols_raw).lower() not in ["null", "undefined", "[]", ""]:
        try:
            # Handle JSON list from React or plain string
            p_cols = json.loads(p_cols_raw) if isinstance(p_cols_raw, str) else p_cols_raw
        except Exception:  # Fixed E722
            p_cols = [c.strip() for c in str(p_cols_raw).split(",") if c.strip()]

    # Auto-detect characteristics if the list is still empty
    if not p_cols:
        common_traits = ['gender', 'race', 'age', 'sex', 'ethnicity', 'nationality']
        p_cols = [col for col in df.columns if col.lower() in common_traits]
    if not p_cols:
        # Fallback: Use first two non-numeric columns
        p_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()[:2]

    # 3. Sanitize Outcome Column (The 'Not Specified' Fix)
    target = None
    forbidden_values = ["", "null", "undefined", "not specified", "auto-detected"]
    if outcome_col and str(outcome_col).lower() not in forbidden_values:
        target = str(outcome_col).strip()

    # 4. Run Analysis
    auditor = BiasAuditor(df, fairness_threshold=threshold)
    results = auditor.full_audit(p_cols, target)

    # 5. Populate Metadata for UI
    if "metadata" not in results:
        results["metadata"] = {}

    results["metadata"].update({
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "prediction_column": target if target else "Auto-detected",
        "protected_characteristics_found": p_cols,
        "timestamp": pd.Timestamp.now().isoformat()
    })

    return results, threshold


# --- API ENDPOINTS ---

@app.get("/health")
def health():
    return {"status": "ok", "port": 9999, "info": "BiasAuditor Backend Active"}


@app.post("/audit")
def audit(
        file: UploadFile = File(...),
        fairness_threshold: str = Form(...),
        protected_columns: str = Form(None),
        outcome_column: str = Form(None)
):
    print(f"🚀 Processing Audit: {file.filename}")
    try:
        df = get_clean_df(file)
        result, _ = process_audit_logic(df, fairness_threshold, protected_columns, outcome_column)
        return result
    except Exception as e:
        print(f"❌ AUDIT ERROR: {traceback.format_exc()}")
        return {"detail": str(e)}


@app.post("/report/pdf")
async def generate_pdf_report(
        file: UploadFile = File(...),
        fairness_threshold: str = Form(...),
        protected_columns: Optional[str] = Form(None),
        outcome_column: Optional[str] = Form(None),
        org_name: str = Form("BiasAuditor Analysis"),
):
    print(f"📄 Generating PDF Report for: {org_name}")
    try:
        df = get_clean_df(file)

        def run_pdf_task():
            result, threshold = process_audit_logic(df, fairness_threshold, protected_columns, outcome_column)
            return build_pdf_response(result, org_name, threshold=threshold)

        return await run_in_threadpool(run_pdf_task)
    except Exception as e:
        print(f"❌ PDF ERROR: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9999)