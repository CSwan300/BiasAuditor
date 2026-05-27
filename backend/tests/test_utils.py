"""
Tests for backend/modules/AuditLogic/utils.py
         backend/modules/AuditLogic/metrics.py
         backend/modules/AuditLogic/services.py (data helpers)
"""
import pytest
import pandas as pd

# ── stats helpers (utils.py inside AuditLogic) ──────────────────────────────
from backend.modules.AuditLogic.utils import risk_level, stat_significance

# ── metrics ─────────────────────────────────────────────────────────────────
from backend.modules.AuditLogic.metrics import compute_rates


# ===========================================================================
# risk_level
# ===========================================================================

class TestRiskLevel:
    def test_zero_failure_is_low(self):
        assert risk_level(0.0) == "Low"

    def test_low_failure_is_moderate(self):
        assert risk_level(0.1) == "Moderate"

    def test_boundary_moderate(self):
        assert risk_level(0.25) == "Moderate"

    def test_above_moderate_is_high(self):
        assert risk_level(0.26) == "High"

    def test_boundary_high(self):
        assert risk_level(0.60) == "High"

    def test_above_high_is_critical(self):
        assert risk_level(0.61) == "Critical"

    def test_full_failure_is_critical(self):
        assert risk_level(1.0) == "Critical"


# ===========================================================================
# stat_significance
# ===========================================================================

class TestStatSignificance:
    @pytest.fixture
    def large_df(self):
        return pd.DataFrame({
            "gender": ["Male"] * 200 + ["Female"] * 200,
            "hired":  [1] * 160 + [0] * 40 + [1] * 60 + [0] * 140,
        })

    def test_returns_dict_with_required_keys(self, large_df):
        result = stat_significance(large_df, "gender", "Male", "Female", "hired")
        for key in ("p_value", "test", "conclusive"):
            assert key in result

    def test_significant_disparity_is_conclusive(self, large_df):
        result = stat_significance(large_df, "gender", "Male", "Female", "hired")
        assert result["conclusive"]

    def test_no_significance_for_equal_rates(self):
        df = pd.DataFrame({
            "gender": ["Male"] * 100 + ["Female"] * 100,
            "hired":  [1] * 50 + [0] * 50 + [1] * 50 + [0] * 50,
        })
        result = stat_significance(df, "gender", "Male", "Female", "hired")
        assert not result["conclusive"]

    def test_small_sample_uses_fisher(self):
        # Source uses n_total < 20 for Fisher, so keep total to 19
        df = pd.DataFrame({
            "gender": ["Male"] * 10 + ["Female"] * 9,
            "hired":  [1, 1, 1, 1, 1, 0, 0, 0, 0, 0] + [0] * 9,
        })
        result = stat_significance(df, "gender", "Male", "Female", "hired")
        assert result["test"] == "fisher"

    def test_large_sample_uses_chi2(self, large_df):
        result = stat_significance(large_df, "gender", "Male", "Female", "hired")
        assert result["test"] == "chi2"

    def test_empty_subset_returns_inconclusive(self, large_df):
        result = stat_significance(large_df, "gender", "Male", "Nonbinary", "hired")
        assert not result["conclusive"]

    def test_p_value_between_zero_and_one(self, large_df):
        result = stat_significance(large_df, "gender", "Male", "Female", "hired")
        assert 0.0 <= result["p_value"] <= 1.0

    def test_error_path_returns_safe_defaults(self):
        df = pd.DataFrame({"gender": [], "hired": []})
        result = stat_significance(df, "gender", "Male", "Female", "hired")
        assert not result["conclusive"]


# ===========================================================================
# compute_rates
# ===========================================================================

class TestComputeRates:
    @pytest.fixture
    def group_df(self):
        return pd.DataFrame({"hired": [1, 1, 0, 1, 0]})

    @pytest.fixture
    def group_df_with_actual(self):
        return pd.DataFrame({
            "hired":  [1, 1, 0, 1, 0, 1, 0, 0, 1, 1],
            "actual": [1, 1, 1, 0, 0, 1, 0, 1, 1, 0],
        })

    def test_basic_rate_calculation(self, group_df):
        result = compute_rates(group_df, "hired")
        assert result["total"] == 5
        assert result["selection_rate"] == pytest.approx(0.6)

    def test_empty_df_returns_zeros(self):
        df = pd.DataFrame({"hired": []})
        result = compute_rates(df, "hired")
        assert result["total"] == 0
        assert result["selection_rate"] == 0

    def test_all_zeros(self):
        df = pd.DataFrame({"hired": [0, 0, 0]})
        result = compute_rates(df, "hired")
        assert result["selection_rate"] == pytest.approx(0.0)

    def test_all_ones(self):
        df = pd.DataFrame({"hired": [1, 1, 1]})
        result = compute_rates(df, "hired")
        assert result["selection_rate"] == pytest.approx(1.0)

    def test_with_actual_column_includes_metrics(self, group_df_with_actual):
        result = compute_rates(group_df_with_actual, "hired")
        for key in ("tp", "fp", "tn", "fn", "tpr", "fpr", "precision"):
            assert key in result

    def test_tpr_in_range(self, group_df_with_actual):
        result = compute_rates(group_df_with_actual, "hired")
        assert 0.0 <= result["tpr"] <= 1.0

    def test_fpr_in_range(self, group_df_with_actual):
        result = compute_rates(group_df_with_actual, "hired")
        assert 0.0 <= result["fpr"] <= 1.0

    def test_precision_in_range(self, group_df_with_actual):
        result = compute_rates(group_df_with_actual, "hired")
        assert 0.0 <= result["precision"] <= 1.0

    def test_non_numeric_outcome_coerced(self):
        df = pd.DataFrame({"hired": ["1", "0", "1", "bad"]})
        result = compute_rates(df, "hired")
        assert result["total"] == 4
        assert result["selection_rate"] == pytest.approx(0.5)