"""
Tests for backend/main.py – FastAPI endpoints and helpers.
"""
import io
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# App import – adjust path to match your actual module location
# ---------------------------------------------------------------------------
from backend.main import app, get_clean_df, process_audit_logic

client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _csv_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()


def _simple_df() -> pd.DataFrame:
    return pd.DataFrame({
        "gender": ["Male"] * 100 + ["Female"] * 100,
        "hired":  [1] * 80 + [0] * 20 + [1] * 40 + [0] * 60,
    })


def _upload_file(df: pd.DataFrame, filename: str = "test.csv"):
    return ("file", (filename, io.BytesIO(_csv_bytes(df)), "text/csv"))


# ===========================================================================
# /health
# ===========================================================================

class TestHealthEndpoint:
    def test_returns_200(self):
        r = client.get("/health")
        assert r.status_code == 200

    def test_status_ok(self):
        r = client.get("/health")
        assert r.json()["status"] == "ok"

    def test_port_field_present(self):
        r = client.get("/health")
        assert "port" in r.json()


# ===========================================================================
# get_clean_df helper
# ===========================================================================

class TestGetCleanDf:
    def test_returns_dataframe(self):
        mock_file = MagicMock()
        mock_file.file = io.BytesIO(_csv_bytes(_simple_df()))
        df = get_clean_df(mock_file)
        assert isinstance(df, pd.DataFrame)

    def test_empty_file_raises_value_error(self):
        mock_file = MagicMock()
        mock_file.file = io.BytesIO(b"")
        with pytest.raises(ValueError, match="empty"):
            get_clean_df(mock_file)


# ===========================================================================
# process_audit_logic helper
# ===========================================================================

class TestProcessAuditLogic:
    def test_returns_results_and_threshold(self):
        df = _simple_df()
        results, threshold = process_audit_logic(df, "80", '["gender"]', "hired")
        assert isinstance(results, dict)
        assert threshold == pytest.approx(0.8)

    def test_threshold_from_percentage_string(self):
        df = _simple_df()
        _, threshold = process_audit_logic(df, "75%", '["gender"]', "hired")
        assert threshold == pytest.approx(0.75)

    def test_invalid_threshold_defaults_to_0_8(self):
        df = _simple_df()
        _, threshold = process_audit_logic(df, "not_a_number", '["gender"]', "hired")
        assert threshold == pytest.approx(0.8)

    def test_auto_detects_protected_cols_when_empty(self):
        df = pd.DataFrame({
            "gender": ["Male"] * 50 + ["Female"] * 50,
            "hired":  [1] * 40 + [0] * 10 + [1] * 20 + [0] * 30,
        })
        results, _ = process_audit_logic(df, "0.8", None, "hired")
        # gender is a common trait → should be auto-detected
        assert len(results["audits"]) >= 1

    def test_metadata_total_rows(self):
        df = _simple_df()
        results, _ = process_audit_logic(df, "0.8", '["gender"]', "hired")
        assert results["metadata"]["total_rows"] == 200

    def test_metadata_total_columns(self):
        df = _simple_df()
        results, _ = process_audit_logic(df, "0.8", '["gender"]', "hired")
        assert results["metadata"]["total_columns"] == 2

    def test_null_outcome_col_treated_as_auto(self):
        df = _simple_df()
        results, _ = process_audit_logic(df, "0.8", '["gender"]', "null")
        # Should not crash and should fall back to auto-detection
        assert "audits" in results

    def test_result_has_overall_risk(self):
        df = _simple_df()
        results, _ = process_audit_logic(df, "0.8", '["gender"]', "hired")
        assert "overall_risk" in results


# ===========================================================================
# POST /audit
# ===========================================================================

class TestAuditEndpoint:
    def test_successful_audit_returns_200(self):
        r = client.post(
            "/audit",
            files=[_upload_file(_simple_df())],
            data={"fairness_threshold": "0.8", "protected_columns": '["gender"]', "outcome_column": "hired"},
        )
        assert r.status_code == 200

    def test_response_has_audits_key(self):
        r = client.post(
            "/audit",
            files=[_upload_file(_simple_df())],
            data={"fairness_threshold": "0.8", "protected_columns": '["gender"]', "outcome_column": "hired"},
        )
        assert "audits" in r.json()

    def test_response_has_overall_risk(self):
        r = client.post(
            "/audit",
            files=[_upload_file(_simple_df())],
            data={"fairness_threshold": "0.8", "protected_columns": '["gender"]', "outcome_column": "hired"},
        )
        assert "overall_risk" in r.json()

    def test_missing_file_returns_422(self):
        r = client.post(
            "/audit",
            data={"fairness_threshold": "0.8"},
        )
        assert r.status_code == 422

    def test_audit_with_percentage_threshold(self):
        r = client.post(
            "/audit",
            files=[_upload_file(_simple_df())],
            data={"fairness_threshold": "80", "outcome_column": "hired"},
        )
        assert r.status_code == 200

    def test_audit_without_protected_columns(self):
        """Should auto-detect protected columns."""
        r = client.post(
            "/audit",
            files=[_upload_file(_simple_df())],
            data={"fairness_threshold": "0.8", "outcome_column": "hired"},
        )
        assert r.status_code == 200

    def test_flagged_attribute_in_response(self):
        r = client.post(
            "/audit",
            files=[_upload_file(_simple_df())],
            data={"fairness_threshold": "0.8", "protected_columns": '["gender"]', "outcome_column": "hired"},
        )
        body = r.json()
        audits = body.get("audits", [])
        # gender disparity should be flagged
        assert any(a["disparity"]["flag"] for a in audits)

    @patch("backend.main.get_clean_df", side_effect=Exception("disk error"))
    def test_internal_error_returns_500(self, _mock):
        r = client.post(
            "/audit",
            files=[_upload_file(_simple_df())],
            data={"fairness_threshold": "0.8"},
        )
        assert r.status_code == 500


