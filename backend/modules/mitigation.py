from backend.config import MIN_GROUP_SIZE


def suggest_mitigation(group_stats: dict, passes: bool, threshold: float) -> list[dict]:
    if passes:
        return [{"type": "none", "message": "No mitigation required."}]

    suggestions = []
    # Filter groups by minimum size per config
    rates = {g: s["selection_rate"] for g, s in group_stats.items() if s.get("total", 0) >= MIN_GROUP_SIZE}

    if not rates:
        return []

    max_r = max(rates.values())
    underrep = [g for g, r in rates.items() if r < max_r * threshold]
    smallest_size = min([group_stats[g]["total"] for g in underrep]) if underrep else 0

    if underrep:
        suggestions.append({
            "type": "reweighting",
            "priority": "high",
            "title": "Sample Reweighting",
            "description": f"Assign higher weights to: {', '.join(underrep)}."
        })

    if 0 < smallest_size < 500:
        suggestions.append({
            "type": "smote",
            "priority": "medium",
            "title": "Synthetic Data Generation (SMOTE)",
            "description": f"Small sample size detected ({smallest_size} rows). Use SMOTE techniques to balance the training set."
        })

    suggestions.append({
        "type": "threshold_adjustment",
        "priority": "low",
        "title": "Decision Threshold Calibration",
        "description": "Adjust the decision boundary specifically for underrepresented groups to achieve parity."
    })

    return suggestions