#!/usr/bin/env python3
"""
generate_eda_findings.py

Standalone EDA script that produces a machine-readable eda_findings.json.
Designed to feed downstream feature engineering and modeling decisions.

Usage:
    python generate_eda_findings.py --input data.csv --target label --task classification
    python generate_eda_findings.py --input data.parquet --task clustering
    python generate_eda_findings.py --input data.csv --target price --task regression

Outputs:
    eda_findings.json in the current directory (or --output path)
"""

import argparse
import json
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_data(input_path: str) -> pd.DataFrame:
    path = Path(input_path)
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    elif path.suffix in (".csv", ".tsv"):
        sep = "\t" if path.suffix == ".tsv" else ","
        return pd.read_csv(path, sep=sep, low_memory=False)
    elif path.suffix in (".xlsx", ".xls"):
        return pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")


# ---------------------------------------------------------------------------
# Shape classification (mirrors shape-aware-strategy.md)
# ---------------------------------------------------------------------------

def classify_shape(df: pd.DataFrame) -> list[str]:
    n_rows, n_cols = df.shape
    null_rate = df.isnull().sum().sum() / df.size
    sparse_col_rate = (df.isnull().mean() > 0.50).mean()

    has_datetime = any(
        pd.api.types.is_datetime64_any_dtype(df[col]) for col in df.columns
    ) or isinstance(df.index, pd.DatetimeIndex)

    tags = []
    if n_cols > 100:
        tags.append("wide")
    if n_rows > 1_000_000:
        tags.append("tall")
    if sparse_col_rate > 0.30:
        tags.append("sparse")
    if has_datetime:
        tags.append("time_series")
    if not tags:
        tags.append("standard")
    return tags


# ---------------------------------------------------------------------------
# Dataset summary
# ---------------------------------------------------------------------------

def build_dataset_summary(df: pd.DataFrame) -> dict:
    n_rows, n_cols = df.shape
    memory_mb = df.memory_usage(deep=True).sum() / (1024 ** 2)
    shape_tags = classify_shape(df)

    dtype_counts = df.dtypes.astype(str).value_counts().to_dict()

    return {
        "rows": n_rows,
        "cols": n_cols,
        "memory_mb": round(memory_mb, 3),
        "shape_tags": shape_tags,
        "dtype_counts": dtype_counts,
        "total_nulls": int(df.isnull().sum().sum()),
        "overall_null_rate": round(df.isnull().sum().sum() / df.size, 4),
        "duplicate_rows": int(df.duplicated().sum()),
    }


# ---------------------------------------------------------------------------
# Target analysis
# ---------------------------------------------------------------------------

def analyze_target(df: pd.DataFrame, target: str, task: str) -> dict:
    if target not in df.columns:
        return {"error": f"Target column '{target}' not found"}

    series = df[target].dropna()
    result = {"column": target, "task": task, "n_nulls": int(df[target].isnull().sum())}

    if task == "classification":
        value_counts = series.value_counts()
        n_classes = len(value_counts)
        class_balance = (value_counts / len(series)).to_dict()
        min_class_pct = min(class_balance.values())
        result.update({
            "type": "categorical",
            "n_classes": n_classes,
            "class_balance": {str(k): round(v, 4) for k, v in class_balance.items()},
            "imbalance_flag": min_class_pct < 0.10,
            "imbalance_severity": (
                "severe" if min_class_pct < 0.02 else
                "moderate" if min_class_pct < 0.10 else
                "mild" if min_class_pct < 0.20 else
                "balanced"
            ),
            "transform_recommendation": (
                "use class_weight='balanced' or SMOTE/oversampling"
                if min_class_pct < 0.10 else "none required"
            ),
        })

    elif task == "regression":
        skewness = float(series.skew())
        kurtosis = float(series.kurtosis())
        shapiro_stat, shapiro_p = (
            stats.shapiro(series.sample(min(5000, len(series)), random_state=42))
            if len(series) >= 3 else (None, None)
        )
        is_normal = (shapiro_p or 0) > 0.05

        if abs(skewness) > 1.0:
            if series.min() > 0:
                transform_rec = "log1p transform recommended (right-skewed, all positive)"
            else:
                transform_rec = "sqrt or Box-Cox transform recommended (skewed, has zeros/negatives)"
        elif abs(skewness) > 0.5:
            transform_rec = "mild skew — consider sqrt transform or leave as-is"
        else:
            transform_rec = "approximately symmetric — no transform needed"

        result.update({
            "type": "continuous",
            "mean": round(float(series.mean()), 4),
            "median": round(float(series.median()), 4),
            "std": round(float(series.std()), 4),
            "min": round(float(series.min()), 4),
            "max": round(float(series.max()), 4),
            "skewness": round(skewness, 4),
            "kurtosis": round(kurtosis, 4),
            "distribution_shape": (
                "right_skewed" if skewness > 0.5 else
                "left_skewed" if skewness < -0.5 else
                "approximately_normal"
            ),
            "normality_test_p": round(shapiro_p, 4) if shapiro_p is not None else None,
            "is_approximately_normal": is_normal,
            "transform_recommendation": transform_rec,
        })

    elif task == "time_series":
        # Minimal stationarity check
        try:
            from statsmodels.tsa.stattools import adfuller
            adf_result = adfuller(series.dropna())
            adf_stat = float(adf_result[0])
            adf_p = float(adf_result[1])
            stationary = adf_p < 0.05
        except ImportError:
            adf_stat, adf_p, stationary = None, None, None

        result.update({
            "type": "time_series",
            "n_observations": len(series),
            "adf_statistic": round(adf_stat, 4) if adf_stat is not None else None,
            "adf_p_value": round(adf_p, 4) if adf_p is not None else None,
            "is_stationary": stationary,
            "transform_recommendation": (
                "apply differencing (.diff()) before modeling"
                if stationary is False else "series appears stationary"
            ),
        })

    return result


