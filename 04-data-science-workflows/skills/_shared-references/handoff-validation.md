# Handoff Validation Pattern

Ensures artifact integrity between pipeline skills. Every skill validates upstream artifacts before processing and stamps its own output for downstream validation.

## Manifest Schema Contract

Every `*_manifest.json` must include these standard fields:

```python
{
    "schema_version": "1.0",
    "skill_name": "<skill-name>",
    "timestamp": "<ISO-8601>",
    "row_count": len(df),
    "column_count": len(df.columns),
    "column_list": sorted(df.columns.tolist()),
    # ... skill-specific fields
}
```

## Upstream Validation (Step 0 of every skill)

Before any processing, validate the upstream manifest:

```python
def validate_upstream(manifest_path, current_df, skill_name):
    """Validate that current DataFrame matches upstream manifest expectations.

    Returns (is_valid, warnings) tuple.
    """
    warnings = []

    if manifest_path is None or not Path(manifest_path).exists():
        warnings.append(f"No upstream manifest found at {manifest_path}. Proceeding without validation.")
        return True, warnings

    with open(manifest_path) as f:
        manifest = json.load(f)

    # Check schema version compatibility
    version = manifest.get("schema_version", "0.0")
    if version != "1.0":
        warnings.append(f"Upstream manifest schema version {version} differs from expected 1.0.")

    # Check row count
    expected_rows = manifest.get("row_count")
    if expected_rows is not None and len(current_df) != expected_rows:
        warnings.append(
            f"Row count mismatch: manifest says {expected_rows}, "
            f"DataFrame has {len(current_df)}. "
            f"Delta: {len(current_df) - expected_rows} rows."
        )

    # Check column set
    expected_cols = manifest.get("column_list")
    if expected_cols is not None:
        current_cols = sorted(current_df.columns.tolist())
        added = set(current_cols) - set(expected_cols)
        removed = set(expected_cols) - set(current_cols)
        if added:
            warnings.append(f"Columns added since upstream: {sorted(added)}")
        if removed:
            warnings.append(f"Columns removed since upstream: {sorted(removed)}")

    is_valid = all("mismatch" not in w.lower() for w in warnings)
    return is_valid, warnings
```

## Output Stamping

Every manifest generator must include the standard fields:

```python
def stamp_manifest(manifest_dict, df, skill_name):
    """Add standard handoff fields to any manifest dict."""
    manifest_dict["schema_version"] = "1.0"
    manifest_dict["skill_name"] = skill_name
    manifest_dict["row_count"] = len(df)
    manifest_dict["column_count"] = len(df.columns)
    manifest_dict["column_list"] = sorted(df.columns.tolist())
    return manifest_dict
```

## Validation Rules

| Upstream Skill | Downstream Skill | What to Validate |
|---|---|---|
| data-cleaning | data-quality-assurance | Row count matches manifest. All columns are snake_case. |
| data-quality-assurance | missing-data-imputation | QA verdict is not FAIL. Row/column counts match. |
| missing-data-imputation | eda-comprehensive | Zero nulls in imputed columns. Row count stable. |
| eda-comprehensive | feature-engineering | `eda_findings.json` exists. All referenced columns exist in DataFrame. |

## Sample Usage in SKILL.md

Add as Step 0 in every skill:

```
### Step 0: Validate Upstream Artifacts

IF upstream manifest exists:
  1. Load manifest JSON
  2. Compare schema_version (warn if mismatch)
  3. Compare row_count (warn if delta)
  4. Compare column_list (warn if added/removed)
  5. Log all warnings to current skill's manifest

IF validation fails with row count mismatch:
  → HALT with message: "DataFrame has been modified between skills.
     Expected {expected} rows, found {actual}. Investigate before proceeding."

IF no upstream manifest:
  → Proceed with warning: "No upstream validation available."
```
