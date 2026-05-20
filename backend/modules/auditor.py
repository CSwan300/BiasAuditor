import pandas as pd
import datetime
from typing import Optional, List, Dict
from backend.config import AGE_BINS, AGE_LABELS


class BiasAuditor:
    def __init__(self, df: pd.DataFrame, fairness_threshold: float = 0.80):
        self.df = df.copy()
        # FIX: Ensure threshold is a decimal (e.g., 0.8) regardless of slider scale (0-100 vs 0-1)
        try:
            val = float(fairness_threshold)
            self.fairness_threshold = val if val <= 1 else val / 100
        except:
            self.fairness_threshold = 0.80

        self._preprocess()

    def _preprocess(self):
        self.df.columns = [c.strip().lower().replace(" ", "_") for c in self.df.columns]
        if "age" in self.df.columns and pd.api.types.is_numeric_dtype(self.df["age"]):
            self.df["age"] = pd.cut(self.df["age"], bins=AGE_BINS, labels=AGE_LABELS, right=True)
        for col in self.df.select_dtypes(include="object").columns:
            self.df[col] = self.df[col].fillna("Unknown").astype(str).str.strip()

    def analyze_attribute(self, protected_col: str, outcome_col: str) -> Dict:
        temp_df = self.df[[protected_col, outcome_col]].copy()
        if not pd.api.types.is_numeric_dtype(temp_df[outcome_col]):
            unique_vals = temp_df[outcome_col].unique()
            favorable = unique_vals[1] if len(unique_vals) > 1 else unique_vals[0]
            temp_df['binary_outcome'] = (temp_df[outcome_col] == favorable).astype(int)
        else:
            temp_df['binary_outcome'] = temp_df[outcome_col]

        stats = temp_df.groupby(protected_col)['binary_outcome'].agg(['count', 'mean']).reset_index()
        stats.columns = [protected_col, 'count', 'rate']

        ref_rate = stats['rate'].max()
        min_rate = stats['rate'].min()
        di_ratio = float(min_rate / ref_rate) if ref_rate > 0 else 1.0

        # THIS IS THE CRITICAL FLAG: Tied to your slider
        is_flagged = bool(di_ratio < self.fairness_threshold)

        return {
            "characteristic": protected_col.replace("_", " ").upper(),
            "groups": [
                {"group": str(r[protected_col]), "rate": float(round(r['rate'] * 100, 1)), "count": int(r['count'])} for
                _, r in stats.iterrows()],
            "disparity": {
                "disparate_impact_ratio": float(round(di_ratio, 3)),
                "flag": is_flagged  # This boolean is sent to the PDF
            }
        }

    def full_audit(self, protected_cols: Optional[List[str]] = None, outcome_col: Optional[str] = None) -> Dict:
        target = outcome_col.strip().lower().replace(" ", "_") if outcome_col else self.df.columns[-1]
        audits = [self.analyze_attribute(col, target) for col in protected_cols if col in self.df.columns]

        # Flags found based on YOUR slider
        flagged_chars = [a['characteristic'] for a in audits if a['disparity']['flag']]

        # Sync Risk Level with Dashboard
        # If no flags exist at your current threshold, it's Low Risk.
        if len(flagged_chars) == 0:
            level = "Low Risk"
        elif len(flagged_chars) < 3:
            level = "Moderate Risk"
        else:
            level = "High Risk"

        return {
            "overall_risk": {"level": level, "score": int(
                min([a['disparity']['disparate_impact_ratio'] for a in audits], default=1.0) * 100)},
            "audits": audits
        }