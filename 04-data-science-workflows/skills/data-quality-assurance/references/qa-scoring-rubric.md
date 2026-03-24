# QA Scoring Rubric

This rubric defines how to score each of the 5 quality dimensions and how to combine scores into a final verdict. Apply it during Step 2 (Run Dataset Audit) and Step 5 (Determine Gate Strictness & Issue Verdict) of the data-quality-assurance workflow.

---

## Dimension 1: Completeness (0–100)

Measures whether all expected values are present — null rates, column presence, and row coverage.

| Score Range | Meaning | Threshold Details |
|-------------|---------|-------------------|
| 90–100 | Excellent | <2% nulls in all critical columns, all expected columns present, row count within 5% of expected |
| 70–89 | Acceptable | 2–10% nulls in critical columns OR 1–3 optional columns missing, row count within 20% of expected |
| 50–69 | Degraded | 10–30% nulls in critical columns OR multiple expected columns missing, row count gap >20% |
| <50 | **FAIL** | >30% nulls in any critical column OR any critical column entirely absent OR row count less than half expected |

### Examples by Severity

**Critical (score < 50):**
- `customer_id` is null in 45% of rows — a join key with this null rate means 45% of records are unresolvable.
- Fix: Halt pipeline. Investigate upstream extraction. Do not proceed to modeling.

**Medium (score 50–69):**
- `annual_income` is null in 22% of rows in a credit-risk model.
- Fix: Invoke `missing-data-imputation` skill with strategy MICE or median-fill depending on MCAR test result.

**Low (score 70–89):**
- `middle_name` is null in 8% of rows (non-critical display field).
- Fix: Accept or fill with empty string. Document in cleaning manifest.

### Scoring Formula

```python
def score_completeness(df, critical_cols=None, expected_cols=None, expected_rows=None):
    null_rate_overall = df.isnull().sum().sum() / df.size
    base_score = (1 - null_rate_overall) * 100

    penalties = 0
    if critical_cols:
        for col in critical_cols:
            if col not in df.columns:
                penalties += 40  # missing critical column is near-fatal
            else:
                col_null_rate = df[col].isnull().mean()
                if col_null_rate > 0.30:
                    penalties += 30
                elif col_null_rate > 0.10:
                    penalties += 10
                elif col_null_rate > 0.02:
                    penalties += 3

    if expected_cols:
        missing_expected = len(set(expected_cols) - set(df.columns))
        penalties += missing_expected * 5

    if expected_rows:
        row_gap = abs(len(df) - expected_rows) / expected_rows
        if row_gap > 0.5:
            penalties += 30
        elif row_gap > 0.2:
            penalties += 10

    return max(0, round(base_score - penalties, 1))
```

---

## Dimension 2: Consistency (0–100)

Measures whether records are internally consistent — no contradictions, duplicates, type instability, format variance, or schema drift.

| Score Range | Meaning | Threshold Details |
|-------------|---------|-------------------|
| 90–100 | Excellent | Zero duplicates on natural key, all columns have stable dtypes, no mixed-type columns |
| 70–89 | Acceptable | <1% row-level duplicates (no key duplicates), ≤1 object column with minor format variance |
| 50–69 | Degraded | 1–5% duplicates OR key duplicates present OR 2–4 mixed-type columns OR schema drift in 1–2 columns |
| <50 | **FAIL** | >5% duplicates on a unique key OR >4 mixed-type columns OR schema change broke a join |

### Examples by Severity

**Critical (score < 50):**
- `order_id` has 8% key duplicates after a join — downstream aggregations will double-count revenue.
- Fix: Identify the bad join condition. Deduplicate on `(order_id, created_at)` keeping latest, then re-audit.

**Medium (score 50–69):**
- `zip_code` column contains both "90210" and 90210 (string/int mixed). 35% are strings.
- Fix: Cast to string, zero-pad to 5 digits. Add dtype assertion to pipeline.

**Low (score 70–89):**
- 0.4% of rows are exact duplicates (all columns identical), likely from a double-load.
- Fix: `df.drop_duplicates(keep='first')` in the cleaning step.

### Scoring Formula

