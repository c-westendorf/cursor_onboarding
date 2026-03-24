# Column Type Transforms

Per-type transform recipes with complete, copy-paste-ready code. Apply these in Step 3 of the feature engineering workflow. Reference `references/dtype-router.md` for the `classify_columns()` function that assigns each column to a type bucket.

Always fit scalers, encoders, and other stateful transforms on training data ONLY. See `references/leakage-guard.md`.

---

## Numeric Continuous

Columns classified as `numeric_continuous` (float dtypes, >20 unique values).

**Skewness check — do this first:**
```python
from scipy.stats import skew
import numpy as np

for col in col_types['numeric_continuous']:
    col_skew = skew(df[col].dropna())
    print(f"{col}: skew={col_skew:.2f}")
```

**Skewed distribution (|skew| > 1) — log transform:**
```python
# np.log1p handles zero values safely (log(1+x))
for col in col_types['numeric_continuous']:
    if abs(skew(df[col].dropna())) > 1 and df[col].min() >= 0:
        df[f'{col}_log'] = np.log1p(df[col])
        # Keep original or drop based on downstream model type
```

**Standardize for linear models:**
```python
from sklearn.preprocessing import StandardScaler, RobustScaler

# StandardScaler: zero mean, unit variance — use when outliers are minimal
scaler = StandardScaler()
df_scaled = df[col_types['numeric_continuous']].copy()
df_scaled[col_types['numeric_continuous']] = scaler.fit_transform(
    df_scaled[col_types['numeric_continuous']]
)

# RobustScaler: median-centered, IQR-scaled — use when outliers are present
robust_scaler = RobustScaler()
df_robust = df[col_types['numeric_continuous']].copy()
df_robust[col_types['numeric_continuous']] = robust_scaler.fit_transform(
    df_robust[col_types['numeric_continuous']]
)
```

**Polynomial features for linear models (non-linear signal):**
```python
from sklearn.preprocessing import PolynomialFeatures
import pandas as pd

# degree=2 with interaction_only=False: adds x^2 terms and x*y cross-terms
# WARNING: grows features quadratically — limit to ≤10 input columns
poly = PolynomialFeatures(degree=2, interaction_only=False, include_bias=False)
poly_cols = col_types['numeric_continuous'][:10]  # cap at 10 to avoid explosion
poly_array = poly.fit_transform(df[poly_cols])
poly_feature_names = poly.get_feature_names_out(poly_cols)
df_poly = pd.DataFrame(poly_array, columns=poly_feature_names, index=df.index)
```

**Manual interaction terms (domain-driven):**
```python
# Ratio: use when the ratio has a known interpretation
df['a_div_b'] = df['a'] / (df['b'] + 1e-8)  # epsilon prevents div-by-zero

# Product: use when multiplicative effect is expected
df['a_times_b'] = df['a'] * df['b']

# Difference: use when the gap has meaning
df['a_minus_b'] = df['a'] - df['b']
```

---

## Numeric Discrete

Columns classified as `numeric_discrete` (≤20 unique integer values).

```python
# For tree-based models (XGBoost, LightGBM, RandomForest): leave as-is
# Trees split on integer values natively

# For linear models with ordered levels (e.g., rating 1-5):
from sklearn.preprocessing import OrdinalEncoder
ord_enc = OrdinalEncoder()
df[col_types['numeric_discrete']] = ord_enc.fit_transform(
    df[col_types['numeric_discrete']]
)

# For linear models with unordered discrete values (e.g., product_count in {1,2,3,5,10}):
discrete_dummies = pd.get_dummies(
    df[col_types['numeric_discrete']],
    drop_first=True,
    dtype=int
)
df = pd.concat([df.drop(columns=col_types['numeric_discrete']), discrete_dummies], axis=1)
```

---

## Categorical Low-Cardinality (≤20 unique values)

Columns classified as `categorical_low_card`.

**For tree-based models — ordinal encoding:**
```python
from sklearn.preprocessing import OrdinalEncoder

ord_enc = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
ord_enc.fit(df_train[col_types['categorical_low_card']])
df_train[col_types['categorical_low_card']] = ord_enc.transform(
    df_train[col_types['categorical_low_card']]
)
df_test[col_types['categorical_low_card']] = ord_enc.transform(
    df_test[col_types['categorical_low_card']]
)
```

**For linear models — one-hot encoding:**
```python
# drop_first=True prevents multicollinearity
dummies = pd.get_dummies(
    df[col_types['categorical_low_card']],
    drop_first=True,
    dtype=int
)
df = pd.concat([df.drop(columns=col_types['categorical_low_card']), dummies], axis=1)
```

**For any model + supervised task — fold-based target encoding (prevents leakage):**
```python
# Paste safe_target_encode from references/leakage-guard.md, then:

from sklearn.model_selection import KFold

def safe_target_encode(df, col, target_col, n_folds=5, smoothing=10):
    """Fold-based target encoding that prevents leakage."""
    encoded = pd.Series(index=df.index, dtype=float)
    global_mean = df[target_col].mean()
    kf = KFold(n_splits=n_folds, shuffle=True, random_state=42)
    for train_idx, val_idx in kf.split(df):
        train_means = df.iloc[train_idx].groupby(col)[target_col].agg(['mean', 'count'])
        smooth_means = (
            (train_means['mean'] * train_means['count'] + global_mean * smoothing)
            / (train_means['count'] + smoothing)
        )
        encoded.iloc[val_idx] = df.iloc[val_idx][col].map(smooth_means).fillna(global_mean)
    return encoded

for col in col_types['categorical_low_card']:
    df[f'{col}_target_enc'] = safe_target_encode(df, col, target_col='target')
```

---

## Categorical High-Cardinality (>20 unique values)

