# Imputation Strategies Reference

Strategy matrix: `column_type × missingness_mechanism × modeling_task → recommended strategy + code`.

Use `references/dtype-router.md` to classify columns before consulting this matrix.

---

## Missingness Mechanism Diagnosis

Before selecting a strategy, diagnose the mechanism. Never assume MCAR without verification.

### Little's MCAR Test

The formal test for MCAR is Little's (1988) test. It is statistically sound but complex to implement from scratch. Use the `pyampute` or `missingpy` libraries if available. Reference only — the heuristic below is sufficient for most production use.

```python
# pip install pyampute (optional, formal test)
# from pyampute.exploration.mcar_statistical_tests import MCARTest
# mcar_test = MCARTest(method="little")
# p_value = mcar_test.little_mcar_test(df)
# if p_value > 0.05: mechanism is consistent with MCAR
```

### Heuristic: Logistic Regression of is_missing ~ other_cols

If any predictor is statistically significant, the column is at minimum MAR. This is the recommended diagnostic for production workflows.

```python
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

def diagnose_missingness(df, col, alpha=0.05):
    """
    Heuristic MAR test for a single column.
    Returns 'MCAR' if no other column predicts missingness, 'MAR' otherwise.
    Falls back to 'MNAR' only based on domain knowledge — this function cannot detect MNAR.
    """
    target = df[col].isnull().astype(int)

    if target.sum() < 10:
        return 'MCAR'  # too few nulls to test

    # Predictors: all OTHER numeric columns, complete-case
    numeric_cols = df.select_dtypes(include='number').columns.drop(col, errors='ignore')
    X = df[numeric_cols].dropna(axis=1, how='any')

    if X.shape[1] == 0:
        return 'UNKNOWN'

    # Align index
    mask = X.notna().all(axis=1)
    X_clean = X[mask]
    y_clean = target[mask]

    if y_clean.sum() < 5 or (y_clean == 0).sum() < 5:
        return 'MCAR'

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_clean)

    clf = LogisticRegression(max_iter=1000, random_state=42)
    clf.fit(X_scaled, y_clean)

    # Heuristic: if max absolute coefficient is large, likely MAR
    max_coef = np.abs(clf.coef_[0]).max()
    return 'MAR' if max_coef > 0.5 else 'MCAR'


def check_missingness_correlations(df):
    """
    Compute correlation between missingness indicators.
    High correlation between two columns' indicators suggests shared MAR structure.
    """
    null_indicators = df.isnull().astype(int)
    cols_with_nulls = null_indicators.columns[null_indicators.sum() > 0]
    return null_indicators[cols_with_nulls].corr()
```

---

## Strategy Matrix

### Numeric Continuous

| Mechanism | Recommended Strategy | Notes |
|-----------|---------------------|-------|
| MCAR | Median imputation | Robust to outliers; never use mean for skewed distributions |
| MAR | IterativeImputer (MICE) | Models each feature as function of others |
| MAR (alt) | KNNImputer | Good when relationships are local/non-linear |
| MNAR | Median + `_was_missing` indicator | Imputed values are biased; indicator preserves signal |
| Time-series | `interpolate(method='time')` | Never forward-fill past gap threshold |

**MCAR — Median:**
```python
from sklearn.impute import SimpleImputer

imputer = SimpleImputer(strategy='median')
imputer.fit(X_train[[col]])
X_train[col] = imputer.transform(X_train[[col]])
X_test[col] = imputer.transform(X_test[[col]])
```

**MAR — IterativeImputer (MICE):**
```python
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import IterativeImputer

imputer = IterativeImputer(max_iter=10, random_state=42)
imputer.fit(X_train[numeric_cols])
X_train[numeric_cols] = imputer.transform(X_train[numeric_cols])
X_test[numeric_cols] = imputer.transform(X_test[numeric_cols])
```

**MAR — KNNImputer:**
```python
from sklearn.impute import KNNImputer

imputer = KNNImputer(n_neighbors=5)
imputer.fit(X_train[numeric_cols])
X_train[numeric_cols] = imputer.transform(X_train[numeric_cols])
X_test[numeric_cols] = imputer.transform(X_test[numeric_cols])
```

