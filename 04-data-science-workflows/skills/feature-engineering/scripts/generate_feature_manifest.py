"""
generate_feature_manifest.py
----------------------------
Produce a feature_manifest.json documenting all features created, selected,
and dropped during a feature engineering run, along with validation results
and leakage guard status.

Usage (as a function):
    from generate_feature_manifest import generate_manifest
    manifest = generate_manifest(
        task_type='classification',
        features=[{'name': 'age_log', 'source_columns': ['age'], ...}],
        featurewiz_metadata={...},
        dropped_features=[{'name': 'id', 'reason': 'identifier column'}],
        validation_results={'raw_score': 0.72, 'featurewiz_score': 0.81, ...},
        pipeline_path='output/feature_pipeline.joblib',
        leakage_guard_passed=True,
        output_path='feature_manifest.json',
    )

Usage (CLI):
    python generate_feature_manifest.py \
        --task-type classification \
        --features-in 42 \
        --features-out 18 \
        --raw-score 0.72 \
        --featurewiz-score 0.81 \
        --metric-name roc_auc \
        --leakage-guard-passed \
        --output feature_manifest.json
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------

def generate_manifest(
    task_type: str,
    features: list,
    featurewiz_metadata: Optional[dict],
    dropped_features: list,
    validation_results: dict,
    pipeline_path: Optional[str],
    leakage_guard_passed: bool,
    output_path: str = "feature_manifest.json",
    row_count: Optional[int] = None,
    column_count: Optional[int] = None,
    column_list: Optional[list] = None,
) -> dict:
    """
    Generate a feature manifest JSON file documenting all feature engineering decisions.

    Parameters
    ----------
    task_type : str
        One of: 'classification', 'regression', 'time-series', 'nlp', 'clustering'
    features : list of dict
        Each entry must have:
            name (str)                  — feature column name
            source_columns (list[str])  — original column(s) this was derived from
            transform_type (str)        — e.g. 'log1p', 'ordinal_encoding', 'tfidf', 'lag'
            creation_method (str)       — 'manual' or 'featurewiz'
            parameters (dict)           — transform parameters used (may be empty dict)
            importance_score (float)    — feature importance from LightGBM/XGBoost (0.0 if unknown)
        Optional keys:
            kept_by_featurewiz (bool)   — True if featurewiz retained this feature
    featurewiz_metadata : dict or None
        If featurewiz was used:
            corr_limit (float)
            feature_engg (str)
            features_in (int)
            features_out (int)
            sulov_eliminated (list[str])  — features removed by SULOV (may be empty list)
            mrmr_ranking (list[str])      — features ranked by MRMR importance (may be empty list)
        Pass None if featurewiz was not used.
    dropped_features : list of dict
        Each entry must have:
            name (str)    — feature column name
            reason (str)  — why it was dropped
    validation_results : dict
        Keys:
            raw_score (float or None)         — score on raw/baseline features
            featurewiz_score (float or None)  — score on featurewiz-selected features
            combined_score (float or None)    — score combining manual + featurewiz
            metric_name (str)                 — e.g. 'roc_auc', 'rmse', 'skipped'
    pipeline_path : str or None
        Path to serialized sklearn Pipeline (joblib). None if not produced.
    leakage_guard_passed : bool
        True if all leakage guard checks passed.
    output_path : str
        File path to write the manifest JSON.

    Returns
    -------
    dict
        The manifest dictionary (also written to output_path).
    """
    # Validate task_type
    valid_task_types = ('classification', 'regression', 'time-series', 'nlp', 'clustering')
    if task_type not in valid_task_types:
        raise ValueError(f"task_type must be one of {valid_task_types}, got '{task_type}'")

    # Normalize each feature entry to ensure required keys are present
    normalized_features = []
    for i, feat in enumerate(features):
        if not isinstance(feat, dict):
            raise TypeError(f"features[{i}] must be a dict, got {type(feat).__name__}")
        normalized_features.append({
            "name": feat.get("name", f"unknown_feature_{i}"),
            "source_columns": feat.get("source_columns", feat.get("source", [feat.get("name", "")])) if isinstance(feat.get("source_columns", feat.get("source")), list) else [feat.get("source_columns", feat.get("source", feat.get("name", "")))],
            "transform_type": feat.get("transform_type", feat.get("transform", "unknown")),
            "creation_method": feat.get("creation_method", feat.get("method", "manual")),
            "parameters": feat.get("parameters", {}),
            "importance_score": feat.get("importance_score", 0.0),
            "kept_by_featurewiz": feat.get("kept_by_featurewiz", None),
        })

    # Normalize dropped features
    normalized_dropped = []
    for feat in dropped_features:
        if isinstance(feat, dict):
            normalized_dropped.append({
                "name": feat.get("name", "unknown"),
                "reason": feat.get("reason", "not specified"),
            })
        elif isinstance(feat, str):
            normalized_dropped.append({"name": feat, "reason": "not specified"})

    # Normalize featurewiz metadata
    if featurewiz_metadata is not None:
        fw_meta = {
            "corr_limit": featurewiz_metadata.get("corr_limit", 0.7),
            "feature_engg": featurewiz_metadata.get("feature_engg", ""),
            "features_in": featurewiz_metadata.get("features_in", None),
            "features_out": featurewiz_metadata.get("features_out", None),
            "sulov_eliminated": featurewiz_metadata.get("sulov_eliminated", []),
            "mrmr_ranking": featurewiz_metadata.get("mrmr_ranking", featurewiz_metadata.get("selected_features", [])),
        }
    else:
        fw_meta = None

    # Normalize validation results
    norm_validation = {
        "raw_score": validation_results.get("raw_score"),
        "featurewiz_score": validation_results.get("featurewiz_score"),
        "combined_score": validation_results.get("combined_score"),
        "metric_name": validation_results.get("metric_name", "unknown"),
    }

    # Compute summary statistics
    manual_count = sum(1 for f in normalized_features if f["creation_method"] == "manual")
    featurewiz_count = sum(1 for f in normalized_features if f["creation_method"] == "featurewiz")
    high_importance = sorted(
        [f for f in normalized_features if f["importance_score"] > 0],
        key=lambda x: x["importance_score"],
        reverse=True,
    )[:10]

    manifest = {
        "schema_version": "1.0",
        "skill_name": "feature-engineering",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "row_count": row_count,
        "column_count": column_count,
        "column_list": column_list,
        "task_type": task_type,
        "summary": {
            "total_features": len(normalized_features),
            "manual_features": manual_count,
            "featurewiz_features": featurewiz_count,
            "dropped_features": len(normalized_dropped),
            "leakage_guard_passed": leakage_guard_passed,
        },
        "features": normalized_features,
        "top_features_by_importance": [
            {"name": f["name"], "importance_score": f["importance_score"]}
            for f in high_importance
        ],
        "featurewiz_metadata": fw_meta,
        "dropped_features": normalized_dropped,
        "validation_results": norm_validation,
        "pipeline_path": str(pipeline_path) if pipeline_path else None,
        "leakage_guard_passed": leakage_guard_passed,
    }

    # Write to file
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(manifest, f, indent=2, default=str)

    print(f"Feature manifest written to: {output_path}")
    print(f"  Task type:          {task_type}")
    print(f"  Total features:     {len(normalized_features)}")
    print(f"  Manual features:    {manual_count}")
    print(f"  featurewiz used:    {'yes' if fw_meta is not None else 'no'}")
    print(f"  Dropped features:   {len(normalized_dropped)}")
    print(f"  Leakage guard:      {'PASSED' if leakage_guard_passed else 'FAILED'}")

    if norm_validation["metric_name"] not in ("unknown", "skipped"):
        print(f"\n  Validation ({norm_validation['metric_name']}):")
        if norm_validation["raw_score"] is not None:
            print(f"    Raw baseline:       {norm_validation['raw_score']:.4f}")
        if norm_validation["featurewiz_score"] is not None:
            print(f"    featurewiz-selected:{norm_validation['featurewiz_score']:.4f}")
        if norm_validation["combined_score"] is not None:
            print(f"    Combined:           {norm_validation['combined_score']:.4f}")

    return manifest


# ---------------------------------------------------------------------------
# CLI interface
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a feature_manifest.json for a feature engineering run.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Minimal run — classification, no scores available yet
  python generate_feature_manifest.py \\
    --task-type classification \\
    --leakage-guard-passed \\
    --output feature_manifest.json

  # With validation scores
  python generate_feature_manifest.py \\
    --task-type regression \\
    --features-in 42 \\
    --features-out 18 \\
    --raw-score 245.3 \\
    --featurewiz-score 198.1 \\
    --metric-name rmse \\
    --leakage-guard-passed \\
    --pipeline-path output/feature_pipeline.joblib \\
    --output feature_manifest.json
""",
    )
    parser.add_argument(
        "--task-type",
        required=True,
        choices=["classification", "regression", "time-series", "nlp", "clustering"],
        help="Supervised learning task type.",
    )
    parser.add_argument(
        "--features-in",
        type=int,
        default=None,
        help="Number of input features before selection.",
    )
    parser.add_argument(
        "--features-out",
        type=int,
        default=None,
        help="Number of features after selection.",
    )
    parser.add_argument(
        "--corr-limit",
        type=float,
        default=None,
        help="featurewiz corr_limit used. Omit if featurewiz was not used.",
    )
    parser.add_argument(
        "--raw-score",
        type=float,
        default=None,
        help="Validation score on raw/baseline features.",
    )
    parser.add_argument(
        "--featurewiz-score",
        type=float,
        default=None,
        help="Validation score on featurewiz-selected features.",
    )
    parser.add_argument(
        "--combined-score",
        type=float,
        default=None,
        help="Validation score combining manual + featurewiz features.",
    )
    parser.add_argument(
        "--metric-name",
        type=str,
        default="unknown",
        help="Name of the evaluation metric (e.g. roc_auc, rmse).",
    )
    parser.add_argument(
        "--pipeline-path",
        type=str,
        default=None,
        help="Path to a serialized sklearn Pipeline (joblib).",
    )
    parser.add_argument(
        "--leakage-guard-passed",
        action="store_true",
        default=False,
        help="Pass this flag if all leakage guard checks passed.",
    )
    parser.add_argument(
        "--features-json",
        type=str,
        default=None,
        help="Path to a JSON file with the full features list (list of dicts).",
    )
    parser.add_argument(
        "--dropped-json",
        type=str,
        default=None,
        help="Path to a JSON file with the dropped features list (list of dicts).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="feature_manifest.json",
        help="Output path for the manifest JSON file. Default: feature_manifest.json",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    # Load features list from file if provided, otherwise build minimal placeholder
    if args.features_json:
        with open(args.features_json) as f:
            features = json.load(f)
    else:
        # Build a placeholder feature list from --features-out count
        if args.features_out:
            features = [
                {
                    "name": f"feature_{i}",
                    "source_columns": [f"feature_{i}"],
                    "transform_type": "unknown",
                    "creation_method": "unknown",
                    "parameters": {},
                    "importance_score": 0.0,
                }
                for i in range(args.features_out)
            ]
        else:
            features = []

    # Build featurewiz metadata if corr_limit or features_in is provided
    if args.corr_limit is not None or args.features_in is not None:
        featurewiz_metadata = {
            "corr_limit": args.corr_limit,
            "feature_engg": "",
            "features_in": args.features_in,
            "features_out": args.features_out,
            "sulov_eliminated": [],
            "mrmr_ranking": [],
        }
    else:
        featurewiz_metadata = None

    # Load dropped features if provided
    if args.dropped_json:
        with open(args.dropped_json) as f:
            dropped_features = json.load(f)
    else:
        dropped_features = []

    validation_results = {
        "raw_score": args.raw_score,
        "featurewiz_score": args.featurewiz_score,
        "combined_score": args.combined_score,
        "metric_name": args.metric_name,
    }

    generate_manifest(
        task_type=args.task_type,
        features=features,
        featurewiz_metadata=featurewiz_metadata,
        dropped_features=dropped_features,
        validation_results=validation_results,
        pipeline_path=args.pipeline_path,
        leakage_guard_passed=args.leakage_guard_passed,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
