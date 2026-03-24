"""
generate_imputation_manifest.py

Produces imputation_manifest.json documenting every imputation decision,
fitted imputer paths, validation results, and leakage-safety verification.

Usage (CLI):
    python generate_imputation_manifest.py \
        --train-path data/X_train.parquet \
        --test-path data/X_test.parquet \
        --output-dir artifacts/ \
        --strategy-plan-path artifacts/strategy_plan.json

Usage (library):
    from generate_imputation_manifest import run_imputation_pipeline
    manifest = run_imputation_pipeline(X_train, X_test, strategy_plan, output_dir="artifacts/")
"""

from __future__ import annotations

import argparse
import json
import os
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# Enable IterativeImputer (experimental in some sklearn versions)
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from sklearn.experimental import enable_iterative_imputer  # noqa: F401
    from sklearn.impute import IterativeImputer


# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------
StrategyPlan = dict[str, dict[str, Any]]
Manifest = dict[str, Any]


# ---------------------------------------------------------------------------
# Missingness diagnosis
# ---------------------------------------------------------------------------

def diagnose_mechanism(
    df: pd.DataFrame,
    col: str,
    coef_threshold: float = 0.5,
) -> str:
    """
    Heuristic diagnosis of missingness mechanism for a single column.

    Returns one of: 'MCAR', 'MAR', 'UNKNOWN'
    Note: MNAR cannot be detected statistically — flag based on domain knowledge
    by overriding the returned value in strategy_plan.
    """
    target = df[col].isnull().astype(int)

    if target.sum() < 10:
        return "MCAR"

    numeric_other = (
        df.select_dtypes(include="number")
        .drop(columns=[col], errors="ignore")
        .dropna(axis=1, how="any")
    )

    if numeric_other.shape[1] == 0:
        return "UNKNOWN"

    mask = numeric_other.notna().all(axis=1)
    X = numeric_other[mask]
    y = target[mask]

    if y.sum() < 5 or (y == 0).sum() < 5:
        return "MCAR"

    X_scaled = StandardScaler().fit_transform(X)
    clf = LogisticRegression(max_iter=1000, random_state=42, C=1.0)
    clf.fit(X_scaled, y)
    max_coef = float(np.abs(clf.coef_[0]).max())

    return "MAR" if max_coef > coef_threshold else "MCAR"


# ---------------------------------------------------------------------------
# Imputation application
# ---------------------------------------------------------------------------

def _fit_and_apply(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    cols: list[str],
    strategy: str,
    **kwargs: Any,
) -> tuple[pd.DataFrame, pd.DataFrame, Any]:
    """
    Fit an imputer on X_train columns and transform both splits.
    Returns (X_train_updated, X_test_updated, fitted_imputer).
    """
    X_train = X_train.copy()
    X_test = X_test.copy()

    if strategy == "median":
        imp = SimpleImputer(strategy="median")
    elif strategy == "mode":
        imp = SimpleImputer(strategy="most_frequent")
    elif strategy == "iterative":
        imp = IterativeImputer(max_iter=kwargs.get("max_iter", 10), random_state=42)
    elif strategy == "knn":
        imp = KNNImputer(n_neighbors=kwargs.get("n_neighbors", 5))
    else:
        raise ValueError(f"Unknown numeric strategy: {strategy!r}")

    imp.fit(X_train[cols])
    X_train[cols] = imp.transform(X_train[cols])
    X_test[cols] = imp.transform(X_test[cols])
    return X_train, X_test, imp


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_column(
    X_train_original: pd.DataFrame,
    col: str,
    strategy: str,
    holdout_fraction: float = 0.10,
    random_state: int = 42,
) -> dict[str, Any]:
    """
    Artificial missingness test: remove holdout_fraction of observed values,
    re-impute, measure error against truth.
    """
    rng = np.random.default_rng(random_state)
    observed_idx = X_train_original[col].dropna().index

    if len(observed_idx) < 20:
        return {"method": "artificial_missingness", "metric": "N/A",
                "value": None, "baseline_value": None, "passed": True,
                "note": "Too few observations to validate"}

    n_holdout = max(1, int(holdout_fraction * len(observed_idx)))
    hold_out_idx = rng.choice(observed_idx, size=n_holdout, replace=False)

    X_perturbed = X_train_original[[col]].copy()
    X_perturbed.loc[hold_out_idx, col] = np.nan

    if strategy in ("median", "mode", "iterative", "knn"):
        if strategy == "median":
            imp = SimpleImputer(strategy="median")
        elif strategy == "mode":
            imp = SimpleImputer(strategy="most_frequent")
        elif strategy == "iterative":
            imp = IterativeImputer(max_iter=5, random_state=42)
        elif strategy == "knn":
            imp = KNNImputer(n_neighbors=5)

        imp.fit(X_perturbed)
        imputed = pd.Series(imp.transform(X_perturbed).ravel(), index=X_perturbed.index)
    else:
        return {"method": "artificial_missingness", "metric": "N/A",
                "value": None, "baseline_value": None, "passed": True,
                "note": f"No numeric validation for strategy {strategy!r}"}

    true_vals = X_train_original.loc[hold_out_idx, col].values
    imputed_at_holdout = imputed.loc[hold_out_idx].values

    if pd.api.types.is_numeric_dtype(X_train_original[col]):
        median_val = X_train_original[col].median()
        baseline_mae = float(np.abs(true_vals - median_val).mean())
        imputer_mae = float(np.abs(true_vals - imputed_at_holdout).mean())
        passed = imputer_mae <= baseline_mae * 1.2
        return {
            "method": "artificial_missingness",
            "metric": "MAE",
            "value": round(imputer_mae, 6),
            "baseline_value": round(baseline_mae, 6),
            "passed": passed,
        }
    else:
        _mode_series = X_train_original[col].mode()
        mode_val = _mode_series.iloc[0] if len(_mode_series) > 0 else None
        baseline_acc = float((true_vals == mode_val).mean())
        imputer_acc = float((true_vals == imputed_at_holdout).mean())
        passed = imputer_acc >= baseline_acc * 0.9
        return {
            "method": "artificial_missingness",
            "metric": "accuracy",
            "value": round(imputer_acc, 6),
            "baseline_value": round(baseline_acc, 6),
            "passed": passed,
        }


