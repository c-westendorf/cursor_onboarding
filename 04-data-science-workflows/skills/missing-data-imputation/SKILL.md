---
name: missing-data-imputation
description: Diagnose missingness mechanisms (MCAR/MAR/MNAR) per column, select and apply statistically appropriate imputation strategies, and produce a complete dataset with full audit trail. Use when data has missing values that need filling, after data cleaning identified nulls, when QA flagged completeness issues, when a model requires complete data and dropping rows would lose >5% of data, or when you need to understand why data is missing. Handles numeric, categorical, datetime, text, and boolean columns with task-aware strategies for classification, regression, time-series, NLP, and clustering.
---

# Missing Data Imputation

## Why Imputation Matters

Naive approaches introduce bias or leak data in ways that are easy to miss and hard to recover from:

- **Dropping rows** is only safe when data is truly MCAR and loss is <5%. Otherwise it systematically removes a subpopulation.
- **Mean/mode fill applied to the full dataset** leaks test-set statistics into training. A model trained this way will underperform in production.
- **Ignoring MNAR** produces imputed values that are systematically wrong — e.g., income fields missing because high earners opted out will be filled with median income, pulling estimates toward the center.
- **No indicator column for MNAR/MAR** discards a predictive signal — the fact that a value was missing is often as informative as the value itself.

## When to Activate

Activate this skill when:
- Data cleaning or QA identified null values in one or more columns
- A downstream model requires complete data (sklearn, XGBoost, neural networks)
- Dropping rows with nulls would eliminate >5% of the dataset
- You need to understand the structure of missingness (why is data missing?)
- Preprocessing is being set up for a train/test pipeline where leakage matters

## Prerequisites

Before starting, confirm:
- **Cleaned DataFrame**: dtypes are correct, sentinel values (-999, "N/A" strings) have been resolved to `NaN` (run `data-cleaning` skill first)
- **Train/test split indices**: `X_train`, `X_test` are available — imputers must be fit on `X_train` only
- **Optional**: `qa_report.json` from the `data-quality-assurance` skill (provides null rates per column)
- **Optional**: domain knowledge about which columns are expected to have structured missingness

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

#### Pre-check: QA Verdict Gate

Before proceeding, check the QA verdict:

```python
import json
from pathlib import Path

qa_path = Path("qa_report.json")
if qa_path.exists():
    qa = json.load(open(qa_path))
    verdict = qa.get("verdict", "UNKNOWN")
    allowed = qa.get("allowed_downstream_skills", [])

    if verdict == "FAIL":
        print("⛔ QA verdict is FAIL. Cannot proceed with imputation.")
        print("   Fix data quality issues and re-run data-quality-assurance first.")
        print(f"   Failing dimensions: {qa.get('failing_dimensions', [])}")
        # HALT
    elif verdict == "CONDITIONAL_PASS":
        print("⚠️  QA verdict is CONDITIONAL_PASS. Proceeding with caution.")
        print(f"   Accepted risks: {qa.get('accepted_risks', [])}")
        # PROCEED with warning
    else:
        print("✓ QA verdict is PASS. Proceeding.")
```

> **Plain language:** We check the QA report before filling in missing values. If the data quality check failed, we must fix the underlying issues first — imputing bad data produces bad results.

### Step 1: Assess Missingness Landscape

Produce a null-rate summary per column and identify columns requiring attention.

```python
import pandas as pd
import numpy as np

def missingness_summary(df):
    """Return a DataFrame summarizing null rates for all columns with any nulls."""
    null_counts = df.isnull().sum()
    null_rates = null_counts / len(df)
    summary = pd.DataFrame({
        'null_count': null_counts,
        'null_rate': null_rates,
        'dtype': df.dtypes,
    })
    summary = summary[summary['null_count'] > 0].sort_values('null_rate', ascending=False)
    summary['action_required'] = summary['null_rate'].apply(
        lambda r: 'HIGH — >50% missing' if r > 0.5
        else 'MEDIUM — 5-50% missing' if r > 0.05
        else 'LOW — <5% missing'
    )
    return summary

summary = missingness_summary(df)
print(summary.to_string())
```

