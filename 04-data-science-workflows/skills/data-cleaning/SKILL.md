---
name: data-cleaning
description: Transform raw, messy data into a structurally consistent DataFrame with correct types, standardized names, and removed corruption. Use when loading a new dataset, starting any analysis or modeling project, after upstream data changes, when a pipeline ingestion completes, or when you see dtype mismatches, duplicate rows, or corrupted values. Handles CSV, Parquet, JSON, SQL, and Excel inputs across all data shapes.
---

Data cleaning is the foundation of every reliable analysis. Downstream decisions about imputation, feature engineering, and modeling all depend on a structurally sound DataFrame: consistent column names, correct dtypes, no accidental duplicates, and no encoding corruption. Skipping this step embeds invisible errors that compound at every stage. This skill walks through the full cleaning sequence — audit first, then load, then structural fixes — and produces a `cleaning_manifest.json` that documents every transformation for reproducibility.

---

## When to Activate

- Loading a dataset for the first time
- Starting any analysis or modeling project
- After upstream data changes or a pipeline ingestion completes
- When you see `object` dtype on columns that should be numeric or datetime
- When row counts seem wrong or duplicate keys appear
- When string values contain unexpected whitespace, encoding artifacts, or sentinel strings like `"N/A"`, `"#REF!"`, `"-999"`
- When merging datasets from different sources before combining

---

## Prerequisites

Required: `pandas>=1.5`, `numpy>=1.23`

Optional: `chardet` (encoding detection), `missingno` (null visualization), `openpyxl` (Excel), `sqlalchemy` (SQL), `dask` (large files)

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

### Step 1 — Run Dataset Audit

**Goal:** Understand what you have before touching anything. Surface all issues with severity labels.

**Reference:** `references/dataset-audit-pattern.md`

**Actions:** Run all five audit dimensions — completeness, consistency, accuracy, timeliness, relevance — and synthesize into a single report.

```python
import pandas as pd
import numpy as np

# Paste audit functions from references/dataset-audit-pattern.md, then:

# Quick preview before loading full data
df_sample = pd.read_csv("data.csv", nrows=1000)
print(df_sample.shape)
print(df_sample.dtypes)
print(df_sample.isnull().mean().sort_values(ascending=False).head(20))

# Run audit on sample (or full df if small enough)
completeness = audit_completeness(df_sample)
consistency = audit_consistency(df_sample)

accuracy_notes = []   # Fill in after domain review
timeliness_notes = []
relevance_notes = []

report = synthesize_audit(completeness, consistency, accuracy_notes, timeliness_notes, relevance_notes)
print(report['overall_health'], "—", report['critical_issues'], "critical issues")
for issue in report['all_issues']:
    print(f"  [{issue['severity'].upper()}] {issue}")
```

**Checkpoint:** If `overall_health == 'poor'` or `critical_issues > 0`, investigate before proceeding. Do not clean data you do not understand.

**Document:** Save `report` to a variable; it feeds the manifest at the end.

---

### Step 2 — Classify Data Shape

**Goal:** Choose the right loading and cleaning strategy based on dataset dimensions.

**Reference:** `references/shape-aware-strategy.md`

**Actions:** Run `classify_shape()` on the sample to get shape tags, then select the appropriate strategy branch.

```python
# Paste classify_shape() from references/shape-aware-strategy.md, then:

shape_info = classify_shape(df_sample)
print(shape_info)
# e.g. {'tags': ['wide', 'sparse'], 'rows': 850000, 'cols': 220, ...}

# Strategy selection
if 'tall' in shape_info['tags']:
    LOAD_STRATEGY = 'chunked'
elif 'nested' in shape_info['tags']:
    LOAD_STRATEGY = 'json_normalize'
else:
    LOAD_STRATEGY = 'standard'

if 'wide' in shape_info['tags']:
    print("Wide dataset: batch column normalization required")
if 'sparse' in shape_info['tags']:
    print("Sparse dataset: flag sparse columns early, separate pipelines")
if 'time_series' in shape_info['tags']:
    print("Time-series: sort by timestamp, validate frequency, deduplicate on timestamp+entity")
```

**Checkpoint:** Shape tags are set and `LOAD_STRATEGY` is chosen before loading the full file.

**Document:** Store `shape_info` for the manifest.

---

### Step 3 — Load Data

**Goal:** Get a complete DataFrame into memory (or a chunked iterator) using the correct loader for the source format.

**Decision point — branch on file type and size:**

