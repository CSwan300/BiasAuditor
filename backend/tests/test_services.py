"""
Tests for backend/modules/AuditLogic/services.py
Covers: load_dataframe, parse_list, build_intersectional_pairs
"""
import io
import pytest
import pandas as pd
from unittest.mock import MagicMock
from fastapi import HTTPException

# Try services module first, fall back to main where these may live
try:
    from backend.modules.AuditLogic.services import (
        load_dataframe,
        parse_list,
        build_intersectional_pairs,
    )
except ImportError:
    from backend.main import (
        load_dataframe,
        parse_list,
        build_intersectional_pairs,
    )


def _make_upload(content: bytes, filename: str) -> MagicMock:
    mock = MagicMock()
    mock.filename = filename
    mock.file = io.BytesIO(content)
    return mock


def _csv(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()


# ===========================================================================
# load_dataframe
# ===========================================================================

class TestLoadDataframe:
    def test_csv_loads(self):
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        upload = _make_upload(_csv(df), "data.csv")
        result = load_dataframe(upload)
        assert list(result.columns) == ["a", "b"]
        assert len(result) == 2

    def test_xlsx_loads(self):
        buf = io.BytesIO()
        pd.DataFrame({"x": [1], "y": [2]}).to_excel(buf, index=False)
        buf.seek(0)
        upload = _make_upload(buf.read(), "data.xlsx")
        result = load_dataframe(upload)
        assert list(result.columns) == ["x", "y"]

    def test_xls_extension_accepted(self):
        buf = io.BytesIO()
        pd.DataFrame({"x": [1]}).to_excel(buf, index=False)
        buf.seek(0)
        upload = _make_upload(buf.read(), "data.xls")
        result = load_dataframe(upload)
        assert len(result) == 1

    def test_unsupported_type_raises_400(self):
        upload = _make_upload(b"hello", "data.json")
        with pytest.raises(HTTPException) as exc:
            load_dataframe(upload)
        assert exc.value.status_code == 422

    def test_empty_file_raises_422(self):
        upload = _make_upload(b"", "data.csv")
        with pytest.raises(HTTPException) as exc:
            load_dataframe(upload)
        assert exc.value.status_code == 422

    def test_malformed_csv_still_loads(self):
        csv_bytes = b"a,b\n1,2\n3,4,extra\n5,6\n"
        upload = _make_upload(csv_bytes, "data.csv")
        result = load_dataframe(upload)
        assert len(result) >= 2


# ===========================================================================
# parse_list
# ===========================================================================

class TestParseList:
    def test_json_array(self):
        assert parse_list('["gender", "race"]') == ["gender", "race"]

    def test_comma_separated(self):
        assert parse_list("gender, race, age") == ["gender", "race", "age"]

    def test_single_value(self):
        assert parse_list("gender") == ["gender"]

    def test_none_returns_none(self):
        assert parse_list(None) is None

    def test_empty_string_returns_none(self):
        assert parse_list("") is None

    def test_whitespace_only_returns_none(self):
        assert parse_list("   ") is None

    def test_broken_json_falls_back_to_split(self):
        result = parse_list("[gender, race")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_strips_whitespace_from_items(self):
        assert parse_list("  gender  ,  race  ") == ["gender", "race"]


# ===========================================================================
# build_intersectional_pairs
# ===========================================================================

class TestBuildIntersectionalPairs:
    @pytest.fixture
    def base_df(self):
        return pd.DataFrame({
            "gender": ["Male", "Female"] * 5,
            "race":   ["White", "Black"] * 5,
            "hired":  [1, 0] * 5,
        })

    def test_creates_combined_column(self, base_df):
        result = build_intersectional_pairs(base_df, ["gender,race"])
        assert "gender_race" in result.columns

    def test_combined_values_format(self, base_df):
        result = build_intersectional_pairs(base_df, ["gender,race"])
        assert result["gender_race"].iloc[0] == "Male | White"

    def test_plus_separator(self, base_df):
        result = build_intersectional_pairs(base_df, ["gender+race"])
        assert "gender_race" in result.columns

    def test_semicolon_separator(self, base_df):
        result = build_intersectional_pairs(base_df, ["gender;race"])
        assert "gender_race" in result.columns

    def test_empty_pairs_unchanged(self, base_df):
        result = build_intersectional_pairs(base_df, [])
        assert list(result.columns) == list(base_df.columns)

    def test_missing_column_skipped(self, base_df):
        result = build_intersectional_pairs(base_df, ["gender,nonexistent"])
        assert "gender_nonexistent" not in result.columns

    def test_original_df_not_mutated(self, base_df):
        original_cols = list(base_df.columns)
        build_intersectional_pairs(base_df, ["gender,race"])
        assert list(base_df.columns) == original_cols

    def test_multiple_pairs(self, base_df):
        result = build_intersectional_pairs(base_df, ["gender,race", "gender,hired"])
        assert "gender_race" in result.columns
        assert "gender_hired" in result.columns