Classify columns by type using `references/dtype-router.md`:

```python
# Use classify_columns() from dtype-router.md
col_types = classify_columns(df)
cols_with_nulls = [c for c in df.columns if df[c].isnull().any()]

# Map each null column to its type bucket
col_type_map = {}
for bucket, cols in col_types.items():
    for col in cols:
        col_type_map[col] = bucket
```

Decision point after Step 1:
- Any column with >50% nulls → go to **Step 4** before imputing
- All columns with 1-50% nulls → continue to **Step 2**
- Columns with <1% nulls → median/mode fill is acceptable without mechanism diagnosis

> **CHECKPOINT — Step 1**
> - [ ] Assert: Every column classified into HIGH (>50%), MEDIUM (5-50%), LOW (<5%), or ZERO (0%) null rate
> - [ ] Assert: 100% null columns auto-classified as DROP with warning logged
> - [ ] PASS: Missingness landscape fully mapped
> - [ ] On FAIL: HALT — "Column classification incomplete. Check for unexpected dtypes."

---

### Step 2: Diagnose Missingness Mechanism

For each column with >1% missing, determine whether the mechanism is MCAR, MAR, or MNAR.

**Run Assumption Audit** (see `references/assumption-audit-pattern.md`) before this step:
- What am I assuming about why this column is missing?
- Could missingness correlate with the target? With another feature? With time?
- What domain knowledge is available?

**Decision tree:**
1. Missingness rate is uniform across subgroups (by target, by time, by segment) → likely **MCAR**
2. Logistic regression of `is_missing ~ other_cols` produces significant coefficients → **MAR**
3. You have domain reason to believe missingness correlates with the unobserved value itself (e.g., sicker patients skip health surveys) → **MNAR**

> **Plain language:** We need to figure out WHY data is missing before deciding how to fill it in:
> - **MCAR** = Missing randomly, like a coin flip. Safe to fill with averages.
> - **MAR** = Missing for a reason we can see in other columns (e.g., younger people skip income). Need smarter fill methods.
> - **MNAR** = Missing because of the value itself (e.g., high earners hide income). The fact that it's missing IS information — we create a flag column to capture this.

```python
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

def diagnose_all_columns(df, threshold=0.01):
    """
    Diagnose missingness mechanism for all columns with null_rate > threshold.
    Returns a dict: {col: 'MCAR' | 'MAR' | 'MNAR_SUSPECTED' | 'UNKNOWN'}
    Note: MNAR cannot be detected statistically — it requires domain knowledge.
    """
    diagnoses = {}
    null_rates = df.isnull().mean()
    candidates = null_rates[null_rates > threshold].index.tolist()

    for col in candidates:
        target = df[col].isnull().astype(int)
        numeric_other = df.select_dtypes(include='number').drop(
            columns=[col], errors='ignore'
        ).dropna(axis=1, how='any')

        if numeric_other.shape[1] == 0:
            diagnoses[col] = 'UNKNOWN'
            continue

        mask = numeric_other.notna().all(axis=1)
        X = numeric_other[mask]
        y = target[mask]

        if y.sum() < 5 or (y == 0).sum() < 5:
            diagnoses[col] = 'MCAR'
            continue

        X_scaled = StandardScaler().fit_transform(X)
        clf = LogisticRegression(max_iter=1000, random_state=42, C=1.0)
        clf.fit(X_scaled, y)

        max_coef = np.abs(clf.coef_[0]).max()
        diagnoses[col] = 'MAR' if max_coef > 0.5 else 'MCAR'

    return diagnoses

diagnoses = diagnose_all_columns(X_train)

# Also check cross-column missingness correlation
missingness_corr = X_train.isnull().astype(int).corr()
# High correlation (>0.7) between two columns' indicators = shared MAR structure
```

**Audit result criteria:**
- MCAR confirmed, low rate → PROCEED
- MAR detected → PROCEED WITH CAUTION (use IterativeImputer or KNN, add indicators for rate >5%)
- MNAR suspected → STOP AND INVESTIGATE with domain expert. Then impute with indicator.