**IF CSV < 500 MB:**
```python
df = pd.read_csv(
    "data.csv",
    dtype=str,           # Load everything as string first; cast later in Step 6
    keep_default_na=False,
    na_values=["", "NA", "N/A", "null", "NULL", "None", "nan", "-999", "9999", "#REF!"],
    low_memory=False,
)
original_shape = df.shape
```

**IF CSV > 500 MB:**
```python
# Chunked pandas (or use dask: dd.read_csv("data.csv", dtype=str))
chunks = []
for chunk in pd.read_csv("data.csv", chunksize=100_000, dtype=str,
                          keep_default_na=False, na_values=["", "NA", "N/A", "null", "NULL"]):
    chunks.append(chunk)
df = pd.concat(chunks, ignore_index=True)
original_shape = df.shape
```

> **At scale (large/very_large):** Replace chunked pandas concat with `dask.dataframe.read_csv(path, dtype=str, blocksize="64MB")`. Process partitions lazily.

**IF JSON with nesting:**
```python
import json
with open("data.json") as f:
    raw = json.load(f)
df = pd.json_normalize(raw, max_level=2)  # adjust max_level based on audit
original_shape = df.shape
```

**IF SQL:**
```python
from sqlalchemy import create_engine
engine = create_engine("postgresql://user:pass@host/dbname")
df = pd.read_sql("SELECT * FROM schema.table WHERE updated_at >= '2024-01-01'", con=engine)
original_shape = df.shape
engine.dispose()
```

**IF Excel with multiple sheets:**
```python
xl = pd.ExcelFile("data.xlsx")
sheets = {name: xl.parse(name, dtype=str) for name in xl.sheet_names}
# Merge if same schema/entity; keep separate otherwise
df = pd.concat(sheets.values(), ignore_index=True)
original_shape = df.shape
```

**IF Parquet:**
```python
df = pd.read_parquet("data.parquet")
original_shape = df.shape
```

**Checkpoint:** `df.shape` matches expected row/column counts from audit. No silent truncation.

> **CHECKPOINT — Step 3**
> - [ ] Assert: `df.shape[0] > 0` and `df.shape[1] > 0`
> - [ ] Assert: No silent truncation — row count matches expected (if known from audit)
> - [ ] PASS: DataFrame is loaded with at least 1 row and 1 column
> - [ ] On FAIL: HALT — "Empty dataset detected. Verify file path and format."

---

### Step 4 — Standardize Column Names

**Goal:** Produce clean, unique, snake_case column names with no spaces, special characters, or numeric prefixes.

```python
import re

def normalize_column_names(df):
    """
    Normalize column names to snake_case.
    Returns (cleaned_df, rename_map) where rename_map is {original: normalized}.
    """
    rename_map = {}
    seen = {}

    for col in df.columns:
        new = str(col).strip()

        # Replace special characters and spaces with underscores
        new = re.sub(r'[^\w\s]', '_', new)
        new = re.sub(r'\s+', '_', new)
        new = re.sub(r'_+', '_', new)

        # Lowercase
        new = new.lower().strip('_')

        # Strip leading numeric prefix (e.g. "1_revenue" -> "col_1_revenue")
        if new and new[0].isdigit():
            new = 'col_' + new

        # Empty name fallback
        if not new:
            new = 'unnamed'

        # Deduplicate: if name already seen, append a counter
        base = new
        count = seen.get(base, 0)
        if count > 0:
            new = f"{base}_{count}"
        seen[base] = count + 1

        rename_map[col] = new

    df = df.rename(columns=rename_map)
    return df, rename_map

df, columns_renamed = normalize_column_names(df)
print(f"Renamed {sum(1 for k, v in columns_renamed.items() if k != v)} columns")
```

**Checkpoint:** `df.columns.tolist()` contains only lowercase snake_case names. No duplicates. Run `df.columns[df.columns.duplicated()]` — must be empty.

> **CHECKPOINT — Step 4**
> - [ ] Assert: `df.columns.duplicated().sum() == 0`
> - [ ] Assert: All column names match `^[a-z][a-z0-9_]*$`
> - [ ] PASS: All columns are unique, lowercase snake_case
> - [ ] On FAIL: Re-run normalization on failing columns. If still failing, append `_dedup_N` suffix.

**Document:** Store `columns_renamed` for the manifest.

---

### Step 5 — Remove Duplicates

**Goal:** Remove unintended duplicate records without destroying valid repeated measurements.

**Run Assumption Audit before proceeding** (see `references/assumption-audit-pattern.md`):
- Identical rows are errors, not valid repeated measurements
- If this is a fact table with valid repeated transactions, do NOT deduplicate on all columns
- Check: `df.duplicated().sum() / len(df)` — if > 5%, investigate upstream joins first

