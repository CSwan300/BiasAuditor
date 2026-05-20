import io
import json
import traceback
import pandas as pd
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from typing import Optional

# Internal module imports - ensure these files exist in /backend/modules/
from backend.modules.auditor import BiasAuditor
from backend.modules.reporting import build_pdf_response

app = FastAPI(title="BiasAuditor API", version="2.0.0")

# --- WIDE OPEN CORS FOR LOCAL DEV ---
# If this still hangs, replace ["*"] with your frontend URL like ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    """Simple health check to verify the server is listening."""
    print("Health check pinged")
    return {"status": "ok", "version": "2.0.0"}


@app.post("/audit")
async def audit(
        file: UploadFile = File(...),
        protected_columns: Optional[str] = Form(None),
        outcome_column: Optional[str] = Form(None),
        fairness_threshold: str = Form("0.80"),
):
    print(f"--- [AUDIT START] Received file: {file.filename} ---")
    try:
        # 1. Read bytes immediately to clear the browser buffer
        content = await file.read()
        print(f"File size read: {len(content)} bytes")

        # 2. Run the heavy processing in a threadpool so the main loop stays alive
        async def process():
            df = pd.read_csv(io.BytesIO(content))

            # Clean inputs
            raw_t = str(fairness_threshold).replace('%', '').strip()
            f_threshold = float(raw_t) / 100 if float(raw_t) > 1 else float(raw_t)

            p_cols = []
            if protected_columns and protected_columns not in ["null", "undefined", "[]", ""]:
                try:
                    p_cols = json.loads(protected_columns)
                except:
                    # Handle comma-separated fallback
                    p_cols = [c.strip() for c in protected_columns.split(",")]

            o_col = outcome_column.strip() if (
                        outcome_column and outcome_column.strip() not in ["", "null", "undefined"]) else None

            auditor = BiasAuditor(df, fairness_threshold=f_threshold)
            return auditor.full_audit(p_cols, o_col)

        result = await run_in_threadpool(process)
        print("--- [AUDIT COMPLETE] Result generated ---")
        return result

    except Exception as e:
        print(f"!!! AUDIT CRASH !!!\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/report/pdf")
async def generate_pdf_report(
        file: UploadFile = File(...),
        protected_columns: Optional[str] = Form(None),
        outcome_column: Optional[str] = Form(None),
        fairness_threshold: str = Form("0.80"),
        org_name: str = Form("BiasAuditor Analysis"),
):
    print(f"--- [PDF START] Generating for: {org_name} ---")
    try:
        content = await file.read()

        async def process_pdf():
            df = pd.read_csv(io.BytesIO(content))

            raw_t = str(fairness_threshold).replace('%', '').strip()
            f_threshold = float(raw_t) / 100 if float(raw_t) > 1 else float(raw_t)

            p_cols = []
            if protected_columns and protected_columns not in ["null", "undefined", "[]", ""]:
                try:
                    p_cols = json.loads(protected_columns)
                except:
                    p_cols = [c.strip() for c in protected_columns.split(",")]

            o_col = outcome_column.strip() if (
                        outcome_column and outcome_column.strip() not in ["", "null", "undefined"]) else None

            auditor = BiasAuditor(df, fairness_threshold=f_threshold)
            result = auditor.full_audit(p_cols, o_col)

            return build_pdf_response(result, org_name, threshold=f_threshold)

        return await run_in_threadpool(process_pdf)

    except Exception as e:
        print(f"!!! PDF CRASH !!!\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


    #