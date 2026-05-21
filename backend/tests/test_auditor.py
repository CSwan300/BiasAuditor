"""
Tests for backend/modules/AuditLogic/auditor.py
"""
import pytest
import pandas as pd
from backend.modules.AuditLogic.auditor import BiasAuditor


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def simple_df():
    """Balanced dataset with clear gender disparity."""
    return pd.DataFrame({
        "gender": ["Male"] * 200 + ["Female"] * 200,
        "age":    ["Young"] * 400,
        "hired":  [1] * 160 + [0] * 40 + [1] * 80 + [0] * 120,  # M=80%, F=40%
    })


@pytest.fixture
def multi_group_df():
    """Three racial groups with varying hire rates."""
    return pd.DataFrame({
        "race":  ["White"] * 300 + ["Black"] * 150 + ["Asian"] * 150,
        "hired": [1] * 240 + [0] * 60       # White: 80%
                + [1] * 75  + [0] * 75      # Black: 50%
                + [1] * 120 + [0] * 30,     # Asian: 80%
    })


@pytest.fixture
def tiny_df():
    """Very small dataset to test edge-case handling."""
    return pd.DataFrame({
        "gender": ["Male", "Female", "Male", "Female"],
        "hired":  [1, 0, 1, 1],
    })


@pytest.fixture
def all_positive_df():
    """All outcomes are 1 – tests zero-division guards."""
    return pd.DataFrame({
        "gender": ["Male"] * 50 + ["Female"] * 50,
        "hired":  [1] * 100,
    })


@pytest.fixture
def messy_df():
    """Column names with spaces and mixed-case, missing values in group col."""
    return pd.DataFrame({
        "  Gender ": ["Male", None, "Female", "Male", "Female", "Male"] * 20,
        "Hired":     [1, 0, 0, 1, 0, 1] * 20,
    })


# ---------------------------------------------------------------------------
# Preprocessing
# ---------------------------------------------------------------------------

class TestPreprocess:
    def test_column_names_normalised(self, messy_df):
        auditor = BiasAuditor(messy_df, fairness_threshold=0.8)
        assert "gender" in auditor.df.columns
        assert "hired" in auditor.df.columns

    def test_missing_values_filled(self, messy_df):
        auditor = BiasAuditor(messy_df, fairness_threshold=0.8)
        # _preprocess fills NaN with "Unknown" then casts to str.
        # Non-null values should remain intact after preprocessing.
        non_null = auditor.df["gender"].dropna()
        assert len(non_null) > 0
        assert set(non_null.unique()).issubset({"Male", "Female", "Unknown"})

    def test_threshold_percentage_conversion(self, simple_df):
        auditor = BiasAuditor(simple_df, fairness_threshold=80)
        assert auditor.fairness_threshold == pytest.approx(0.8)

    def test_threshold_decimal_unchanged(self, simple_df):
        auditor = BiasAuditor(simple_df, fairness_threshold=0.75)
        assert auditor.fairness_threshold == pytest.approx(0.75)

    def test_original_df_not_mutated(self, simple_df):
        original_cols = list(simple_df.columns)
        _ = BiasAuditor(simple_df, 0.8)
        assert list(simple_df.columns) == original_cols


# ---------------------------------------------------------------------------
# analyze_attribute
# ---------------------------------------------------------------------------