**MNAR — Median + indicator:**
```python
from sklearn.impute import SimpleImputer

# Create indicator BEFORE imputation (never after)
X_train[f'{col}_was_missing'] = X_train[col].isnull().astype(int)
X_test[f'{col}_was_missing'] = X_test[col].isnull().astype(int)

imputer = SimpleImputer(strategy='median')
imputer.fit(X_train[[col]])
X_train[col] = imputer.transform(X_train[[col]])
X_test[col] = imputer.transform(X_test[[col]])

# MNAR WARNING: imputed values are likely biased. Document this.
# The _was_missing indicator may be more predictive than the imputed value.
```

**Time-Series — interpolate:**
```python
GAP_THRESHOLD = 3  # Never interpolate across more than this many consecutive nulls

def safe_time_interpolate(series, gap_threshold=GAP_THRESHOLD):
    """Interpolate only within short gaps; leave long gaps as NaN."""
    # Identify gap lengths
    null_groups = series.isnull().astype(int)
    cumsum = null_groups.cumsum()
    gap_sizes = series.groupby((null_groups != null_groups.shift()).cumsum()).transform('sum')

    interpolated = series.interpolate(method='time')

    # Restore NaN where gap exceeded threshold
    long_gap_mask = (series.isnull()) & (gap_sizes > gap_threshold)
    interpolated[long_gap_mask] = np.nan

    return interpolated
```

---

### Numeric Discrete

| Mechanism | Recommended Strategy | Notes |
|-----------|---------------------|-------|
| MCAR | Mode (most_frequent) | Preserves the distribution of integer levels |
| MAR | KNN (ordinal-aware) | Treat levels as ordered integers before KNN |
| MNAR | Mode + `_was_missing` indicator | Same pattern as continuous MNAR |

**MCAR — Mode:**
```python
from sklearn.impute import SimpleImputer

imputer = SimpleImputer(strategy='most_frequent')
imputer.fit(X_train[[col]])
X_train[col] = imputer.transform(X_train[[col]]).astype('Int64')
X_test[col] = imputer.transform(X_test[[col]]).astype('Int64')
```

**MAR — KNN ordinal-aware:**
```python
from sklearn.impute import KNNImputer
import numpy as np

# KNNImputer works on numeric arrays; discrete columns need rounding post-impute
imputer = KNNImputer(n_neighbors=5)
imputer.fit(X_train[ordinal_cols])
X_train[ordinal_cols] = np.round(imputer.transform(X_train[ordinal_cols])).astype('Int64')
X_test[ordinal_cols] = np.round(imputer.transform(X_test[ordinal_cols])).astype('Int64')
```

**MNAR — Mode + indicator:**
```python
from sklearn.impute import SimpleImputer

X_train[f'{col}_was_missing'] = X_train[col].isnull().astype(int)
X_test[f'{col}_was_missing'] = X_test[col].isnull().astype(int)

imputer = SimpleImputer(strategy='most_frequent')
imputer.fit(X_train[[col]])
X_train[col] = imputer.transform(X_train[[col]]).astype('Int64')
X_test[col] = imputer.transform(X_test[[col]]).astype('Int64')
```

---

### Categorical Low-Cardinality

| Mechanism | Recommended Strategy | Notes |
|-----------|---------------------|-------|
| MCAR | Mode | Fill with most common label |
| MAR | Mode (simple) or Random Forest imputer | RF imputer is more accurate but slower |
| MNAR | Explicit "Unknown" category | Missingness is itself a signal; do not obscure it |

**MCAR — Mode:**
```python
from sklearn.impute import SimpleImputer

imputer = SimpleImputer(strategy='most_frequent')
imputer.fit(X_train[[col]])
X_train[col] = imputer.transform(X_train[[col]]).ravel()
X_test[col] = imputer.transform(X_test[[col]]).ravel()
```

**MAR — Random Forest imputer (via sklearn IterativeImputer + RF estimator):**
```python
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import IterativeImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OrdinalEncoder

# Encode categoricals first (IterativeImputer requires numeric input)
enc = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
X_train_enc = enc.fit_transform(X_train[cat_cols])
X_test_enc = enc.transform(X_test[cat_cols])

imputer = IterativeImputer(
    estimator=RandomForestClassifier(n_estimators=50, random_state=42),
    max_iter=5,
    random_state=42
)
imputer.fit(X_train_enc)
X_train[cat_cols] = enc.inverse_transform(
    np.round(imputer.transform(X_train_enc)).astype(int)
)
X_test[cat_cols] = enc.inverse_transform(
    np.round(imputer.transform(X_test_enc)).astype(int)
)
```

