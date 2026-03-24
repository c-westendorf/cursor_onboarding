---
name: data-quality-assurance
description: Evaluate a dataset against business rules, statistical expectations, and data contracts to produce a PASS/CONDITIONAL_PASS/FAIL quality gate. Use when checking data before modeling, after pipeline ingestion, when upstream data changes, when model performance degrades unexpectedly, on a schedule for production pipelines, or whenever you need to validate data quality. Integrates with Great Expectations and YAML data contracts.
---

# Data Quality Assurance Skill

## Why QA Matters

Bad data corrupts models silently. A model trained on data with 30% sentinel values in a key feature will learn the wrong signal, pass all unit tests, and only fail in production — often weeks after deployment when metrics drift.

Quality gating forces the question: "Is this data safe to use?" before any irreversible step (model training, feature store writes, report publication). A failed gate is not a pipeline failure — it is the pipeline working correctly.

**The three failure modes QA prevents:**

1. **Garbage-in corruption** — sentinel values, impossible ranges, and type inconsistencies produce nonsense features. The model learns noise.
2. **Silent distribution shift** — data from the wrong time period or a changed upstream schema looks valid row-by-row but is statistically incompatible with the training distribution.
3. **Incomplete coverage** — missing rows or columns mean the model never learned certain segments, producing silent underperformance for those users.

---

## When to Activate

Invoke this skill in any of these situations:

- Before model training — gate the training dataset
- After pipeline ingestion — validate freshly loaded data before it reaches feature stores
- When upstream data sources change — a schema migration or vendor switch
- When model performance degrades unexpectedly — suspect data drift before retraining
- On a production schedule — weekly or daily health checks on live data pipelines
- When a data contract is created or updated — verify the dataset satisfies it

---

## Prerequisites

| Prerequisite | Required | Notes |
|---|---|---|
| Cleaned DataFrame | Yes | Run the `data-cleaning` skill first. QA does not clean; it evaluates. |
| `cleaning_manifest.json` | Recommended | Produced by data-cleaning skill. Contains dtype map, imputation log, and row counts. |
| Data contract YAML | Optional | Defines expected schema, ranges, and freshness SLAs. Enables contract-based validation. |
| Prior QA report (`qa_report.json`) | Optional | Enables distribution drift detection via KS-test and chi-squared. |
| Column criticality list | Optional | Marks which columns are load-bearing (used as model features or join keys). |

---

## Workflow

#### Scale Classification

At the start of processing, classify the dataset scale:

```python
scale = classify_scale(df)  # Returns: "small", "medium", "large", or "very_large"
print(f"Dataset scale: {scale} ({len(df):,} rows × {len(df.columns)} cols, "
      f"{df.memory_usage(deep=True).sum() / 1e6:.0f} MB)")
```

> **Plain language:** We check how big your data is to choose the right processing strategy. Small datasets use standard methods; large datasets automatically switch to faster approaches that sample or use parallel processing.

See `_shared-references/shape-aware-strategy.md` → Scale-Aware Strategy Table for skill-specific branching.

### Step 1: Load Context

Read all available context before scoring anything. The context determines which validation path is taken.

```python
import json
import yaml
from pathlib import Path

def load_qa_context(manifest_path=None, contract_path=None, prior_report_path=None):
    context = {
        "cleaning_manifest": None,
        "data_contract": None,
        "prior_report": None,
    }

    if manifest_path and Path(manifest_path).exists():
        with open(manifest_path) as f:
            context["cleaning_manifest"] = json.load(f)
        print(f"Loaded cleaning manifest: {len(context['cleaning_manifest'])} keys")

    if contract_path and Path(contract_path).exists():
        with open(contract_path) as f:
            context["data_contract"] = yaml.safe_load(f)
        print(f"Loaded data contract: {contract_path}")

    if prior_report_path and Path(prior_report_path).exists():
        with open(prior_report_path) as f:
            context["prior_report"] = json.load(f)
        print(f"Loaded prior QA report from: {context['prior_report'].get('timestamp', 'unknown')}")
    else:
        print("No prior QA report found — drift checks will be skipped; this run establishes the baseline.")

    return context
```

**What to check in the cleaning manifest:**
- `rows_before` vs `rows_after` — large drop may indicate an upstream issue, not just cleaning
- `imputed_columns` — these columns have synthetic values; flag them in accuracy scoring
- `dtype_changes` — confirms that type issues were already handled