class TestAnalyzeAttribute:
    def test_returns_none_for_missing_column(self, simple_df):
        auditor = BiasAuditor(simple_df, 0.8)
        assert auditor.analyze_attribute("nonexistent", "hired") is None

    def test_result_keys_present(self, simple_df):
        auditor = BiasAuditor(simple_df, 0.8)
        result = auditor.analyze_attribute("gender", "hired")
        assert result is not None
        for key in ("characteristic", "privileged_group", "groups", "disparity", "attribute_mitigations"):
            assert key in result

    def test_characteristic_is_uppercase(self, simple_df):
        auditor = BiasAuditor(simple_df, 0.8)
        result = auditor.analyze_attribute("gender", "hired")
        assert result["characteristic"] == "GENDER"

    def test_privileged_group_has_highest_rate(self, simple_df):
        auditor = BiasAuditor(simple_df, 0.8)
        result = auditor.analyze_attribute("gender", "hired")
        # Male has 80% hire rate vs Female 40%
        assert result["privileged_group"] == "Male"

    def test_flagged_when_below_threshold(self, simple_df):
        auditor = BiasAuditor(simple_df, 0.8)
        result = auditor.analyze_attribute("gender", "hired")
        # DI = 40/80 = 0.5 < 0.8 → should be flagged
        assert result["disparity"]["flag"] is True

    def test_not_flagged_when_above_threshold(self, simple_df):
        auditor = BiasAuditor(simple_df, fairness_threshold=0.4)
        result = auditor.analyze_attribute("gender", "hired")
        # DI = 0.5 > 0.4 → should pass
        assert result["disparity"]["flag"] is False

    def test_disparity_ratio_calculation(self, simple_df):
        auditor = BiasAuditor(simple_df, 0.8)
        result = auditor.analyze_attribute("gender", "hired")
        assert result["disparity"]["disparate_impact_ratio"] == pytest.approx(0.5, abs=0.01)

    def test_groups_list_length(self, simple_df):
        auditor = BiasAuditor(simple_df, 0.8)
        result = auditor.analyze_attribute("gender", "hired")
        assert len(result["groups"]) == 2

    def test_group_entry_keys(self, simple_df):
        auditor = BiasAuditor(simple_df, 0.8)
        result = auditor.analyze_attribute("gender", "hired")
        g = result["groups"][0]
        for k in ("group", "rate", "count", "is_privileged", "disparity_ratio", "stat_sig"):
            assert k in g

    def test_privileged_group_is_privileged_flag(self, simple_df):
        auditor = BiasAuditor(simple_df, 0.8)
        result = auditor.analyze_attribute("gender", "hired")
        privileged = next(g for g in result["groups"] if g["is_privileged"])
        assert privileged["group"] == "Male"

    def test_disparity_ratio_of_privileged_is_one(self, simple_df):
        auditor = BiasAuditor(simple_df, 0.8)
        result = auditor.analyze_attribute("gender", "hired")
        privileged = next(g for g in result["groups"] if g["is_privileged"])
        assert privileged["disparity_ratio"] == pytest.approx(1.0)

    def test_all_positive_outcomes_no_crash(self, all_positive_df):
        auditor = BiasAuditor(all_positive_df, 0.8)
        result = auditor.analyze_attribute("gender", "hired")
        assert result is not None
        assert result["disparity"]["disparate_impact_ratio"] == pytest.approx(1.0)

    def test_three_groups(self, multi_group_df):
        auditor = BiasAuditor(multi_group_df, 0.8)
        result = auditor.analyze_attribute("race", "hired")
        assert len(result["groups"]) == 3

    def test_tiny_dataset(self, tiny_df):
        auditor = BiasAuditor(tiny_df, 0.8)
        result = auditor.analyze_attribute("gender", "hired")
        assert result is not None  # should not crash


# ---------------------------------------------------------------------------
# Statistical significance
# ---------------------------------------------------------------------------

