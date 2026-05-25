# Bias Auditing Formulas Reference
# The Four-Fifths Rule

The **four-fifths rule** (also called the **80% rule**) is a guideline used to spot possible adverse impact in selection decisions such as hiring, promotion, or admissions. A group may raise concern if its selection rate is less than 80% of the selection rate of the highest-scoring group. [web:21][web:24][web:30]

## Formula

The FormulaTo calculate the 4/5ths rule, you compare the selection rates of different groups. The formula is:$$\text{Impact Ratio} = \frac{\text{Selection Rate of the Minority Group}}{\text{Selection Rate of the Majority Group}}$$Step-by-Step BreakdownCalculate the Selection Rate ($SR$) for each group:$$SR = \frac{\text{Number of applicants hired (or promoted)}}{\text{Total number of applicants in that group}}$$Identify the group with the highest selection rate. This is your "Majority" or benchmark group.Divide the selection rate of the group you are testing by the benchmark group's rate.Analyze the result:If the ratio is less than 0.80 (80%), adverse impact is indicated.If the ratio is 0.80 or higher, the process generally passes the 4/5ths rule.

## How to apply it

1. Calculate the selection rate for each group.  
2. Identify the group with the highest selection rate.  
3. Divide each other group’s selection rate by the highest rate.  
4. If any group is below `0.80`, it may indicate adverse impact. 

## Example

If one group is selected 50% of the time and another group is selected 35% of the time:

\[
\frac{35\%}{50\%} = 0.70
\]

Since `0.70 < 0.80`, the result falls below the four-fifths rule and may warrant further review. 

## Why it is used

The rule is used as a quick fairness screen, not a final legal judgment. It helps identify potential bias in a selection process before deeper statistical testing is done. It is especially useful in bias auditing because it gives an easy-to-explain threshold for comparing groups. [web:21][web:30]
## Selection and outcome rates

- **Selection rate:** `selection_rate = mean(outcome)`. This works because the code coerces outcomes to 0/1, so the mean is the share of positive outcomes for a group. It is used to compare how often each group receives the favorable result.
- **Total count:** `total = n`, where `n` is the number of rows in the group. This is used to know sample size, because very small groups can make fairness results unreliable.

## Confusion-matrix formulas

These are used in `compute_rates(...)` when an `actual` column exists.

- **True positives:** `TP = ∑((predicted = 1) ∧ (actual = 1))`. This measures correct positive decisions. It matters in bias auditing because one group may receive positive predictions correctly more or less often than another.
- **False positives:** `FP = ∑((predicted = 1) ∧ (actual = 0))`. This measures incorrect positive decisions, which can create unfair harm if one group is flagged more often.
- **True negatives:** `TN = ∑((predicted = 0) ∧ (actual = 0))`. This measures correct negative decisions and helps complete the error profile.
- **False negatives:** `FN = ∑((predicted = 0) ∧ (actual = 1))`. This measures missed positive cases, which is important because fairness problems can show up as under-allocation or missed opportunities.

## Error-rate formulas

- **True positive rate:** `TPR = TP / (TP + FN)`. This is the share of actual positives correctly found. In fairness work, comparing TPR across groups can reveal equal-opportunity style gaps.
- **False positive rate:** `FPR = FP / (FP + TN)`. This is the share of actual negatives incorrectly labeled positive. In bias audits, a higher FPR for one group can mean more unjustified harm.
- **Precision:** `Precision = TP / (TP + FP)`. This measures how often a positive prediction is correct. It is useful because different groups can have the same selection rate but very different prediction quality.

## Fairness ratio formulas

These are the core fairness checks in `analyze_attribute(...)`.

- **Group disparity ratio:** `disparity_ratio = group_mean / reference_group_mean`. The reference group is the group with the highest selection rate. This shows how a given group compares to the best-off group, which is a common bias-auditing baseline.
- **Disparate impact ratio:** `DI = min(group_mean) / max(group_mean)`. The code uses the worst group divided by the privileged group. This is used because it gives a single worst-case fairness indicator, which is easy to threshold and report.
- **Flag rule:** `flag = (DI < fairness_threshold)`. This turns the ratio into a pass/fail outcome. A threshold like 0.8 is used because it gives a policy boundary for deciding when disparity is large enough to investigate.

## Significance test formulas

These decide whether observed differences are likely real or just random sample noise.

- **Contingency table:** counts of group by outcome in a 2×2 table. This is the input for both Fisher’s exact test and chi-square test. It is used because fairness questions often boil down to whether two groups have different outcome distributions.
- **Fisher’s exact test:** used when sample sizes are small. The code uses it below a size cutoff because it is more reliable than chi-square for small or sparse tables.
- **Chi-square test of independence:** used when sample sizes are larger. It tests whether group membership and outcome appear independent. In bias auditing, a low p-value suggests the disparity is less likely to be random.
- **p-value rule:** `conclusive = (p < 0.05)`. The code uses 0.05 as a conventional significance cutoff. This is used to mark whether a disparity is statistically notable, not just numerically different.

## Risk scoring formulas

These are reporting rules rather than statistical tests.

- **Risk level mapping:** `0 -> Low`, `0 < p <= 0.25 -> Moderate`, `0.25 < p <= 0.60 -> High`, `p > 0.60 -> Critical`. This is used to turn a failure percentage into an operational label that non-technical reviewers can act on.
- **Flagged count:** `flagged_count = ∑(disparity.flag)`. This counts how many protected attributes failed the fairness threshold. It is used because multiple failed attributes usually indicate broader model risk.
- **Overall risk level:** `>= 3` flagged attributes -> `High Risk`; `> 0` flagged attributes -> `Moderate Risk`; otherwise `Low Risk`. This gives a simple audit summary across all protected characteristics.
- **Overall score:** `score = floor(100 × min(disparate_impact_ratios))`. This compresses the worst fairness ratio into a report-friendly number. It is chosen for readability, not because it is a universal fairness standard.

## Why these formulas are used

These formulas are used because bias auditing needs three things: a way to measure outcomes, a way to compare groups, and a way to decide whether the gap is meaningful. Selection rates and disparity ratios show the size of the difference, while significance tests help determine whether the difference is likely real rather than random. Thresholds and risk labels then convert those numbers into decisions for review or escalation.
# Tests


## Four-fifths rule

The four-fifths rule is a quick screening guideline for adverse impact. It says a group’s selection rate should generally be at least 80% of the highest group’s selection rate. It is useful because it gives a simple first-pass check for fairness, but it is not a final legal or statistical conclusion.
## Fisher’s exact test

Fisher’s exact test is used when sample sizes are small, especially in a 2×2 table. It is preferred in small or sparse data because chi-square can behave inconsistently when expected counts are low. In bias auditing, that matters because tiny groups can make a disparity look bigger or smaller just by chance. 
## Chi-square test

The chi-square test of independence is used when the sample size is large enough. It checks whether group membership and outcome appear related, which helps determine whether an observed disparity is likely random or systematic. In bias audits, it gives a statistical test behind the raw disparity ratio.
## Why both are needed

The code uses Fisher’s exact test for smaller samples and chi-square for larger ones because the right test depends on how much data you have. This avoids overtrusting noisy results from tiny groups while still using a standard large-sample test when the data are sufficient. Together, they help separate “possible bias” from “maybe just chance.”