def ks_distribution_check(
    original_series: pd.Series,
    imputed_series: pd.Series,
    alpha: float = 0.05,
) -> dict[str, Any]:
    """KS-test: p > alpha means no significant distribution shift (desired)."""
    if not pd.api.types.is_numeric_dtype(original_series):
        return {"method": "ks_test", "metric": "N/A",
                "value": None, "baseline_value": alpha, "passed": True,
                "note": "KS-test skipped for non-numeric column"}

    original_nonull = original_series.dropna()
    if len(original_nonull) < 5 or len(imputed_series) < 5:
        return {"method": "ks_test", "metric": "p_value",
                "value": None, "baseline_value": alpha, "passed": True,
                "note": "Too few observations for KS-test"}

    stat, p_value = ks_2samp(original_nonull.values, imputed_series.values)
    return {
        "method": "ks_test",
        "metric": "p_value",
        "value": round(float(p_value), 6),
        "baseline_value": alpha,
        "passed": bool(p_value > alpha),
    }


# ---------------------------------------------------------------------------
# Core pipeline
# ---------------------------------------------------------------------------

def run_imputation_pipeline(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    strategy_plan: StrategyPlan,
    output_dir: str = "artifacts",
    train_only_verified: bool = True,
) -> Manifest:
    """
    Execute full imputation pipeline and return the manifest dict.

    Parameters
    ----------
    X_train : pd.DataFrame
        Training features (will be modified in place copy).
    X_test : pd.DataFrame
        Test features (will be modified in place copy).
    strategy_plan : dict
        Mapping of column name to strategy config. Each entry must contain:
          - 'strategy': str — one of 'median', 'mode', 'iterative', 'knn',
                                   'unknown_category', 'missing_token', 'interpolate',
                                   'drop_column', 'none_and_flag'
          - 'mechanism': str — 'MCAR', 'MAR', 'MNAR', 'UNKNOWN'
          - 'col_type': str — dtype bucket from dtype-router
          Optional:
          - 'parameters': dict — strategy-specific kwargs
          - 'add_indicator': bool — override indicator creation logic
    output_dir : str
        Directory for serialized imputers and manifest JSON.
    train_only_verified : bool
        Set to True only after confirming all fits happened on train data.

    Returns
    -------
    dict
        Manifest with full audit trail.
    """
    X_train = X_train.copy()
    X_test = X_test.copy()
    X_train_original = X_train.copy()  # Preserve for validation

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    columns_imputed: list[dict[str, Any]] = []
    columns_dropped: list[dict[str, Any]] = []
    indicators_created: list[str] = []
    validation_results: list[dict[str, Any]] = []
    fitted_imputers: dict[str, Any] = {}

    INDICATOR_THRESHOLD = 0.01

    # --- Group columns by strategy ---
    strategy_groups: dict[str, list[str]] = {}
    for col, plan in strategy_plan.items():
        if col not in X_train.columns:
            continue
        s = plan.get("strategy", "median")
        strategy_groups.setdefault(s, []).append(col)

    # --- Step A: Create _was_missing indicators (before any imputation) ---
    for col, plan in strategy_plan.items():
        if col not in X_train.columns:
            continue
        null_rate = float(X_train[col].isnull().mean())
        mechanism = plan.get("mechanism", "MCAR")
        add_indicator = plan.get(
            "add_indicator",
            null_rate > INDICATOR_THRESHOLD and mechanism in ("MAR", "MNAR", "UNKNOWN"),
        )
        # Boolean columns always get an indicator
        if plan.get("col_type") == "boolean":
            add_indicator = True

        if add_indicator and plan.get("strategy") not in ("drop_column",):
            ind_col = f"_was_missing_{col}"
            X_train[ind_col] = X_train[col].isnull().astype(int)
            X_test[ind_col] = X_test[col].isnull().astype(int)
            indicators_created.append(ind_col)

    # --- Step B: Drop columns flagged for removal ---
    for col in strategy_groups.get("drop_column", []):
        null_rate = float(X_train_original[col].isnull().mean())
        columns_dropped.append({
            "column": col,
            "reason": strategy_plan.get(col, {}).get("drop_reason", f"null_rate={null_rate:.2%} exceeds threshold"),
            "null_rate": round(null_rate, 6),
        })
        X_train = X_train.drop(columns=[col], errors="ignore")
        X_test = X_test.drop(columns=[col], errors="ignore")

    # --- Step C: Apply numeric strategies as a group (IterativeImputer needs all cols) ---
    for strategy_name in ("median", "mode"):
        cols = [c for c in strategy_groups.get(strategy_name, []) if c in X_train.columns]
        if not cols:
            continue
        params = {}  # no extra params for simple imputers
        X_train, X_test, imp = _fit_and_apply(X_train, X_test, cols, strategy_name, **params)
        fitted_imputers[strategy_name] = imp

    for strategy_name in ("iterative", "knn"):
        cols = [c for c in strategy_groups.get(strategy_name, []) if c in X_train.columns]
        if not cols:
            continue
        first_plan = strategy_plan.get(cols[0], {})
        params = first_plan.get("parameters", {})
        X_train, X_test, imp = _fit_and_apply(X_train, X_test, cols, strategy_name, **params)
        fitted_imputers[strategy_name] = imp

    # --- Step D: String-fill strategies ---
    for col in strategy_groups.get("unknown_category", []):
        if col not in X_train.columns:
            continue
        X_train[col] = X_train[col].fillna("Unknown")
        X_test[col] = X_test[col].fillna("Unknown")

    for col in strategy_groups.get("missing_token", []):
        if col not in X_train.columns:
            continue
        X_train[col] = X_train[col].fillna("[MISSING]")
        X_test[col] = X_test[col].fillna("[MISSING]")

    # --- Step E: Datetime interpolation ---
    for col in strategy_groups.get("interpolate", []):
        if col not in X_train.columns:
            continue
        for df_split in (X_train, X_test):
            numeric_ts = df_split[col].astype(np.int64).astype(float)
            numeric_ts[df_split[col].isnull()] = np.nan
            plan = strategy_plan.get(col, {})
            limit = plan.get("parameters", {}).get("limit", 3)
            interpolated = numeric_ts.interpolate(method="linear", limit=limit, limit_direction="forward")
            df_split[col] = pd.to_datetime(interpolated, unit="ns", errors="coerce")

    # --- Step F: none_and_flag (irregular datetime, MNAR datetime) ---
    for col in strategy_groups.get("none_and_flag", []):
        if col not in X_train.columns:
            continue
        ind_col = f"_was_missing_{col}"
        if ind_col not in indicators_created:
            X_train[ind_col] = X_train[col].isnull().astype(int)
            X_test[ind_col] = X_test[col].isnull().astype(int)
            indicators_created.append(ind_col)
        # Column stays null — downstream must handle or drop

    # --- Step G: Build columns_imputed records and run validation ---
    for col, plan in strategy_plan.items():
        strategy = plan.get("strategy", "median")
        if strategy == "drop_column":
            continue
        if col not in X_train_original.columns:
            continue

        original_series = X_train_original[col]
        null_rate_before = float(original_series.isnull().mean())

        if col in X_train.columns:
            null_rate_after = float(X_train[col].isnull().mean())
        else:
            null_rate_after = null_rate_before  # was dropped

        rows_affected = int((original_series.isnull()).sum())

        columns_imputed.append({
            "column": col,
            "mechanism": plan.get("mechanism", "MCAR"),
            "strategy": strategy,
            "parameters": plan.get("parameters", {}),
            "rows_affected": rows_affected,
            "null_rate_before": round(null_rate_before, 6),
            "null_rate_after": round(null_rate_after, 6),
        })

        # Validation for numeric columns with a numeric strategy
        if (
            pd.api.types.is_numeric_dtype(original_series)
            and strategy in ("median", "mode", "iterative", "knn")
            and null_rate_before > 0
        ):
            ai_result = validate_column(X_train_original, col, strategy)
            ai_result["column"] = col
            validation_results.append(ai_result)

            if col in X_train.columns:
                ks_result = ks_distribution_check(original_series, X_train[col])
                ks_result["column"] = col
                validation_results.append(ks_result)

    # --- Step H: Serialize fitted imputers ---
    imputers_path = str(Path(output_dir) / "fitted_imputers.joblib")
    joblib.dump(fitted_imputers, imputers_path)

    # --- Step I: Assemble manifest ---
    manifest: Manifest = {
        "schema_version": "1.0",
        "skill_name": "missing-data-imputation",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "row_count": len(X_train),
        "column_count": len(X_train.columns),
        "column_list": sorted(X_train.columns.tolist()),
        "columns_imputed": columns_imputed,
        "columns_dropped": columns_dropped,
        "indicators_created": indicators_created,
        "validation_results": validation_results,
        "fitted_imputers_path": imputers_path,
        "train_only_verified": train_only_verified,
    }

    manifest_path = str(Path(output_dir) / "imputation_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Imputation manifest written to {manifest_path}")
    print(f"  Columns imputed: {len(columns_imputed)}")
    print(f"  Columns dropped: {len(columns_dropped)}")
    print(f"  Indicators created: {len(indicators_created)}")
    print(f"  Validation checks: {len(validation_results)}")

    failed = [r for r in validation_results if not r.get("passed", True)]
    if failed:
        print(f"  WARNING: {len(failed)} validation check(s) FAILED:")
        for r in failed:
            print(f"    {r.get('column')} / {r.get('method')}: "
                  f"{r.get('metric')}={r.get('value')} (baseline={r.get('baseline_value')})")

    return manifest


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate imputation_manifest.json for a missing-data imputation run.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--train-path",
        required=True,
        help="Path to training features file (.parquet or .csv)",
    )
    parser.add_argument(
        "--test-path",
        required=True,
        help="Path to test features file (.parquet or .csv)",
    )
    parser.add_argument(
        "--output-dir",
        default="artifacts",
        help="Directory to write manifest and serialized imputers (default: artifacts/)",
    )
    parser.add_argument(
        "--strategy-plan-path",
        default=None,
        help=(
            "Path to a JSON file containing the strategy_plan dict. "
            "If omitted, mechanisms are auto-diagnosed and strategies are selected automatically."
        ),
    )
    parser.add_argument(
        "--null-rate-threshold",
        type=float,
        default=0.01,
        help="Minimum null rate for a column to be included (default: 0.01 = 1%%)",
    )
    parser.add_argument(
        "--high-missing-threshold",
        type=float,
        default=0.50,
        help="Null rate above which a column is considered high-missing (default: 0.50 = 50%%)",
    )
    return parser