# ---------------------------------------------------------------------------
# Recommended transforms
# ---------------------------------------------------------------------------

def find_recommended_transforms(df: pd.DataFrame, target: str = None) -> list[dict]:
    transforms = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if target and target in numeric_cols:
        numeric_cols = [c for c in numeric_cols if c != target]

    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) < 10:
            continue

        skewness = float(series.skew())
        null_rate = df[col].isnull().mean()

        # High null rate → imputation needed before transforms
        if null_rate > 0.05:
            transforms.append({
                "column": col,
                "transform_type": "impute_first",
                "reason": f"null_rate={null_rate:.2%} — impute before applying other transforms",
                "code_snippet": f"df['{col}'].fillna(df['{col}'].median(), inplace=True)",
            })

        # Skewness
        if skewness > 1.0 and series.min() > 0:
            transforms.append({
                "column": col,
                "transform_type": "log1p",
                "reason": f"right-skewed (skew={skewness:.2f}), all values positive",
                "code_snippet": f"df['{col}_log'] = np.log1p(df['{col}'])",
            })
        elif skewness > 1.0:
            transforms.append({
                "column": col,
                "transform_type": "quantile_transform",
                "reason": f"right-skewed (skew={skewness:.2f}), contains zeros/negatives",
                "code_snippet": (
                    f"from sklearn.preprocessing import QuantileTransformer\n"
                    f"qt = QuantileTransformer(output_distribution='normal', random_state=42)\n"
                    f"df['{col}_qt'] = qt.fit_transform(df[['{col}']])"
                ),
            })
        elif skewness < -1.0:
            transforms.append({
                "column": col,
                "transform_type": "reflect_log",
                "reason": f"left-skewed (skew={skewness:.2f})",
                "code_snippet": f"df['{col}_rlog'] = np.log1p(df['{col}'].max() - df['{col}'])",
            })

        # Near-zero variance
        if series.std() < 1e-8:
            transforms.append({
                "column": col,
                "transform_type": "drop_constant",
                "reason": "near-zero variance — constant or near-constant column",
                "code_snippet": f"df.drop(columns=['{col}'], inplace=True)",
            })

    return transforms


# ---------------------------------------------------------------------------
# Feature candidates (interaction signals)
# ---------------------------------------------------------------------------

