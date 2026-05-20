import pandas as pd
from typing import List, Optional, Dict


class BiasAuditor:
    def __init__(self, df: pd.DataFrame, fairness_threshold: float = 0.80):
        self.df = df.copy()
        self.fairness_threshold = float(fairness_threshold)
        self._preprocess()

    def _preprocess(self):
        # Normalize columns: No spaces, all lowercase
        self.df.columns = [str(c).strip().lower().replace(" ", "_") for c in self.df.columns]
        # Fill missing values so the groupby doesn't drop rows
        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                self.df[col] = self.df[col].fillna("Unknown").astype(str)

    def analyze_attribute(self, protected_col: str, outcome_col: str) -> Dict:
        # Safety check: does the column actually exist?
        if protected_col not in self.df.columns:
            return None

        # Convert outcome to numeric (1 for pass, 0 for fail)
        target_series = pd.to_numeric(self.df[outcome_col], errors='coerce').fillna(0)

        temp_df = pd.DataFrame({
            'group': self.df[protected_col].astype(str),
            'outcome': target_series
        })

        stats = temp_df.groupby('group')['outcome'].agg(['count', 'mean']).reset_index()

        ref_rate = stats['mean'].max()
        min_rate = stats['mean'].min()

        # Division by zero safety
        di_ratio = float(min_rate / ref_rate) if ref_rate > 0 else 1.0
        is_flagged = bool(di_ratio < self.fairness_threshold)

        return {
            "characteristic": protected_col.upper(),
            "groups": [
                {"group": row['group'], "rate": round(row['mean'] * 100, 1), "count": int(row['count'])}
                for _, row in stats.iterrows()
            ],
            "disparity": {
                "disparate_impact_ratio": round(di_ratio, 3),
                "flag": is_flagged
            }
        }

    def full_audit(self, protected_cols: List[str] = None, outcome_col: str = None) -> Dict:
        # Default to last column if none provided
        target = outcome_col if outcome_col else self.df.columns[-1]

        audits = []
        for col in (protected_cols or []):
            res = self.analyze_attribute(col, target)
            if res: audits.append(res)

        flagged_count = sum(1 for a in audits if a['disparity']['flag'])

        level = "Low Risk"
        if flagged_count >= 3:
            level = "High Risk"
        elif flagged_count > 0:
            level = "Moderate Risk"

        return {
            "overall_risk": {
                "level": level,
                "score": int(min([a['disparity']['disparate_impact_ratio'] for a in audits], default=1.0) * 100)
            },
            "audits": audits
        }