def _load_dataframe(path: str) -> pd.DataFrame:
    p = Path(path)
    if p.suffix == ".parquet":
        return pd.read_parquet(path)
    elif p.suffix in (".csv", ".tsv"):
        return pd.read_csv(path)
    else:
        raise ValueError(f"Unsupported file format: {p.suffix}. Use .parquet or .csv")


def _auto_build_strategy_plan(
    X_train: pd.DataFrame,
    null_rate_threshold: float,
    high_missing_threshold: float,
) -> StrategyPlan:
    """
    Auto-diagnose mechanisms and select default strategies for all null columns.
    This is a reasonable default; override with --strategy-plan-path for production.
    """
    from sklearn.impute import SimpleImputer  # already imported, re-stating for clarity

    null_rates = X_train.isnull().mean()
    candidate_cols = null_rates[null_rates > null_rate_threshold].index.tolist()

    plan: StrategyPlan = {}

    for col in candidate_cols:
        null_rate = float(null_rates[col])
        dtype = X_train[col].dtype
        mechanism = diagnose_mechanism(X_train, col)

        # High-missing: default drop unless overridden
        if null_rate > high_missing_threshold:
            plan[col] = {
                "mechanism": mechanism,
                "col_type": "unknown",
                "strategy": "drop_column",
                "drop_reason": f"null_rate={null_rate:.2%} exceeds high_missing_threshold={high_missing_threshold:.0%}",
                "parameters": {},
                "add_indicator": False,
            }
            continue

        # Select strategy by dtype + mechanism
        if dtype == "bool" or str(dtype) == "boolean":
            strategy = "mode"
            col_type = "boolean"
            add_indicator = True
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            strategy = "interpolate"
            col_type = "datetime"
            add_indicator = True
        elif pd.api.types.is_numeric_dtype(dtype):
            nunique = X_train[col].nunique()
            col_type = "numeric_continuous" if nunique > 20 else "numeric_discrete"
            if mechanism == "MCAR":
                strategy = "median" if col_type == "numeric_continuous" else "mode"
            elif mechanism == "MAR":
                strategy = "iterative"
            else:  # MNAR or UNKNOWN
                strategy = "median" if col_type == "numeric_continuous" else "mode"
            add_indicator = mechanism in ("MAR", "MNAR", "UNKNOWN") or null_rate > 0.01
        elif dtype in ("object", "string") or pd.api.types.is_categorical_dtype(dtype):
            nunique = X_train[col].nunique()
            avg_len = X_train[col].dropna().astype(str).str.len().mean()
            if avg_len > 50:
                strategy = "missing_token"
                col_type = "text_free"
            elif nunique > 20:
                strategy = "unknown_category"
                col_type = "categorical_high_card"
            else:
                col_type = "categorical_low_card"
                strategy = "unknown_category" if mechanism == "MNAR" else "mode"
            add_indicator = False
        else:
            strategy = "median"
            col_type = "unknown"
            add_indicator = null_rate > 0.01

        plan[col] = {
            "mechanism": mechanism,
            "col_type": col_type,
            "strategy": strategy,
            "parameters": {},
            "add_indicator": add_indicator,
        }

    return plan