```python
def score_consistency(df, key_columns=None):
    score = 100
    issues = []

    dup_rate = df.duplicated().sum() / len(df)
    if dup_rate > 0.05:
        score -= 35
    elif dup_rate > 0.01:
        score -= 15
    elif dup_rate > 0:
        score -= 5

    if key_columns:
        key_dup_rate = df.duplicated(subset=key_columns).sum() / len(df)
        if key_dup_rate > 0.05:
            score -= 40
        elif key_dup_rate > 0:
            score -= 20

    mixed_type_cols = 0
    for col in df.select_dtypes(include=['object']).columns:
        sample = df[col].dropna().head(1000)
        numeric_frac = sample.apply(
            lambda x: str(x).replace('.','').replace('-','').isdigit()
        ).mean()
        if 0.15 < numeric_frac < 0.85:
            mixed_type_cols += 1

    if mixed_type_cols > 4:
        score -= 30
    elif mixed_type_cols > 1:
        score -= mixed_type_cols * 8
    elif mixed_type_cols == 1:
        score -= 5

    return max(0, round(score, 1))
```

---

## Dimension 3: Accuracy (0–100)

Measures whether values make domain sense — within expected ranges, free of sentinel values, and statistically plausible.

| Score Range | Meaning | Threshold Details |
|-------------|---------|-------------------|
| 90–100 | Excellent | No out-of-range values, no sentinel values, no column with outlier rate >0.5% |
| 70–89 | Acceptable | ≤2 columns with minor range violations (<1% of rows), no sentinels in critical columns |
| 50–69 | Degraded | 3–5 columns with range issues OR sentinel values in non-critical columns OR outlier rate 1–5% |
| <50 | **FAIL** | Sentinel values in critical columns OR >5% of rows have physically impossible values |

### Sentinel Value Registry (Always Flag as Critical)

| Sentinel | Common Source | Critical If |
|----------|--------------|-------------|
| -999, -9999 | Legacy SPSS exports | In any numeric feature column |
| 9999, 99999 | Database default fills | In date proxies or ID columns |
| "N/A", "NULL", "NONE", "n/a" | Manual data entry | In any column used as a feature |
| "#REF!", "#VALUE!" | Excel exports | Always critical |
| 0 in a ratio denominator | Computed columns | Depends on context |
| 1900-01-01, 1970-01-01 | Epoch/default date | In any date column |

### Examples by Severity

**Critical (score < 50):**
- `age` column contains values of -999 in 3% of rows and 200 in 0.5% of rows.
- Fix: Replace -999 with NaN, cap age at domain max (e.g., 120), re-run completeness audit.

**Medium (score 50–69):**
- `discount_pct` has 47 rows where the value exceeds 100 (>100% discount is impossible).
- Fix: Cap at 100 or null-fill and investigate source system.

**Low (score 70–89):**
- `salary` has 12 rows >5 standard deviations above mean — likely real outliers, not errors.
- Fix: Document. Handle during feature engineering (log transform or winsorize).

### Scoring Formula

```python
def score_accuracy(df, range_constraints=None, sentinel_values=None):
    score = 100
    default_sentinels = [-999, -9999, 9999, 99999, -1]

    sentinel_check = sentinel_values if sentinel_values else default_sentinels
    sentinel_string_check = ["N/A", "NULL", "NONE", "n/a", "#REF!", "#VALUE!", ""]

    for col in df.select_dtypes(include='number').columns:
        sentinel_hits = df[col].isin(sentinel_check).mean()
        if sentinel_hits > 0.01:
            score -= 25
        elif sentinel_hits > 0:
            score -= 10

        # Outlier rate (>4 IQR fences)
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        outlier_rate = ((df[col] < q1 - 4 * iqr) | (df[col] > q3 + 4 * iqr)).mean()
        if outlier_rate > 0.05:
            score -= 15
        elif outlier_rate > 0.01:
            score -= 5

    for col in df.select_dtypes(include='object').columns:
        string_sentinel_hits = df[col].isin(sentinel_string_check).mean()
        if string_sentinel_hits > 0.01:
            score -= 20

    if range_constraints:
        for col, (low, high) in range_constraints.items():
            if col in df.columns:
                violation_rate = ((df[col] < low) | (df[col] > high)).mean()
                if violation_rate > 0.05:
                    score -= 20
                elif violation_rate > 0.01:
                    score -= 8

    return max(0, round(score, 1))
```

---

## Dimension 4: Timeliness (0–100)

Measures whether the data is current enough and temporally coherent — freshness, date range coverage, and gap classification.

