# Bias Auditing Formulas Reference

---

## ⚖️ The Four-Fifths Rule

The **four-fifths rule** (also called the **80% rule**) is a screening guideline used to detect possible adverse impact in selection decisions such as hiring, promotion, or admissions. A group may warrant review if its selection rate is less than **80%** of the highest selection rate among the compared groups.

### Formulas

The four-fifths rule is based on selection rates:

$$
\text{Selection Rate} = \frac{\text{Number of Favorable Outcomes}}{\text{Total Number of Cases in the Group}}
$$

$$
\text{Impact Ratio} = \frac{\text{Selection Rate of the Evaluated Group}}{\text{Selection Rate of the Reference Group}}
$$

> **Note:** The reference group is the demographic with the highest selection rate. If the impact ratio is below **0.80**, the result may indicate adverse impact.

### Example Calculation
If Group A is selected 50% of the time and Group B is selected 35% of the time:

$$
\frac{0.35}{0.50} = 0.70
$$

Since $0.70 < 0.80$, the result falls below the four-fifths rule threshold and merits further review.

---

## 📊 Confusion Matrix Formulas

These apply when an `actual` ground-truth column is available for comparison.

* **True Positives ($TP$):** $\sum(\text{predicted} = 1 \land \text{actual} = 1)$ — Correct positive decisions.
* **False Positives ($FP$):** $\sum(\text{predicted} = 1 \land \text{actual} = 0)$ — Incorrect positive decisions.
* **True Negatives ($TN$):** $\sum(\text{predicted} = 0 \land \text{actual} = 0)$ — Correct negative decisions.
* **False Negatives ($FN$):** $\sum(\text{predicted} = 0 \land \text{actual} = 1)$ — Missed positive cases.

---

## 📉 Performance & Error Metrics

* **True Positive Rate ($TPR$):** $\frac{TP}{TP + FN}$ — The share of actual positives correctly identified.
* **False Positive Rate ($FPR$):** $\frac{FP}{FP + TN}$ — The share of actual negatives incorrectly labeled positive.
* **Precision:** $\frac{TP}{TP + FP}$ — The share of positive predictions that are correct.

---

## 🔄 Fairness & Disparity Ratios

* **Group Disparity Ratio:** $\frac{\text{Group Selection Rate}}{\text{Reference Group Selection Rate}}$
* **Disparate Impact Ratio ($DI$):** $\frac{\min(\text{Selection Rates})}{\max(\text{Selection Rates})}$
* **Flag Rule:** $\text{Flag} = DI < \text{Fairness Threshold}$ (Standard threshold is $0.8$).

---

## 🔬 Statistical Significance

| Test | Use Case |
| :--- | :--- |
| **Fisher’s Exact Test** | Used for small or sparse samples (especially in $2 \times 2$ tables). |
| **Chi-Square Test** | Used for larger samples to test the independence of variables. |
| **P-Value Rule** | If $p < 0.05$, the difference is considered statistically significant. |

---

## 🚨 Risk Scoring & Logic

### Risk Level Mapping
The system maps disparity probabilities ($p$) or impact ratios to the following levels:
* **Low:** $0$
* **Moderate:** $0 < p \le 0.25$
* **High:** $0.25 < p \le 0.60$
* **Critical:** $p > 0.60$

### Overall Audit Score
The final auditor score is calculated as a floor percentage based on the worst-performing metric:
$$
\text{Score} = \lfloor 100 \times \min(DI_{\text{ratios}}) \rfloor
$$

### Flagging Logic
* **High Risk:** $\ge 3$ flagged attributes.
* **Moderate Risk:** $> 0$ flagged attributes.
* **Low Risk:** $0$ flags.

---

## 💡 Why These Tests Matter

The auditor uses both **Fisher’s Exact Test** and **Chi-Square** because the validity of the result depends on sample size. Fisher's avoids over-trusting noisy results from tiny groups, while Chi-Square provides a standard for large-scale data analysis. This ensures the Bias Auditor remains both statistically rigorous and legally relevant.