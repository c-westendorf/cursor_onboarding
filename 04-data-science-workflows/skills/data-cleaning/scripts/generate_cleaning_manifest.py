"""
generate_cleaning_manifest.py

Produce a cleaning_manifest.json that documents every transformation applied
during data cleaning. Can be used as a CLI tool or imported as a module.

Usage (CLI):
    python generate_cleaning_manifest.py --help
    python generate_cleaning_manifest.py \\
        --original-shape 50000 42 \\
        --final-shape 49800 40 \\
        --rows-removed 200 \\
        --output cleaning_manifest.json

Usage (import):
    from generate_cleaning_manifest import generate_manifest

    manifest = generate_manifest(
        original_shape=[50000, 42],
        final_shape=[49800, 40],
        columns_renamed={"First Name": "first_name", "DOB": "date_of_birth"},
        columns_dropped=["unnamed_col", "debug_flag"],
        rows_removed=200,
        dtype_changes={"age": {"from": "object", "to": "Int64"}},
        encoding_fixes=["notes: 12 sentinel values -> NaN"],
        output_path="cleaning_manifest.json",
    )
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Core function — importable
# ---------------------------------------------------------------------------

def generate_manifest(
    original_shape: list[int],
    final_shape: list[int],
    columns_renamed: dict[str, str] | None = None,
    columns_dropped: list[str] | None = None,
    rows_removed: int | None = None,
    dtype_changes: dict[str, dict[str, str]] | None = None,
    encoding_fixes: list[str] | None = None,
    output_path: str | Path = "cleaning_manifest.json",
    validate: bool = True,
) -> dict[str, Any]:
    """
    Generate a cleaning manifest and write it to output_path as JSON.

    Parameters
    ----------
    original_shape : [rows, cols]
        Shape of the DataFrame before any cleaning steps.
    final_shape : [rows, cols]
        Shape of the DataFrame after all cleaning steps.
    columns_renamed : dict, optional
        Mapping of {original_name: new_name} for every renamed column.
        Columns whose names did not change should still be included with
        identical keys and values so the full rename history is captured.
        Columns that were dropped should appear in columns_dropped, not here.
    columns_dropped : list, optional
        Column names that existed in the original DataFrame but were removed.
    rows_removed : int, optional
        Total number of rows removed during cleaning. If None, inferred from
        original_shape[0] - final_shape[0]. Must satisfy:
            original_rows == final_rows + rows_removed
    dtype_changes : dict, optional
        Mapping of {column_name: {"from": old_dtype, "to": new_dtype}} for
        every column whose dtype was changed.
    encoding_fixes : list, optional
        Human-readable descriptions of encoding or structural corruption fixes
        that were applied (e.g., ["notes: 12 sentinel values -> NaN"]).
    output_path : str or Path
        Where to write the manifest JSON file.
    validate : bool
        If True, raise ValueError if the row accounting does not balance.

    Returns
    -------
    dict
        The manifest as a Python dictionary (same content as the JSON file).

    Raises
    ------
    ValueError
        If validate=True and original_rows != final_rows + rows_removed.
    TypeError
        If original_shape or final_shape are not two-element lists/tuples.
    """
    # --- Input validation ---------------------------------------------------
    if len(original_shape) != 2:
        raise TypeError(f"original_shape must be [rows, cols], got {original_shape}")
    if len(final_shape) != 2:
        raise TypeError(f"final_shape must be [rows, cols], got {final_shape}")

    original_rows, original_cols = int(original_shape[0]), int(original_shape[1])
    final_rows, final_cols = int(final_shape[0]), int(final_shape[1])

    # Infer rows_removed if not explicitly provided
    if rows_removed is None:
        rows_removed = original_rows - final_rows

    rows_removed = int(rows_removed)

    # Row accounting check
    expected_final = original_rows - rows_removed
    if validate and final_rows != expected_final:
        raise ValueError(
            f"Row accounting mismatch: original_rows ({original_rows}) != "
            f"final_rows ({final_rows}) + rows_removed ({rows_removed}). "
            f"Expected final_rows = {expected_final}. "
            f"Pass validate=False to suppress this check."
        )

    # --- Normalize optional fields -----------------------------------------
    columns_renamed = columns_renamed or {}
    # Filter to only columns where the name actually changed
    actual_renames = {k: v for k, v in columns_renamed.items() if k != v}

    columns_dropped = sorted(columns_dropped or [])
    dtype_changes = dtype_changes or {}
    encoding_fixes = encoding_fixes or []

    # --- Build manifest -----------------------------------------------------
    manifest: dict[str, Any] = {
        "schema_version": "1.0",
        "skill_name": "data-cleaning",
        "original_shape": [original_rows, original_cols],
        "final_shape": [final_rows, final_cols],
        "row_count": final_rows,
        "column_count": final_cols,
        "column_list": None,  # column names not available via shape-only API; use generate_manifest_from_dataframes for column_list
        "columns_renamed": actual_renames,
        "columns_dropped": columns_dropped,
        "rows_removed": rows_removed,
        "dtype_changes": dtype_changes,
        "encoding_fixes": encoding_fixes,
        "summary": {
            "columns_renamed_count": len(actual_renames),
            "columns_dropped_count": len(columns_dropped),
            "rows_removed_count": rows_removed,
            "dtype_changes_count": len(dtype_changes),
            "encoding_fixes_count": len(encoding_fixes),
            "row_reduction_pct": round(rows_removed / original_rows * 100, 2) if original_rows > 0 else 0.0,
            "col_reduction_pct": round((original_cols - final_cols) / original_cols * 100, 2) if original_cols > 0 else 0.0,
        },
        "validation": {
            "row_accounting_balanced": final_rows == (original_rows - rows_removed),
            "original_rows": original_rows,
            "final_rows": final_rows,
            "rows_accounted_for": rows_removed,
        },
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    }

    # --- Write to disk -------------------------------------------------------
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, default=str)

    print(f"Manifest written to: {output_path.resolve()}")
    print(f"  Original shape : {original_rows:,} rows x {original_cols:,} cols")
    print(f"  Final shape    : {final_rows:,} rows x {final_cols:,} cols")
    print(f"  Rows removed   : {rows_removed:,} ({manifest['summary']['row_reduction_pct']}%)")
    print(f"  Columns renamed: {len(actual_renames)}")
    print(f"  Columns dropped: {len(columns_dropped)}")
    print(f"  Dtype changes  : {len(dtype_changes)}")
    print(f"  Encoding fixes : {len(encoding_fixes)}")
    balanced = manifest["validation"]["row_accounting_balanced"]
    print(f"  Row accounting : {'BALANCED' if balanced else 'MISMATCH — check rows_removed'}")

    return manifest


# ---------------------------------------------------------------------------
# DataFrame-aware convenience wrapper
# ---------------------------------------------------------------------------

def generate_manifest_from_dataframes(
    df_before,
    df_after,
    columns_renamed: dict[str, str] | None = None,
    columns_dropped: list[str] | None = None,
    dtype_changes: dict[str, dict[str, str]] | None = None,
    encoding_fixes: list[str] | None = None,
    output_path: str | Path = "cleaning_manifest.json",
) -> dict[str, Any]:
    """
    Convenience wrapper that accepts pandas DataFrames directly and extracts
    shape information automatically.

    Parameters
    ----------
    df_before : pd.DataFrame
        The DataFrame as loaded, before any cleaning.
    df_after : pd.DataFrame
        The DataFrame after all cleaning steps are complete.

    All other parameters match generate_manifest().

    Returns
    -------
    dict
        The manifest dictionary.
    """
    # Infer dropped columns from column sets if not provided
    if columns_dropped is None:
        before_cols = set(df_before.columns.tolist())
        after_cols = set(df_after.columns.tolist())
        # Adjust for renames: after_cols after rename are new names, not originals
        renamed_new_names = set((columns_renamed or {}).values())
        columns_dropped = sorted(
            col for col in before_cols
            if col not in after_cols and col not in (columns_renamed or {})
        )

    manifest = generate_manifest(
        original_shape=list(df_before.shape),
        final_shape=list(df_after.shape),
        columns_renamed=columns_renamed,
        columns_dropped=columns_dropped,
        rows_removed=None,  # inferred from shapes
        dtype_changes=dtype_changes,
        encoding_fixes=encoding_fixes,
        output_path=output_path,
    )
    # Backfill column_list now that we have the DataFrame available
    manifest["column_list"] = sorted(df_after.columns.tolist())
    output_path_obj = Path(output_path)
    with open(output_path_obj, "w", encoding="utf-8") as f:
        import json as _json
        _json.dump(manifest, f, indent=2, default=str)
    return manifest


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="generate_cleaning_manifest",
        description=(
            "Generate a cleaning_manifest.json documenting transformations applied "
            "during data cleaning. Validates that row counts balance: "
            "original_rows == final_rows + rows_removed."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Minimal — infer rows_removed from shapes
  python generate_cleaning_manifest.py \\
      --original-shape 50000 42 \\
      --final-shape 49800 40

  # Full example with all fields
  python generate_cleaning_manifest.py \\
      --original-shape 50000 42 \\
      --final-shape 49800 40 \\
      --rows-removed 200 \\
      --columns-renamed '{"First Name": "first_name", "DOB": "date_of_birth"}' \\
      --columns-dropped unnamed_col debug_flag \\
      --dtype-changes '{"age": {"from": "object", "to": "Int64"}}' \\
      --encoding-fixes "notes: 12 sentinel values -> NaN" \\
      --output cleaning_manifest.json

  # Suppress row accounting validation (use with care)
  python generate_cleaning_manifest.py \\
      --original-shape 50000 42 \\
      --final-shape 49700 40 \\
      --rows-removed 200 \\
      --no-validate
        """,
    )

    parser.add_argument(
        "--original-shape",
        nargs=2,
        type=int,
        metavar=("ROWS", "COLS"),
        required=True,
        help="Shape of the DataFrame before cleaning: ROWS COLS",
    )
    parser.add_argument(
        "--final-shape",
        nargs=2,
        type=int,
        metavar=("ROWS", "COLS"),
        required=True,
        help="Shape of the DataFrame after cleaning: ROWS COLS",
    )
    parser.add_argument(
        "--rows-removed",
        type=int,
        default=None,
        help=(
            "Total rows removed during cleaning. "
            "If omitted, inferred as original_rows - final_rows."
        ),
    )
    parser.add_argument(
        "--columns-renamed",
        type=str,
        default=None,
        metavar="JSON",
        help='JSON object mapping original column names to new names. e.g. \'{"Old Name": "old_name"}\'',
    )
    parser.add_argument(
        "--columns-dropped",
        nargs="*",
        default=None,
        metavar="COL",
        help="Space-separated list of column names that were dropped.",
    )
    parser.add_argument(
        "--dtype-changes",
        type=str,
        default=None,
        metavar="JSON",
        help=(
            'JSON object mapping column names to {"from": old_type, "to": new_type}. '
            'e.g. \'{"age": {"from": "object", "to": "Int64"}}\''
        ),
    )
    parser.add_argument(
        "--encoding-fixes",
        nargs="*",
        default=None,
        metavar="FIX",
        help="Space-separated list of encoding fix descriptions (quote each one).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="cleaning_manifest.json",
        metavar="PATH",
        help="Output file path (default: cleaning_manifest.json)",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        default=False,
        help="Suppress row accounting validation. Use when rows_removed is an estimate.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Parse JSON arguments
    columns_renamed = None
    if args.columns_renamed:
        try:
            columns_renamed = json.loads(args.columns_renamed)
        except json.JSONDecodeError as e:
            print(f"ERROR: --columns-renamed is not valid JSON: {e}", file=sys.stderr)
            return 1

    dtype_changes = None
    if args.dtype_changes:
        try:
            dtype_changes = json.loads(args.dtype_changes)
        except json.JSONDecodeError as e:
            print(f"ERROR: --dtype-changes is not valid JSON: {e}", file=sys.stderr)
            return 1

    try:
        generate_manifest(
            original_shape=args.original_shape,
            final_shape=args.final_shape,
            columns_renamed=columns_renamed,
            columns_dropped=args.columns_dropped,
            rows_removed=args.rows_removed,
            dtype_changes=dtype_changes,
            encoding_fixes=args.encoding_fixes,
            output_path=args.output,
            validate=not args.no_validate,
        )
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("Pass --no-validate to suppress row accounting check.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