---

### Step 3: Select Strategy Per Column

Consult `references/imputation-strategies.md` for the full matrix. The key branches are:

| Column Type | MCAR | MAR | MNAR |
|-------------|------|-----|------|
| Numeric Continuous | `SimpleImputer(strategy='median')` | `IterativeImputer` or `KNNImputer` | Median + `_was_missing` |
| Numeric Discrete | `SimpleImputer(strategy='most_frequent')` | KNN + round | Mode + `_was_missing` |
| Categorical Low-Card | Mode | Mode or RF IterativeImputer | `"Unknown"` |
| Categorical High-Card | `"Unknown"` | `"Unknown"` | `"Unknown"` |
| Datetime (regular) | Interpolate (limit=3) | Interpolate (limit=3) | None + flag |
| Boolean | Mode + `_was_missing` | Mode + `_was_missing` | Mode + `_was_missing` |
| Text | `"[MISSING]"` | `"[MISSING]"` | `"[MISSING]"` |

Additional task-specific guidance:

- **Classification**: Preserve the `_was_missing` indicator — it may be among the strongest features
- **Regression**: Prefer IterativeImputer for MAR in numeric columns; minimizes RMSE impact
- **Time-series**: Use `interpolate(method='time')` for regular-frequency data; never forward-fill past the gap threshold (default: 3 periods)
- **NLP/text tasks**: Always `"[MISSING]"` token — never synthesize text
- **Clustering**: Prefer KNNImputer — distances are more meaningful than global statistics

Build a strategy plan before writing code:

```python
strategy_plan = {}
for col in cols_with_nulls:
    col_type = col_type_map.get(col, 'unknown')
    mechanism = diagnoses.get(col, 'MCAR')
    null_rate = df[col].isnull().mean()

    strategy_plan[col] = {
        'col_type': col_type,
        'mechanism': mechanism,
        'null_rate': null_rate,
        # Fill in from references/imputation-strategies.md:
        'strategy': None,   # e.g. 'median', 'iterative', 'knn', 'unknown_category'
        'add_indicator': null_rate > 0.01 and mechanism in ('MAR', 'MNAR'),
    }
```

> **CHECKPOINT — Step 3**
> - [ ] Assert: Every column with null_rate > 0 has an assigned strategy in `strategy_plan`
> - [ ] Assert: No strategy is `None` or empty
> - [ ] PASS: All columns have explicit imputation strategies
> - [ ] On FAIL: HALT — list unassigned columns. Assign median/mode as safe defaults.

---

### Step 4: Handle High-Missing Columns (>50% Null)

For any column with >50% missing, make an explicit keep/drop decision before imputing.

```python
HIGH_MISSING_THRESHOLD = 0.50

high_missing_cols = [c for c in cols_with_nulls if df[c].isnull().mean() > HIGH_MISSING_THRESHOLD]
cols_to_drop = []
cols_to_impute_with_warning = []

for col in high_missing_cols:
    null_rate = df[col].isnull().mean()

    # Decision criteria — must be answered by analyst:
    # Q1: Is this column critical to the model (domain requirement)?
    # Q2: Is this column the only source of information about a concept?
    # Q3: What is the cost of a wrong imputed value?

    # Default: drop unless overridden
    print(f"REVIEW REQUIRED — {col}: {null_rate:.1%} missing")
    print(f"  Options:")
    print(f"    A) Drop column")
    print(f"    B) Impute + add _was_missing indicator (high bias risk — document)")
    print(f"    C) Keep as-is (only for tree models that handle NaN natively)")

# After manual review, populate:
# cols_to_drop = [...]
# cols_to_impute_with_warning = [...]

if cols_to_drop:
    X_train = X_train.drop(columns=cols_to_drop)
    X_test = X_test.drop(columns=cols_to_drop)
    print(f"Dropped {len(cols_to_drop)} high-missing columns: {cols_to_drop}")
```

---

### Step 5: Apply Imputation

**Fit on TRAIN ONLY.** See `references/leakage-guard.md` for the full checklist.

