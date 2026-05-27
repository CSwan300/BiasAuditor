import pandas as pd

def compute_rates(group_df: pd.DataFrame, outcome_col: str) -> dict:
    total = len(group_df)
    if total == 0:
        return {"total": 0, "selection_rate": 0}

    series = pd.to_numeric(group_df[outcome_col], errors='coerce').fillna(0)
    pos_rate = series.mean()

    result = {"total": total, "selection_rate": round(float(pos_rate), 4)}

    if "actual" in group_df.columns:
        actual = pd.to_numeric(group_df["actual"], errors='coerce').fillna(0)
        predicted = series

        tp = ((predicted == 1) & (actual == 1)).sum()
        fp = ((predicted == 1) & (actual == 0)).sum()
        tn = ((predicted == 0) & (actual == 0)).sum()
        fn = ((predicted == 0) & (actual == 1)).sum()

        result.update({
            "tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn),
            "tpr": round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0,
            "fpr": round(fp / (fp + tn), 4) if (fp + tn) > 0 else 0,
            "precision": round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0,
        })
    return result