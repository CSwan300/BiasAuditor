import pytest
import pandas as pd
import numpy as np
import io
import json
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
        "prediction": [1] * 90 + [0] * 10,  # 90% positive for males
    })
    female_rows = pd.DataFrame({
        "gender": ["Female"] * 100,
        "prediction": [1] * 30 + [0] * 70,  # 30% positive for females
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


@pytest.fixture
def no_prediction_df():
    """Dataset with protected cols but no prediction column (all non-numeric except age)."""
    return pd.DataFrame({
        "gender": ["Male", "Female", "Male"],
        "education": ["Bachelor", "Master", "PhD"],
        "department": ["Engineering", "Sales", "HR"],
    })


@pytest.fixture
def multichar_df():
    """Dataset with multiple protected characteristics."""
    np.random.seed(99)
    n = 300
    return pd.DataFrame({
        "gender": np.random.choice(["Male", "Female", "Non-binary"], n),
        "ethnicity": np.random.choice(["White", "Black", "Hispanic", "Asian"], n),
        "age": np.random.randint(20, 65, n),
        "prediction": np.random.choice([0, 1], n),
    })


# ─────────────────────────────────────────────
# BiasAuditor Unit Tests
# ─────────────────────────────────────────────

class TestBiasAuditorInit:
    def test_columns_normalized_to_lowercase(self):
        df = pd.DataFrame({"Gender": ["M", "F"], "PREDICTION": [1, 0]})
        auditor = BiasAuditor(df)
        assert "gender" in auditor.df.columns
        assert "prediction" in auditor.df.columns

    def test_original_df_not_mutated(self):
        df = pd.DataFrame({"Gender": ["M", "F"], "Prediction": [1, 0]})
        original_cols = list(df.columns)
        BiasAuditor(df)
        assert list(df.columns) == original_cols


class TestProtectedColumnDetection:
    def test_detects_gender(self):
        df = pd.DataFrame({"gender": ["M"], "prediction": [1]})
        auditor = BiasAuditor(df)
        assert "gender" in auditor._detect_protected_cols()

    def test_detects_ethnicity(self):
        df = pd.DataFrame({"ethnicity": ["White"], "prediction": [1]})
        auditor = BiasAuditor(df)
        assert "ethnicity" in auditor._detect_protected_cols()

    def test_detects_age(self):
        df = pd.DataFrame({"age": [25], "prediction": [1]})
        auditor = BiasAuditor(df)
        assert "age" in auditor._detect_protected_cols()

    def test_detects_multiple(self, multichar_df):
        auditor = BiasAuditor(multichar_df)
        cols = auditor._detect_protected_cols()
        assert "gender" in cols
        assert "ethnicity" in cols
        assert "age" in cols

    def test_returns_empty_when_none(self, no_protected_df):
        auditor = BiasAuditor(no_protected_df)
        assert auditor._detect_protected_cols() == []


class TestPredictionColumnDetection:
    def test_detects_prediction(self):
        df = pd.DataFrame({"gender": ["M"], "prediction": [1]})
        assert BiasAuditor(df)._detect_prediction_col() == "prediction"

    def test_detects_label(self):
        df = pd.DataFrame({"gender": ["M"], "label": [1]})
        assert BiasAuditor(df)._detect_prediction_col() == "label"

    def test_detects_outcome(self):
        df = pd.DataFrame({"gender": ["M"], "outcome": [1]})
        assert BiasAuditor(df)._detect_prediction_col() == "outcome"

    def test_fallback_to_last_numeric(self):
        df = pd.DataFrame({"gender": ["M"], "score_x": [0.8]})
        col = BiasAuditor(df)._detect_prediction_col()
        assert col == "score_x"

    def test_returns_none_when_no_numeric(self, no_prediction_df):
        # remove numeric cols entirely
        df = pd.DataFrame({"gender": ["M", "F"], "label_text": ["yes", "no"]})
        assert BiasAuditor(df)._detect_prediction_col() is None


class TestAgeBinning:
    def test_bins_numeric_ages(self):
        df = pd.DataFrame({"age": [10, 25, 35, 50, 65, 80], "prediction": [1] * 6})
        auditor = BiasAuditor(df)
        binned = auditor._bin_age(df["age"])
        assert "<18" in binned.values
        assert "18-29" in binned.values
        assert "75+" in binned.values

    def test_passthrough_string_age(self):
        df = pd.DataFrame({"age": ["young", "old"], "prediction": [1, 0]})
        auditor = BiasAuditor(df)
        result = auditor._bin_age(df["age"])
        assert list(result) == ["young", "old"]


class TestGroupStats:
    def test_returns_list_of_dicts(self, balanced_df):
        auditor = BiasAuditor(balanced_df)
        stats = auditor._group_stats("gender", "prediction")
        assert isinstance(stats, list)
        assert all(isinstance(s, dict) for s in stats)

    def test_stats_have_required_keys(self, balanced_df):
        auditor = BiasAuditor(balanced_df)
        stats = auditor._group_stats("gender", "prediction")
        for stat in stats:
            assert "group" in stat
            assert "count" in stat
            assert "percentage" in stat
            assert "rate" in stat

    def test_counts_sum_to_total(self, balanced_df):
        auditor = BiasAuditor(balanced_df)
        stats = auditor._group_stats("gender", "prediction")
        total_count = sum(s["count"] for s in stats)
        assert total_count == len(balanced_df)

    def test_percentages_sum_to_100(self, balanced_df):
        auditor = BiasAuditor(balanced_df)
        stats = auditor._group_stats("gender", "prediction")
        total_pct = sum(s["percentage"] for s in stats)
        assert abs(total_pct - 100.0) < 0.5  # rounding tolerance

    def test_rates_between_0_and_1(self, balanced_df):
        auditor = BiasAuditor(balanced_df)
        stats = auditor._group_stats("gender", "prediction")
        for s in stats:
            assert 0.0 <= s["rate"] <= 1.0


class TestDisparityCalculation:
    def test_flags_biased_dataset(self, biased_df):
        auditor = BiasAuditor(biased_df)
        stats = auditor._group_stats("gender", "prediction")
        disparity = auditor._calculate_disparity(stats)
        assert disparity["flag"] is True

    def test_no_flag_for_balanced(self, balanced_df):
        # Force a perfectly balanced dataset
        df = pd.DataFrame({
            "gender": ["Male"] * 100 + ["Female"] * 100,
            "prediction": [1] * 50 + [0] * 50 + [1] * 50 + [0] * 50,
        })
        auditor = BiasAuditor(df)
        stats = auditor._group_stats("gender", "prediction")
        disparity = auditor._calculate_disparity(stats)
        assert disparity["flag"] is False

    def test_disparity_ratio_range(self, biased_df):
        auditor = BiasAuditor(biased_df)
        stats = auditor._group_stats("gender", "prediction")
        disparity = auditor._calculate_disparity(stats)
        assert 0.0 <= disparity["disparate_impact_ratio"] <= 1.0

    def test_single_group_no_flag(self):
        df = pd.DataFrame({"gender": ["Male"] * 50, "prediction": [1] * 50})
        auditor = BiasAuditor(df)
        stats = auditor._group_stats("gender", "prediction")
        disparity = auditor._calculate_disparity(stats)
        assert disparity["flag"] is False


class TestRunAudit:
    def test_returns_expected_keys(self, balanced_df):
        result = BiasAuditor(balanced_df).run_audit()
        assert "metadata" in result
        assert "audits" in result
        assert "overall_risk" in result
        assert "warnings" in result

    def test_metadata_row_count(self, balanced_df):
        result = BiasAuditor(balanced_df).run_audit()
        assert result["metadata"]["total_rows"] == len(balanced_df)

    def test_audit_per_characteristic(self, multichar_df):
        result = BiasAuditor(multichar_df).run_audit()
        chars = [a["characteristic"] for a in result["audits"]]
        assert "gender" in chars
        assert "ethnicity" in chars

    def test_warns_when_no_protected_cols(self, no_protected_df):
        result = BiasAuditor(no_protected_df).run_audit()
        assert len(result["warnings"]) > 0
        assert result["audits"] == []

    def test_warns_when_no_prediction_col(self, no_prediction_df):
        result = BiasAuditor(no_prediction_df).run_audit()
        assert len(result["warnings"]) > 0

    def test_overall_risk_level_present(self, balanced_df):
        result = BiasAuditor(balanced_df).run_audit()
        assert result["overall_risk"]["level"] in ["Low", "Moderate", "High", "Critical", "Unknown"]

    def test_biased_data_raises_risk(self, biased_df):
        result = BiasAuditor(biased_df).run_audit()
        assert result["overall_risk"]["level"] != "Low"

    def test_handles_missing_values(self):
        df = pd.DataFrame({
            "gender": ["Male", None, "Female", np.nan, "Male"],
            "prediction": [1, 0, 1, 1, 0],
        })
        result = BiasAuditor(df).run_audit()
        assert result["metadata"]["total_rows"] == 5
        groups = result["audits"][0]["groups"]
        group_names = [g["group"] for g in groups]
        assert "Unknown" in group_names

    def test_handles_continuous_prediction(self):
        df = pd.DataFrame({
            "gender": ["Male"] * 50 + ["Female"] * 50,
            "prediction": np.random.uniform(0, 1, 100),
        })
        result = BiasAuditor(df).run_audit()
        assert len(result["audits"]) == 1


# ─────────────────────────────────────────────
# API Endpoint Tests
# ─────────────────────────────────────────────

def make_csv_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()


class TestHealthEndpoint:
    def test_returns_ok(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestAuditEndpoint:
    def test_valid_csv_returns_200(self, balanced_df):
        csv_bytes = make_csv_bytes(balanced_df)
        resp = client.post(
            "/audit",
            files={"file": ("data.csv", csv_bytes, "text/csv")},
        )
        assert resp.status_code == 200

    def test_response_has_required_keys(self, balanced_df):
        csv_bytes = make_csv_bytes(balanced_df)
        resp = client.post("/audit", files={"file": ("data.csv", csv_bytes, "text/csv")})
        body = resp.json()
        assert "metadata" in body
        assert "audits" in body
        assert "overall_risk" in body

    def test_biased_data_flagged(self, biased_df):
        csv_bytes = make_csv_bytes(biased_df)
        resp = client.post("/audit", files={"file": ("data.csv", csv_bytes, "text/csv")})
        body = resp.json()
        flagged = [a for a in body["audits"] if a["disparity"]["flag"]]
        assert len(flagged) > 0

    def test_invalid_extension_returns_400(self):
        resp = client.post(
            "/audit",
            files={"file": ("data.txt", b"some,data\n1,2", "text/plain")},
        )
        assert resp.status_code == 400

    def test_malformed_csv_returns_422(self):
        resp = client.post(
            "/audit",
            files={"file": ("data.csv", b"\x00\xff\xfe broken binary", "text/csv")},
        )
        assert resp.status_code == 422

    def test_empty_file_returns_422(self):
        resp = client.post(
            "/audit",
            files={"file": ("data.csv", b"", "text/csv")},
        )
        assert resp.status_code == 422

    def test_no_protected_cols_returns_warnings(self, no_protected_df):
        csv_bytes = make_csv_bytes(no_protected_df)
        resp = client.post("/audit", files={"file": ("data.csv", csv_bytes, "text/csv")})
        body = resp.json()
        assert len(body["warnings"]) > 0

    def test_metadata_correct_row_count(self, balanced_df):
        csv_bytes = make_csv_bytes(balanced_df)
        resp = client.post("/audit", files={"file": ("data.csv", csv_bytes, "text/csv")})
        body = resp.json()
        assert body["metadata"]["total_rows"] == len(balanced_df)

    def test_excel_file_accepted(self, balanced_df):
        buf = io.BytesIO()
        balanced_df.to_excel(buf, index=False)
        buf.seek(0)
        resp = client.post(
            "/audit",
            files={"file": ("data.xlsx", buf.read(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
        assert resp.status_code == 200

    def test_case_insensitive_columns(self):
        df = pd.DataFrame({
            "Gender": ["Male", "Female"] * 50,
            "Ethnicity": ["White", "Black"] * 50,
            "Prediction": [1, 0] * 50,
        })
        csv_bytes = make_csv_bytes(df)
        resp = client.post("/audit", files={"file": ("data.csv", csv_bytes, "text/csv")})
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["audits"]) >= 1


class TestSampleSchemaEndpoint:
    def test_returns_200(self):
        resp = client.get("/sample-schema")
        assert resp.status_code == 200

    def test_has_expected_structure(self):
        resp = client.get("/sample-schema")
        body = resp.json()
        assert "description" in body
        assert "expected_columns" in body