---

### Step 2: Run Dataset Audit

Score all 5 quality dimensions. See `references/dataset-audit-pattern.md` for the audit functions and `references/qa-scoring-rubric.md` for the scoring thresholds.

```python
from references.dataset_audit_pattern import (
    audit_completeness,
    audit_consistency,
)

def run_full_audit(df, critical_cols=None, key_columns=None,
                   expected_cols=None, expected_rows=None,
                   date_col=None, range_constraints=None):

    print("--- Scoring: Completeness ---")
    completeness = audit_completeness(df, expected_columns=expected_cols)

    print("--- Scoring: Consistency ---")
    consistency = audit_consistency(df, key_columns=key_columns)

    print("--- Scoring: Accuracy ---")
    accuracy_score, accuracy_issues = score_accuracy_with_issues(
        df, range_constraints=range_constraints
    )

    print("--- Scoring: Timeliness ---")
    timeliness_score, timeliness_issues = score_timeliness_with_issues(
        df, date_col=date_col
    )

    print("--- Scoring: Relevance ---")
    relevance_score, relevance_issues = score_relevance_with_issues(df)

    scores = {
        "completeness": completeness["score"],
        "consistency": consistency["score"],
        "accuracy": accuracy_score,
        "timeliness": timeliness_score,
        "relevance": relevance_score,
    }

    all_issues = (
        completeness.get("issues", [])
        + consistency.get("issues", [])
        + accuracy_issues
        + timeliness_issues
        + relevance_issues
    )

    print("\n--- Dimension Scores ---")
    for dim, score in scores.items():
        status = "PASS" if score >= 70 else "DEGRADED" if score >= 50 else "FAIL"
        print(f"  {dim:<15} {score:>6.1f}  [{status}]")

    return scores, all_issues
```

> **At scale (large/very_large):** Run statistical profiling (`.quantile()`, `.value_counts()`) on a 500K stratified sample via `get_analysis_sample()`. Full-data checks limited to schema validation, null rates, and duplicate counts (all O(n) or faster). Report effect sizes alongside p-values — KS-test over-rejects on large samples.

**Assumption audit — run this before proceeding.** See `references/assumption-audit-pattern.md`:
- Am I assuming nulls are random? Run `df.isnull().corrwith(df[target])` if a target exists.
- Am I assuming no schema drift since the last run? Check against the cleaning manifest dtypes.
- Am I assuming the time range is correct? Verify `max(date_col)` matches expectations.

> **CHECKPOINT — Step 2**
> - [ ] Assert: All 5 dimensions (completeness, consistency, accuracy, timeliness, relevance) have numeric scores
> - [ ] Assert: Every issue has severity, dimension, and recommended_action fields
> - [ ] PASS: Audit is complete with all dimensions scored
> - [ ] On FAIL: HALT — "Incomplete audit. Review dimension scoring logic."

---

### Step 3: Select Quality Framework

**Decision point — choose the validation strategy based on what context is available:**

```
Contract YAML exists?
    YES → Validate against contract (schema, ranges, freshness SLAs)
    NO  → Data dictionary / expected columns available?
              YES → Generate Great Expectations suite from dictionary
              NO  → Statistical profiling with percentile bounds
```