**Decision point — branch on key availability:**

**IF natural key exists** (e.g., `customer_id`, `order_id`):
```python
key_cols = ['order_id']   # adjust to your dataset
before = len(df)
df = df.sort_values('updated_at', ascending=True).drop_duplicates(subset=key_cols, keep='last')
rows_removed_dedup = before - len(df)
print(f"Removed {rows_removed_dedup} duplicate rows on key {key_cols}")
```

**IF no natural key** (deduplicate on all columns):
```python
before = len(df)
df = df.drop_duplicates(keep='first')
rows_removed_dedup = before - len(df)
print(f"Removed {rows_removed_dedup} fully duplicate rows")
```

**IF time-series** (deduplicate on timestamp + entity):
```python
ts_key = ['entity_id', 'timestamp']   # adjust to your dataset
before = len(df)
df = df.sort_values('timestamp').drop_duplicates(subset=ts_key, keep='last')
rows_removed_dedup = before - len(df)
print(f"Removed {rows_removed_dedup} duplicate timestamp+entity rows")
```

**IF valid repeated measurements** (e.g., sensor readings, A/B test events):
```python
# Do NOT remove duplicates. Document this explicitly.
rows_removed_dedup = 0
print("No deduplication: repeated measurements are valid by design")
```

**Checkpoint:** `df.duplicated(subset=key_cols).sum() == 0` (or `df.duplicated().sum() == 0` if no key). Document your choice.

> **At scale (large/very_large):** Full `.drop_duplicates()` on all columns is O(n). For very_large datasets, deduplicate within partitions first, then cross-partition on key columns only.

**Document:** Store `rows_removed_dedup` for the manifest.

---

### Step 6 — Fix Dtype Mismatches

**Goal:** Assign every column its correct pandas dtype, eliminating silent `object` columns that are actually numeric, datetime, boolean, or categorical.

**Reference:** `references/dtype-router.md` for bucket classification, `references/assumption-audit-pattern.md` before casting.

**Run Assumption Audit before proceeding** (see `references/assumption-audit-pattern.md`):
- Object columns >80% parseable as numeric should be cast — but verify first with `df[col].value_counts().head(20)`
- Zip codes and phone numbers that look numeric must NOT be cast (leading zeros lost)
- Float columns with all whole values are discrete integers — confirm before casting to `Int64`

> **Plain language:** If more than 80% of values in a column look like numbers, we convert the whole column to numeric. The remaining 20% become null values (which imputation will handle later). This threshold is a practical default — if your domain requires stricter handling, adjust it.

```python
# Paste classify_columns() from references/dtype-router.md, then:

dtype_changes = {}

# --- Numeric coercion for object columns ---
for col in df.select_dtypes(include=['object']).columns:
    sample = df[col].dropna().head(500)
    numeric_frac = pd.to_numeric(sample, errors='coerce').notna().mean()

    if numeric_frac > 0.80:
        old_dtype = str(df[col].dtype)
        df[col] = pd.to_numeric(df[col], errors='coerce')
        dtype_changes[col] = {'from': old_dtype, 'to': str(df[col].dtype)}
        print(f"  Cast {col}: object -> {df[col].dtype}")

# --- Datetime coercion for object columns ---
date_patterns = [
    r'\d{4}-\d{2}-\d{2}',           # ISO 8601
    r'\d{2}/\d{2}/\d{4}',           # US format
    r'\d{4}\d{2}\d{2}',             # compact
]
for col in df.select_dtypes(include=['object']).columns:
    sample_str = df[col].dropna().astype(str).head(100)
    is_date = any(sample_str.str.match(pat).mean() > 0.80 for pat in date_patterns)
    if is_date:
        old_dtype = str(df[col].dtype)
        df[col] = pd.to_datetime(df[col], errors='coerce', infer_datetime_format=True)
        dtype_changes[col] = {'from': old_dtype, 'to': str(df[col].dtype)}
        print(f"  Cast {col}: object -> datetime")

# --- Float -> Int64 for whole-number floats ---
for col in df.select_dtypes(include=['float64']).columns:
    non_null = df[col].dropna()
    if len(non_null) > 0 and (non_null % 1 == 0).all():
        old_dtype = str(df[col].dtype)
        df[col] = df[col].astype('Int64')   # nullable integer
        dtype_changes[col] = {'from': old_dtype, 'to': 'Int64'}
        print(f"  Cast {col}: float64 -> Int64 (whole-number floats)")

# --- Numeric IDs / zip codes -> string ---
# Identify likely ID columns (high cardinality integers with no arithmetic meaning)
id_patterns = ['_id', '_zip', '_code', '_phone', 'postal']
for col in df.select_dtypes(include=['number']).columns:
    if any(pat in col for pat in id_patterns):
        old_dtype = str(df[col].dtype)
        df[col] = df[col].astype('string')
        dtype_changes[col] = {'from': old_dtype, 'to': 'string'}
        print(f"  Cast {col}: {old_dtype} -> string (ID/zip column)")

# --- Boolean-like object columns -> bool ---
bool_map = {
    'true': True, 'false': False,
    'yes': True, 'no': False,
    '1': True, '0': False,
    'y': True, 'n': False,
}
for col in df.select_dtypes(include=['object']).columns:
    unique_lower = set(df[col].dropna().astype(str).str.lower().unique())
    if unique_lower <= set(bool_map.keys()):
        old_dtype = str(df[col].dtype)
        df[col] = df[col].astype(str).str.lower().map(bool_map)
        dtype_changes[col] = {'from': old_dtype, 'to': 'bool'}
        print(f"  Cast {col}: object -> bool")

print(f"\nTotal dtype changes: {len(dtype_changes)}")
```

