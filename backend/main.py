import logging
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool  # Essential for unblocking
from typing import Optional

from backend.modules.services import load_dataframe, parse_list
from backend.modules.reporting import build_pdf_response
from backend.modules.auditor import BiasAuditor

# Setup basic logging to help you see what's happening in the terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="BiasAuditor API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True, # Added this
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/audit")
async def audit(
        file: UploadFile = File(...),
        protected_columns: Optional[str] = Form(None),
        outcome_column: Optional[str] = Form(None),
        fairness_threshold: float = Form(0.80),
):
    # High-visibility print for debugging
    print("\n" + "=" * 50)
    print(f"🚀 API HIT: /audit | File: {file.filename}")
    print("=" * 50 + "\n")

    try:
        logger.info(f"Received audit request for file: {file.filename}")

        # 1. Load Data
        df = await run_in_threadpool(load_dataframe, file)
        print(f"✅ Data loaded successfully. Rows: {len(df)}")

        # 2. Init Auditor
        auditor = BiasAuditor(df, fairness_threshold=fairness_threshold)

        # 3. Run Audit
        logger.info("Starting heavy audit calculation...")
        print("⏳ Running full_audit logic...")

        result = await run_in_threadpool(
            auditor.full_audit,
            protected_cols=parse_list(protected_columns),
            outcome_col=outcome_column.strip() if outcome_column else None,
        )

        print("✨ Audit finished successfully!")
        logger.info("Audit complete. Sending results.")
        return result

    except Exception as e:
        print(f"❌ ERROR IN /AUDIT: {str(e)}")
        logger.error(f"Audit failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/report/pdf")
async def generate_pdf_report(
        file: UploadFile = File(...),
        protected_columns: Optional[str] = Form(None),
        outcome_column: Optional[str] = Form(None),
        fairness_threshold: float = Form(0.80),
        org_name: str = Form("Your Organisation"),
):
    try:
        df = await run_in_threadpool(load_dataframe, file)
        auditor = BiasAuditor(df, fairness_threshold=fairness_threshold)

        result = await run_in_threadpool(
            auditor.full_audit,
            protected_cols=parse_list(protected_columns),
            outcome_col=outcome_column.strip() if outcome_column else None
        )

        return build_pdf_response(result, org_name, fairness_threshold)
    except Exception as e:
        logger.error(f"PDF Generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))