```python
def select_and_run_framework(df, context):
    if context["data_contract"]:
        print("Framework: CONTRACT VALIDATION")
        return validate_against_contract(df, context["data_contract"])

    elif context["cleaning_manifest"] and "expected_columns" in context["cleaning_manifest"]:
        print("Framework: EXPECTATION GENERATION from data dictionary")
        return generate_expectations_from_dict(df, context["cleaning_manifest"])

    else:
        print("Framework: STATISTICAL PROFILING (no contract or dictionary available)")
        return statistical_profile_validation(df)


def validate_against_contract(df, contract):
    """Validate DataFrame against a YAML data contract."""
    violations = []
    schema = contract.get("schema", {})

    for col, spec in schema.items():
        if col not in df.columns:
            violations.append({
                "column": col, "dimension": "completeness",
                "severity": "critical",
                "description": f"Contract requires column '{col}' but it is absent.",
                "recommended_action": "Re-run data-cleaning skill or fix upstream extraction.",
            })
            continue

        expected_dtype = spec.get("dtype")
        if expected_dtype and str(df[col].dtype) != expected_dtype:
            violations.append({
                "column": col, "dimension": "consistency",
                "severity": "medium",
                "description": f"Expected dtype {expected_dtype}, got {df[col].dtype}.",
                "recommended_action": f"Cast {col} to {expected_dtype} in cleaning step.",
            })

        if "min" in spec and "max" in spec:
            out_of_range = ((df[col] < spec["min"]) | (df[col] > spec["max"])).mean()
            if out_of_range > 0:
                severity = "critical" if out_of_range > 0.05 else "medium"
                violations.append({
                    "column": col, "dimension": "accuracy",
                    "severity": severity,
                    "description": f"{out_of_range:.1%} of values outside contract range [{spec['min']}, {spec['max']}].",
                    "recommended_action": "Clip or null-fill out-of-range values.",
                })

    return violations


def statistical_profile_validation(df):
    """Generate bounds from data itself using percentile fences."""
    issues = []
    for col in df.select_dtypes(include='number').columns:
        p01 = df[col].quantile(0.01)
        p99 = df[col].quantile(0.99)
        extreme_rate = ((df[col] < p01) | (df[col] > p99)).mean()
        if extreme_rate > 0.02:
            issues.append({
                "column": col, "dimension": "accuracy",
                "severity": "low",
                "description": f"{extreme_rate:.1%} of values outside [p1, p99] bounds.",
                "recommended_action": "Investigate distribution tails; winsorize if modeling.",
            })
    return issues
```

**Great Expectations integration (when a data dictionary is available):**

```python
import great_expectations as ge

def generate_expectations_from_dict(df, manifest):
    gdf = ge.from_pandas(df)
    suite_violations = []

    for col in manifest.get("expected_columns", []):
        gdf.expect_column_to_exist(col)

    for col, null_threshold in manifest.get("max_null_rates", {}).items():
        result = gdf.expect_column_values_to_not_be_null(col, mostly=1 - null_threshold)
        if not result["success"]:
            suite_violations.append({
                "column": col, "dimension": "completeness",
                "severity": "medium",
                "description": f"Null rate exceeds contract threshold of {null_threshold:.0%}.",
                "recommended_action": "Invoke missing-data-imputation skill.",
            })

    return suite_violations
```

---

### Step 4: Check Distribution Drift

**Decision point — drift checks require a prior QA report as baseline:**

```
Prior QA report exists?
    YES → Run KS-test (numeric) + chi-squared (categorical) + volume % change
          Multi-column simultaneous drift → critical flag (suspect upstream change)
    NO  → Establish baseline from this run, skip drift checks
```

`check_distribution_drift(df, prior_report)` runs KS-test on numeric columns, chi-squared on categoricals, and a volume % change check. When 3+ columns drift simultaneously it adds a `__multi_column_drift__` critical flag signaling an upstream ETL or schema change.

> **Plain language:** We compare today's data against previous data to check if anything has changed significantly. Think of it like comparing two histograms — if they look very different, something may have changed in how the data is collected or what it represents.

See `references/qa-scoring-rubric.md` for the full `check_distribution_drift()` implementation.

---

### Step 5: Determine Gate Strictness & Issue Verdict

**Decision point — the verdict threshold depends on the execution context:**

| Context | FAIL Trigger | CONDITIONAL_PASS Allowed |
|---|---|---|
| `production_training` | Any critical issue OR any dimension < 50 | Yes, if <=2 criticals documented |
| `feature_store` | Schema violations (completeness/consistency critical) | Yes, for stat issues only |
| `exploratory` | Never hard FAIL | Always warn only |
| `ad_hoc` | Never | Always PASS with warnings |

```python
from references.qa_scoring_rubric import calculate_overall_verdict

def issue_verdict(scores, all_issues, drift_metrics, context="production_training"):
    critical_issues = [i for i in all_issues if i.get("severity") == "critical"]

    # Promote multi-column drift to a critical issue
    if "__multi_column_drift__" in drift_metrics:
        drift_info = drift_metrics["__multi_column_drift__"]
        critical_issues.append({
            "column": "__multi_column__",
            "dimension": "timeliness",
            "severity": "critical",
            "description": drift_info["description"],
            "recommended_action": drift_info["recommended_action"],
        })

    result = calculate_overall_verdict(scores, critical_issues, context=context)

    print(f"\n=== VERDICT: {result['verdict']} ===")
    print(f"Reason: {result['reason']}")

    if result["failing_dimensions"]:
        print(f"Failing dimensions: {result['failing_dimensions']}")

    if result["accepted_risks"]:
        print(f"Accepted risks ({len(result['accepted_risks'])}):")
        for risk in result["accepted_risks"]:
            if isinstance(risk, dict):
                print(f"  - [{risk.get('dimension')}] {risk.get('description')}")
            else:
                print(f"  - {risk}")

    return result
```

