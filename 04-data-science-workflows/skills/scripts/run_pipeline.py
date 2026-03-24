#!/usr/bin/env python3
"""
Data Science Pipeline Runner
=============================
Runs the full 5-skill pipeline with sensible defaults.
Designed for junior data scientists who need a single entry point.

Usage:
    python run_pipeline.py --data customers.csv --target churn --task classification
    python run_pipeline.py --data sales.csv --target revenue --task regression
    python run_pipeline.py --data transactions.csv --target amount --task time-series --date-col date
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def print_step(step_num, total, name, status="starting"):
    """Print a clear progress indicator."""
    bar = "█" * step_num + "░" * (total - step_num)
    print(f"\n{'='*60}")
    print(f"  Step {step_num}/{total}: {name}")
    print(f"  [{bar}]")
    print(f"{'='*60}\n")


def print_warn(msg):
    print(f"  WARNING: {msg}")


def print_error(msg):
    print(f"  ERROR: {msg}")


def print_ok(msg):
    print(f"  OK: {msg}")


def run_pipeline(data_path, target_col, task_type, date_col=None, output_dir="pipeline_output"):
    """Run the full 5-skill data preparation pipeline.

    Args:
        data_path: Path to input CSV/Parquet file
        target_col: Name of target column
        task_type: One of 'classification', 'regression', 'time-series', 'clustering', 'nlp'
        date_col: Date column name (required for time-series)
        output_dir: Directory for all outputs

    Returns:
        dict: Pipeline summary with all manifests
    """
    import numpy as np
    import pandas as pd

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    pipeline_start = time.time()
    total_steps = 5
    summary = {
        "pipeline_version": "1.0",
        "start_time": datetime.now(timezone.utc).isoformat(),
        "input_file": str(data_path),
        "target_column": target_col,
        "task_type": task_type,
        "steps": {}
    }

    # ── Step 1: Data Cleaning ─────────────────────────────────────
    print_step(1, total_steps, "Data Cleaning")

    # Load data
    data_path = Path(data_path)
    if data_path.suffix == ".parquet":
        df = pd.read_parquet(data_path)
    elif data_path.suffix in (".csv", ".tsv"):
        sep = "\t" if data_path.suffix == ".tsv" else ","
        df = pd.read_csv(data_path, sep=sep)
    elif data_path.suffix in (".xlsx", ".xls"):
        df = pd.read_excel(data_path)
    else:
        print_error(f"Unsupported file format: {data_path.suffix}")
        sys.exit(1)

    original_shape = df.shape
    print_ok(f"Loaded {df.shape[0]:,} rows x {df.shape[1]} columns ({df.memory_usage(deep=True).sum() / 1e6:.1f} MB)")

    if df.shape[0] == 0:
        print_error("Dataset is empty. Nothing to process.")
        sys.exit(1)

    if target_col not in df.columns:
        print_error(f"Target column '{target_col}' not found. Available: {list(df.columns)}")
        sys.exit(1)

    # Basic cleaning
    # Standardize column names
    import re
    original_cols = df.columns.tolist()
    df.columns = [re.sub(r'[^a-z0-9]', '_', c.lower().strip()).strip('_') for c in df.columns]
    df.columns = [re.sub(r'_+', '_', c) for c in df.columns]
    # Handle duplicate names
    seen = {}
    new_cols = []
    for c in df.columns:
        if c in seen:
            seen[c] += 1
            new_cols.append(f"{c}_{seen[c]}")
        else:
            seen[c] = 0
            new_cols.append(c)
    df.columns = new_cols

    # Update target_col if it was renamed
    target_col_clean = re.sub(r'[^a-z0-9]', '_', target_col.lower().strip()).strip('_')
    target_col_clean = re.sub(r'_+', '_', target_col_clean)
    if target_col_clean in df.columns:
        target_col = target_col_clean

    renamed = {o: n for o, n in zip(original_cols, df.columns) if o != n}
    if renamed:
        print_ok(f"Renamed {len(renamed)} columns to snake_case")

    # Remove duplicates
    n_before = len(df)
    df = df.drop_duplicates()
    n_removed = n_before - len(df)
    if n_removed > 0:
        print_ok(f"Removed {n_removed:,} duplicate rows")

    # Replace sentinels
    sentinels = ['N/A', 'n/a', 'NA', 'NULL', 'null', 'None', 'none', '#N/A', '#REF!',
                 '-999', '999', 'missing', 'MISSING', '', ' ']
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].replace(sentinels, np.nan)
        df[col] = df[col].str.strip() if df[col].dtype == 'object' else df[col]

    # Fix dtypes
    for col in df.select_dtypes(include='object').columns:
        if col == target_col:
            continue
        try:
            numeric = pd.to_numeric(df[col], errors='coerce')
            if numeric.notna().sum() / max(len(df), 1) > 0.8:
                df[col] = numeric
        except Exception:
            pass

    # Sort by date for time-series
    if task_type == "time-series" and date_col:
        date_col_clean = re.sub(r'[^a-z0-9]', '_', date_col.lower().strip()).strip('_')
        date_col_clean = re.sub(r'_+', '_', date_col_clean)
        if date_col_clean in df.columns:
            df[date_col_clean] = pd.to_datetime(df[date_col_clean], errors='coerce')
            df = df.sort_values(date_col_clean)
            date_col = date_col_clean

    df.to_parquet(output_path / "cleaned.parquet", index=False)

    summary["steps"]["cleaning"] = {
        "status": "completed",
        "original_shape": list(original_shape),
        "cleaned_shape": list(df.shape),
        "rows_removed": n_removed,
        "columns_renamed": len(renamed)
    }
    print_ok(f"Cleaning complete: {df.shape[0]:,} rows x {df.shape[1]} columns")

    # ── Step 2: Data Quality Assurance ────────────────────────────
    print_step(2, total_steps, "Data Quality Assurance")

    issues = []
    scores = {}

    # Completeness
    null_rates = df.isnull().mean()
    high_null_cols = null_rates[null_rates > 0.5].index.tolist()
    completeness = max(0, 100 - null_rates.mean() * 200)
    scores["completeness"] = round(completeness, 1)
    if high_null_cols:
        print_warn(f"{len(high_null_cols)} columns are >50% null: {high_null_cols[:5]}")
        issues.append({"severity": "critical", "dimension": "completeness",
                       "description": f"{len(high_null_cols)} columns >50% null"})

    # Consistency
    n_duplicates = df.duplicated().sum()
    dup_rate = n_duplicates / max(len(df), 1)
    consistency = max(0, 100 - dup_rate * 200)
    scores["consistency"] = round(consistency, 1)

    # Relevance
    constant_cols = [c for c in df.columns if df[c].nunique() <= 1]
    relevance = max(0, 100 - len(constant_cols) / max(len(df.columns), 1) * 200)
    scores["relevance"] = round(relevance, 1)
    if constant_cols:
        print_warn(f"{len(constant_cols)} constant columns: {constant_cols[:5]}")
        issues.append({"severity": "medium", "dimension": "relevance",
                       "description": f"{len(constant_cols)} zero-variance columns"})

    scores["accuracy"] = 100.0  # Simplified
    scores["timeliness"] = 100.0  # Simplified

    # Verdict
    min_score = min(scores.values())
    n_critical = sum(1 for i in issues if i["severity"] == "critical")

    if min_score < 50 or n_critical > 0:
        verdict = "FAIL"
        allowed = ["data-cleaning"]
    elif min_score < 70 or n_critical > 0:
        verdict = "CONDITIONAL_PASS"
        allowed = ["missing-data-imputation", "eda-comprehensive"]
    else:
        verdict = "PASS"
        allowed = ["missing-data-imputation", "eda-comprehensive", "feature-engineering"]

    qa_report = {
        "schema_version": "1.0",
        "skill_name": "data-quality-assurance",
        "verdict": verdict,
        "allowed_downstream_skills": allowed,
        "scores": scores,
        "issues": issues,
        "row_count": len(df),
        "column_count": len(df.columns)
    }

    with open(output_path / "qa_report.json", "w") as f:
        json.dump(qa_report, f, indent=2, default=str)

    print_ok(f"Scores: {scores}")

    if verdict == "FAIL":
        print_error(f"QA VERDICT: FAIL (min score: {min_score:.0f})")
        print_error("Fix data quality issues before proceeding.")
        print_error(f"Issues: {issues}")
        summary["steps"]["qa"] = {"status": "failed", "verdict": verdict, "scores": scores}
        summary["end_time"] = datetime.now(timezone.utc).isoformat()
        with open(output_path / "pipeline_summary.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)
        sys.exit(1)
    elif verdict == "CONDITIONAL_PASS":
        print_warn(f"QA VERDICT: CONDITIONAL_PASS — proceeding with caution")
    else:
        print_ok(f"QA VERDICT: PASS")

    summary["steps"]["qa"] = {"status": "completed", "verdict": verdict, "scores": scores}

    # ── Step 3: Missing Data Imputation ───────────────────────────
    print_step(3, total_steps, "Missing Data Imputation")

    total_nulls = df.isnull().sum().sum()
    if total_nulls == 0:
        print_ok("No missing values detected. Skipping imputation.")
        summary["steps"]["imputation"] = {"status": "skipped", "reason": "no_nulls"}
    else:
        print_ok(f"Found {total_nulls:,} missing values across {(df.isnull().any()).sum()} columns")

        # Simple, robust imputation
        for col in df.columns:
            if df[col].isnull().any():
                null_rate = df[col].isnull().mean()

                # Skip target
                if col == target_col:
                    df = df.dropna(subset=[target_col])
                    print_ok(f"Dropped {int(null_rate * len(df)):,} rows with missing target")
                    continue

                # Drop 100% null columns
                if null_rate == 1.0:
                    df = df.drop(columns=[col])
                    print_warn(f"Dropped 100% null column: {col}")
                    continue

                # Create indicator for high-missing columns
                if null_rate > 0.05:
                    df[f"_was_missing_{col}"] = df[col].isnull().astype(int)

                # Impute based on dtype
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].fillna(df[col].median())
                else:
                    mode_vals = df[col].mode()
                    fill_val = mode_vals.iloc[0] if len(mode_vals) > 0 else "Unknown"
                    df[col] = df[col].fillna(fill_val)

        remaining_nulls = df.isnull().sum().sum()
        print_ok(f"Imputation complete. Remaining nulls: {remaining_nulls}")
        df.to_parquet(output_path / "imputed.parquet", index=False)
        summary["steps"]["imputation"] = {
            "status": "completed",
            "nulls_before": int(total_nulls),
            "nulls_after": int(remaining_nulls)
        }

    # ── Step 4: Exploratory Data Analysis ─────────────────────────
    print_step(4, total_steps, "Exploratory Data Analysis")

    findings = {
        "schema_version": "1.0",
        "skill_name": "eda-comprehensive",
        "task": task_type,
        "target_column": target_col,
        "dataset_summary": {
            "rows": len(df),
            "cols": len(df.columns),
            "memory_mb": round(df.memory_usage(deep=True).sum() / 1e6, 1),
            "dtypes": df.dtypes.value_counts().to_dict()
        },
        "recommended_transforms": [],
        "feature_candidates": [],
        "drop_candidates": [],
        "top_features": [],
        "modeling_notes": []
    }

    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    if target_col in numeric_cols:
        numeric_cols.remove(target_col)
    cat_cols = df.select_dtypes(include='object').columns.tolist()

    # Recommend transforms for skewed numeric columns
    for col in numeric_cols[:50]:  # Limit for performance
        try:
            skew = df[col].skew()
            if abs(skew) > 1 and df[col].min() >= 0:
                findings["recommended_transforms"].append({
                    "column": col,
                    "transform_type": "log1p",
                    "reason": f"Skewness = {skew:.2f}"
                })
        except Exception:
            pass

    # Identify drop candidates
    for col in df.columns:
        if col == target_col:
            continue
        if df[col].nunique() <= 1:
            findings["drop_candidates"].append({"column": col, "reason": "zero_variance"})
        elif df[col].nunique() == len(df) and df[col].dtype == 'object':
            findings["drop_candidates"].append({"column": col, "reason": "unique_id_column"})

    # Target analysis
    if task_type == "classification":
        class_counts = df[target_col].value_counts()
        imbalance_ratio = class_counts.min() / max(class_counts.max(), 1)
        if imbalance_ratio < 0.1:
            findings["modeling_notes"].append("SEVERE class imbalance detected. Use SMOTE or class_weight='balanced'.")
        elif imbalance_ratio < 0.3:
            findings["modeling_notes"].append("Moderate class imbalance. Consider class_weight='balanced'.")
        print_ok(f"Target classes: {class_counts.to_dict()}")
    elif task_type == "regression":
        skew = df[target_col].skew()
        if abs(skew) > 1:
            findings["modeling_notes"].append(f"Target is skewed ({skew:.2f}). Consider log transform.")
        print_ok(f"Target: mean={df[target_col].mean():.2f}, std={df[target_col].std():.2f}, skew={skew:.2f}")

    print_ok(f"Found {len(findings['recommended_transforms'])} recommended transforms")
    print_ok(f"Found {len(findings['drop_candidates'])} drop candidates")

    with open(output_path / "eda_findings.json", "w") as f:
        json.dump(findings, f, indent=2, default=str)

    summary["steps"]["eda"] = {
        "status": "completed",
        "transforms_recommended": len(findings["recommended_transforms"]),
        "drop_candidates": len(findings["drop_candidates"])
    }

    # ── Step 5: Feature Engineering ───────────────────────────────
    print_step(5, total_steps, "Feature Engineering")

    # Check QA verdict allows feature engineering
    if "feature-engineering" not in allowed:
        print_warn("QA verdict does not allow feature-engineering. Skipping.")
        print_warn("Fix quality issues and re-run pipeline to enable this step.")
        summary["steps"]["feature_engineering"] = {
            "status": "skipped",
            "reason": "qa_verdict_blocked"
        }
    else:
        from sklearn.model_selection import train_test_split

        # Separate target
        y = df[target_col]
        X = df.drop(columns=[target_col])

        # Drop candidates identified by EDA
        drop_cols = [d["column"] for d in findings["drop_candidates"] if d["column"] in X.columns]
        if drop_cols:
            X = X.drop(columns=drop_cols)
            print_ok(f"Dropped {len(drop_cols)} EDA-flagged columns")

        # Encode remaining categoricals
        for col in X.select_dtypes(include='object').columns:
            if X[col].nunique() < 20:
                X[col] = X[col].astype('category').cat.codes
            else:
                # Frequency encoding for high-cardinality
                freq = X[col].value_counts(normalize=True)
                X[col] = X[col].map(freq).fillna(0)

        # Apply recommended transforms
        for transform in findings["recommended_transforms"]:
            col = transform["column"]
            if col in X.columns and transform["transform_type"] == "log1p":
                if X[col].min() >= 0:
                    X[col] = np.log1p(X[col])

        # Split
        if task_type == "time-series":
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
            y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        elif task_type == "classification":
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, stratify=y, random_state=42
            )
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

        # Save
        X_train.to_parquet(output_path / "X_train.parquet", index=False)
        X_test.to_parquet(output_path / "X_test.parquet", index=False)
        y_train.to_frame().to_parquet(output_path / "y_train.parquet", index=False)
        y_test.to_frame().to_parquet(output_path / "y_test.parquet", index=False)

        print_ok(f"Train: {X_train.shape[0]:,} rows x {X_train.shape[1]} features")
        print_ok(f"Test:  {X_test.shape[0]:,} rows x {X_test.shape[1]} features")

        summary["steps"]["feature_engineering"] = {
            "status": "completed",
            "n_features": X_train.shape[1],
            "train_rows": X_train.shape[0],
            "test_rows": X_test.shape[0]
        }

    # ── Pipeline Complete ─────────────────────────────────────────
    elapsed = time.time() - pipeline_start
    summary["end_time"] = datetime.now(timezone.utc).isoformat()
    summary["elapsed_seconds"] = round(elapsed, 1)
    summary["final_status"] = "completed"

    with open(output_path / "pipeline_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"\n{'='*60}")
    print(f"  PIPELINE COMPLETE")
    print(f"  Time: {elapsed:.0f}s")
    print(f"  Output: {output_path}/")
    print(f"  Summary: {output_path}/pipeline_summary.json")
    print(f"{'='*60}")

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Run the full data science preparation pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_pipeline.py --data customers.csv --target churn --task classification
  python run_pipeline.py --data sales.csv --target revenue --task regression
  python run_pipeline.py --data timeseries.csv --target value --task time-series --date-col date
  python run_pipeline.py --data products.csv --task clustering
        """
    )
    parser.add_argument("--data", required=True, help="Path to input data file (CSV, Parquet, Excel)")
    parser.add_argument("--target", required=True, help="Name of target column")
    parser.add_argument("--task", required=True,
                       choices=["classification", "regression", "time-series", "clustering", "nlp"],
                       help="Type of modeling task")
    parser.add_argument("--date-col", default=None, help="Date column (required for time-series)")
    parser.add_argument("--output", default="pipeline_output", help="Output directory (default: pipeline_output)")

    args = parser.parse_args()

    if args.task == "time-series" and not args.date_col:
        parser.error("--date-col is required for time-series tasks")

    run_pipeline(args.data, args.target, args.task, args.date_col, args.output)


if __name__ == "__main__":
    main()
