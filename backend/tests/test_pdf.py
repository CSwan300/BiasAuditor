"""
Tests for backend/modules/Build_pdf/pdf_builder.py  and
         backend/modules/Build_pdf/reporting.py
"""
import pytest
from unittest.mock import patch
from backend.modules.Build_pdf.pdf_builder import generate_pdf_content, create_bar_chart
from backend.modules.Build_pdf.reporting import build_pdf_response


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def minimal_result():
    return {
        "overall_risk": {"level": "Moderate Risk", "score": 50, "flagged_count": 1},
        "audits": [],
        "mitigations": [],
        "metadata": {},
    }


@pytest.fixture
def flagged_result():
    return {
        "overall_risk": {"level": "High Risk", "score": 30, "flagged_count": 3},
        "audits": [
            {
                "characteristic": "GENDER",
                "privileged_group": "Male",
                "disparity": {"disparate_impact_ratio": 0.5, "flag": True},
                "groups": [
                    {"group": "Male",   "rate": 80.0, "count": 200, "is_privileged": True,  "disparity_ratio": 1.0, "stat_sig": True},
                    {"group": "Female", "rate": 40.0, "count": 200, "is_privileged": False, "disparity_ratio": 0.5, "stat_sig": True},
                ],
                "attribute_mitigations": [],
            }
        ],
        "mitigations": [
            {"type": "reweighting", "priority": "high", "title": "Sample Reweighting", "description": "Reweight Female."}
        ],
    }


@pytest.fixture
def passing_result():
    return {
        "overall_risk": {"level": "Low Risk", "score": 95, "flagged_count": 0},
        "audits": [
            {
                "characteristic": "AGE",
                "privileged_group": "Young",
                "disparity": {"disparate_impact_ratio": 0.92, "flag": False},
                "groups": [
                    {"group": "Young", "rate": 80.0, "count": 100, "is_privileged": True,  "disparity_ratio": 1.0, "stat_sig": False},
                    {"group": "Old",   "rate": 74.0, "count": 100, "is_privileged": False, "disparity_ratio": 0.92, "stat_sig": False},
                ],
                "attribute_mitigations": [{"type": "none", "message": "No mitigation required."}],
            }
        ],
        "mitigations": [],
    }


# ===========================================================================
# create_bar_chart
# ===========================================================================

class TestCreateBarChart:
    def test_returns_drawing_for_valid_groups(self, flagged_result):
        groups = flagged_result["audits"][0]["groups"]
        chart = create_bar_chart(groups)
        # Should return a Drawing (has an add method) or a Spacer
        assert chart is not None

    def test_empty_groups_returns_spacer(self):
        from reportlab.platypus import Spacer
        chart = create_bar_chart([])
        assert isinstance(chart, Spacer)

    def test_single_group(self):
        groups = [{"group": "Male", "rate": 75.0}]
        chart = create_bar_chart(groups)
        assert chart is not None

    def test_group_with_missing_rate_defaults_zero(self):
        groups = [{"group": "Male"}, {"group": "Female", "rate": 50.0}]
        # Should not raise
        chart = create_bar_chart(groups)
        assert chart is not None


# ===========================================================================
# generate_pdf_content
# ===========================================================================

class TestGeneratePdfContent:
    def test_returns_bytes(self, flagged_result):
        result = generate_pdf_content(flagged_result, "Test Org", threshold=0.8)
        assert isinstance(result, bytes)

    def test_bytes_non_empty(self, flagged_result):
        result = generate_pdf_content(flagged_result, "Test Org", threshold=0.8)
        assert len(result) > 0

    def test_pdf_magic_bytes(self, flagged_result):
        result = generate_pdf_content(flagged_result, "Test Org", threshold=0.8)
        assert result[:4] == b"%PDF"

    def test_minimal_result_does_not_crash(self, minimal_result):
        result = generate_pdf_content(minimal_result, "Org", threshold=0.8)
        assert isinstance(result, bytes)

    def test_passing_result_does_not_crash(self, passing_result):
        result = generate_pdf_content(passing_result, "Org", threshold=0.8)
        assert isinstance(result, bytes)

    def test_threshold_as_decimal(self, flagged_result):
        result = generate_pdf_content(flagged_result, "Org", threshold=0.75)
        assert isinstance(result, bytes)

    def test_threshold_as_percentage(self, flagged_result):
        result = generate_pdf_content(flagged_result, "Org", threshold=75.0)
        assert isinstance(result, bytes)

    def test_high_risk_level(self):
        result_data = {
            "overall_risk": {"level": "High Risk", "score": 20, "flagged_count": 4},
            "audits": [],
            "mitigations": [],
        }
        result = generate_pdf_content(result_data, "Org", threshold=0.8)
        assert isinstance(result, bytes)

    def test_critical_risk_level(self):
        result_data = {
            "overall_risk": {"level": "Critical Risk", "score": 10, "flagged_count": 6},
            "audits": [],
            "mitigations": [],
        }
        result = generate_pdf_content(result_data, "Org", threshold=0.8)
        assert isinstance(result, bytes)

    def test_low_risk_level(self, passing_result):
        result = generate_pdf_content(passing_result, "Org", threshold=0.8)
        assert isinstance(result, bytes)

    def test_missing_overall_risk_key(self):
        result_data = {"audits": [], "mitigations": []}
        result = generate_pdf_content(result_data, "Org", threshold=0.8)
        assert isinstance(result, bytes)

    def test_empty_org_name(self, flagged_result):
        result = generate_pdf_content(flagged_result, "", threshold=0.8)
        assert isinstance(result, bytes)

    def test_chart_error_handled_gracefully(self, flagged_result):
        with patch("backend.modules.Build_pdf.pdf_builder.create_bar_chart", side_effect=Exception("chart fail")):
            # Should not propagate exception
            result = generate_pdf_content(flagged_result, "Org", threshold=0.8)
            assert isinstance(result, bytes)


# ===========================================================================
# build_pdf_response
# ===========================================================================

class TestBuildPdfResponse:
    def test_returns_streaming_response(self, flagged_result):
        from fastapi.responses import StreamingResponse
        response = build_pdf_response(flagged_result, "Test Org", threshold=0.8)
        assert isinstance(response, StreamingResponse)

    def test_content_type_is_pdf(self, flagged_result):
        response = build_pdf_response(flagged_result, "Test Org", threshold=0.8)
        assert response.media_type == "application/pdf"

    def test_content_disposition_contains_filename(self, flagged_result):
        response = build_pdf_response(flagged_result, "Test Org", threshold=0.8)
        disposition = response.headers.get("content-disposition", "")
        assert "bias_audit_" in disposition
        assert ".pdf" in disposition

    def test_expose_headers_set(self, flagged_result):
        response = build_pdf_response(flagged_result, "Test Org", threshold=0.8)
        expose = response.headers.get("access-control-expose-headers", "")
        assert "Content-Disposition" in expose

    def test_default_threshold(self, flagged_result):
        response = build_pdf_response(flagged_result, "Test Org")
        assert response.media_type == "application/pdf"

    def test_raises_on_empty_pdf(self, flagged_result):
        with patch("backend.modules.Build_pdf.reporting.generate_pdf_content", return_value=b""):
            with pytest.raises(ValueError, match="empty"):
                build_pdf_response(flagged_result, "Test Org", threshold=0.8)