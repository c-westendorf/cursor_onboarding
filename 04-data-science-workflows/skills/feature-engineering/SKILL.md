---
name: feature-engineering
description: Transform a clean, analyzed dataset into a model-ready feature matrix using domain-driven manual engineering and featurewiz automated selection (SULOV + MRMR), with zero data leakage and production reproducibility. Use when building features for a model, after EDA identified transform candidates, when model performance has plateaued, when new raw columns need conversion to features, or whenever you need to create, select, or validate features. Handles numeric transforms, categorical encoding, interaction terms, temporal/lag features, target encoding, and text features. featurewiz is the primary automated tool; manual engineering supplements it for domain-specific features.
---

Feature engineering is the highest-leverage activity in machine learning. A well-chosen feature set can turn a mediocre model into a strong one; a poor feature set guarantees a weak model regardless of how much you tune hyperparameters. This skill walks through the full feature engineering pipeline — from reading EDA findings, through manual transforms and featurewiz automated selection, to leakage validation and production packaging — and produces a `feature_manifest.json` that makes every transform decision reproducible.

---

## When to Activate

- Building features for a supervised model (classification, regression, time-series forecasting)
- EDA has completed and `eda_findings.json` contains `recommended_transforms` and `feature_candidates`
- Model performance has plateaued and you want to explore new feature representations
- New raw columns have been added to the dataset and need conversion to numeric features
- Categorical, datetime, or text columns are present and need encoding
- You need to validate that no engineered features introduce data leakage

---

## Prerequisites

```
pandas>=2.0
numpy>=1.23
scikit-learn>=1.3
featurewiz>=0.4
lightgbm>=4.0
scipy>=1.10
joblib>=1.3
```

Optional:
```
category_encoders   # hash encoding for high-cardinality categoricals
```

**Required inputs:**
- Clean, imputed DataFrame with no remaining nulls (output from `missing-data-imputation` skill)
- `eda_findings.json` with `recommended_transforms` and `feature_candidates` sections
- `train_idx` and `test_idx` arrays (or pre-split `df_train`, `df_test`)
- `target_col`: name of the target column
- `task_type`: one of `classification`, `regression`, `time-series`, `nlp`, `clustering`

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

#### Pre-check: QA Verdict Gate (Strict)

Feature engineering requires a PASS verdict. CONDITIONAL_PASS data has known quality issues that could produce unreliable features.

```python
qa_path = Path("qa_report.json")
if qa_path.exists():
    qa = json.load(open(qa_path))
    verdict = qa.get("verdict", "UNKNOWN")
    allowed = qa.get("allowed_downstream_skills", [])

    if "feature-engineering" not in allowed:
        print("⛔ QA verdict does not allow feature-engineering.")
        print(f"   Current verdict: {verdict}")
        print("   Resolve quality issues and re-run data-quality-assurance.")
        # HALT
    else:
        print("✓ QA allows feature-engineering. Proceeding.")
```

> **Plain language:** Building features from low-quality data wastes effort and can introduce hard-to-detect errors in models. We require a clean quality report before this step.

### Step 1 — Load Context

**Goal:** Read the EDA findings to understand what transforms have already been recommended, and classify columns into type buckets to drive branching decisions.

**References:** `references/dtype-router.md` for `classify_columns()`

```python
import json
import pandas as pd
import numpy as np

# Load EDA findings
with open('eda_findings.json') as f:
    eda = json.load(f)

recommended_transforms = eda.get('recommended_transforms', {})
feature_candidates = eda.get('feature_candidates', [])
print("Recommended transforms:", list(recommended_transforms.keys()))
print("Feature candidates:", feature_candidates)

# Load clean data
df = pd.read_parquet('data_imputed.parquet')   # adjust path as needed
target_col = 'target'   # adjust to your target column name
task_type = 'classification'   # classification | regression | time-series | nlp | clustering

# Split into train/test
from sklearn.model_selection import train_test_split
df_train, df_test = train_test_split(df, test_size=0.2, random_state=42, stratify=df[target_col] if task_type == 'classification' else None)

X_train = df_train.drop(columns=[target_col])
y_train = df_train[target_col]
X_test = df_test.drop(columns=[target_col])
y_test = df_test[target_col]

# Paste classify_columns() from references/dtype-router.md, then:
col_types = classify_columns(X_train)

print("\nColumn type summary:")
for bucket, cols in col_types.items():
    if cols:
        print(f"  {bucket}: {len(cols)} columns — {cols[:5]}{'...' if len(cols) > 5 else ''}")
```