> **At scale (large/very_large):** Replace `IterativeImputer` with `SimpleImputer(strategy='median')` for numeric columns. Replace `KNNImputer` with mode-based imputation. Fit imputers on a 200K stratified sample, then apply `.transform()` to full dataset. For very_large: consider Dask-compatible imputers or treat missingness as a feature (`_was_missing_*` indicators only, no fill).

Create `_was_missing_{col}` indicators for all columns with >1% imputed values **before** imputation (indicators must reflect original missingness, not imputed data).

```python
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import IterativeImputer
import joblib
import os

INDICATOR_THRESHOLD = 0.01  # Create indicator if null_rate > 1%

# Step A: Create indicators (always before imputation)
indicators_created = []
for col, plan in strategy_plan.items():
    if plan['add_indicator']:
        ind_col = f'_was_missing_{col}'
        X_train[ind_col] = X_train[col].isnull().astype(int)
        X_test[ind_col] = X_test[col].isnull().astype(int)
        indicators_created.append(ind_col)

# Step B: Group by strategy and apply
fitted_imputers = {}

# --- Median imputation (MCAR numeric continuous) ---
median_cols = [c for c, p in strategy_plan.items()
               if p['strategy'] == 'median' and c in X_train.columns]
if median_cols:
    imp = SimpleImputer(strategy='median')
    imp.fit(X_train[median_cols])
    X_train[median_cols] = imp.transform(X_train[median_cols])
    X_test[median_cols] = imp.transform(X_test[median_cols])
    fitted_imputers['median'] = imp

# --- Mode imputation (MCAR discrete/categorical) ---
mode_cols = [c for c, p in strategy_plan.items()
             if p['strategy'] == 'mode' and c in X_train.columns]
if mode_cols:
    imp = SimpleImputer(strategy='most_frequent')
    imp.fit(X_train[mode_cols])
    X_train[mode_cols] = imp.transform(X_train[mode_cols])
    X_test[mode_cols] = imp.transform(X_test[mode_cols])
    fitted_imputers['mode'] = imp

# --- IterativeImputer / MICE (MAR numeric) ---
iterative_cols = [c for c, p in strategy_plan.items()
                  if p['strategy'] == 'iterative' and c in X_train.columns]
if iterative_cols:
    # Single model: deterministic settings
    imp = IterativeImputer(max_iter=10, random_state=42)
    # Uncertainty quantification: set sample_posterior=True
    imp.fit(X_train[iterative_cols])
    X_train[iterative_cols] = imp.transform(X_train[iterative_cols])
    X_test[iterative_cols] = imp.transform(X_test[iterative_cols])
    fitted_imputers['iterative'] = imp

# --- KNNImputer (MAR numeric, ordinal discrete) ---
knn_cols = [c for c, p in strategy_plan.items()
            if p['strategy'] == 'knn' and c in X_train.columns]
if knn_cols:
    imp = KNNImputer(n_neighbors=5)
    imp.fit(X_train[knn_cols])
    X_train[knn_cols] = imp.transform(X_train[knn_cols])
    X_test[knn_cols] = imp.transform(X_test[knn_cols])
    fitted_imputers['knn'] = imp

# --- Unknown category (high-card categorical, MNAR categorical) ---
unknown_cols = [c for c, p in strategy_plan.items()
                if p['strategy'] == 'unknown_category' and c in X_train.columns]
for col in unknown_cols:
    X_train[col] = X_train[col].fillna('Unknown')
    X_test[col] = X_test[col].fillna('Unknown')

# --- Text sentinel ---
text_cols = [c for c, p in strategy_plan.items()
             if p['strategy'] == 'missing_token' and c in X_train.columns]
for col in text_cols:
    X_train[col] = X_train[col].fillna('[MISSING]')
    X_test[col] = X_test[col].fillna('[MISSING]')

# Step C: Serialize imputers for production use
imputers_path = 'artifacts/fitted_imputers.joblib'
os.makedirs('artifacts', exist_ok=True)
joblib.dump(fitted_imputers, imputers_path)

# Step D: Verify no nulls remain in imputed columns
remaining_nulls = X_train[list(strategy_plan.keys())].isnull().sum()
if remaining_nulls.sum() > 0:
    print("WARNING — nulls remain after imputation:")
    print(remaining_nulls[remaining_nulls > 0])
```

