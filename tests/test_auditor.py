import pytest
import pandas as pd
import numpy as np
import io
from fastapi.testclient import TestClient

from backend.modules.auditor import BiasAuditor
from backend.main import app

client = TestClient(app)

# ─────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def balanced_df():
    """Dataset with no significant bias."""
    np.random.seed(42)
    n = 200
    return pd.DataFrame({
        "gender": np.random.choice(["Male", "Female"], n),
        "ethnicity": np.random.choice(["White", "Black", "Hispanic", "Asian"], n),
        "age": np.random.randint(18, 70, n),
        "prediction": np.random.choice([0, 1], n, p=[0.5, 0.5]),
    })

@pytest.fixture
def biased_df():
    """Dataset with clear gender bias in predictions."""
    male_rows = pd.DataFrame({
        "gender": ["Male"] * 100,
        "prediction": [1] * 90 + [0] * 10,
    })
    female_rows = pd.DataFrame({
        "gender": ["Female"] * 100,
        "prediction": [1] * 30 + [0] * 70,
    })
    return pd.concat([male_rows, female_rows], ignore_index=True)

@pytest.fixture
def no_protected_df():
    """Dataset without any protected characteristic columns."""
    return pd.DataFrame({
        "income": [50000, 60000, 45000],
        "credit_score": [700, 750, 680],
        "prediction": [1, 1, 0],
    })

# ─────────────────────────────────────────────
# BiasAuditor Unit Tests
# ─────────────────────────────────────────────

class TestBiasAuditorCore:
    def test_columns_normalized(self):
        df = pd.DataFrame({"Gender": ["M", "F"], "PREDICTION": [1, 0]})
        auditor = BiasAuditor(df)
        assert "gender" in auditor.df.columns
        assert "prediction" in auditor.df.columns

    def test_age_binning_applied(self):
        df = pd.DataFrame({"age": [25, 45, 65], "prediction": [1, 1, 1]})
        auditor = BiasAuditor(df)
        # Check if age column was converted to binned categories
        assert auditor.df["age"].dtype == 'category' or auditor.df["age"].dtype == 'object'

    def test_full_audit_structure(self, biased_df):
        auditor = BiasAuditor(biased_df)
        result = auditor.full_audit()
        assert "overall_risk" in result
        assert "audits" in result
        assert "metadata" in result
        assert result["metadata"]["total_rows"] == 200

    def test_bias_detection_logic(self, biased_df):
        auditor = BiasAuditor(biased_df)
        result = auditor.full_audit()
        # Gender should be flagged given the fixture data
        gender_audit = next(a for a in result["audits"] if a["characteristic"] == "Gender")
        assert gender_audit["disparity"]["flag"] is True
        assert gender_audit["disparity"]["disparate_impact_ratio"] < 0.8

class TestDataIntegrity:
    def test_handles_missing_values(self):
        df = pd.DataFrame({
            "gender": ["Male", None, "Female", np.nan, "Male"],
            "prediction": [1, 0, 1, 1, 0],
        })
        result = BiasAuditor(df).full_audit()
        # Preprocessor should fill NaN with "Unknown"
        groups = [g["group"] for g in result["audits"][0]["groups"]]
        assert "Unknown" in groups

    def test_handles_continuous_prediction(self):
        """Tests that non-binary targets are handled by using the mean."""
        df = pd.DataFrame({
            "gender": ["Male"] * 50 + ["Female"] * 50,
            "prediction": np.random.uniform(0, 1, 100),
        })
        result = BiasAuditor(df).full_audit()
        assert len(result["audits"]) == 1
        assert 0 <= result["audits"][0]["groups"][0]["rate"] <= 1

# ─────────────────────────────────────────────
# API & Integration Tests
# ─────────────────────────────────────────────

def make_csv_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()

class TestEndpoints:
    def test_health_check(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_audit_upload_process(self, balanced_df):
        csv_bytes = make_csv_bytes(balanced_df)
        resp = client.post(
            "/audit",
            files={"file": ("data.csv", csv_bytes, "text/csv")},
        )
        assert resp.status_code == 200
        assert "overall_risk" in resp.json()

    def test_pdf_report_generation(self, biased_df):
        """Tests the logic inside your recently updated pdf_builder.py."""
        csv_bytes = make_csv_bytes(biased_df)
        resp = client.post(
            "/report/pdf",
            files={"file": ("data.csv", csv_bytes, "text/csv")},
            data={"outcome_column": "prediction"}
        )
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        # Ensure it's not a dummy empty file
        assert len(resp.content) > 1000

    def test_invalid_file_extension(self):
        resp = client.post(
            "/audit",
            files={"file": ("data.txt", b"not,a,csv", "text/plain")},
        )
        assert resp.status_code == 400