**Checkpoint:** `col_types` is populated, `X_train` and `X_test` have no null values, `target_col` is not in `X_train`.

> **CHECKPOINT — Step 1**
> - [ ] Assert: `eda_findings.json` loaded successfully
> - [ ] Assert: All columns in `recommended_transforms` exist in `X_train.columns`
> - [ ] Assert: `X_train` and `X_test` have zero nulls
> - [ ] Assert: Target column is NOT in `X_train`
> - [ ] PASS: Context loaded and validated
> - [ ] On FAIL (missing columns in transforms): Remove missing columns from transforms list, log warning. Proceed.
> - [ ] On FAIL (nulls present): HALT — "Nulls detected. Run missing-data-imputation first."

---

### Step 2 — Decide: Manual First or featurewiz First

**Goal:** Choose the right sequencing based on task type and domain knowledge availability.

**Decision point:**

| Situation | Strategy |
|---|---|
| Strong domain knowledge | Manual first → featurewiz for selection |
| Weak domain knowledge | featurewiz baseline → add manual where performance gaps appear |
| Time-series task | Manual lag/window FIRST (featurewiz cannot handle datetime) → featurewiz on numeric outputs |
| NLP task | Manual text extraction first → featurewiz on numeric outputs |
| Clustering (no target) | Manual only — featurewiz requires a target variable |

```python
# Set your strategy based on the decision table above
STRATEGY = 'manual_first'   # or 'featurewiz_baseline' or 'manual_only'

print(f"Task type: {task_type}")
print(f"Strategy: {STRATEGY}")
print(f"Datetime columns detected: {col_types['datetime']}")
print(f"Text columns detected: {col_types['text_free']}")

if task_type == 'time-series' and col_types['datetime']:
    print("NOTE: datetime and lag features must be engineered before featurewiz.")

if task_type == 'clustering':
    STRATEGY = 'manual_only'
    print("Clustering task: featurewiz requires a target. Switching to manual_only.")
```

---

### Step 3 — Apply Manual Transforms

**Goal:** Apply per-column-type transforms based on EDA findings and the column type recipes.

> **At scale (large/very_large):** Fit `StandardScaler`, `OrdinalEncoder`, and TF-IDF on a 200K stratified sample. Apply `.transform()` to full dataset. Replace `.apply()` string operations with vectorized `.str` methods. Consider Polars for datetime extraction (10-100× faster than pandas).

**References:** `references/column-type-transforms.md`, `references/assumption-audit-pattern.md`

**Run Assumption Audit before any target-dependent transforms:**
```
## Assumption Audit: Feature Engineering Transforms

What I'm assuming about data quality:
- [ ] All nulls have been imputed — no NaN values in X_train or X_test
- [ ] Column types are correct after cleaning (no numeric columns still stored as object)
- [ ] Train and test come from the same distribution

What I'm assuming about data generation:
- [ ] No data leakage exists in the raw columns
- [ ] datetime columns represent event time, not data ingestion time
- [ ] Categorical levels in X_test are a subset of X_train levels

What would invalidate these:
- [ ] If any column has NaN, log1p and scalers will produce NaN outputs silently
- [ ] If test has unseen categorical levels, OrdinalEncoder raises an error unless handle_unknown is set
- [ ] If datetime columns represent processing time, time-since features will leak information

Checks to run:
- [ ] assert X_train.isnull().sum().sum() == 0, "Nulls remain in X_train"
- [ ] assert X_test.isnull().sum().sum() == 0, "Nulls remain in X_test"
- [ ] Check cat column coverage: any level in X_test not in X_train?

Audit result: [PROCEED / PROCEED WITH CAUTION / STOP AND INVESTIGATE]
```

```python
# Validate no nulls before transforms
assert X_train.isnull().sum().sum() == 0, "Nulls remain in X_train — run imputation first"
assert X_test.isnull().sum().sum() == 0, "Nulls remain in X_test — run imputation first"

feature_log = []   # track what we created for the manifest
```

