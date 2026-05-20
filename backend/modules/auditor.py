import pandas as pd
import datetime
import numpy as np
from typing import Optional, List, Dict

from backend.modules.utils import risk_level, stat_significance
from backend.modules.mitigation import suggest_mitigation
from backend.config import AGE_BINS, AGE_LABELS


class BiasAuditor:
    def __init__(self, df: pd.DataFrame, fairness_threshold: float = 0.80):
        self.df = df.copy()
        self.fairness_threshold = fairness_threshold
        self._preprocess()

    def _preprocess(self):
        """Normalizes columns and handles basic data cleaning."""
        self.df.columns = [c.strip().lower().replace(" ", "_") for c in self.df.columns]

        if "age" in self.df.columns and pd.api.types.is_numeric_dtype(self.df["age"]):
            self.df["age"] = pd.cut(self.df["age"], bins=AGE_BINS, labels=AGE_LABELS, right=True)

        for col in self.df.select_dtypes(include="object").columns:
            self.df[col] = self.df[col].fillna("Unknown").astype(str).str.strip()

    def full_audit(self, protected_cols: Optional[List[str]] = None, outcome_col: Optional[str] = None) -> Dict:
        """Entry point: returns JSON structure matching AuditResponse TypeScript interface."""

        # 1. Resolve Outcome Column
        target = outcome_col.strip().lower().replace(" ", "_") if outcome_col else None
        if not target or target not in self.df.columns:
            common_targets = ['hired', 'target', 'label', 'approved', 'output']
            found = [c for c in self.df.columns if any(t in c for t in common_targets)]
            target = found[0] if found else self.df.columns[-1]

        # 2. Resolve Protected Columns
        if not protected_cols:
            protected_cols = [
                c for c in self.df.columns
                if 1 < self.df[c].nunique() < 15 and c != target
            ]

        audits = []
        flagged_chars = []

        for col in protected_cols:
            try:
                report = self.analyze_attribute(col, target)
                audits.append(report)
                if report['disparity']['flag']:
                    flagged_chars.append(report['characteristic'])
            except Exception as e:
                print(f"Error auditing {col}: {str(e)}")
                continue

        # 3. Calculate Overall Risk
        all_di = [a['disparity']['disparate_impact_ratio'] for a in audits]
        min_di = min(all_di) if all_di else 1.0

        # Calculate score and level for frontend enum
        score = int((1 - min_di) * 100)
        if min_di < 0.5:
            level = "Critical"
        elif min_di < 0.8:
            level = "High"
        elif min_di < 0.9:
            level = "Moderate"
        else:
            level = "Low"

        return {
            "overall_risk": {
                "level": level,
                "score": max(0, score),
                "flagged_characteristics": flagged_chars
            },
            "metadata": {
                "timestamp": datetime.datetime.now().isoformat(),
                "total_rows": int(len(self.df)),
                "total_columns": int(len(self.df.columns)),
                "prediction_column": str(target),
                "protected_characteristics_found": protected_cols,
                "columns_detected": list(self.df.columns)
            },
            "warnings": [],
            "audits": audits
        }

    def analyze_attribute(self, protected_col: str, outcome_col: str) -> Dict:
        """Computes metrics and casts all types to standard Python for JSON safety."""
        temp_df = self.df[[protected_col, outcome_col]].copy()

        # Convert outcome to binary
        if not pd.api.types.is_numeric_dtype(temp_df[outcome_col]):
            unique_vals = temp_df[outcome_col].unique()
            favorable = unique_vals[1] if len(unique_vals) > 1 else unique_vals[0]
            temp_df['binary_outcome'] = (temp_df[outcome_col] == favorable).astype(int)
        else:
            temp_df['binary_outcome'] = temp_df[outcome_col]

        # Stats calculation
        stats = temp_df.groupby(protected_col)['binary_outcome'].agg(['count', 'mean']).reset_index()
        stats.columns = [protected_col, 'count', 'rate']

        ref_idx = stats['rate'].idxmax()
        low_idx = stats['rate'].idxmin()
        ref_group = stats.loc[ref_idx, protected_col]
        ref_rate = stats.loc[ref_idx, 'rate']

        groups = []
        total_rows = len(temp_df)
        for _, row in stats.iterrows():
            groups.append({
                "group": str(row[protected_col]),
                "rate": float(round(row['rate'], 4)),
                "count": int(row['count']),
                "percentage": f"{(row['count'] / total_rows) * 100:.1f}%"
            })

        min_rate = stats['rate'].min()
        di_ratio = float(min_rate / ref_rate) if ref_rate > 0 else 1.0

        # CRITICAL: Wrap comparisons in bool() to avoid numpy.bool_ errors
        is_flagged = bool(di_ratio < self.fairness_threshold)

        return {
            "characteristic": protected_col.replace("_", " ").title(),
            "groups": groups,
            "disparity": {
                "disparate_impact_ratio": float(round(di_ratio, 3)),
                "max_disparity": float(round(1 - di_ratio, 3)),
                "flag": is_flagged,
                "highest_group": str(ref_group),
                "lowest_group": str(stats.loc[low_idx, protected_col])
            }
        }