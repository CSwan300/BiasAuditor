"""
Shared pytest fixtures and configuration.
"""
import io
import pytest
import pandas as pd


@pytest.fixture
def simple_df():
    return pd.DataFrame({
        "gender": ["Male"] * 200 + ["Female"] * 200,
        "hired":  [1] * 160 + [0] * 40 + [1] * 80 + [0] * 120,
    })


@pytest.fixture
def equal_outcome_df():
    return pd.DataFrame({
        "gender": ["Male"] * 200 + ["Female"] * 200,
        "hired":  [1] * 160 + [0] * 40 + [1] * 160 + [0] * 40,
    })


@pytest.fixture
def csv_bytes(simple_df):
    buf = io.BytesIO()
    simple_df.to_csv(buf, index=False)
    return buf.getvalue()