**Checkpoint:** `df.select_dtypes(include=['object']).columns.tolist()` should contain only genuinely string/text columns. Verify with `df.dtypes.value_counts()`.

> **CHECKPOINT — Step 6**
> - [ ] Assert: No remaining object columns that should be numeric (per 80% coercion rule)
> - [ ] Assert: ID/code columns preserved as string (not coerced to numeric)
> - [ ] PASS: All dtype assignments are intentional and documented
> - [ ] On FAIL: Log unresolved columns to `cleaning_manifest.json` as `unresolved_dtypes`. Proceed with warning.

**Document:** Store `dtype_changes` for the manifest.

---

### Step 7 — Fix Structural Corruption

**Goal:** Catch and repair low-level data corruption — bad encodings, delimiter misdetections, embedded whitespace, and sentinel strings — that survives the earlier steps.

```python
import re

encoding_fixes = []
sentinel_values = [
    'N/A', 'NA', 'n/a', 'na', 'NULL', 'null', 'None', 'none',
    'NaN', 'nan', '-', '--', '?', '#REF!', '#N/A', '#VALUE!',
    '-999', '-9999', '9999', '99999', 'missing', 'MISSING',
]

for col in df.select_dtypes(include=['object', 'string']).columns:
    # Strip whitespace, normalize empty strings to NaN
    before_nulls = df[col].isnull().sum()
    df[col] = df[col].str.strip().replace('', pd.NA)
    after_nulls = df[col].isnull().sum()
    if after_nulls != before_nulls:
        encoding_fixes.append(f"{col}: {after_nulls - before_nulls} empty strings -> NaN")

    # Replace sentinel strings with NaN
    mask = df[col].isin(sentinel_values)
    if mask.sum() > 0:
        df.loc[mask, col] = pd.NA
        encoding_fixes.append(f"{col}: {mask.sum()} sentinel values -> NaN")

    # Collapse internal whitespace
    df[col] = df[col].apply(
        lambda x: re.sub(r'\s+', ' ', x).strip() if isinstance(x, str) else x
    )

# Encoding repair (requires chardet)
try:
    import chardet
    def fix_encoding(s):
        if not isinstance(s, str):
            return s
        try:
            raw = s.encode('latin-1')
            detected = chardet.detect(raw)
            if detected['encoding'] and detected['encoding'].lower() not in ('ascii', 'utf-8'):
                return raw.decode(detected['encoding'], errors='replace')
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
        return s
    for col in df.select_dtypes(include=['object']).columns:
        if df[col].dropna().head(100).apply(lambda x: any(ord(c) > 127 for c in str(x))).any():
            df[col] = df[col].apply(fix_encoding)
            encoding_fixes.append(f"{col}: encoding normalization applied")
except ImportError:
    print("chardet not installed — skipping encoding detection")

print(f"Structural fixes: {len(encoding_fixes)}")
for fix in encoding_fixes:
    print(f"  {fix}")
```

> **At scale (large/very_large):** Replace `.apply(lambda x: ...)` with vectorized `.str.replace()` and `.str.strip()`. Vectorized string ops are 10-100× faster.

**Checkpoint:**
- `df.select_dtypes(include=['object']).apply(lambda c: c.str.strip().eq(c).all()).all()` should be True (no leading/trailing whitespace remains)
- Sentinel strings no longer appear in value counts

