"""
generate_qa_report.py
---------------------
Standalone script (and importable module) that evaluates a DataFrame against
business rules, statistical expectations, and an optional data contract, then
writes a qa_report.json with a PASS / CONDITIONAL_PASS / FAIL verdict.

CLI usage
---------
    python generate_qa_report.py \
        --input data/clean_dataset.parquet \
        --contract contracts/sales_contract.yaml \
        --prior-report reports/qa_report_prev.json \
        --context production_training \
        --output reports/qa_report.json

Programmatic usage
------------------
    from scripts.generate_qa_report import generate_qa_report
    report = generate_qa_report(
        df=my_dataframe,
        contract_path="contracts/sales_contract.yaml",
        prior_report_path="reports/qa_report_prev.json",
        context="production_training",
        output_path="reports/qa_report.json",
    )
    print(report["verdict"])  # "PASS" | "CONDITIONAL_PASS" | "FAIL"
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats


# ---------------------------------------------------------------------------
# Dimension scorers
# ---------------------------------------------------------------------------

def _score_completeness(
    df: pd.DataFrame,
    critical_cols: list[str] | None = None,
    expected_cols: list[str] | None = None,
    expected_rows: int | None = None,
) -> tuple[float, list[dict]]:
    """Return (score 0-100, issues list)."""
    issues: list[dict] = []
    score = 100.0

    # Missing critical columns
    if critical_cols:
        for col in critical_cols:
            if col not in df.columns:
                issues.append({
                    "column": col,
                    "dimension": "completeness",
                    "severity": "critical",
                    "description": f"Critical column '{col}' is entirely absent.",
                    "recommended_action": "Re-run data-cleaning skill or fix upstream extraction.",
                })
                score -= 40

    # Missing expected columns
    if expected_cols:
        missing_expected = [c for c in expected_cols if c not in df.columns]
        for col in missing_expected:
            issues.append({
                "column": col,
                "dimension": "completeness",
                "severity": "medium",
                "description": f"Expected column '{col}' is missing.",
                "recommended_action": "Verify upstream schema or add column to cleaning output.",
            })
            score -= 5

    # Per-column null rates
    for col in df.columns:
        null_rate = df[col].isnull().mean()
        if null_rate == 0:
            continue
        is_critical = critical_cols and col in critical_cols
        if null_rate > 0.30:
            severity = "critical"
            score -= 30 if is_critical else 15
            action = "Halt — critical column is >30% null. Investigate source." if is_critical else \
                     "Invoke missing-data-imputation skill or drop column if non-essential."
        elif null_rate > 0.10:
            severity = "medium"
            score -= 10 if is_critical else 5
            action = "Invoke missing-data-imputation skill (MICE or median strategy)."
        else:
            severity = "low"
            score -= 3 if is_critical else 1
            action = "Accept or fill with domain-appropriate default."

        issues.append({
            "column": col,
            "dimension": "completeness",
            "severity": severity,
            "description": f"Null rate: {null_rate:.1%}.",
            "null_rate": round(float(null_rate), 4),
            "recommended_action": action,
        })

    # Row count check
    if expected_rows and expected_rows > 0:
        row_gap = abs(len(df) - expected_rows) / expected_rows
        if row_gap > 0.50:
            severity = "critical"
            score -= 30
        elif row_gap > 0.20:
            severity = "medium"
            score -= 10
        else:
            severity = "low"
            score -= 2

        if row_gap > 0.02:
            issues.append({
                "column": "__row_count__",
                "dimension": "completeness",
                "severity": severity,
                "description": (
                    f"Row count {len(df):,} differs from expected {expected_rows:,} "
                    f"by {row_gap:.1%}."
                ),
                "recommended_action": "Check upstream extraction and join conditions.",
            })

    return max(0.0, round(score, 1)), issues


def _score_consistency(
    df: pd.DataFrame,
    key_columns: list[str] | None = None,
) -> tuple[float, list[dict]]:
    """Return (score 0-100, issues list)."""
    issues: list[dict] = []
    score = 100.0

    # Row-level duplicates
    dup_count = int(df.duplicated().sum())
    if dup_count > 0:
        dup_rate = dup_count / len(df) if len(df) > 0 else 0.0
        severity = "critical" if dup_rate >= 0.05 else "medium" if dup_rate >= 0.01 else "low"
        score -= 35 if dup_rate >= 0.05 else 15 if dup_rate >= 0.01 else 5
        issues.append({
            "column": "__all__",
            "dimension": "consistency",
            "severity": severity,
            "description": f"{dup_count:,} duplicate rows ({dup_rate:.1%} of dataset).",
            "recommended_action": "df.drop_duplicates(keep='first') in data-cleaning skill.",
        })

    # Key-level duplicates
    if key_columns:
        valid_keys = [c for c in key_columns if c in df.columns]
        if valid_keys:
            key_dup_count = int(df.duplicated(subset=valid_keys).sum())
            if key_dup_count > 0:
                key_dup_rate = key_dup_count / len(df) if len(df) > 0 else 0.0
                score -= 40
                issues.append({
                    "column": str(valid_keys),
                    "dimension": "consistency",
                    "severity": "critical",
                    "description": (
                        f"{key_dup_count:,} key duplicates on {valid_keys} "
                        f"({key_dup_rate:.1%} of rows)."
                    ),
                    "recommended_action": (
                        "Investigate join cardinality. Deduplicate on key, keep latest by timestamp."
                    ),
                })

    # Mixed-type columns
    mixed_type_count = 0
    for col in df.select_dtypes(include=["object"]).columns:
        sample = df[col].dropna().head(1000)
        if len(sample) == 0:
            continue
        numeric_frac = sample.apply(
            lambda x: str(x).replace(".", "").replace("-", "").isdigit()
        ).mean()
        if 0.15 < numeric_frac < 0.85:
            mixed_type_count += 1
            score -= 8
            issues.append({
                "column": col,
                "dimension": "consistency",
                "severity": "medium",
                "description": (
                    f"Mixed types: {numeric_frac:.0%} of sampled values appear numeric "
                    "but column is object dtype."
                ),
                "recommended_action": "Cast to correct dtype in data-cleaning skill.",
            })

    return max(0.0, round(score, 1)), issues


def _score_accuracy(
    df: pd.DataFrame,
    range_constraints: dict[str, tuple[float, float]] | None = None,
    sentinel_values: list[Any] | None = None,
) -> tuple[float, list[dict]]:
    """Return (score 0-100, issues list)."""
    issues: list[dict] = []
    score = 100.0

    DEFAULT_NUMERIC_SENTINELS = {-999, -9999, 9999, 99999, -1}
    DEFAULT_STRING_SENTINELS = {"N/A", "NULL", "NONE", "n/a", "#REF!", "#VALUE!", ""}
    numeric_sentinels = set(sentinel_values) if sentinel_values else DEFAULT_NUMERIC_SENTINELS

    for col in df.select_dtypes(include="number").columns:
        series = df[col].dropna()
        if len(series) == 0:
            continue

        # Sentinel check
        sentinel_hits = series.isin(numeric_sentinels).mean()
        if sentinel_hits > 0.01:
            score -= 25
            issues.append({
                "column": col,
                "dimension": "accuracy",
                "severity": "critical",
                "description": (
                    f"Sentinel values detected in {sentinel_hits:.1%} of non-null rows "
                    f"(checked: {sorted(numeric_sentinels)})."
                ),
                "recommended_action": (
                    "Replace sentinels with NaN in data-cleaning skill. "
                    "Re-run completeness audit."
                ),
            })
        elif sentinel_hits > 0:
            score -= 10
            issues.append({
                "column": col,
                "dimension": "accuracy",
                "severity": "medium",
                "description": f"Rare sentinel values detected ({sentinel_hits:.2%} of rows).",
                "recommended_action": "Replace sentinels with NaN in data-cleaning skill.",
            })

        # IQR outlier fence (4x IQR)
        q1 = float(series.quantile(0.25))
        q3 = float(series.quantile(0.75))
        iqr = q3 - q1
        if iqr > 0:
            outlier_rate = float(
                ((series < q1 - 4 * iqr) | (series > q3 + 4 * iqr)).mean()
            )
            if outlier_rate > 0.05:
                score -= 15
                issues.append({
                    "column": col,
                    "dimension": "accuracy",
                    "severity": "medium",
                    "description": f"Extreme outlier rate {outlier_rate:.1%} (beyond 4×IQR fence).",
                    "recommended_action": "Investigate; winsorize or log-transform during feature engineering.",
                })
            elif outlier_rate > 0.01:
                score -= 5
                issues.append({
                    "column": col,
                    "dimension": "accuracy",
                    "severity": "low",
                    "description": f"Minor outlier rate {outlier_rate:.1%} (beyond 4×IQR fence).",
                    "recommended_action": "Document; handle during feature engineering.",
                })

    # String sentinel check
    for col in df.select_dtypes(include="object").columns:
        string_sentinel_rate = df[col].isin(DEFAULT_STRING_SENTINELS).mean()
        if string_sentinel_rate > 0.01:
            score -= 20
            issues.append({
                "column": col,
                "dimension": "accuracy",
                "severity": "critical",
                "description": (
                    f"String sentinel values found in {string_sentinel_rate:.1%} of rows "
                    f"(e.g., 'N/A', 'NULL', '#REF!')."
                ),
                "recommended_action": "Replace with NaN in data-cleaning skill.",
            })

    # Range constraint violations
    if range_constraints:
        for col, (low, high) in range_constraints.items():
            if col not in df.columns:
                continue
            violation_rate = float(((df[col] < low) | (df[col] > high)).mean())
            if violation_rate > 0.05:
                score -= 20
                severity = "critical"
            elif violation_rate > 0.01:
                score -= 8
                severity = "medium"
            elif violation_rate > 0:
                score -= 3
                severity = "low"
            else:
                continue

            issues.append({
                "column": col,
                "dimension": "accuracy",
                "severity": severity,
                "description": (
                    f"{violation_rate:.1%} of values outside expected range "
                    f"[{low}, {high}]."
                ),
                "recommended_action": f"Clip to [{low}, {high}] or null-fill and re-audit.",
            })

    return max(0.0, round(score, 1)), issues


def _score_timeliness(
    df: pd.DataFrame,
    date_col: str | None = None,
    expected_max_date: str | None = None,
    expected_min_date: str | None = None,
    freshness_days: int | None = None,
) -> tuple[float, list[dict]]:
    """Return (score 0-100, issues list)."""
    issues: list[dict] = []

    if date_col is None or date_col not in df.columns:
        return 75.0, []  # Cannot assess timeliness without a date column

    dates = pd.to_datetime(df[date_col], errors="coerce").dropna()
    if len(dates) == 0:
        issues.append({
            "column": date_col,
            "dimension": "timeliness",
            "severity": "critical",
            "description": f"Date column '{date_col}' has zero parseable date values.",
            "recommended_action": "Fix date parsing in data-cleaning skill.",
        })
        return 0.0, issues

    score = 100.0
    actual_max = dates.max()
    actual_min = dates.min()

    # Freshness check
    if expected_max_date:
        expected_max = pd.Timestamp(expected_max_date)
        staleness_days = (expected_max - actual_max).days
        if staleness_days > 30:
            score -= 40
            severity = "critical"
        elif staleness_days > 7:
            score -= 20
            severity = "medium"
        elif staleness_days > 2:
            score -= 8
            severity = "low"
        else:
            staleness_days = 0
            severity = None

        if severity:
            issues.append({
                "column": date_col,
                "dimension": "timeliness",
                "severity": severity,
                "description": (
                    f"Most recent record is {staleness_days} days older than expected max date "
                    f"{expected_max_date}."
                ),
                "recommended_action": (
                    "Re-run ingestion pipeline. If source is stale, "
                    "do not use recency-dependent features."
                ),
            })

    # Coverage start check
    if expected_min_date:
        expected_min = pd.Timestamp(expected_min_date)
        undershoot_days = (actual_min - expected_min).days
        if undershoot_days > 30:
            score -= 25
            issues.append({
                "column": date_col,
                "dimension": "timeliness",
                "severity": "critical",
                "description": (
                    f"Data starts {undershoot_days} days after expected min date "
                    f"{expected_min_date}. Coverage gap at start of period."
                ),
                "recommended_action": "Re-extract historical data to cover required date range.",
            })
        elif undershoot_days > 7:
            score -= 10
            issues.append({
                "column": date_col,
                "dimension": "timeliness",
                "severity": "medium",
                "description": (
                    f"Data starts {undershoot_days} days after expected min date."
                ),
                "recommended_action": "Verify source has data for the full required period.",
            })

    # Gap detection (daily resolution heuristic)
    date_range_index = pd.date_range(actual_min, actual_max, freq="D")
    present_dates = set(dates.dt.normalize())
    gap_count = sum(1 for d in date_range_index if d not in present_dates)
    gap_rate = gap_count / len(date_range_index) if len(date_range_index) > 0 else 0

    if gap_rate > 0.20:
        score -= 35
        issues.append({
            "column": date_col,
            "dimension": "timeliness",
            "severity": "critical",
            "description": f"Timeline has {gap_count} missing days ({gap_rate:.1%} of date range).",
            "recommended_action": "Halt. Re-extract data for missing periods before modeling.",
        })
    elif gap_rate > 0.05:
        score -= 15
        issues.append({
            "column": date_col,
            "dimension": "timeliness",
            "severity": "medium",
            "description": f"Timeline has {gap_count} missing days ({gap_rate:.1%} of date range).",
            "recommended_action": "Investigate source gaps. Forward-fill if gap < 3 days.",
        })
    elif gap_rate > 0.01:
        score -= 5
        issues.append({
            "column": date_col,
            "dimension": "timeliness",
            "severity": "low",
            "description": f"Minor timeline gaps: {gap_count} missing days ({gap_rate:.1%}).",
            "recommended_action": "Document; acceptable for most use cases.",
        })

    return max(0.0, round(score, 1)), issues


def _score_relevance(
    df: pd.DataFrame,
    task_columns: list[str] | None = None,
) -> tuple[float, list[dict]]:
    """Return (score 0-100, issues list)."""
    issues: list[dict] = []
    score = 100.0

    zero_var_cols = [col for col in df.columns if df[col].nunique(dropna=True) <= 1]
    near_zero_var_cols = [
        col for col in df.select_dtypes(include="number").columns
        if df[col].std(skipna=True) < 0.001 and col not in zero_var_cols
    ]

    for col in zero_var_cols:
        score -= 5
        issues.append({
            "column": col,
            "dimension": "relevance",
            "severity": "medium",
            "description": f"Zero variance: '{col}' has only 1 unique value.",
            "recommended_action": "Drop column — adds no information to a model.",
        })

    for col in near_zero_var_cols:
        score -= 3
        issues.append({
            "column": col,
            "dimension": "relevance",
            "severity": "low",
            "description": f"Near-zero variance in '{col}' (std < 0.001).",
            "recommended_action": "Confirm relevance; consider dropping before feature engineering.",
        })

    # Extra penalty when zero-variance column count is very high (likely granularity issue)
    if len(zero_var_cols) > 8:
        score -= 20
        issues.append({
            "column": "__multiple__",
            "dimension": "relevance",
            "severity": "critical",
            "description": (
                f"{len(zero_var_cols)} zero-variance columns detected. "
                "This may indicate a granularity mismatch (e.g., dataset-level vs row-level data)."
            ),
            "recommended_action": (
                "Verify that each row represents the correct observational unit. "
                "Drop all zero-variance columns."
            ),
        })

    return max(0.0, round(score, 1)), issues


# ---------------------------------------------------------------------------
# Per-column score aggregation
# ---------------------------------------------------------------------------

def _build_per_column_scores(
    df: pd.DataFrame,
    completeness_issues: list[dict],
    consistency_issues: list[dict],
    accuracy_issues: list[dict],
    timeliness_issues: list[dict],
    relevance_issues: list[dict],
) -> dict[str, dict]:
    """Build per-column score summary from issue lists."""
    per_col: dict[str, dict] = {
        col: {
            "completeness": 100,
            "consistency": 100,
            "accuracy": 100,
            "timeliness": None,
            "relevance": 100,
        }
        for col in df.columns
    }

    severity_penalty = {"critical": 40, "medium": 15, "low": 5}

    def _apply_issues(issue_list: list[dict], dim: str) -> None:
        for issue in issue_list:
            col = issue.get("column", "__all__")
            if col in per_col:
                penalty = severity_penalty.get(issue.get("severity", "low"), 5)
                current = per_col[col].get(dim, 100) or 100
                per_col[col][dim] = max(0, current - penalty)

    _apply_issues(completeness_issues, "completeness")
    _apply_issues(consistency_issues, "consistency")
    _apply_issues(accuracy_issues, "accuracy")
    _apply_issues(timeliness_issues, "timeliness")
    _apply_issues(relevance_issues, "relevance")

    return per_col


# ---------------------------------------------------------------------------
# Drift detection
# ---------------------------------------------------------------------------

def _check_drift(
    df: pd.DataFrame,
    prior_report: dict,
    significance_level: float = 0.05,
) -> dict[str, dict]:
    """Compare current DataFrame against prior QA report for distribution drift."""
    drift_metrics: dict[str, dict] = {}
    prior_col_stats = prior_report.get("column_stats", {})
    drifted_cols: list[str] = []

    for col in df.columns:
        if col not in prior_col_stats:
            continue

        col_stats = prior_col_stats[col]
        col_drift: dict[str, Any] = {}

        if df[col].dtype in [np.float64, np.float32, np.int64, np.int32, "float64", "float32", "int64", "int32"]:
            prior_samples = col_stats.get("sample_values")
            if prior_samples and len(prior_samples) >= 10:
                current_vals = df[col].dropna().values
                if len(current_vals) >= 10:
                    stat, p_value = stats.ks_2samp(
                        current_vals,
                        np.array(prior_samples, dtype=float),
                    )
                    drifted = bool(p_value < significance_level)
                    col_drift = {
                        "test": "ks_2samp",
                        "statistic": round(float(stat), 4),
                        "p_value": round(float(p_value), 4),
                        "drifted": drifted,
                    }
                    if drifted:
                        drifted_cols.append(col)

        elif df[col].dtype == object:
            prior_freq = col_stats.get("value_counts", {})
            if prior_freq:
                current_freq = df[col].value_counts(normalize=True).to_dict()
                all_cats = sorted(set(prior_freq) | set(current_freq))
                prior_vec = np.array([prior_freq.get(c, 0.0) for c in all_cats])
                current_vec = np.array([current_freq.get(c, 0.0) for c in all_cats])

                if prior_vec.sum() > 0 and current_vec.sum() > 0:
                    prior_vec = prior_vec / prior_vec.sum()
                    current_vec = current_vec / current_vec.sum()
                    n = max(int(df[col].dropna().shape[0]), 1)
                    # Add small epsilon to avoid zero expected frequencies
                    expected = prior_vec * n + 1e-8
                    observed = current_vec * n
                    try:
                        stat, p_value = stats.chisquare(observed, f_exp=expected)
                        drifted = bool(p_value < significance_level)
                        col_drift = {
                            "test": "chisquare",
                            "statistic": round(float(stat), 4),
                            "p_value": round(float(p_value), 4),
                            "drifted": drifted,
                        }
                        if drifted:
                            drifted_cols.append(col)
                    except Exception:
                        pass

        if col_drift:
            drift_metrics[col] = col_drift

    # Volume check
    prior_row_count = prior_report.get("row_count", 0)
    if prior_row_count > 0:
        volume_change_pct = (len(df) - prior_row_count) / prior_row_count
        volume_drifted = abs(volume_change_pct) > 0.20
        drift_metrics["__volume__"] = {
            "test": "volume_pct_change",
            "statistic": round(float(volume_change_pct), 4),
            "p_value": None,
            "drifted": volume_drifted,
        }
        if volume_drifted:
            drifted_cols.append("__volume__")

    # Multi-column simultaneous drift
    if len(drifted_cols) >= 3:
        drift_metrics["__multi_column_drift__"] = {
            "columns": drifted_cols,
            "severity": "critical",
            "description": (
                f"Simultaneous drift in {len(drifted_cols)} columns/metrics: "
                f"{drifted_cols}. Likely indicates an upstream ETL or schema change."
            ),
            "recommended_action": (
                "Halt pipeline. Investigate upstream data source. "
                "Re-run eda-comprehensive skill on the new data."
            ),
        }

    return drift_metrics


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def _calculate_verdict(
    scores: dict[str, float],
    all_issues: list[dict],
    drift_metrics: dict,
    context: str,
) -> dict:
    """Compute PASS / CONDITIONAL_PASS / FAIL verdict."""
    dimensions = ["completeness", "consistency", "accuracy", "timeliness", "relevance"]
    failing = [d for d in dimensions if scores.get(d, 100) < 50]
    critical_issues = [i for i in all_issues if i.get("severity") == "critical"]

    # Promote multi-column drift to a critical issue
    if "__multi_column_drift__" in drift_metrics:
        di = drift_metrics["__multi_column_drift__"]
        critical_issues.append({
            "column": "__multi_column__",
            "dimension": "timeliness",
            "severity": "critical",
            "description": di["description"],
            "recommended_action": di["recommended_action"],
        })

    n_critical = len(critical_issues)

    # Ad-hoc: always PASS
    if context == "ad_hoc":
        return {
            "verdict": "PASS",
            "reason": "Ad-hoc context: all issues are warnings only.",
            "accepted_risks": [i["description"] for i in critical_issues],
            "failing_dimensions": failing,
        }

    # Exploratory: at worst CONDITIONAL_PASS
    if context == "exploratory":
        return {
            "verdict": "CONDITIONAL_PASS",
            "reason": "Exploratory context: no hard FAILs. Review before production use.",
            "accepted_risks": [i["description"] for i in critical_issues],
            "failing_dimensions": failing,
        }

    # Hard FAIL on any dimension < 50
    if failing:
        return {
            "verdict": "FAIL",
            "reason": f"Dimension(s) scored below 50: {failing}.",
            "accepted_risks": [],
            "failing_dimensions": failing,
        }

    # Feature store: fail on schema/structural criticals
    if context == "feature_store":
        schema_criticals = [
            i for i in critical_issues
            if i.get("dimension") in ("completeness", "consistency")
        ]
        if schema_criticals:
            return {
                "verdict": "FAIL",
                "reason": "Feature store context: schema/completeness critical issues are hard FAILs.",
                "accepted_risks": [],
                "failing_dimensions": failing,
            }

    # Production training: fail on any critical
    if context == "production_training" and n_critical > 0:
        return {
            "verdict": "FAIL",
            "reason": (
                f"Production training context: {n_critical} critical issue(s) present. "
                "Zero tolerance."
            ),
            "accepted_risks": [],
            "failing_dimensions": failing,
        }

    # CONDITIONAL_PASS: <=2 criticals, all dims >= 50
    if n_critical <= 2:
        accepted = [
            {
                "column": i.get("column"),
                "dimension": i.get("dimension"),
                "description": i.get("description"),
                "recommended_action": i.get("recommended_action"),
                "accepted_risk": "Acknowledged and documented — proceed with caution.",
            }
            for i in critical_issues
        ]
        if n_critical > 0:
            return {
                "verdict": "CONDITIONAL_PASS",
                "reason": (
                    f"All dimensions >= 50. {n_critical} critical issue(s) documented."
                ),
                "accepted_risks": accepted,
                "failing_dimensions": failing,
            }

    # >2 criticals in any non-exploratory context
    if n_critical > 2:
        return {
            "verdict": "FAIL",
            "reason": f"{n_critical} critical issues exceed the maximum of 2 for a CONDITIONAL_PASS.",
            "accepted_risks": [],
            "failing_dimensions": failing,
        }

    # Clean PASS
    return {
        "verdict": "PASS",
        "reason": "All dimensions >= 70, zero critical issues.",
        "accepted_risks": [],
        "failing_dimensions": [],
    }


# ---------------------------------------------------------------------------
# Column stats snapshot (for future drift baseline)
# ---------------------------------------------------------------------------

def _snapshot_column_stats(df: pd.DataFrame, sample_size: int = 500) -> dict:
    stats_out: dict[str, Any] = {}
    rng = np.random.default_rng(42)

    for col in df.columns:
        series = df[col].dropna()
        if len(series) == 0:
            continue

        if df[col].dtype in [np.float64, np.float32, np.int64, np.int32]:
            n = min(sample_size, len(series))
            idx = rng.choice(len(series), size=n, replace=False)
            stats_out[col] = {
                "sample_values": series.iloc[idx].tolist(),
                "mean": round(float(series.mean()), 6),
                "std": round(float(series.std()), 6),
                "p25": round(float(series.quantile(0.25)), 6),
                "p50": round(float(series.quantile(0.50)), 6),
                "p75": round(float(series.quantile(0.75)), 6),
            }
        elif df[col].dtype == object:
            stats_out[col] = {
                "value_counts": series.value_counts(normalize=True).head(50).to_dict()
            }

    return stats_out


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_qa_report(
    df: pd.DataFrame,
    contract_path: str | None = None,
    prior_report_path: str | None = None,
    output_path: str = "qa_report.json",
    context: str = "production_training",
    critical_cols: list[str] | None = None,
    expected_cols: list[str] | None = None,
    expected_rows: int | None = None,
    key_columns: list[str] | None = None,
    date_col: str | None = None,
    expected_max_date: str | None = None,
    expected_min_date: str | None = None,
    freshness_days: int | None = None,
    range_constraints: dict[str, tuple[float, float]] | None = None,
    sentinel_values: list[Any] | None = None,
) -> dict:
    """
    Evaluate a DataFrame and write a qa_report.json.

    Parameters
    ----------
    df : pd.DataFrame
        The cleaned DataFrame to evaluate (this function does NOT modify it).
    contract_path : str, optional
        Path to a YAML data contract.
    prior_report_path : str, optional
        Path to a previous qa_report.json for drift comparison.
    output_path : str
        Where to write qa_report.json.
    context : str
        Execution context. One of:
        'production_training' | 'exploratory' | 'feature_store' | 'ad_hoc'
    critical_cols : list[str], optional
        Columns that are load-bearing (join keys, target variables, required features).
    expected_cols : list[str], optional
        Full list of columns the dataset should have.
    expected_rows : int, optional
        Expected approximate row count for volume validation.
    key_columns : list[str], optional
        Columns that form the natural/business key (must be unique per row).
    date_col : str, optional
        Name of the primary date/timestamp column.
    expected_max_date : str, optional
        ISO date string for expected most-recent record (freshness check).
    expected_min_date : str, optional
        ISO date string for expected earliest record (coverage check).
    freshness_days : int, optional
        Maximum acceptable staleness in days.
    range_constraints : dict, optional
        {column_name: (min_value, max_value)} for hard-coded range checks.
    sentinel_values : list, optional
        Additional numeric sentinels to check (defaults cover -999, 9999, etc.).

    Returns
    -------
    dict
        The full QA report as a Python dict (also written to output_path).
    """
    print(f"[QA] Starting quality assessment — context: {context}")
    print(f"[QA] DataFrame shape: {df.shape[0]:,} rows x {df.shape[1]} columns")

    # Load optional inputs
    data_contract: dict | None = None
    prior_report: dict | None = None

    if contract_path and Path(contract_path).exists():
        try:
            import yaml
        except ImportError:
            yaml = None
        if yaml is None:
            raise ImportError("Install PyYAML (pip install pyyaml) to use data contracts")
        with open(contract_path) as f:
            data_contract = yaml.safe_load(f)
        print(f"[QA] Loaded data contract: {contract_path}")

    if prior_report_path and Path(prior_report_path).exists():
        with open(prior_report_path) as f:
            prior_report = json.load(f)
        print(f"[QA] Loaded prior report (timestamp: {prior_report.get('timestamp', 'unknown')})")
    else:
        print("[QA] No prior report — drift checks skipped; this run establishes baseline.")

    # Score all 5 dimensions
    completeness_score, completeness_issues = _score_completeness(
        df, critical_cols=critical_cols, expected_cols=expected_cols, expected_rows=expected_rows
    )
    consistency_score, consistency_issues = _score_consistency(df, key_columns=key_columns)
    accuracy_score, accuracy_issues = _score_accuracy(
        df, range_constraints=range_constraints, sentinel_values=sentinel_values
    )
    timeliness_score, timeliness_issues = _score_timeliness(
        df, date_col=date_col, expected_max_date=expected_max_date,
        expected_min_date=expected_min_date, freshness_days=freshness_days,
    )
    relevance_score, relevance_issues = _score_relevance(df)

    scores = {
        "completeness": completeness_score,
        "consistency": consistency_score,
        "accuracy": accuracy_score,
        "timeliness": timeliness_score,
        "relevance": relevance_score,
    }

    all_issues = (
        completeness_issues
        + consistency_issues
        + accuracy_issues
        + timeliness_issues
        + relevance_issues
    )

    # Contract violations (if available) are added as additional issues
    if data_contract:
        contract_issues = _validate_contract(df, data_contract)
        all_issues.extend(contract_issues)

    # Distribution drift
    drift_metrics: dict = {}
    if prior_report:
        drift_metrics = _check_drift(df, prior_report)

    # Per-column scores
    per_column_scores = _build_per_column_scores(
        df,
        completeness_issues, consistency_issues,
        accuracy_issues, timeliness_issues, relevance_issues,
    )

    # Verdict
    verdict_result = _calculate_verdict(scores, all_issues, drift_metrics, context)

    # Determine which downstream skills are allowed based on verdict
    verdict = verdict_result["verdict"]
    if verdict == "PASS":
        allowed_downstream_skills = [
            "missing-data-imputation", "eda-comprehensive", "feature-engineering"
        ]
    elif verdict == "CONDITIONAL_PASS":
        allowed_downstream_skills = [
            "missing-data-imputation", "eda-comprehensive"
        ]
        # feature-engineering blocked until issues resolved and re-QA'd
    else:  # FAIL
        allowed_downstream_skills = ["data-cleaning"]
        # Only cleaning allowed — must fix issues and re-QA

    # Column stats snapshot for future baseline
    column_stats = _snapshot_column_stats(df)

    # Assemble report
    report: dict = {
        "schema_version": "1.0",
        "skill_name": "data-quality-assurance",
        "verdict": verdict_result["verdict"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": context,
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "column_list": sorted(df.columns.tolist()),
        "overall_scores": scores,
        "per_column_scores": per_column_scores,
        "issues": all_issues,
        "drift_metrics": drift_metrics,
        "accepted_risks": verdict_result.get("accepted_risks", []),
        "failing_dimensions": verdict_result.get("failing_dimensions", []),
        "verdict_reason": verdict_result["reason"],
        "allowed_downstream_skills": allowed_downstream_skills,
        "column_stats": column_stats,
        "reviewer": None,
    }

    # Write report
    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path_obj, "w") as f:
        json.dump(report, f, indent=2, default=str)

    # Print summary
    print("\n[QA] === DIMENSION SCORES ===")
    for dim, score in scores.items():
        status = "PASS" if score >= 70 else "DEGRADED" if score >= 50 else "FAIL"
        bar = "#" * int(score // 10) + "." * (10 - int(score // 10))
        print(f"  {dim:<15} {score:>6.1f}  [{bar}]  {status}")

    critical_count = sum(1 for i in all_issues if i.get("severity") == "critical")
    medium_count = sum(1 for i in all_issues if i.get("severity") == "medium")
    low_count = sum(1 for i in all_issues if i.get("severity") == "low")

    print(f"\n[QA] Issues: {critical_count} critical, {medium_count} medium, {low_count} low")
    if drift_metrics:
        drifted = sum(
            1 for k, v in drift_metrics.items()
            if k not in ("__multi_column_drift__",) and v.get("drifted")
        )
        print(f"[QA] Drift: {drifted} column(s) with detected drift")

    print(f"\n[QA] VERDICT: {report['verdict']}")
    print(f"[QA] Reason:  {verdict_result['reason']}")
    print(f"[QA] Report saved to: {output_path}")

    return report


def _validate_contract(df: pd.DataFrame, contract: dict) -> list[dict]:
    """Validate DataFrame against a YAML data contract and return issues."""
    violations: list[dict] = []
    schema = contract.get("schema", {})

    for col, spec in schema.items():
        if col not in df.columns:
            violations.append({
                "column": col,
                "dimension": "completeness",
                "severity": "critical",
                "description": f"Contract requires column '{col}' but it is absent from the DataFrame.",
                "recommended_action": "Re-run data-cleaning skill or fix upstream extraction.",
            })
            continue

        # dtype check
        expected_dtype = spec.get("dtype")
        if expected_dtype and str(df[col].dtype) != expected_dtype:
            violations.append({
                "column": col,
                "dimension": "consistency",
                "severity": "medium",
                "description": (
                    f"Contract expects dtype '{expected_dtype}', "
                    f"actual dtype is '{df[col].dtype}'."
                ),
                "recommended_action": f"Cast '{col}' to '{expected_dtype}' in data-cleaning skill.",
            })

        # Range check
        if "min" in spec or "max" in spec:
            col_min = spec.get("min", float("-inf"))
            col_max = spec.get("max", float("inf"))
            try:
                out_of_range = float(((df[col] < col_min) | (df[col] > col_max)).mean())
                if out_of_range > 0:
                    severity = "critical" if out_of_range > 0.05 else "medium"
                    violations.append({
                        "column": col,
                        "dimension": "accuracy",
                        "severity": severity,
                        "description": (
                            f"{out_of_range:.1%} of values are outside the contract "
                            f"range [{col_min}, {col_max}]."
                        ),
                        "recommended_action": "Clip or null-fill out-of-range values.",
                    })
            except TypeError:
                pass  # Non-numeric column with range spec — skip

        # Not-null requirement
        if spec.get("not_null"):
            null_rate = float(df[col].isnull().mean())
            if null_rate > 0:
                severity = "critical" if null_rate > 0.01 else "low"
                violations.append({
                    "column": col,
                    "dimension": "completeness",
                    "severity": severity,
                    "description": (
                        f"Contract marks '{col}' as not-null, "
                        f"but {null_rate:.1%} of values are null."
                    ),
                    "recommended_action": "Investigate nulls — this column must be complete per contract.",
                })

        # Allowed values check
        allowed_values = spec.get("allowed_values")
        if allowed_values:
            invalid_rate = float((~df[col].isin(allowed_values) & df[col].notna()).mean())
            if invalid_rate > 0:
                severity = "critical" if invalid_rate > 0.05 else "medium"
                violations.append({
                    "column": col,
                    "dimension": "accuracy",
                    "severity": severity,
                    "description": (
                        f"{invalid_rate:.1%} of values for '{col}' are not in the "
                        f"contract's allowed_values list."
                    ),
                    "recommended_action": "Filter or correct values not in the allowed set.",
                })

    return violations


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a QA report for a dataset. "
            "Produces qa_report.json with a PASS/CONDITIONAL_PASS/FAIL verdict."
        )
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Path to input dataset. Supports .parquet, .csv, .json.",
    )
    parser.add_argument(
        "--contract", "-c", default=None,
        help="Path to YAML data contract (optional).",
    )
    parser.add_argument(
        "--prior-report", "-p", default=None,
        help="Path to a prior qa_report.json for drift detection (optional).",
    )
    parser.add_argument(
        "--output", "-o", default="qa_report.json",
        help="Output path for qa_report.json (default: qa_report.json).",
    )
    parser.add_argument(
        "--context", default="production_training",
        choices=["production_training", "exploratory", "feature_store", "ad_hoc"],
        help="Execution context that controls verdict strictness (default: production_training).",
    )
    parser.add_argument(
        "--critical-cols", nargs="*", default=None,
        help="Space-separated list of critical (load-bearing) column names.",
    )
    parser.add_argument(
        "--key-columns", nargs="*", default=None,
        help="Space-separated list of columns that form the natural/business key.",
    )
    parser.add_argument(
        "--date-col", default=None,
        help="Name of the primary date/timestamp column for timeliness checks.",
    )
    parser.add_argument(
        "--expected-max-date", default=None,
        help="ISO date string for expected most-recent record (e.g. '2024-12-31').",
    )
    parser.add_argument(
        "--expected-min-date", default=None,
        help="ISO date string for expected earliest record.",
    )
    parser.add_argument(
        "--expected-rows", type=int, default=None,
        help="Expected approximate row count for volume validation.",
    )
    return parser


def _load_input(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        print(f"ERROR: Input file not found: {path}", file=sys.stderr)
        sys.exit(1)

    suffix = p.suffix.lower()
    if suffix == ".parquet":
        return pd.read_parquet(path)
    elif suffix == ".csv":
        return pd.read_csv(path)
    elif suffix == ".json":
        return pd.read_json(path)
    else:
        print(f"ERROR: Unsupported file format '{suffix}'. Use .parquet, .csv, or .json.",
              file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = _build_arg_parser()
    args = parser.parse_args()

    df = _load_input(args.input)

    report = generate_qa_report(
        df=df,
        contract_path=args.contract,
        prior_report_path=args.prior_report,
        output_path=args.output,
        context=args.context,
        critical_cols=args.critical_cols,
        key_columns=args.key_columns,
        date_col=args.date_col,
        expected_max_date=args.expected_max_date,
        expected_min_date=args.expected_min_date,
        expected_rows=args.expected_rows,
    )

    # Exit with non-zero code on FAIL so CI pipelines can gate on it
    if report["verdict"] == "FAIL":
        sys.exit(1)


if __name__ == "__main__":
    main()