**Production vs. uncertainty quantification:**
- Single model / production: `IterativeImputer(random_state=42)` — deterministic, reproducible
- Uncertainty quantification (confidence intervals, ensembles): `IterativeImputer(sample_posterior=True, random_state=42)` — stochastic draws, run multiple times and aggregate

> **CHECKPOINT — Step 5**
> - [ ] Assert: `df.isnull().sum().sum() == 0` for all imputed columns
> - [ ] Assert: `np.isinf(df.select_dtypes(include='number')).sum().sum() == 0`
> - [ ] Assert: No constant columns created by imputation (`df.nunique() > 1` for imputed cols)
> - [ ] PASS: Zero nulls, zero Inf, no zero-variance artifacts
> - [ ] On FAIL: Log failing columns. Fallback to median/mode for numeric, "Unknown" for categorical. Re-check.

---

### Step 6: Validate Imputation Quality

Three checks must pass before the imputed dataset is considered ready.

**Check A: Artificial missingness test (hold-out validation)**

```python
from scipy.stats import ks_2samp
import numpy as np

def validate_imputation(X_train_original, col, strategy, null_rate, random_state=42):
    """
    Remove 10% of non-null values, impute, compare imputed vs. true values.
    Returns RMSE (numeric) or accuracy (categorical).
    """
    rng = np.random.default_rng(random_state)
    observed_idx = X_train_original[col].dropna().index
    hold_out_idx = rng.choice(observed_idx, size=int(0.10 * len(observed_idx)), replace=False)

    X_perturbed = X_train_original.copy()
    X_perturbed.loc[hold_out_idx, col] = np.nan

    # Apply same strategy
    if strategy == 'median':
        imp = SimpleImputer(strategy='median')
        imp.fit(X_perturbed[[col]])
        imputed_vals = imp.transform(X_perturbed[[col]]).ravel()
    # ... extend for other strategies

    true_vals = X_train_original.loc[hold_out_idx, col].values
    imputed_at_holdout = pd.Series(imputed_vals, index=X_perturbed.index).loc[hold_out_idx].values

    if pd.api.types.is_numeric_dtype(X_train_original[col]):
        baseline = np.abs(true_vals - X_train_original[col].median()).mean()  # MAE of median baseline
        error = np.abs(true_vals - imputed_at_holdout).mean()
        passed = error <= baseline * 1.2  # Imputer should not be much worse than trivial baseline
        return {'metric': 'MAE', 'value': error, 'baseline': baseline, 'passed': passed}
    else:
        accuracy = (true_vals == imputed_at_holdout).mean()
        baseline = (X_train_original[col].value_counts().iloc[0] / X_train_original[col].notna().sum())
        passed = accuracy >= baseline * 0.9
        return {'metric': 'accuracy', 'value': accuracy, 'baseline': baseline, 'passed': passed}
```

**Check B: Distribution comparison (KS-test)**

```python
def check_distribution_shift(original_series, imputed_series, alpha=0.05):
    """
    Compare distribution before and after imputation using KS-test.
    p > alpha means distributions are not significantly different — this is what we want.
    """
    original_nonull = original_series.dropna()
    stat, p_value = ks_2samp(original_nonull, imputed_series)
    passed = p_value > alpha
    if not passed:
        print(f"WARNING: Distribution shift detected (KS p={p_value:.4f}). "
              f"Consider simpler imputation strategy.")
    return {'ks_stat': stat, 'p_value': p_value, 'passed': passed}
```

**Check C: Fallback on failure**