**Scoring reference:** See `references/qa-scoring-rubric.md` for per-dimension thresholds, examples at each severity level, and the full `calculate_overall_verdict()` logic.

> **CHECKPOINT — Step 5**
> - [ ] Assert: Verdict is exactly one of: `PASS`, `CONDITIONAL_PASS`, `FAIL`
> - [ ] Assert: If `CONDITIONAL_PASS`, then `accepted_risks` list is non-empty AND `conditional_pass_allows` field is set
> - [ ] PASS: Verdict determined with clear downstream permissions
> - [ ] On FAIL: Default to `FAIL` if verdict cannot be determined.
>
> **CONDITIONAL_PASS rules:**
> - Allowed downstream: `[missing-data-imputation, eda-comprehensive]`
> - Blocked downstream: `[feature-engineering]` (must re-QA after fixing issues)
> - All critical issues must have `recommended_action` populated

#### Verdict Contract

The verdict controls which downstream skills may proceed:

| Verdict | Allowed Next Skills | Rationale |
|---|---|---|
| `PASS` | imputation, EDA, feature-engineering | All quality dimensions acceptable |
| `CONDITIONAL_PASS` | imputation, EDA | Critical issues documented but manageable; feature-engineering blocked until re-QA after fixes |
| `FAIL` | data-cleaning only | Must fix issues and re-run QA before any downstream processing |

The `qa_report.json` includes an `allowed_downstream_skills` field that downstream skills should check.

---

### Step 6: Generate Report & Recommend Next Steps

**Decision point on FAIL — the recommended action depends on which dimension failed:**

| Failure Type | Root Cause | Next Step |
|---|---|---|
| Schema violation (missing/wrong columns) | Upstream schema change or incomplete extraction | Re-run `data-cleaning` skill with updated column map |
| Completeness FAIL (high null rates) | Incomplete data, bad join, or extraction cutoff | Invoke `missing-data-imputation` skill |
| Distribution drift (stat shift) | Upstream data changed | Re-run `eda-comprehensive` skill on fresh data |
| Volume anomaly (>20% row count change) | ETL failure or source truncation | Halt pipeline. Alert upstream data engineering team. |
| Accuracy FAIL (sentinels, range violations) | Source system issue or encoding error | Re-run `data-cleaning` skill with extended sentinel list |