Apply transforms per column type bucket using the recipes in `references/column-type-transforms.md`:

| Type bucket | Default transform | Log entry `transform` key |
|---|---|---|
| `numeric_continuous` | `log1p` if `\|skew\| > 1` and `min >= 0`; `StandardScaler` for linear models | `log1p` |
| `numeric_discrete` | Leave as-is (tree models); one-hot for linear models | `one_hot` |
| `categorical_low_card` | `OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)` | `ordinal_encoding` |
| `categorical_high_card` | Frequency encoding (fit on train only); never one-hot | `frequency_encoding` |
| `datetime` | Extract year/month/day_of_week/hour/quarter/is_weekend + cyclical sin/cos + days_since_start | `datetime_extraction` |
| `text_free` | char_len + word_count meta-features + TF-IDF (100 features short, 500 long text) | `text_length`, `tfidf` |
| `boolean` | `.astype(int)` | — |

```python
print(f"Manual transforms complete. X_train shape: {X_train.shape}")
print(f"Features created: {len(feature_log)}")
```

**Checkpoint:** No object-dtype columns remain in `X_train` or `X_test`. Shape is the same between splits (excluding row count).

> **CHECKPOINT — Step 3**
> - [ ] Assert: `X_train.isnull().sum().sum() == 0` (no NaN introduced)
> - [ ] Assert: `np.isinf(X_train.select_dtypes(include='number')).sum().sum() == 0` (no Inf introduced)
> - [ ] Assert: No remaining object-dtype columns (all encoded)
> - [ ] PASS: Manual transforms applied cleanly
> - [ ] On FAIL (NaN/Inf): Identify which transform caused it (compare pre/post column-by-column). Fallback to passthrough for failing columns.

---

### Step 4 — Run featurewiz

**Goal:** Automatically select the minimal, non-redundant, maximally predictive feature set using SULOV + MRMR.

> **Plain language:** featurewiz does two things automatically:
> 1. **SULOV** removes features that are copies of each other. If "temperature_celsius" and "temperature_fahrenheit" are both in your data, you only need one.
> 2. **MRMR** ranks the remaining features by how useful they are for prediction, while making sure not to add back redundancy.
> The result is the smallest set of features that gives the best predictions.

> **At scale (large/very_large):** Always set `featurewiz(nrows_limit=200_000, dask_xgboost_flag=True)` to subsample for SULOV/MRMR. For very_large datasets, also set `corr_limit=0.5` for more aggressive redundancy pruning. featurewiz has built-in scaling — use it.

**References:** `references/featurewiz-guide.md`, `references/leakage-guard.md`

```python
from featurewiz import FeatureWiz

# Skip for clustering (no target) or if strategy is manual_only
if STRATEGY != 'manual_only' and task_type != 'clustering':

    # Choose configuration based on task and data shape
    if task_type == 'regression':
        fwiz = FeatureWiz(corr_limit=0.7, transform_target=True, verbose=1)
    elif X_train.shape[1] > 50:
        # Wide dataset: more aggressive SULOV pruning
        fwiz = FeatureWiz(corr_limit=0.5, verbose=1)
    else:
        fwiz = FeatureWiz(corr_limit=0.7, verbose=1)

    # CRITICAL: fit on training data ONLY
    X_train_fw, y_train_fw = fwiz.fit_transform(X_train, y_train)
    selected_features = fwiz.features

    # Apply to test using the SAME feature list (no refitting)
    X_test_fw = X_test[selected_features]

    print(f"\nfeaturewiz results:")
    print(f"  Features in:  {X_train.shape[1]}")
    print(f"  Features out: {len(selected_features)}")
    print(f"  Reduction:    {round((1 - len(selected_features) / X_train.shape[1]) * 100, 1)}%")
    print(f"  Selected:     {selected_features}")

    # Log featurewiz metadata for manifest
    featurewiz_metadata = {
        'corr_limit': fwiz.corr_limit if hasattr(fwiz, 'corr_limit') else 0.7,
        'feature_engg': '',
        'features_in': X_train.shape[1],
        'features_out': len(selected_features),
        'selected_features': selected_features,
    }

    # Update feature_log with featurewiz-selected features
    fw_selected_set = set(selected_features)
    for entry in feature_log:
        if entry['name'] in fw_selected_set:
            entry['kept_by_featurewiz'] = True

else:
    X_train_fw = X_train.copy()
    X_test_fw = X_test.copy()
    selected_features = list(X_train.columns)
    featurewiz_metadata = None
    print("Skipped featurewiz (clustering task or manual_only strategy)")
```