def find_feature_candidates(df: pd.DataFrame, target: str = None, task: str = None) -> list[dict]:
    candidates = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if target and target in numeric_cols:
        numeric_cols = [c for c in numeric_cols if c != target]

    # Pairs with high mutual information or correlation divergence
    checked = 0
    for i, col_a in enumerate(numeric_cols):
        for col_b in numeric_cols[i + 1:]:
            if checked >= 30:  # cap pairwise checks for performance
                break
            checked += 1
            a = df[col_a].dropna()
            b = df[col_b].dropna()
            shared_idx = a.index.intersection(b.index)
            if len(shared_idx) < 20:
                continue
            a, b = a[shared_idx], b[shared_idx]
            try:
                pearson_r, _ = stats.pearsonr(a, b)
                spearman_r, _ = stats.spearmanr(a, b)
                divergence = abs(abs(pearson_r) - abs(spearman_r))
                if divergence > 0.15:
                    candidates.append({
                        "columns": [col_a, col_b],
                        "interaction_type": "nonlinear_relationship",
                        "expected_signal": f"Pearson={pearson_r:.3f}, Spearman={spearman_r:.3f} — divergence={divergence:.3f} suggests non-linearity",
                        "code_snippet": (
                            f"df['{col_a}_x_{col_b}'] = df['{col_a}'] * df['{col_b}']\n"
                            f"df['{col_a}_ratio_{col_b}'] = df['{col_a}'] / (df['{col_b}'] + 1e-9)"  # TODO: verify this calculation
                        ),
                    })
                elif abs(pearson_r) > 0.7:
                    candidates.append({
                        "columns": [col_a, col_b],
                        "interaction_type": "high_correlation",
                        "expected_signal": f"Pearson={pearson_r:.3f} — consider VIF check and possible collinearity",
                        "code_snippet": (
                            f"# Check VIF before including both:\n"
                            f"from statsmodels.stats.outliers_influence import variance_inflation_factor"
                        ),
                    })
            except Exception:
                continue

    return candidates


# ---------------------------------------------------------------------------
# Drop candidates
# ---------------------------------------------------------------------------

def find_drop_candidates(df: pd.DataFrame, target: str = None) -> list[dict]:
    drops = []
    for col in df.columns:
        if col == target:
            continue
        series = df[col]
        null_rate = series.isnull().mean()
        n_unique = series.nunique(dropna=True)

        if null_rate > 0.80:
            drops.append({
                "column": col,
                "reason": f"null_rate={null_rate:.2%} exceeds 80% — too sparse to be useful",
            })
        elif n_unique <= 1:
            drops.append({
                "column": col,
                "reason": "zero variance — constant column provides no information",
            })
        elif pd.api.types.is_object_dtype(series) and n_unique / max(len(series), 1) > 0.90:
            drops.append({
                "column": col,
                "reason": f"high cardinality object column ({n_unique} unique / {len(series)} rows) — likely an ID or free-text field",
            })

    return drops


# ---------------------------------------------------------------------------
# Modeling notes
# ---------------------------------------------------------------------------

def derive_modeling_notes(
    df: pd.DataFrame,
    target: str,
    task: str,
    shape_tags: list[str],
    target_analysis: dict,
    drop_candidates: list[dict],
) -> list[str]:
    notes = []
    n_rows, n_cols = df.shape

    # Shape-driven notes
    if "wide" in shape_tags:
        notes.append(
            f"Wide dataset ({n_cols} cols): use mutual information for feature selection before modeling. "
            "Skip full pairwise correlation matrix."
        )
    if "tall" in shape_tags:
        notes.append(
            f"Tall dataset ({n_rows:,} rows): use stratified sampling for visualization and validation splits."
        )
    if "sparse" in shape_tags:
        notes.append(
            "Sparse dataset: consider regularized models (L1/ElasticNet) or sparse-aware algorithms (XGBoost with tree_method='hist')."
        )
    if "time_series" in shape_tags:
        notes.append(
            "Temporal data detected: ensure train/test split respects time order. "
            "No future leakage. Consider ARIMA, Prophet, or LSTM depending on horizon."
        )

    # Task-driven model recommendations
    if task == "classification":
        if target_analysis.get("imbalance_severity") in ("severe", "moderate"):
            notes.append(
                f"Class imbalance ({target_analysis.get('imbalance_severity')}): "
                "use class_weight='balanced', SMOTE, or precision-recall AUC instead of accuracy."
            )
        if n_cols > 50:
            notes.append(
                "High dimensionality + classification: start with gradient boosting (XGBoost/LightGBM). "
                "Linear baseline with L2 regularization as sanity check."
            )
        else:
            notes.append(
                "Standard classification: try logistic regression (baseline), "
                "random forest (non-linear), and gradient boosting (performance)."
            )

    elif task == "regression":
        shape = target_analysis.get("distribution_shape", "")
        if shape in ("right_skewed", "left_skewed"):
            notes.append(
                f"Target is {shape}: apply recommended transform before fitting linear models. "
                "Tree-based models are transform-agnostic."
            )
        if n_cols < 20:
            notes.append(
                "Low dimensionality regression: linear baseline is viable. "
                "Check residuals for non-linearity before moving to trees."
            )
        else:
            notes.append(
                "Regression with moderate+ dimensionality: "
                "gradient boosting (XGBoost/LightGBM) recommended as primary model."
            )

    elif task == "time_series":
        stationary = target_analysis.get("is_stationary")
        if stationary is False:
            notes.append(
                "Series is non-stationary: apply differencing before ARIMA. "
                "Prophet handles trend natively. LSTM requires careful normalization."
            )
        notes.append(
            "Time-series modeling: validate with walk-forward cross-validation, "
            "not random k-fold."
        )

    elif task == "clustering":
        notes.append(
            "Clustering: scale all numeric features (StandardScaler) before distance-based algorithms. "
            "Run Hopkins statistic to confirm clusterability before committing to k."
        )
        notes.append(
            "Algorithm selection: "
            "K-means (spherical clusters, known k), "
            "DBSCAN (arbitrary shapes, noise points), "
            "Agglomerative (hierarchical structure needed)."
        )

    if drop_candidates:
        notes.append(
            f"{len(drop_candidates)} column(s) flagged for dropping before modeling: "
            + ", ".join(d["column"] for d in drop_candidates[:5])
            + ("..." if len(drop_candidates) > 5 else "")
        )

    return notes


