import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact

def risk_level(pct_failed: float) -> str:
    if pct_failed == 0:
        return "Low"
    elif pct_failed <= 0.25:
        return "Moderate"
    elif pct_failed <= 0.60:
        return "High"
    return "Critical"

def stat_significance(df: pd.DataFrame, group_col: str, group_a: str, group_b: str, outcome_col: str) -> dict:
    try:
        subset = df[df[group_col].isin([group_a, group_b])].copy()
        subset[outcome_col] = pd.to_numeric(subset[outcome_col], errors='coerce').fillna(0).astype(int)

        ct = pd.crosstab(subset[group_col], subset[outcome_col])
        ct = ct.reindex(index=[group_a, group_b], columns=[0, 1], fill_value=0)

        n_total = ct.values.sum()
        if n_total == 0:
            return {"p_value": 1.0, "test": "none", "conclusive": False}

        if n_total < 20:
            _, p = fisher_exact(ct.values)
            test = "fisher"
        else:
            _, p, _, _ = chi2_contingency(ct.values)
            test = "chi2"

        return {
            "p_value": round(float(p), 4),
            "test": test,
            "conclusive": p < 0.05
        }
    except Exception:
        return {"p_value": 1.0, "test": "error", "conclusive": False}