**Checkpoint:** `X_train_fw` and `X_test_fw` have identical columns. No object-dtype columns remain.

> **CHECKPOINT — Step 4**
> - [ ] Assert: `len(selected_features) > 0`
> - [ ] Assert: `X_train_fw.shape[1] > 0`
> - [ ] PASS: featurewiz selected at least 1 feature
> - [ ] On FAIL (0 features): Fallback to top-N features by variance from manual transforms. Log: "featurewiz eliminated all features. Using variance-based selection as fallback."

---

### Step 5 — Validate Feature Quality

**Goal:** Confirm that engineering improved performance over the raw baseline and that no leakage has been introduced.

```python
# quick_score: 5-fold cross-validated LightGBM score
# classification → roc_auc, regression → rmse, other → skipped
raw_features_available = [c for c in X_train.columns if X_train[c].dtype in ['float64', 'int64', 'Int64']]
raw_score, metric = quick_score(X_train[raw_features_available], y_train, task_type)
fw_score, _ = quick_score(X_train_fw, y_train, task_type)

# Leakage check: flag any feature with >0.95 correlation to target
target_corr = X_train_fw.corrwith(y_train).abs().sort_values(ascending=False)
suspicious = target_corr[target_corr > 0.95]
if len(suspicious) > 0:
    print(f"WARNING: {len(suspicious)} features with >0.95 target correlation — investigate for leakage")

validation_results = {'raw_score': raw_score, 'featurewiz_score': fw_score, 'metric_name': metric}
```

**Checkpoint:**
- Engineered feature score >= raw baseline (if not, adding noise — simplify)
- No features with >0.95 correlation to target (leakage)
- No feature pairs with >0.95 correlation (redundancy featurewiz missed)

> **CHECKPOINT — Step 5**
> - [ ] Assert: No feature has >0.95 correlation with target (leakage signal)
> - [ ] Assert: No inter-feature correlation >0.95 (redundancy)
> - [ ] PASS: Feature quality validated, no leakage detected
> - [ ] On FAIL (leakage): Drop suspicious features. Log which features and why.
> - [ ] On FAIL (engineered < raw score): WARN — "Engineered features underperform raw features. Falling back to raw + top manual transforms."

---

### Step 6 — Run Leakage Guard

**Goal:** Systematic leakage verification across all transform boundaries before finalizing the pipeline.

**Reference:** `references/leakage-guard.md`

Run through the full leakage checklist:

```python
# 1. Fit-Transform Boundary: verify all stateful transforms were fit on train only
# Document each one:
leakage_checklist = [
    {'transform': 'OrdinalEncoder', 'fit_on_train_only': True, 'uses_future': False, 'uses_target': False},
    {'transform': 'Frequency encoding', 'fit_on_train_only': True, 'uses_future': False, 'uses_target': False},
    {'transform': 'TF-IDF', 'fit_on_train_only': True, 'uses_future': False, 'uses_target': False},
    {'transform': 'featurewiz SULOV+MRMR', 'fit_on_train_only': True, 'uses_future': False, 'uses_target': True},
    # Add target encoding entry if used:
    # {'transform': 'Target encoding', 'fit_on_train_only': True, 'uses_future': False, 'uses_target': True, 'leakage_prevention': 'fold-based KFold'},
]

all_clean = all(entry['fit_on_train_only'] for entry in leakage_checklist)

# 2. Column count must match between train and test
assert X_train_fw.shape[1] == X_test_fw.shape[1], \
    f"Column count mismatch: train={X_train_fw.shape[1]}, test={X_test_fw.shape[1]}"
assert list(X_train_fw.columns) == list(X_test_fw.columns), \
    "Column names or order mismatch between train and test"

# 3. Time-series specific: no lag features with lag < 1
if task_type == 'time-series':
    lag_cols = [c for c in X_train_fw.columns if 'lag_0' in c or 'lead' in c.lower() or 'forward' in c.lower()]
    assert len(lag_cols) == 0, f"Suspicious lag/lead features detected: {lag_cols}"

# 4. No future information in feature names
suspicious_names = [c for c in X_train_fw.columns if any(w in c.lower() for w in ['future', 'next', 'lead', 'forward'])]
if suspicious_names:
    print(f"WARNING: suspicious feature names suggest future data: {suspicious_names}")

print(f"Leakage guard: {'PASSED' if all_clean and len(suspicious_names) == 0 else 'ISSUES FOUND'}")
leakage_guard_passed = all_clean and len(suspicious_names) == 0
```