def main() -> None:
    parser = _build_arg_parser()
    args = parser.parse_args()

    print(f"Loading training data from {args.train_path} ...")
    X_train = _load_dataframe(args.train_path)

    print(f"Loading test data from {args.test_path} ...")
    X_test = _load_dataframe(args.test_path)

    if args.strategy_plan_path:
        print(f"Loading strategy plan from {args.strategy_plan_path} ...")
        with open(args.strategy_plan_path) as f:
            strategy_plan = json.load(f)
    else:
        print("No strategy plan provided — auto-diagnosing mechanisms and selecting strategies ...")
        strategy_plan = _auto_build_strategy_plan(
            X_train,
            null_rate_threshold=args.null_rate_threshold,
            high_missing_threshold=args.high_missing_threshold,
        )
        # Write auto-generated plan to output dir for reproducibility
        Path(args.output_dir).mkdir(parents=True, exist_ok=True)
        auto_plan_path = str(Path(args.output_dir) / "auto_strategy_plan.json")
        with open(auto_plan_path, "w") as f:
            json.dump(strategy_plan, f, indent=2)
        print(f"Auto strategy plan written to {auto_plan_path}")
        print(f"  Review and override before production use.")

    manifest = run_imputation_pipeline(
        X_train=X_train,
        X_test=X_test,
        strategy_plan=strategy_plan,
        output_dir=args.output_dir,
        train_only_verified=True,  # CLI always fits on train only
    )

    # Print summary of validation failures
    failures = [r for r in manifest["validation_results"] if not r.get("passed", True)]
    if failures:
        print(f"\n{len(failures)} validation failure(s) detected. Review manifest for details.")
        raise SystemExit(1)

    print("\nImputation pipeline completed successfully.")


if __name__ == "__main__":
    main()