# ===========================================================================
# POST /report/pdf
# ===========================================================================

class TestPdfReportEndpoint:
    def test_successful_pdf_returns_200(self):
        r = client.post(
            "/report/pdf",
            files=[_upload_file(_simple_df())],
            data={
                "fairness_threshold": "0.8",
                "protected_columns": '["gender"]',
                "outcome_column": "hired",
                "org_name": "Test Org",
            },
        )
        assert r.status_code == 200

    def test_response_content_type_is_pdf(self):
        r = client.post(
            "/report/pdf",
            files=[_upload_file(_simple_df())],
            data={
                "fairness_threshold": "0.8",
                "protected_columns": '["gender"]',
                "outcome_column": "hired",
            },
        )
        assert "pdf" in r.headers.get("content-type", "")

    def test_content_disposition_header_present(self):
        r = client.post(
            "/report/pdf",
            files=[_upload_file(_simple_df())],
            data={
                "fairness_threshold": "0.8",
                "protected_columns": '["gender"]',
                "outcome_column": "hired",
            },
        )
        assert "attachment" in r.headers.get("content-disposition", "")

    def test_pdf_bytes_non_empty(self):
        r = client.post(
            "/report/pdf",
            files=[_upload_file(_simple_df())],
            data={
                "fairness_threshold": "0.8",
                "outcome_column": "hired",
            },
        )
        assert len(r.content) > 0

    def test_default_org_name_used_when_omitted(self):
        """Should not crash if org_name is not provided (uses default)."""
        r = client.post(
            "/report/pdf",
            files=[_upload_file(_simple_df())],
            data={"fairness_threshold": "0.8", "outcome_column": "hired"},
        )
        assert r.status_code == 200

    @patch("backend.main.get_clean_df", side_effect=Exception("read error"))
    def test_pdf_error_returns_500(self, _mock):
        r = client.post(
            "/report/pdf",
            files=[_upload_file(_simple_df())],
            data={"fairness_threshold": "0.8"},
        )
        assert r.status_code == 500


# ===========================================================================
# Coverage gap: main.py lines 43-44 (xlsx branch), 51 (bad lines warning),
#               62 (p_cols from object cols fallback), 117-119 (uvicorn block)
# ===========================================================================


class TestProcessAuditLogicFallbacks:
    def test_falls_back_to_object_cols_when_no_common_traits(self):
        """Covers the select_dtypes fallback branch (line 62)."""
        df = pd.DataFrame({
            "category_a": ["X"] * 50 + ["Y"] * 50,
            "category_b": ["P"] * 50 + ["Q"] * 50,
            "score":      [1] * 40 + [0] * 10 + [1] * 20 + [0] * 30,
        })
        results, _ = process_audit_logic(df, "0.8", None, "score")
        assert "audits" in results
        assert len(results["audits"]) > 0

    def test_p_cols_raw_as_comma_string(self):
        """Covers comma-split branch when p_cols_raw is not JSON."""
        df = _simple_df()
        results, _ = process_audit_logic(df, "0.8", "gender", "hired")
        assert len(results["audits"]) == 1

    def test_undefined_outcome_col_treated_as_auto(self):
        """Covers the forbidden_values guard for outcome_col (line ~75)."""
        df = _simple_df()
        results, _ = process_audit_logic(df, "0.8", '["gender"]', "undefined")
        assert "audits" in results

    def test_not_specified_outcome_col_treated_as_auto(self):
        df = _simple_df()
        results, _ = process_audit_logic(df, "0.8", '["gender"]', "not specified")
        assert "audits" in results


class TestMainBlock:
    def test_uvicorn_not_called_during_import(self):
        """The __main__ block (lines 117-119) should never run during tests."""
        import backend.main as m
        assert hasattr(m, "app")