```python
import json
from datetime import datetime, timezone

def generate_report(df, scores, all_issues, drift_metrics, verdict_result,
                    output_path="qa_report.json"):

    # Build per-column dimension scores (simplified — full version in generate_qa_report.py)
    per_column_scores = {}
    for col in df.columns:
        null_rate = df[col].isnull().mean()
        per_column_scores[col] = {
            "completeness": round(max(0, 100 - null_rate * 200), 1),
            "consistency": 100 if df[col].nunique() > 1 else 50,
            "accuracy": 100,  # placeholder — detailed scoring in generate_qa_report.py
            "timeliness": None,
            "relevance": 50 if df[col].nunique() <= 1 else 100,
        }

    # Build column_stats for future drift baseline
    column_stats = {}
    for col in df.columns:
        if df[col].dtype in ['float64', 'float32', 'int64', 'int32']:
            sample = df[col].dropna().sample(min(500, len(df[col].dropna())),
                                             random_state=42).tolist()
            column_stats[col] = {"sample_values": sample}
        elif df[col].dtype == 'object':
            column_stats[col] = {
                "value_counts": df[col].value_counts(normalize=True).head(50).to_dict()
            }

    report = {
        "verdict": verdict_result["verdict"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "row_count": len(df),
        "column_count": len(df.columns),
        "overall_scores": scores,
        "per_column_scores": per_column_scores,
        "issues": all_issues,
        "drift_metrics": drift_metrics,
        "accepted_risks": verdict_result.get("accepted_risks", []),
        "failing_dimensions": verdict_result.get("failing_dimensions", []),
        "column_stats": column_stats,
        "reviewer": None,
    }

    with open(output_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\nQA report saved to: {output_path}")
    _print_recommended_actions(verdict_result, all_issues, drift_metrics)

    return report


def _print_recommended_actions(verdict_result, all_issues, drift_metrics):
    if verdict_result["verdict"] == "PASS":
        print("Next step: Proceed to feature engineering or model training.")
        return

    print("\n--- Recommended Next Steps ---")

    failing = verdict_result.get("failing_dimensions", [])

    if "completeness" in failing:
        print("  COMPLETENESS FAIL → Invoke missing-data-imputation skill.")
        print("    Command: /missing-data-imputation on the current DataFrame")

    if "consistency" in failing:
        schema_issues = [i for i in all_issues
                         if i.get("dimension") == "consistency" and i.get("severity") == "critical"]
        if schema_issues:
            print("  CONSISTENCY/SCHEMA FAIL → Re-run data-cleaning skill.")
            print("    Command: /data-cleaning with updated dtype map and dedup rules")

    if "accuracy" in failing:
        print("  ACCURACY FAIL → Re-run data-cleaning skill with extended sentinel list.")
        print("    Command: /data-cleaning — add sentinel values to cleaning config")

    if "timeliness" in failing:
        print("  TIMELINESS FAIL → Re-run ingestion pipeline. Check upstream source.")
        print("    If gap confirmed: halt and alert data engineering.")

    if "__multi_column_drift__" in drift_metrics:
        print("  DISTRIBUTION DRIFT (multi-column) → Re-run eda-comprehensive skill.")
        print("    Command: /eda-comprehensive to characterize the new distribution")
        print("    Then re-train model or update data contract.")

    volume_drift = drift_metrics.get("__volume__", {})
    if volume_drift.get("drifted"):
        change = volume_drift.get("statistic", 0)
        print(f"  VOLUME ANOMALY ({change:+.0%} change) → Halt and alert upstream.")
        print("    Do not proceed until row count anomaly is explained.")
```

---

## Edge Case Handling

| Edge Case | Detection | Action |
|---|---|---|
| **Empty DataFrame (0 rows)** | `len(df) == 0` | HALT — "Cannot perform quality assessment on empty dataset." |
| **Single-row DataFrame** | `len(df) == 1` | WARN — completeness scores are trivially perfect. Consistency checks are meaningless. Score all dimensions but flag: "Single-row dataset — scores are unreliable." |
| **All columns constant (zero variance)** | `df.nunique().max() <= 1` | Relevance dimension scores 0. Verdict: FAIL with note "No variance in dataset." |
| **100% null column** | `df[col].isnull().all()` | Completeness score = 0 for that column. Flag as critical issue. |
| **Mixed-type object columns** | Object column with mixed numeric/string values | Flag as consistency violation (critical). Recommend return to data-cleaning. |
| **No prior QA report (first run)** | `prior_report.json` not found | Skip drift detection. Establish current run as baseline. |
| **All columns pass perfectly** | Every dimension ≥ 90 | Verdict: PASS. But WARN if this seems suspicious — "Perfect scores may indicate insufficient test coverage." |
| **Very high cardinality (>100K uniques)** | `df[col].nunique() > 100_000` | Flag as relevance concern — "High-cardinality column may be an ID or free-text field." Score relevance accordingly. |

---

## Quality Bar

Every QA run must meet this standard before a report is considered complete:

- Every column has been scored on all applicable dimensions.
- Every issue has: a `severity` (critical / medium / low), a `dimension`, and a `recommended_action`.
- The verdict is exactly one of: `PASS`, `CONDITIONAL_PASS`, or `FAIL`. No other values.
- A `CONDITIONAL_PASS` is only valid when `accepted_risks` is populated with documented acknowledgments.
- The `qa_report.json` is saved so the next run can use it as a drift baseline.

---

## Scope Boundary

This skill is **read-only**. It:

- Does NOT modify the DataFrame.
- Does NOT impute missing values (that is the `missing-data-imputation` skill).
- Does NOT perform exploratory data analysis (that is the `eda-comprehensive` skill).
- Does NOT clean or transform data (that is the `data-cleaning` skill).

If this skill finds problems, it tells you what skill to invoke next. It does not fix the problems itself.