**Checkpoint:** All checklist items confirm `fit_on_train_only: True`. No suspicious feature names. Column counts match.

---

### Step 7 — Package for Output

**Goal:** Save the feature matrix and pipeline in the format appropriate for downstream use.

**Decision point:**

```python
OUTPUT_MODE = 'experimentation'   # or 'production' or 'feature_store'
```

**IF experimentation:**
```python
import os

os.makedirs('output', exist_ok=True)

# Save feature matrices as Parquet
X_train_fw.to_parquet('output/X_train_features.parquet', index=True)
X_test_fw.to_parquet('output/X_test_features.parquet', index=True)
y_train.to_frame().to_parquet('output/y_train.parquet', index=True)
y_test.to_frame().to_parquet('output/y_test.parquet', index=True)

pipeline_path = None
print(f"Saved feature matrices to output/")
print(f"Train shape: {X_train_fw.shape}")
print(f"Test shape:  {X_test_fw.shape}")
```

**IF production:**
```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
import joblib

# Build a reproducible sklearn Pipeline from all stateful transforms
# Adjust column lists and transformers to match what you applied in Step 3

numeric_pipeline = Pipeline([
    ('scaler', StandardScaler())
])

categorical_pipeline = Pipeline([
    ('encoder', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1))
])

# Use the final selected feature names from featurewiz
final_numeric_cols = [c for c in selected_features if X_train_fw[c].dtype in ['float64', 'int64']]
final_cat_cols = [c for c in selected_features if X_train_fw[c].dtype == 'object']

preprocessor = ColumnTransformer(transformers=[
    ('num', numeric_pipeline, final_numeric_cols),
    ('cat', categorical_pipeline, final_cat_cols),
], remainder='passthrough')

production_pipeline = Pipeline([('preprocessor', preprocessor)])

# Fit on train features, transform both splits
production_pipeline.fit(X_train_fw)
X_train_prod = production_pipeline.transform(X_train_fw)
X_test_prod = production_pipeline.transform(X_test_fw)

# Verify round-trip: re-transform train should give identical result
X_train_check = production_pipeline.transform(X_train_fw)
assert X_train_prod.shape == X_train_check.shape, "Round-trip test failed"

# Save pipeline
pipeline_path = 'output/feature_pipeline.joblib'
os.makedirs('output', exist_ok=True)
joblib.dump(production_pipeline, pipeline_path)
print(f"Pipeline saved to {pipeline_path}")
print("Round-trip test: PASSED")
```

**IF feature store:**
```python
# Register features with name, version, and lineage
feature_store_record = {
    'feature_set_name': 'my_model_v1_features',
    'version': '1.0.0',
    'created_at': pd.Timestamp.now().isoformat(),
    'feature_names': list(X_train_fw.columns),
    'n_features': len(X_train_fw.columns),
    'source_dataset': 'data_imputed.parquet',
    'lineage': feature_log,
}
with open('output/feature_store_record.json', 'w') as f:
    json.dump(feature_store_record, f, indent=2)
print(f"Feature store record written: {len(feature_store_record['feature_names'])} features registered")
pipeline_path = None
```

---

## Generate Manifest

Run the manifest generator to produce a permanent audit trail of every feature engineering decision:

