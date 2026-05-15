import pandas as pd
import numpy as np
from typing import Any

PROTECTED_CHARACTERISTICS = ["age", "gender", "ethnicity", "race", "sex"]
PREDICTION_COLUMNS = ["prediction", "label", "outcome", "result", "score", "target"]


class BiasAuditor:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.df.columns = [c.strip().lower() for c in self.df.columns]

    def _detect_protected_cols(self) -> list[str]:
        return [c for c in self.df.columns if c in PROTECTED_CHARACTERISTICS]

    def _detect_prediction_col(self) -> str | None:
        for col in PREDICTION_COLUMNS:
            if col in self.df.columns:
                return col
        # Fallback: last numeric column
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            return numeric_cols[-1]
        return None

    def _bin_age(self, series: pd.Series) -> pd.Series:
        """Bin numeric age into readable groups."""
        try:
            numeric = pd.to_numeric(series, errors="coerce")
            if numeric.notna().sum() > len(series) * 0.5:
                bins = [0, 18, 30, 45, 60, 75, 120]
                labels = ["<18", "18-29", "30-44", "45-59", "60-74", "75+"]
                return pd.cut(numeric, bins=bins, labels=labels, right=False).astype(str)
        except Exception:
            pass
        return series.astype(str)

    def _group_stats(self, protected_col: str, prediction_col: str) -> list[dict]:
        col_data = self.df[protected_col].copy()
        if protected_col == "age":
            col_data = self._bin_age(col_data)

        col_data = col_data.fillna("Unknown").astype(str)
        pred_data = pd.to_numeric(self.df[prediction_col], errors="coerce")

        results = []
        total = len(col_data)

        for group, group_df in col_data.groupby(col_data):
            indices = group_df.index
            group_pred = pred_data.loc[indices]
            count = len(indices)

            if pred_data.dropna().isin([0, 1]).all():
                rate = float(group_pred.mean()) if count > 0 else 0.0
                metric_label = "Positive Prediction Rate"
            else:
                rate = float(group_pred.mean()) if count > 0 else 0.0
                metric_label = "Average Prediction Score"

            results.append({
                "group": group,
                "count": int(count),
                "percentage": round(count / total * 100, 1),
                "rate": round(rate, 4),
                "metric_label": metric_label,
            })

        results.sort(key=lambda x: x["count"], reverse=True)
        return results

    def _calculate_disparity(self, group_stats: list[dict]) -> dict:
        rates = [g["rate"] for g in group_stats if g["count"] > 0]
        if len(rates) < 2:
            return {"max_disparity": 0, "disparate_impact_ratio": 1.0, "flag": False}

        max_rate = max(rates)
        min_rate = min(rates)
        disparity = round(max_rate - min_rate, 4)

        # Disparate impact ratio: minority rate / majority rate
        dir_ratio = round(min_rate / max_rate, 4) if max_rate > 0 else 1.0

        # 80% rule: flag if ratio < 0.8
        flagged = dir_ratio < 0.8

        return {
            "max_disparity": disparity,
            "disparate_impact_ratio": dir_ratio,
            "flag": flagged,
            "highest_group": max(group_stats, key=lambda x: x["rate"])["group"],
            "lowest_group": min(group_stats, key=lambda x: x["rate"])["group"],
        }

    def _overall_risk_score(self, audits: list[dict]) -> dict:
        flagged = [a for a in audits if a["disparity"]["flag"]]
        score = len(flagged) / len(audits) if audits else 0
        if score == 0:
            level = "Low"
            color = "green"
        elif score <= 0.33:
            level = "Moderate"
            color = "yellow"
        elif score <= 0.66:
            level = "High"
            color = "orange"
        else:
            level = "Critical"
            color = "red"

        return {
            "score": round(score * 100),
            "level": level,
            "color": color,
            "flagged_characteristics": [a["characteristic"] for a in flagged],
        }

    def run_audit(self) -> dict[str, Any]:
        protected_cols = self._detect_protected_cols()
        prediction_col = self._detect_prediction_col()

        metadata = {
            "total_rows": int(len(self.df)),
            "total_columns": int(len(self.df.columns)),
            "columns_detected": list(self.df.columns),
            "protected_characteristics_found": protected_cols,
            "prediction_column": prediction_col,
        }

        if not protected_cols:
            return {
                "metadata": metadata,
                "audits": [],
                "overall_risk": {"score": 0, "level": "Unknown", "color": "gray", "flagged_characteristics": []},
                "warnings": ["No protected characteristic columns found. Expected columns: age, gender, ethnicity, race, sex."],
            }

        if not prediction_col:
            return {
                "metadata": metadata,
                "audits": [],
                "overall_risk": {"score": 0, "level": "Unknown", "color": "gray", "flagged_characteristics": []},
                "warnings": ["No prediction/outcome column found. Expected: prediction, label, outcome, result, score, target."],
            }

        audits = []
        for col in protected_cols:
            group_stats = self._group_stats(col, prediction_col)
            disparity = self._calculate_disparity(group_stats)
            audits.append({
                "characteristic": col,
                "groups": group_stats,
                "disparity": disparity,
            })

        overall_risk = self._overall_risk_score(audits)

        return {
            "metadata": metadata,
            "audits": audits,
            "overall_risk": overall_risk,
            "warnings": [],
        }