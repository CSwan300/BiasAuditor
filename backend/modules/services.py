import io
import json
import pandas as pd
from fastapi import HTTPException, UploadFile
from typing import Optional


def load_dataframe(file: UploadFile) -> pd.DataFrame:
    """
    Reads an uploaded file into a Pandas DataFrame.
    Supports CSV and Excel formats.
    """
    filename = file.filename.lower()

    try:
        # Reset file pointer to the beginning before reading
        file.file.seek(0)
        contents = file.file.read()

        if not contents:
            raise ValueError("The uploaded file is empty.")

        if filename.endswith(".csv"):
            # Use 'on_bad_lines' to skip corrupted rows instead of crashing
            return pd.read_csv(io.BytesIO(contents), on_bad_lines='warn')

        elif filename.endswith((".xlsx", ".xls")):
            # Note: requires 'openpyxl' for .xlsx or 'xlrd' for .xls
            return pd.read_excel(io.BytesIO(contents))

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {filename}. Please upload .csv or .xlsx"
            )

    except Exception as e:
        # Log the error here if you have a logger
        raise HTTPException(status_code=422, detail=f"Data Processing Error: {str(e)}")


def parse_list(raw: Optional[str]) -> Optional[list[str]]:
    """
    Parses a string (comma-separated or JSON list) into a Python list.
    """
    if not raw or not str(raw).strip():
        return None

    raw = raw.strip()
    try:
        # Handle JSON format: ["Race", "Gender"]
        if raw.startswith("[") and raw.endswith("]"):
            return json.loads(raw)

        # Handle CSV format: Race, Gender
        return [item.strip() for item in raw.split(",") if item.strip()]
    except (json.JSONDecodeError, Exception):
        # Fallback to simple split if JSON parsing fails
        return [item.strip() for item in raw.split(",") if item.strip()]


def build_intersectional_pairs(df: pd.DataFrame, pairs: list[str]) -> pd.DataFrame:
    """
    Creates intersectional features.
    If input is ['Race', 'Gender'], it creates a column 'Race_Gender'
    with values like 'Black | Female'.
    """
    df_result = df.copy()

    if not pairs:
        return df_result

    for pair_str in pairs:
        # Normalize separators
        clean_pair = pair_str.replace("+", ",").replace(";", ",")
        cols = [c.strip() for c in clean_pair.split(",") if c.strip()]

        # Only process if columns exist in the actual data
        valid_cols = [c for c in cols if c in df_result.columns]

        if len(valid_cols) > 1:
            new_col_name = "_".join(valid_cols)
            # Create the combined feature
            # We use ' | ' as a separator to make it human-readable in the UI
            df_result[new_col_name] = (
                df_result[valid_cols]
                .astype(str)
                .agg(" | ".join, axis=1)
            )

    return df_result