| Score Range | Meaning | Threshold Details |
|-------------|---------|-------------------|
| 90–100 | Excellent | Most recent record within expected freshness window, date range fully covers required period, no unexpected gaps |
| 70–89 | Acceptable | Data slightly stale (1–2 windows behind) OR ≤3 small gaps in timeline |
| 50–69 | Degraded | Data 3–7 windows behind expected freshness OR gaps covering >5% of expected date range |
| <50 | **FAIL** | Data is from wrong time period entirely OR most recent record is >30 days old in a daily pipeline OR gaps cover >20% of range |

### Gap Severity Classification

| Gap Duration | Classification | Action |
|--------------|---------------|--------|
| 1–2 periods | Noise | Document, proceed |
| 3–6 periods | Minor gap | Flag as medium, investigate source |
| 7–29 periods | Major gap | Flag as critical, halt if modeling window overlaps |
| 30+ periods | Missing segment | Hard FAIL — data cannot represent the period |

### Examples by Severity

**Critical (score < 50):**
- A daily sales pipeline has no data from 2024-11-01 to 2024-11-28. A demand forecasting model trained on this data will not learn November seasonality.
- Fix: Halt. Re-extract November data from source. Do not train until gap is filled.

**Medium (score 50–69):**
- `last_login_date` max value is 47 days ago in a pipeline that should refresh weekly.
- Fix: Re-run ingestion job. If source is stale, document as known lag; do not use recency-based features.

**Low (score 70–89):**
- Two individual days are missing from a 2-year daily dataset (0.03% gap rate).
- Fix: Forward-fill or document as acceptable gap.

### Scoring Formula

```python
def score_timeliness(df, date_col=None, expected_max_date=None,
                     expected_min_date=None, freshness_days=None):
    if date_col is None or date_col not in df.columns:
        return 75  # Cannot assess, assume neutral

    score = 100
    dates = pd.to_datetime(df[date_col], errors='coerce').dropna()
    if len(dates) == 0:
        return 0

    actual_max = dates.max()
    actual_min = dates.min()

    if freshness_days and expected_max_date:
        staleness = (pd.Timestamp(expected_max_date) - actual_max).days
        if staleness > 30:
            score -= 40
        elif staleness > 7:
            score -= 20
        elif staleness > 2:
            score -= 8

    if expected_min_date:
        undershoot = (actual_min - pd.Timestamp(expected_min_date)).days
        if undershoot > 30:
            score -= 25
        elif undershoot > 7:
            score -= 10

    # Gap detection for daily-resolution data
    date_range = pd.date_range(actual_min, actual_max, freq='D')
    present_dates = set(dates.dt.normalize())
    gap_count = sum(1 for d in date_range if d not in present_dates)
    gap_rate = gap_count / len(date_range) if len(date_range) > 0 else 0

    if gap_rate > 0.20:
        score -= 35
    elif gap_rate > 0.05:
        score -= 15
    elif gap_rate > 0.01:
        score -= 5

    return max(0, round(score, 1))
```

---

## Dimension 5: Relevance (0–100)

Measures whether the data is fit for the specific modeling task — no zero-variance columns, no unrelated features, correct granularity.

| Score Range | Meaning | Threshold Details |
|-------------|---------|-------------------|
| 90–100 | Excellent | No constant columns, all columns plausibly related to task, granularity correct |
| 70–89 | Acceptable | 1–3 low-variance columns (variance <0.001), 1–2 columns of questionable relevance |
| 50–69 | Degraded | 4–8 zero/near-zero variance columns OR granularity ambiguity (e.g., user vs. session level mixed) |
| <50 | **FAIL** | >8 constant columns OR granularity is fundamentally wrong (e.g., row is a dataset not an observation) |

### Examples by Severity

**Critical (score < 50):**
- Dataset has 12 columns that are all constant (single unique value). This inflates feature count without adding information and can cause model instability.
- Fix: Drop all zero-variance columns before feature engineering.

**Medium (score 50–69):**
- Dataset mixes user-level rows and session-level rows identified by a `row_type` column. Aggregations will be meaningless without stratification.
- Fix: Split into separate DataFrames before any analysis. Re-run audit on each.

**Low (score 70–89):**
- `internal_audit_flag` column has only 3 unique values across 500k rows, near-zero variance.
- Fix: Confirm relevance with domain expert. Drop if confirmed irrelevant.

### Scoring Formula