> **CHECKPOINT — Step 7**
> - [ ] Assert: Zero sentinel strings remain (`N/A`, `#REF!`, `-999`, etc.)
> - [ ] Assert: No leading/trailing whitespace in string columns
> - [ ] PASS: All structural corruption resolved
> - [ ] On FAIL: List remaining sentinels. HALT if >5% of values affected; otherwise proceed with warning.

**Document:** Store `encoding_fixes` for the manifest.

---

## Generate Manifest

Run `scripts/generate_cleaning_manifest.py` to produce a permanent audit trail:

```python
import sys
sys.path.insert(0, 'skills/data-cleaning/scripts')
from generate_cleaning_manifest import generate_manifest

columns_dropped = [col for col in original_columns if col not in df.columns]
manifest = generate_manifest(
    original_shape=list(original_shape),
    final_shape=list(df.shape),
    columns_renamed=columns_renamed,
    columns_dropped=columns_dropped,
    rows_removed=original_shape[0] - len(df),
    dtype_changes=dtype_changes,
    encoding_fixes=encoding_fixes,
    output_path="cleaning_manifest.json",
)
```

CLI equivalent:
```bash
python skills/data-cleaning/scripts/generate_cleaning_manifest.py \
  --original-shape 50000 42 --final-shape 49800 40 --rows-removed 200
```

---

## Edge Case Handling

| Edge Case | Detection | Action |
|---|---|---|
| **Empty file (0 rows)** | `df.shape[0] == 0` after loading | HALT — "Empty dataset. Verify file path, format, and permissions." |
| **Single-row file** | `df.shape[0] == 1` | WARN — "Single-row dataset. Deduplication and statistical checks are trivial. Proceed with caution." |
| **Zero columns after loading** | `df.shape[1] == 0` | HALT — "No columns detected. Check file delimiter and format." |
| **100% null column** | `df[col].isnull().all()` | Flag in manifest as `fully_null_columns`. Do NOT drop — pass to imputation for explicit keep/drop decision. |
| **Mixed-type column** | Object column with 40-60% numeric values | Log as `mixed_type_columns` in manifest. Attempt coercion if >80% parseable; otherwise preserve as object with warning. |
| **All-duplicate rows** | `df.duplicated().all()` after first row | WARN — "All rows are identical. Verify this is not a data loading error." Proceed after confirmation. |
| **Very long column names (>100 chars)** | `max(len(c) for c in df.columns) > 100` | Truncate to 100 chars, append hash suffix for uniqueness. Log original→truncated mapping. |
| **Unicode normalization** | Columns with combining characters (é vs e+´) | Apply `unicodedata.normalize('NFC', col)` during name standardization. |
| **Dataset > available RAM** | `classify_scale()` returns `"very_large"` | Switch to Dask/Polars loading. See Scale Classification section. |
| **Binary/image columns** | Object column with bytes-like content | Flag as `unsupported_dtype`. Exclude from cleaning operations. |

---

## Quality Bar

A cleaned DataFrame is "done" when ALL of the following are true:

- [ ] `df.dtypes` contains no unexpected `object` columns (all have been reviewed and intentionally left as string, or cast)
- [ ] `df.duplicated().sum() == 0` (or deduplication was intentionally skipped and documented)
- [ ] `df.columns.tolist()` contains only valid snake_case names, no spaces, no special characters
- [ ] `df.isnull().mean().max()` is understood — every column with nulls has an explanation
- [ ] No sentinel strings (`-999`, `N/A`, `#REF!`) remain in any string column
- [ ] `cleaning_manifest.json` exists and validates (original rows == final rows + rows_removed)
- [ ] Shape tags from Step 2 are documented and shape-specific handling was applied

---

## Scope Boundary

This skill does NOT:
- Impute missing values (see `missing-data-imputation` skill)
- Detect statistical outliers or apply outlier treatment (see `data-quality-assurance` skill)
- Engineer features, encode categoricals for modeling, or scale numeric columns
- Validate business logic or domain-specific constraints (e.g., "revenue must be positive")
- Handle schema migration or multi-source dataset alignment beyond basic column naming

If a column has high null rates after cleaning, stop — do not impute here. Pass the cleaned DataFrame to the imputation skill.

---

## Downstream Skills

Run in this order after cleaning completes:

1. **`data-quality-assurance`** — statistical validation, outlier detection, distribution checks, and schema contract enforcement. Run this before any analysis.
2. **`missing-data-imputation`** — once the DataFrame is structurally clean, use this skill to decide on and apply an imputation strategy for each column based on missingness mechanism (MCAR/MAR/MNAR).