**MNAR — Explicit "Unknown":**
```python
X_train[col] = X_train[col].fillna('Unknown')
X_test[col] = X_test[col].fillna('Unknown')
# Downstream encoders must handle 'Unknown' as a valid category.
```

---

### Categorical High-Cardinality

**Always use "Unknown" — mode imputation is meaningless at 1000+ categories.**

With high cardinality, the mode covers a tiny fraction of the distribution. Any imputed label introduces false signal. "Unknown" is always the correct choice, regardless of mechanism.

```python
X_train[col] = X_train[col].fillna('Unknown')
X_test[col] = X_test[col].fillna('Unknown')
# Ensure downstream frequency/target encoders include 'Unknown' in their mapping.
```

---

### Datetime

| Situation | Recommended Strategy | Notes |
|-----------|---------------------|-------|
| Regular frequency (hourly, daily) | Interpolate between surrounding timestamps | Produces plausible intermediate values |
| Irregular frequency | Set to None + flag | No safe interpolation exists |

**Regular frequency — interpolate:**
```python
import pandas as pd

# Ensure column is datetime dtype first
df[col] = pd.to_datetime(df[col], errors='coerce')

# Convert to numeric, interpolate, convert back
numeric_ts = df[col].astype(np.int64).astype(float)
numeric_ts[df[col].isnull()] = np.nan
interpolated = numeric_ts.interpolate(method='linear', limit=3, limit_direction='forward')
df[col] = pd.to_datetime(interpolated, unit='ns', errors='coerce')
```

**Irregular frequency — flag and leave null:**
```python
df[f'{col}_was_missing'] = df[col].isnull().astype(int)
# Do not impute. Downstream models must handle NaT or the column must be dropped.
```

---

### Boolean

**Always: mode imputation + always create `_was_missing` indicator.**

Boolean missingness is always informative — a missing True/False is rarely random.

```python
from sklearn.impute import SimpleImputer

# Indicator first
X_train[f'{col}_was_missing'] = X_train[col].isnull().astype(int)
X_test[f'{col}_was_missing'] = X_test[col].isnull().astype(int)

# Convert bool to int for imputer compatibility
X_train[col] = X_train[col].astype('object')
X_test[col] = X_test[col].astype('object')

imputer = SimpleImputer(strategy='most_frequent')
imputer.fit(X_train[[col]])
X_train[col] = imputer.transform(X_train[[col]]).ravel().astype(bool)
X_test[col] = imputer.transform(X_test[[col]]).ravel().astype(bool)
```

---

### Text (Free-Form)

**Always: "[MISSING]" token or empty string. NEVER hallucinate text.**

```python
# Option A: Sentinel token (preferred — downstream NLP models can learn to ignore it)
X_train[col] = X_train[col].fillna('[MISSING]')
X_test[col] = X_test[col].fillna('[MISSING]')

# Option B: Empty string (use when model chokes on unknown tokens)
X_train[col] = X_train[col].fillna('')
X_test[col] = X_test[col].fillna('')

# Always create indicator regardless
X_train[f'{col}_was_missing'] = X_train[col].isin(['[MISSING]', '']).astype(int)
X_test[f'{col}_was_missing'] = X_test[col].isin(['[MISSING]', '']).astype(int)
```

Do NOT:
- Fill with average text, generated summaries, or any model-generated text
- Use the mode (most common text string) — this is almost never a valid imputation

---

## Quick-Reference Summary Table

| Column Type | MCAR | MAR | MNAR |
|-------------|------|-----|------|
| Numeric Continuous | `SimpleImputer(strategy='median')` | `IterativeImputer` or `KNNImputer` | Median + `_was_missing` |
| Numeric Discrete | `SimpleImputer(strategy='most_frequent')` | KNN + round | Mode + `_was_missing` |
| Categorical Low-Card | Mode | Mode or RF IterativeImputer | `"Unknown"` |
| Categorical High-Card | `"Unknown"` | `"Unknown"` | `"Unknown"` |
| Datetime (regular) | Interpolate (limit=3) | Interpolate (limit=3) | None + flag |
| Datetime (irregular) | None + flag | None + flag | None + flag |
| Boolean | Mode + `_was_missing` | Mode + `_was_missing` | Mode + `_was_missing` |
| Text | `"[MISSING]"` | `"[MISSING]"` | `"[MISSING]"` |