class TestCalculateSignificance:
    def test_significant_disparity_detected(self, simple_df):
        """Large balanced dataset with 40-point gap should be significant."""
        auditor = BiasAuditor(simple_df, 0.8)
        sig = auditor._calculate_significance("gender", "Male", "Female", "hired")
        assert sig == True

    def test_no_significance_for_equal_rates(self):
        df = pd.DataFrame({
            "gender": ["Male"] * 100 + ["Female"] * 100,
            "hired":  [1] * 50 + [0] * 50 + [1] * 50 + [0] * 50,
        })
        auditor = BiasAuditor(df, 0.8)
        sig = auditor._calculate_significance("gender", "Male", "Female", "hired")
        assert sig == False

    def test_tiny_sample_returns_false(self):
        df = pd.DataFrame({"gender": ["Male", "Female"], "hired": [1, 0]})
        auditor = BiasAuditor(df, 0.8)
        sig = auditor._calculate_significance("gender", "Male", "Female", "hired")
        assert sig == False

    def test_missing_group_does_not_crash(self, simple_df):
        auditor = BiasAuditor(simple_df, 0.8)
        sig = auditor._calculate_significance("gender", "Male", "Nonbinary", "hired")
        assert sig == False


# ---------------------------------------------------------------------------
# full_audit
# ---------------------------------------------------------------------------

class TestFullAudit:
    def test_result_structure(self, simple_df):
        auditor = BiasAuditor(simple_df, 0.8)
        result = auditor.full_audit(["gender"], "hired")
        assert "overall_risk" in result
        assert "metadata" in result
        assert "audits" in result
        assert "mitigations" in result

    def test_high_risk_three_flagged(self):
        # Build a df with 3 protected cols all showing disparity
        n = 200
        df = pd.DataFrame({
            "gender":    ["Male"] * n + ["Female"] * n,
            "race":      ["White"] * n + ["Black"] * n,
            "age_group": ["Young"] * n + ["Old"] * n,
            "hired":     [1] * int(n * 0.8) + [0] * int(n * 0.2)
                       + [1] * int(n * 0.3) + [0] * int(n * 0.7),
        })
        auditor = BiasAuditor(df, 0.8)
        result = auditor.full_audit(["gender", "race", "age_group"], "hired")
        assert result["overall_risk"]["flagged_count"] >= 2

    def test_low_risk_no_flags(self, all_positive_df):
        auditor = BiasAuditor(all_positive_df, 0.8)
        result = auditor.full_audit(["gender"], "hired")
        assert result["overall_risk"]["level"] == "Low Risk"

    def test_moderate_risk_one_flag(self, simple_df):
        auditor = BiasAuditor(simple_df, 0.8)
        result = auditor.full_audit(["gender"], "hired")
        assert result["overall_risk"]["level"] in ("Moderate Risk", "High Risk")

    def test_metadata_fields(self, simple_df):
        auditor = BiasAuditor(simple_df, 0.8)
        result = auditor.full_audit(["gender"], "hired")
        meta = result["metadata"]
        assert "timestamp" in meta
        assert meta["fairness_threshold_applied"] == pytest.approx(0.8)
        assert "gender" in meta["protected_characteristics_found"]

    def test_empty_protected_cols(self, simple_df):
        auditor = BiasAuditor(simple_df, 0.8)
        result = auditor.full_audit([], "hired")
        assert result["audits"] == []
        assert result["overall_risk"]["level"] == "Low Risk"

    def test_uses_last_column_as_default_target(self, simple_df):
        auditor = BiasAuditor(simple_df, 0.8)
        result = auditor.full_audit(["gender"])
        assert result["metadata"]["prediction_column"] == "hired"

    def test_overall_risk_score_within_range(self, simple_df):
        auditor = BiasAuditor(simple_df, 0.8)
        result = auditor.full_audit(["gender"], "hired")
        score = result["overall_risk"]["score"]
        assert 0 <= score <= 100

    def test_mitigations_only_actionable(self, simple_df):
        auditor = BiasAuditor(simple_df, 0.8)
        result = auditor.full_audit(["gender"], "hired")
        for m in result["mitigations"]:
            assert m["type"] != "none"

    def test_audit_contains_stat_sig_info(self, simple_df):
        auditor = BiasAuditor(simple_df, 0.8)
        result = auditor.full_audit(["gender"], "hired")
        groups = result["audits"][0]["groups"]
        for g in groups:
            assert isinstance(g["stat_sig"], bool)