```python
# If validation error > baseline, fall back to simpler method
for col, plan in strategy_plan.items():
    result = validate_imputation(X_train_backup, col, plan['strategy'], plan['null_rate'])
    if not result['passed']:
        print(f"Imputation validation FAILED for {col}. "
              f"Strategy: {plan['strategy']}. Error: {result['value']:.4f}, Baseline: {result['baseline']:.4f}")
        print(f"Falling back to median/mode for {col}")
        # Re-impute with simpler strategy
        fallback_strategy = 'median' if col_type_map.get(col) in ('numeric_continuous', 'numeric_discrete') else 'mode'
        fallback_imp = SimpleImputer(strategy=fallback_strategy if fallback_strategy == 'median' else 'most_frequent')
        fallback_imp.fit(X_train_backup[[col]])
        X_train[col] = fallback_imp.transform(X_train_backup[[col]])
        X_test[col] = fallback_imp.transform(X_test[[col]])
```

> **CHECKPOINT — Step 6**
> - [ ] Assert: Artificial missingness test error ≤ 1.2× baseline for all validated columns
> - [ ] Assert: KS-test p > 0.05 for numeric columns (distribution preserved)
> - [ ] PASS: Imputation quality validated
> - [ ] On FAIL (primary): Fallback to simpler imputation (median/mode). Re-validate.
> - [ ] On FAIL (fallback): HALT — "Imputation quality insufficient for columns: [list]. Consider dropping these columns."

---

## Edge Case Handling

| Edge Case | Detection | Action |
|---|---|---|
| **Empty DataFrame (0 rows)** | `len(df) == 0` | HALT — "Cannot impute empty dataset." |
| **Single-row DataFrame** | `len(df) == 1` | WARN — statistical imputation is meaningless. Use median/mode from domain knowledge or flag for manual review. |
| **100% null column** | `df[col].isnull().all()` | Auto-DROP with warning logged to manifest. Cannot impute from no information. |
| **Column becomes constant after imputation** | `df[col].nunique() == 1` post-imputation | Flag in manifest as `constant_after_imputation`. WARN — "Column {col} has zero variance after imputation. Consider dropping." |
| **"Unknown" category already exists** | `"Unknown"` in `df[col].unique()` before imputation | Use `"__MISSING__"` instead of `"Unknown"` to avoid collision. Log the alternative sentinel. |
| **Datetime gaps after interpolation** | NaNs remain after `interpolate(limit=3)` | Fill remaining NaNs with `None` and create `_was_missing_{col}` indicator. Do not force-fill dates. |
| **All values missing in test set** | `X_test[col].isnull().all()` | Apply train-fitted imputer (will fill all with train median/mode). WARN — "Entire test column imputed." |
| **Boolean column with nulls** | Boolean dtype with NaN | Impute with mode. Always create `_was_missing_{col}` indicator (missingness in boolean is often informative). |
| **Very high missing rate across all columns** | `df.isnull().mean().mean() > 0.5` | WARN — "Dataset is >50% missing overall. Consider whether this data is usable. Imputation may introduce more noise than signal." |
| **Imputer fails to converge** | IterativeImputer `max_iter` reached without convergence | Fallback to SimpleImputer(strategy='median'). Log convergence failure. |

---

## Quality Bar

Before handing off the imputed dataset, confirm:

- [ ] Zero nulls remain in all columns that were targeted for imputation
- [ ] All imputers were fit on `X_train` only (leakage-guard verified)
- [ ] `_was_missing` indicators exist for all columns with >1% original null rate that are MAR or MNAR
- [ ] KS-test passed (p > 0.05) for all numeric columns, OR distribution shift is documented with justification
- [ ] Artificial missingness test: imputation error <= 1.2x baseline for all columns
- [ ] Imputers serialized to `artifacts/fitted_imputers.joblib`
- [ ] `imputation_manifest.json` generated (see `scripts/generate_imputation_manifest.py`)
- [ ] MNAR columns documented with domain-knowledge note explaining why values are missing

---

## Scope Boundary

This skill covers:
- Diagnosing missingness mechanisms
- Selecting and applying imputation strategies
- Creating `_was_missing` indicators
- Validating imputation quality

This skill does NOT cover:
- Initial null detection and dtype correction (use `data-cleaning` skill)
- Dropping columns based on overall data quality (use `data-quality-assurance` skill)
- Feature engineering on imputed columns (use `feature-engineering` skill)
- Model-specific hyperparameter tuning of imputers (out of scope)
