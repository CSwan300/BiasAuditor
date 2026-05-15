from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pandas as pd
import numpy as np
import io
import json
from pathlib import Path

from .auditor import BiasAuditor

app = FastAPI(title="Bias Auditor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PROTECTED_CHARACTERISTICS = ["age", "gender", "ethnicity", "race", "sex"]


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/audit")
async def audit_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Only CSV and Excel files are supported."
        )

    content = await file.read()
    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not parse file: {str(e)}")

    if df.empty:
        raise HTTPException(status_code=422, detail="Uploaded file is empty.")

    auditor = BiasAuditor(df)
    result = auditor.run_audit()
    return result


@app.get("/sample-schema")
def sample_schema():
    """Return info about expected dataset format."""
    return {
        "description": "Upload a CSV or Excel file with columns for protected characteristics and a prediction/outcome column.",
        "expected_columns": {
            "protected": "age, gender, ethnicity (or any subset)",
            "prediction": "A column named 'prediction', 'label', 'outcome', or 'result'",
            "optional": "Any additional feature columns"
        },
        "example_row": {
            "age": 34,
            "gender": "Female",
            "ethnicity": "Hispanic",
            "prediction": 1
        }
    }