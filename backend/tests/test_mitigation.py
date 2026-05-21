"""
Tests for backend/modules/Build_pdf/mitigation.py
"""
from unittest.mock import patch
from backend.modules.Build_pdf.mitigation import suggest_mitigation


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

PASSING_STATS = {
    "Male":   {"total": 500, "selection_rate": 0.8},
    "Female": {"total": 500, "selection_rate": 0.75},
}

FAILING_STATS_LARGE = {
    "White": {"total": 600, "selection_rate": 0.8},
    "Black": {"total": 600, "selection_rate": 0.3},
}

FAILING_STATS_SMALL = {
    "White": {"total": 600, "selection_rate": 0.8},
    "Black": {"total": 80,  "selection_rate": 0.3},   # < 500 → SMOTE
}

FAILING_STATS_TINY = {
    "White": {"total": 600, "selection_rate": 0.8},
    "Black": {"total": 3,   "selection_rate": 0.3},   # below MIN_GROUP_SIZE
}


# ---------------------------------------------------------------------------
# Passing scenario
# ---------------------------------------------------------------------------

class TestPassing:
    def test_returns_no_mitigation_when_passing(self):
        result = suggest_mitigation(PASSING_STATS, passes=True, threshold=0.8)
        assert len(result) == 1
        assert result[0]["type"] == "none"

    def test_message_present_when_passing(self):
        result = suggest_mitigation(PASSING_STATS, passes=True, threshold=0.8)
        assert "message" in result[0]


# ---------------------------------------------------------------------------
# Failing scenario – large sample
# ---------------------------------------------------------------------------

class TestFailingLargeSample:
    def test_reweighting_suggestion_present(self):
        result = suggest_mitigation(FAILING_STATS_LARGE, passes=False, threshold=0.8)
        types = [r["type"] for r in result]
        assert "reweighting" in types

    def test_threshold_adjustment_always_included(self):
        result = suggest_mitigation(FAILING_STATS_LARGE, passes=False, threshold=0.8)
        types = [r["type"] for r in result]
        assert "threshold_adjustment" in types

    def test_smote_not_suggested_for_large_sample(self):
        result = suggest_mitigation(FAILING_STATS_LARGE, passes=False, threshold=0.8)
        types = [r["type"] for r in result]
        assert "smote" not in types

    def test_reweighting_mentions_underrep_group(self):
        result = suggest_mitigation(FAILING_STATS_LARGE, passes=False, threshold=0.8)
        rw = next(r for r in result if r["type"] == "reweighting")
        assert "Black" in rw["description"]

    def test_all_results_have_required_keys(self):
        result = suggest_mitigation(FAILING_STATS_LARGE, passes=False, threshold=0.8)
        for item in result:
            for key in ("type", "priority", "title", "description"):
                assert key in item

    def test_reweighting_priority_is_high(self):
        result = suggest_mitigation(FAILING_STATS_LARGE, passes=False, threshold=0.8)
        rw = next(r for r in result if r["type"] == "reweighting")
        assert rw["priority"] == "high"

    def test_threshold_adjustment_priority_is_low(self):
        result = suggest_mitigation(FAILING_STATS_LARGE, passes=False, threshold=0.8)
        ta = next(r for r in result if r["type"] == "threshold_adjustment")
        assert ta["priority"] == "low"


# ---------------------------------------------------------------------------
# Failing scenario – small sample (SMOTE expected)
# ---------------------------------------------------------------------------

class TestFailingSmallSample:
    def test_smote_suggested_for_small_sample(self):
        result = suggest_mitigation(FAILING_STATS_SMALL, passes=False, threshold=0.8)
        types = [r["type"] for r in result]
        assert "smote" in types

    def test_smote_description_mentions_size(self):
        result = suggest_mitigation(FAILING_STATS_SMALL, passes=False, threshold=0.8)
        smote = next(r for r in result if r["type"] == "smote")
        assert "80" in smote["description"]

    def test_smote_priority_is_medium(self):
        result = suggest_mitigation(FAILING_STATS_SMALL, passes=False, threshold=0.8)
        smote = next(r for r in result if r["type"] == "smote")
        assert smote["priority"] == "medium"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_group_stats_returns_empty(self):
        result = suggest_mitigation({}, passes=False, threshold=0.8)
        assert result == []

    def test_all_groups_below_min_size_returns_empty(self):
        """Groups filtered out by MIN_GROUP_SIZE → rates dict is empty."""
        with patch("backend.modules.Build_pdf.mitigation.MIN_GROUP_SIZE", 1000):
            tiny_stats = {
                "A": {"total": 5, "selection_rate": 0.9},
                "B": {"total": 3, "selection_rate": 0.2},
            }
            result = suggest_mitigation(tiny_stats, passes=False, threshold=0.8)
            assert result == []

    def test_single_group_no_underrep(self):
        stats = {"Male": {"total": 500, "selection_rate": 0.8}}
        result = suggest_mitigation(stats, passes=False, threshold=0.8)
        # No underrepresented group means no reweighting, but threshold_adjustment still added
        types = [r["type"] for r in result]
        assert "threshold_adjustment" in types

    def test_result_is_list(self):
        result = suggest_mitigation(PASSING_STATS, passes=True, threshold=0.8)
        assert isinstance(result, list)

    def test_no_duplicates_in_types(self):
        result = suggest_mitigation(FAILING_STATS_SMALL, passes=False, threshold=0.8)
        types = [r["type"] for r in result]
        assert len(types) == len(set(types))