import io
import json
import pandas as pd
from fastapi import HTTPException, UploadFile
from typing import Optional

def load_dataframe(file: UploadFile) -> pd.DataFrame:
    filename = file.filename.lower()

    try:
        file.file.seek(0)
        contents = file.file.read()

        if not contents:
            raise ValueError("The uploaded file is empty.")

        if filename.endswith(".csv"):
            return pd.read_csv(io.BytesIO(contents), on_bad_lines='warn')

        elif filename.endswith((".xlsx", ".xls")):
            return pd.read_excel(io.BytesIO(contents))

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {filename}"
            )

    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Data Processing Error: {str(e)}")

def parse_list(raw: Optional[str]) -> Optional[list[str]]:
    if not raw or not str(raw).strip():
        return None

    raw = raw.strip()
    try:
        if raw.startswith("[") and raw.endswith("]"):
            return json.loads(raw)
        return [item.strip() for item in raw.split(",") if item.strip()]
    except (json.JSONDecodeError, Exception):
        return [item.strip() for item in raw.split(",") if item.strip()]

def build_intersectional_pairs(df: pd.DataFrame, pairs: list[str]) -> pd.DataFrame:
    df_result = df.copy()

    if not pairs:
        return df_result

    for pair_str in pairs:
        clean_pair = pair_str.replace("+", ",").replace(";", ",")
        cols = [c.strip() for c in clean_pair.split(",") if c.strip()]
        valid_cols = [c for c in cols if c in df_result.columns]

        if len(valid_cols) > 1:
            new_col_name = "_".join(valid_cols)
            df_result[new_col_name] = (
                df_result[valid_cols]
                .astype(str)
                .agg(" | ".join, axis=1)
            )

    return df_result