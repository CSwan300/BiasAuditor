import pandas as pd
from datetime import datetime
from typing import List, Dict
from scipy.stats import chi2_contingency, fisher_exact
from backend.config import MIN_GROUP_SIZE
from backend.modules.Build_pdf.mitigation import suggest_mitigation


class BiasAuditor:
    def __init__(self, df: pd.DataFrame, fairness_threshold: float):
        self.df = df.copy()
        self.fairness_threshold = float(fairness_threshold) if fairness_threshold <= 1 else float(
            fairness_threshold) / 100
        self._preprocess()

    def _preprocess(self):
        self.df.columns = [str(c).strip().lower().replace(" ", "_") for c in self.df.columns]
        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                self.df[col] = self.df[col].fillna("Unknown").astype(str)

    def _calculate_significance(self, group_col: str, group_a: str, group_b: str, outcome_col: str) -> bool:
        try:
            subset = self.df[self.df[group_col].isin([group_a, group_b])].copy()
            subset[outcome_col] = pd.to_numeric(subset[outcome_col], errors='coerce').fillna(0).astype(int)
            ct = pd.crosstab(subset[group_col], subset[outcome_col])
            ct = ct.reindex(index=[group_a, group_b], columns=[0, 1], fill_value=0)

            n_total = ct.values.sum()
            if n_total < 5:
                return False

            if n_total < 30:
                _, p = fisher_exact(ct.values)
            else:
                _, p, _, _ = chi2_contingency(ct.values)

            return p < 0.05
        except Exception:
            return False

    def analyze_attribute(self, protected_col: str, outcome_col: str) -> Dict:
        if protected_col not in self.df.columns:
            return None

        target_series = pd.to_numeric(self.df[outcome_col], errors='coerce').fillna(0)
        temp_df = pd.DataFrame({
            'group': self.df[protected_col].astype(str),
            'outcome': target_series
        })

        stats_df = temp_df.groupby('group')['outcome'].agg(['count', 'mean']).reset_index()

        group_stats_map = {}
        for _, row in stats_df.iterrows():
            group_stats_map[row['group']] = {
                "total": int(row['count']),
                "selection_rate": float(row['mean'])
            }

        ref_idx = stats_df['mean'].idxmax()
        ref_group = stats_df.loc[ref_idx, 'group']
        ref_rate = stats_df.loc[ref_idx, 'mean']

        groups_list = []
        for _, row in stats_df.iterrows():
            ratio = float(row['mean'] / ref_rate) if ref_rate > 0 else 1.0
            is_significant = self._calculate_significance(protected_col, ref_group, row['group'], outcome_col)

            groups_list.append({
                "group": row['group'],
                "rate": round(row['mean'] * 100, 1),
                "count": int(row['count']),
                "is_privileged": row['group'] == ref_group,
                "disparity_ratio": round(ratio, 3),
                "stat_sig": bool(is_significant)
            })

        min_rate = stats_df['mean'].min()
        di_ratio = float(min_rate / ref_rate) if ref_rate > 0 else 1.0
        is_flagged = bool(di_ratio < self.fairness_threshold)

        mitigations = suggest_mitigation(
            group_stats=group_stats_map,
            passes=not is_flagged,
            threshold=self.fairness_threshold
        )

        return {
            "characteristic": protected_col.upper(),
            "privileged_group": ref_group,
            "groups": groups_list,
            "disparity": {
                "disparate_impact_ratio": round(di_ratio, 3),
                "flag": is_flagged
            },
            "attribute_mitigations": mitigations
        }

    def full_audit(self, protected_cols: List[str] = None, outcome_col: str = None) -> Dict:
        # Ensure we aren't auditing a timestamp or ID by default because im an idiot and left that in
        target = outcome_col if outcome_col else self.df.columns[-1]

        audits = []
        all_mitigations = []

        for col in (protected_cols or []):
            res = self.analyze_attribute(col, target)
            if res:
                audits.append(res)
                actionable = [m for m in res["attribute_mitigations"] if m["type"] != "none"]
                all_mitigations.extend(actionable)

        # Use single words for levels to avoid "High Risk Risk" in UI
        flagged_count = sum(1 for a in audits if a['disparity']['flag'])
        if flagged_count >= 3:
            level = "High"
        elif flagged_count > 0:
            level = "Moderate"
        else:
            level = "Low"

        # min_ratio of 0.2 (Bad) now becomes 80 (High Risk)
        # min_ratio of 1.0 (Good) now becomes 0 (Low Risk)
        min_ratio = min([a['disparity']['disparate_impact_ratio'] for a in audits], default=1.0)
        risk_score = int((1.0 - min_ratio) * 100)

        return {
            "overall_risk": {
                "level": level,
                "score": risk_score,
                "flagged_count": flagged_count,
                "flagged_characteristics": [a['characteristic'] for a in audits if a['disparity']['flag']]
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "protected_characteristics_found": protected_cols or [],
                "prediction_column": target,
                "fairness_threshold_applied": self.fairness_threshold,
                "min_group_size_config": MIN_GROUP_SIZE
            },
            "audits": audits,
            "mitigations": all_mitigations
        }