```python
def score_relevance(df, task_columns=None):
    score = 100

    # Zero-variance columns
    zero_var_cols = [col for col in df.columns
                     if df[col].nunique(dropna=True) <= 1]
    near_zero_var_cols = [col for col in df.select_dtypes(include='number').columns
                          if df[col].std() < 0.001 and col not in zero_var_cols]

    total_low_var = len(zero_var_cols) + len(near_zero_var_cols)
    if total_low_var > 8:
        score -= 40
    elif total_low_var > 3:
        score -= total_low_var * 5
    elif total_low_var > 0:
        score -= total_low_var * 3

    # Granularity check: if row count >> unique values in what should be a key, flag
    # (heuristic: if >3 columns have a single unique value, suspect granularity issue)
    single_value_cols = sum(1 for col in df.columns if df[col].nunique() == 1)
    if single_value_cols > 5:
        score -= 15  # additional granularity concern penalty

    return max(0, round(score, 1))
```

---

## Overall Verdict: `calculate_overall_verdict()`

```python
def calculate_overall_verdict(scores: dict, critical_issues: list,
                               context: str = "production_training") -> dict:
    """
    Compute the final QA gate verdict.

    Parameters
    ----------
    scores : dict
        Keys: completeness, consistency, accuracy, timeliness, relevance
        Values: float 0–100
    critical_issues : list
        List of issue dicts with severity == 'critical', each must have
        'column', 'dimension', 'description', 'recommended_action'
    context : str
        One of: 'production_training', 'exploratory', 'feature_store', 'ad_hoc'

    Returns
    -------
    dict with keys: verdict, reason, accepted_risks, failing_dimensions
    """
    dimensions = ['completeness', 'consistency', 'accuracy', 'timeliness', 'relevance']
    failing = [d for d in dimensions if scores.get(d, 0) < 50]
    degraded = [d for d in dimensions if 50 <= scores.get(d, 0) < 70]
    n_critical = len(critical_issues)

    # Ad-hoc context: always pass with warnings
    if context == "ad_hoc":
        return {
            "verdict": "PASS",
            "reason": "Ad-hoc context: warnings logged but verdict is always PASS.",
            "accepted_risks": [i['description'] for i in critical_issues],
            "failing_dimensions": failing,
        }

    # Exploratory: warn only
    if context == "exploratory":
        return {
            "verdict": "CONDITIONAL_PASS",
            "reason": "Exploratory context: no hard FAIL. Review warnings before production use.",
            "accepted_risks": [i['description'] for i in critical_issues],
            "failing_dimensions": failing,
        }

    # Hard FAIL conditions
    if failing:
        return {
            "verdict": "FAIL",
            "reason": f"Dimension(s) below 50: {failing}. Data is not safe to use.",
            "accepted_risks": [],
            "failing_dimensions": failing,
        }

    # Feature store: fail on schema violations
    if context == "feature_store":
        schema_issues = [i for i in critical_issues
                         if i.get('dimension') in ('completeness', 'consistency')]
        if schema_issues:
            return {
                "verdict": "FAIL",
                "reason": "Feature store context: schema violations are hard FAILs.",
                "accepted_risks": [],
                "failing_dimensions": failing,
            }

    # Production training: fail on any critical issue
    if context == "production_training" and n_critical > 0:
        return {
            "verdict": "FAIL",
            "reason": f"{n_critical} critical issue(s) present. Production training requires zero critical issues.",
            "accepted_risks": [],
            "failing_dimensions": failing,
        }

    # CONDITIONAL_PASS: all dims >= 50, <=2 critical issues, each documented
    if n_critical <= 2 and not failing:
        accepted = []
        for issue in critical_issues:
            accepted.append({
                "column": issue.get("column"),
                "dimension": issue.get("dimension"),
                "description": issue.get("description"),
                "accepted_risk": "Acknowledged and documented — proceed with caution.",
                "recommended_action": issue.get("recommended_action"),
            })
        return {
            "verdict": "CONDITIONAL_PASS",
            "reason": f"All dimensions >= 50. {n_critical} critical issue(s) documented with accepted risk.",
            "accepted_risks": accepted,
            "failing_dimensions": failing,
        }

    # Everything passes
    return {
        "verdict": "PASS",
        "reason": "All dimensions >= 70, zero critical issues.",
        "accepted_risks": [],
        "failing_dimensions": [],
    }
```

### Verdict Decision Table