Columns classified as `categorical_high_card`. NEVER one-hot encode these — it causes dimensionality explosion.

**Frequency encoding (model-agnostic, no target needed):**
```python
for col in col_types['categorical_high_card']:
    freq_map = df_train[col].value_counts(normalize=True)
    df_train[f'{col}_freq'] = df_train[col].map(freq_map).fillna(0)
    df_test[f'{col}_freq'] = df_test[col].map(freq_map).fillna(0)
```

**Fold-based target encoding (use the same safe_target_encode function above):**
```python
for col in col_types['categorical_high_card']:
    df_train[f'{col}_target_enc'] = safe_target_encode(df_train, col, 'target')
    # For test: compute global encoding map from full training data
    global_mean = df_train['target'].mean()
    train_map = df_train.groupby(col)['target'].mean()
    df_test[f'{col}_target_enc'] = df_test[col].map(train_map).fillna(global_mean)
```

**Hash encoding (when you need a fixed-width numeric representation):**
```python
# Requires: pip install category_encoders
import category_encoders as ce

hash_enc = ce.HashingEncoder(cols=col_types['categorical_high_card'], n_components=8)
hash_enc.fit(df_train[col_types['categorical_high_card']])
df_train_hashed = hash_enc.transform(df_train[col_types['categorical_high_card']])
df_test_hashed = hash_enc.transform(df_test[col_types['categorical_high_card']])
```

---

## Datetime

Columns classified as `datetime`.

**Always extract these base features:**
```python
for col in col_types['datetime']:
    df[f'{col}_year'] = df[col].dt.year
    df[f'{col}_month'] = df[col].dt.month
    df[f'{col}_day_of_week'] = df[col].dt.dayofweek   # 0=Monday, 6=Sunday
    df[f'{col}_day_of_month'] = df[col].dt.day
    df[f'{col}_hour'] = df[col].dt.hour
    df[f'{col}_quarter'] = df[col].dt.quarter
    df[f'{col}_is_weekend'] = (df[col].dt.dayofweek >= 5).astype(int)
```

**Cyclical encoding — preserves circular structure (Jan is close to Dec, midnight close to 11 PM):**
```python
for col in col_types['datetime']:
    hour = df[col].dt.hour
    month = df[col].dt.month
    dow = df[col].dt.dayofweek

    df[f'{col}_hour_sin'] = np.sin(2 * np.pi * hour / 24)
    df[f'{col}_hour_cos'] = np.cos(2 * np.pi * hour / 24)
    df[f'{col}_month_sin'] = np.sin(2 * np.pi * month / 12)
    df[f'{col}_month_cos'] = np.cos(2 * np.pi * month / 12)
    df[f'{col}_dow_sin'] = np.sin(2 * np.pi * dow / 7)
    df[f'{col}_dow_cos'] = np.cos(2 * np.pi * dow / 7)
```

**Time-since features:**
```python
for col in col_types['datetime']:
    reference_date = df[col].min()
    df[f'{col}_days_since_start'] = (df[col] - reference_date).dt.days
    df[f'{col}_days_since_today'] = (pd.Timestamp.now() - df[col]).dt.days
```

**Time-series lag and rolling features (fit on train only):**
```python
# Sort by timestamp before computing lag/rolling
df = df.sort_values(timestamp_col)

lag_col = 'value'   # replace with your target/signal column
for lag in [1, 7, 14, 30]:
    df[f'{lag_col}_lag_{lag}'] = df[lag_col].shift(lag)

for window in [7, 30]:
    df[f'{lag_col}_rolling_mean_{window}'] = df[lag_col].shift(1).rolling(window).mean()
    df[f'{lag_col}_rolling_std_{window}'] = df[lag_col].shift(1).rolling(window).std()

# .shift(1) before rolling ensures no same-timestep leakage
```

---

## Text (Free-Form)

Columns classified as `text_free`.

**Always add meta-features first (model-agnostic, no vectorization needed):**
```python
for col in col_types['text_free']:
    df[f'{col}_char_len'] = df[col].str.len().fillna(0)
    df[f'{col}_word_count'] = df[col].str.split().str.len().fillna(0)
    df[f'{col}_has_digits'] = df[col].str.contains(r'\d', na=False).astype(int)
    df[f'{col}_has_punctuation'] = df[col].str.contains(r'[!?.,;:]', na=False).astype(int)
```

**TF-IDF for short text (avg <50 tokens):**
```python
from sklearn.feature_extraction.text import TfidfVectorizer
import scipy.sparse

for col in col_types['text_free']:
    tfidf = TfidfVectorizer(max_features=100, ngram_range=(1, 1), min_df=2)
    tfidf.fit(df_train[col].fillna(''))
    train_tfidf = tfidf.transform(df_train[col].fillna(''))
    test_tfidf = tfidf.transform(df_test[col].fillna(''))

    # Convert to DataFrame and join
    tfidf_cols = [f'{col}_tfidf_{w}' for w in tfidf.get_feature_names_out()]
    df_train = df_train.join(
        pd.DataFrame(train_tfidf.toarray(), columns=tfidf_cols, index=df_train.index)
    )
    df_test = df_test.join(
        pd.DataFrame(test_tfidf.toarray(), columns=tfidf_cols, index=df_test.index)
    )
```

**TF-IDF for long text (avg ≥50 tokens):**
```python
# Increase max_features and add bigrams for longer documents
tfidf = TfidfVectorizer(max_features=500, ngram_range=(1, 2), min_df=3, sublinear_tf=True)
```

---

## Boolean

Columns classified as `boolean`.

```python
# Convert True/False to 1/0 — no other transform needed
for col in col_types['boolean']:
    df[col] = df[col].astype(int)
```
