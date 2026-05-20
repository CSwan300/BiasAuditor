from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from typing import Optional
from backend.modules.services import load_dataframe, parse_list
from backend.modules.reporting import build_pdf_response
from backend.modules.auditor import BiasAuditor

app = FastAPI(title="BiasAuditor API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/audit")
async def audit(
        file: UploadFile = File(...),
        protected_columns: Optional[str] = Form(None),
        outcome_column: Optional[str] = Form(None),
        fairness_threshold: str = Form("0.80"),  # Receive as string to prevent parse errors
):
    try:
        # 1. Load Data
        df = await run_in_threadpool(load_dataframe, file)

        # 2. Safe Threshold Parsing
        try:
            f_threshold = float(fairness_threshold)
        except (ValueError, TypeError):
            f_threshold = 0.80

        # 3. Safe List Parsing
        p_cols = parse_list(protected_columns) if protected_columns else None

        # 4. Safe String Trimming
        o_col = outcome_column.strip() if (outcome_column and outcome_column.strip()) else None

        auditor = BiasAuditor(df, fairness_threshold=f_threshold)

        result = await run_in_threadpool(
            auditor.full_audit,
            protected_cols=p_cols,
            outcome_col=o_col
        )
        return result

    except Exception as e:
        print(f"AUDIT ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Audit failed: {str(e)}")


@app.post("/report/pdf")
async def generate_pdf_report(
        file: UploadFile = File(...),
        protected_columns: Optional[str] = Form(None),
        outcome_column: Optional[str] = Form(None),
        fairness_threshold: str = Form("0.80"),
        org_name: str = Form("Your Organisation"),
):
    try:
        df = await run_in_threadpool(load_dataframe, file)

        # Consistent Parsing
        try:
            f_threshold = float(fairness_threshold)
        except:
            f_threshold = 0.80

        p_cols = parse_list(protected_columns) if protected_columns else None
        o_col = outcome_column.strip() if (outcome_column and outcome_column.strip()) else None

        auditor = BiasAuditor(df, fairness_threshold=f_threshold)

        result = await run_in_threadpool(
            auditor.full_audit,
            protected_cols=p_cols,
            outcome_col=o_col
        )

        # CRITICAL FIX: Ensure threshold is passed to the PDF builder
        # so the report actually shows the fucking slider value
        return build_pdf_response(result, org_name, threshold=f_threshold)

    except Exception as e:
        print(f"PDF GENERATION ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF Error: {str(e)}")