| Condition | Verdict |
|-----------|---------|
| Any dimension < 50 | FAIL |
| >2 critical issues (non-exploratory, non-ad-hoc) | FAIL |
| Production training + any critical issue | FAIL |
| Feature store + schema critical issue | FAIL |
| All dims >= 50, <=2 critical issues documented | CONDITIONAL_PASS |
| All dims >= 70, 0 critical issues | PASS |
| Exploratory context | CONDITIONAL_PASS (at worst) |
| Ad-hoc context | PASS (always) |

### CONDITIONAL_PASS Requirements

A CONDITIONAL_PASS is only valid when ALL of the following are true:
1. Every accepted risk is explicitly listed in `accepted_risks` with a description.
2. Every accepted risk has a `recommended_action` even if deferred.
3. The final report is saved so future runs can compare against it.
4. A human reviewer has signed off (document in `qa_report.json` under `reviewer`).

---

## Distribution Drift: `check_distribution_drift()`

Called in Step 4 of the data-quality-assurance workflow. Requires a prior `qa_report.json` as baseline; on first run it returns `{}` and the current report establishes the baseline.

```python
from scipy import stats
import numpy as np

def check_distribution_drift(df, prior_report, significance_level=0.05):
    if not prior_report:
        print("No prior report — establishing baseline. Drift checks skipped this run.")
        return {}

    drift_metrics = {}
    prior_stats = prior_report.get("column_stats", {})
    simultaneous_drift_cols = []

    for col in df.columns:
        if col not in prior_stats:
            continue

        col_stats = prior_stats[col]

        if df[col].dtype in ['float64', 'float32', 'int64', 'int32']:
            # KS-test: compare current values to prior distribution samples
            prior_samples = col_stats.get("sample_values")
            if prior_samples and len(prior_samples) >= 30:
                stat, p_value = stats.ks_2samp(
                    df[col].dropna().values,
                    np.array(prior_samples)
                )
                drifted = p_value < significance_level
                drift_metrics[col] = {
                    "test": "ks_2samp",
                    "statistic": round(float(stat), 4),
                    "p_value": round(float(p_value), 4),
                    "drifted": drifted,
                }
                if drifted:
                    simultaneous_drift_cols.append(col)

        elif df[col].dtype == 'object':
            # Chi-squared: compare category frequency distributions
            prior_freq = col_stats.get("value_counts", {})
            if prior_freq:
                current_freq = df[col].value_counts(normalize=True).to_dict()
                all_cats = set(prior_freq) | set(current_freq)
                prior_vec = np.array([prior_freq.get(c, 0) for c in all_cats])
                current_vec = np.array([current_freq.get(c, 0) for c in all_cats])

                if prior_vec.sum() > 0 and current_vec.sum() > 0:
                    prior_vec = prior_vec / prior_vec.sum()
                    current_vec = current_vec / current_vec.sum()
                    n = len(df[col].dropna())
                    stat, p_value = stats.chisquare(
                        current_vec * n,
                        f_exp=prior_vec * n
                    )
                    drifted = p_value < significance_level
                    drift_metrics[col] = {
                        "test": "chisquare",
                        "statistic": round(float(stat), 4),
                        "p_value": round(float(p_value), 4),
                        "drifted": drifted,
                    }
                    if drifted:
                        simultaneous_drift_cols.append(col)

    # Volume change check
    prior_row_count = prior_report.get("row_count", 0)
    if prior_row_count > 0:
        volume_change_pct = (len(df) - prior_row_count) / prior_row_count
        drift_metrics["__volume__"] = {
            "test": "volume_pct_change",
            "statistic": round(volume_change_pct, 4),
            "p_value": None,
            "drifted": abs(volume_change_pct) > 0.20,
        }
        if abs(volume_change_pct) > 0.20:
            simultaneous_drift_cols.append("__volume__")

    # Multi-column simultaneous drift is a critical signal
    if len(simultaneous_drift_cols) >= 3:
        print(
            f"WARNING: {len(simultaneous_drift_cols)} columns drifted simultaneously: "
            f"{simultaneous_drift_cols}. This suggests an upstream schema or ETL change."
        )
        drift_metrics["__multi_column_drift__"] = {
            "columns": simultaneous_drift_cols,
            "severity": "critical",
            "description": "Simultaneous drift across multiple columns — likely upstream change.",
            "recommended_action": "Halt pipeline. Investigate ETL job and upstream source.",
        }

    return drift_metrics
```