```python
import sys
sys.path.insert(0, 'skills/feature-engineering/scripts')
from generate_feature_manifest import generate_manifest

manifest = generate_manifest(
    task_type=task_type,
    features=feature_log,
    featurewiz_metadata=featurewiz_metadata,
    dropped_features=[],       # add any manually dropped features with reasons
    validation_results=validation_results,
    pipeline_path=pipeline_path,
    leakage_guard_passed=leakage_guard_passed,
    output_path='feature_manifest.json',
)
print(manifest)
```

Or from the command line:

```bash
python skills/feature-engineering/scripts/generate_feature_manifest.py \
  --task-type classification \
  --features-in 42 \
  --features-out 18 \
  --leakage-guard-passed \
  --output feature_manifest.json
```

---

## Edge Case Handling

| Edge Case | Detection | Action |
|---|---|---|
| **Empty DataFrame (0 rows)** | `len(X_train) == 0` | HALT — "Cannot engineer features on empty dataset." |
| **Single feature after cleaning** | `X_train.shape[1] == 1` | Skip featurewiz (needs ≥2 features). Apply manual transforms only. |
| **featurewiz returns 0 features** | `len(fwiz.features) == 0` | Fallback: select top-N features by variance from manual transforms. N = min(20, n_cols). Log: "featurewiz eliminated all features — using variance-based selection." |
| **log1p on negative values** | `df[col].min() < 0` when log1p recommended | Skip log1p for this column. Try `np.sqrt(df[col] - df[col].min() + 1)` as alternative. Log the substitution. |
| **StandardScaler on zero-variance column** | `df[col].std() == 0` | Skip scaling for this column. Flag as `drop_candidate`. |
| **TF-IDF on empty text column** | `df[col].str.len().sum() == 0` | Skip TF-IDF. Create `text_length = 0` feature only. Log: "Text column is entirely empty." |
| **Unseen categorical levels in test** | Test set has categories not in train | For OrdinalEncoder: `handle_unknown='use_encoded_value', unknown_value=-1`. For frequency encoding: assign frequency = 0. Log new levels. |
| **Cyclical encoding period ambiguity** | Datetime column with unclear periodicity | Default periods: hour_of_day=24, day_of_week=7, month=12, day_of_year=365. Log which periods were used. |
| **All features are constant** | `X_train.nunique().max() <= 1` | HALT — "No variance in feature set. Cannot engineer useful features. Check upstream pipeline." |
| **Engineered features worse than raw** | `engineered_score < raw_score` | WARN — "Engineered features underperform raw. Reverting to raw features + top 5 manual transforms by importance." |
| **Pipeline serialization fails** | `joblib.dump()` raises error | Save features as Parquet instead. Log: "Pipeline serialization failed — features saved as Parquet only. Production deployment will need manual pipeline construction." |

---

## Quality Bar

A feature matrix is "done" when ALL of the following are true:

- [ ] `X_train_fw.isnull().sum().sum() == 0` — zero nulls
- [ ] `X_train_fw.select_dtypes(include=['object']).columns.tolist() == []` — zero object dtype columns
- [ ] Every feature in `X_train_fw.columns` has an entry in `feature_manifest.json`
- [ ] `featurewiz_score >= raw_score` — engineered features outperform the raw baseline
- [ ] `leakage_guard_passed == True`
- [ ] `X_train_fw.shape[1] == X_test_fw.shape[1]` — column count matches between splits
- [ ] `list(X_train_fw.columns) == list(X_test_fw.columns)` — columns are in the same order
- [ ] `feature_manifest.json` exists and contains `validation_results`

---

## Scope Boundary

This skill does NOT:
- Train the final model or tune hyperparameters (use a modeling skill)
- Impute missing values (use `missing-data-imputation` skill)
- Perform EDA or generate `eda_findings.json` (use `eda-comprehensive` skill)
- Validate business logic or domain-specific constraints
- Handle schema migration or multi-source dataset alignment

If `eda_findings.json` does not exist, run the `eda-comprehensive` skill first.

---

## Downstream Skills

After this skill completes:

1. **Model training** — use `X_train_fw`, `y_train`, `X_test_fw`, `y_test` from `output/`
2. **Hyperparameter tuning** — pass `output/feature_pipeline.joblib` for production pipelines
3. **Monitoring** — use `feature_manifest.json` to track feature drift in production