# ---------------------------------------------------------------------------
# Top features (feature-target association)
# ---------------------------------------------------------------------------

def compute_top_features(
    df: pd.DataFrame, target: str, task: str, max_features: int = 20
) -> list[dict]:
    if not target or target not in df.columns:
        return []

    results = []
    target_series = df[target].dropna()

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c != target]

    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    # Numeric features vs target
    for col in numeric_cols[:50]:  # cap for performance
        feature_series = df[col].dropna()
        shared_idx = feature_series.index.intersection(target_series.index)
        if len(shared_idx) < 10:
            continue
        feat = feature_series[shared_idx]
        tgt = target_series[shared_idx]

        try:
            if task == "classification":
                groups = [feat[tgt == cls].values for cls in tgt.unique() if (tgt == cls).sum() >= 3]
                if len(groups) >= 2:
                    if len(groups) == 2:
                        stat, p = stats.mannwhitneyu(*groups, alternative="two-sided")
                        method = "mann_whitney_u"
                    else:
                        stat, p = stats.kruskal(*groups)
                        method = "kruskal_wallis"
                    results.append({
                        "column": col,
                        "association_method": method,
                        "statistic": round(float(stat), 4),
                        "p_value": round(float(p), 6),
                    })
            elif task in ("regression", "time_series"):
                r, p = stats.spearmanr(feat, tgt)
                results.append({
                    "column": col,
                    "association_method": "spearman_r",
                    "statistic": round(float(r), 4),
                    "p_value": round(float(p), 6),
                })
        except Exception:
            continue

    # Categorical features vs target (classification only)
    if task == "classification":
        for col in categorical_cols[:20]:
            try:
                contingency = pd.crosstab(df[col], df[target])
                if contingency.shape[0] < 2 or contingency.shape[1] < 2:
                    continue
                chi2, p, dof, expected = stats.chi2_contingency(contingency)
                n = contingency.sum().sum()
                r, c = contingency.shape
                v = float(np.sqrt(chi2 / (n * (min(r, c) - 1)))) if (n * (min(r, c) - 1)) > 0 else 0.0
                results.append({
                    "column": col,
                    "association_method": "cramers_v",
                    "statistic": round(v, 4),
                    "p_value": round(float(p), 6),
                })
            except Exception:
                continue

    # Sort by significance (p-value ascending, then statistic magnitude descending)
    results.sort(key=lambda x: (x["p_value"], -abs(x["statistic"])))
    return results[:max_features]


# ---------------------------------------------------------------------------
# Outlier summary
# ---------------------------------------------------------------------------

def compute_outlier_summary(df: pd.DataFrame, target: str = None) -> list[dict]:
    summary = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if target and target in numeric_cols:
        numeric_cols = [c for c in numeric_cols if c != target]

    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) < 10:
            continue
        q1 = float(series.quantile(0.25))
        q3 = float(series.quantile(0.75))
        iqr = q3 - q1
        if iqr == 0:
            continue
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outlier_mask = (series < lower) | (series > upper)
        n_outliers = int(outlier_mask.sum())
        pct_outliers = round(n_outliers / len(series), 4)

        if n_outliers == 0:
            continue

        skewness = float(series.skew())
        if pct_outliers > 0.05 and abs(skewness) > 2:
            disposition = "heavy_tailed_distribution — use robust methods or log transform"
        elif pct_outliers < 0.01:
            disposition = "likely_data_error — investigate individual values before modeling"
        elif pct_outliers < 0.03:
            disposition = "plausible_extremes — flag for winsorization in feature engineering"
        else:
            disposition = "moderate_outlier_rate — consider winsorization or robust scaler"

        summary.append({
            "column": col,
            "n_outliers": n_outliers,
            "pct_outliers": pct_outliers,
            "lower_fence": round(lower, 4),
            "upper_fence": round(upper, 4),
            "disposition": disposition,
        })

    # Sort by pct_outliers descending
    summary.sort(key=lambda x: x["pct_outliers"], reverse=True)
    return summary


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def run_eda(
    df: pd.DataFrame,
    target: str = None,
    task: str = "classification",
    output_path: str = "eda_findings.json",
) -> dict:
    """
    Run full EDA and produce findings dict.

    Parameters
    ----------
    df : pd.DataFrame
    target : str or None — target column name
    task : str — 'classification', 'regression', 'time_series', or 'clustering'
    output_path : str — path to write JSON output

    Returns
    -------
    dict — the findings structure
    """
    dataset_summary = build_dataset_summary(df)
    target_analysis = analyze_target(df, target, task) if target else {}
    recommended_transforms = find_recommended_transforms(df, target)
    feature_candidates = find_feature_candidates(df, target, task)
    drop_candidates = find_drop_candidates(df, target)
    top_features = compute_top_features(df, target, task)
    outlier_summary = compute_outlier_summary(df, target)
    modeling_notes = derive_modeling_notes(
        df, target, task,
        dataset_summary["shape_tags"],
        target_analysis,
        drop_candidates,
    )

    findings = {
        "schema_version": "1.0",
        "skill_name": "eda-comprehensive",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "row_count": len(df),
        "column_count": len(df.columns),
        "column_list": sorted(df.columns.tolist()),
        "input_file": None,  # set by CLI
        "task": task,
        "target_column": target,
        "dataset_summary": dataset_summary,
        "target_analysis": target_analysis,
        "recommended_transforms": recommended_transforms,
        "feature_candidates": feature_candidates,
        "drop_candidates": drop_candidates,
        "top_features": top_features,
        "outlier_summary": outlier_summary,
        "modeling_notes": modeling_notes,
    }

    with open(output_path, "w") as f:
        json.dump(findings, f, indent=2, default=str)

    print(f"EDA findings written to: {output_path}")
    print(f"  Rows: {dataset_summary['rows']:,}  Cols: {dataset_summary['cols']}")
    print(f"  Shape tags: {dataset_summary['shape_tags']}")
    print(f"  Drop candidates: {len(drop_candidates)}")
    print(f"  Recommended transforms: {len(recommended_transforms)}")
    print(f"  Top features identified: {len(top_features)}")
    print(f"  Columns with outliers: {len(outlier_summary)}")

    return findings


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Run comprehensive EDA and produce eda_findings.json"
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Path to input data file (.csv, .parquet, .xlsx)"
    )
    parser.add_argument(
        "--target", "-t", default=None,
        help="Target column name (omit for unsupervised/clustering)"
    )
    parser.add_argument(
        "--task", default="classification",
        choices=["classification", "regression", "time_series", "clustering"],
        help="Modeling task type"
    )
    parser.add_argument(
        "--output", "-o", default="eda_findings.json",
        help="Output path for JSON findings (default: eda_findings.json)"
    )
    parser.add_argument(
        "--sample", type=int, default=None,
        help="Randomly sample N rows for faster EDA on very large datasets"
    )

    args = parser.parse_args()

    print(f"Loading data from: {args.input}")
    df = load_data(args.input)

    if args.sample and args.sample < len(df):
        print(f"Sampling {args.sample:,} rows from {len(df):,} total rows")
        df = df.sample(n=args.sample, random_state=42).reset_index(drop=True)

    findings = run_eda(
        df=df,
        target=args.target,
        task=args.task,
        output_path=args.output,
    )
    findings["input_file"] = args.input

    # Re-write with input_file populated
    with open(args.output, "w") as f:
        json.dump(findings, f, indent=2, default=str)

    print("\nDone.")


if __name__ == "__main__":
    main()
