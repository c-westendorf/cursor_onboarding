# Leakage Guard

Data leakage is the #1 silent model killer. It makes validation metrics look great while production performance is terrible. Run this checklist at every transform boundary.

## The Core Rule

**All `.fit()` calls happen on training data ONLY. All `.transform()` calls can happen on any split.**

## Leakage Checklist

Run before finalizing any imputation or feature engineering pipeline:

### 1. Fit-Transform Boundary

```python
def verify_fit_transform_boundary(pipeline, X_train, X_test):
    """Verify that pipeline was fit on train only."""
    # Fit on train
    pipeline.fit(X_train)

    # Transform both splits
    X_train_transformed = pipeline.transform(X_train)
    X_test_transformed = pipeline.transform(X_test)

    # Verify shapes match expectations
    assert X_train_transformed.shape[0] == X_train.shape[0]
    assert X_test_transformed.shape[0] == X_test.shape[0]
    assert X_train_transformed.shape[1] == X_test_transformed.shape[1], \
        f"Column mismatch: train has {X_train_transformed.shape[1]}, test has {X_test_transformed.shape[1]}"

    return True
```

### 2. No Future Information (Time-Series)

For any lag or window feature:
- Minimum lag >= 1 (no same-timestep features)
- Rolling windows are backward-looking ONLY
- No features derived from future events

```python
def verify_no_future_leakage(df, timestamp_col, feature_cols):
    """Check that no feature uses future information."""
    issues = []

    for col in feature_cols:
        # Check if feature correlates with future target more than past
        # This is a heuristic — manual review is still needed
        if 'lead' in col.lower() or 'forward' in col.lower() or 'next' in col.lower():
            issues.append(f"Suspicious feature name suggests future data: {col}")

    return issues
```

### 3. Target Encoding Safety

Target encoding MUST use fold-based approach to prevent leakage:

```python
from sklearn.model_selection import KFold

def safe_target_encode(df, col, target_col, n_folds=5, smoothing=10):
    """Fold-based target encoding that prevents leakage."""
    encoded = pd.Series(index=df.index, dtype=float)
    global_mean = df[target_col].mean()

    kf = KFold(n_splits=n_folds, shuffle=True, random_state=42)

    for train_idx, val_idx in kf.split(df):
        # Calculate means from OTHER folds only
        train_means = df.iloc[train_idx].groupby(col)[target_col].agg(['mean', 'count'])

        # Smoothed encoding
        smooth_means = (
            (train_means['mean'] * train_means['count'] + global_mean * smoothing) /
            (train_means['count'] + smoothing)
        )

        # Apply to held-out fold
        encoded.iloc[val_idx] = df.iloc[val_idx][col].map(smooth_means).fillna(global_mean)

    return encoded


def safe_target_encode_test(df_test, col, train_encoding_map, global_mean):
    """Apply target encoding to test set using ONLY training statistics."""
    return df_test[col].map(train_encoding_map).fillna(global_mean)
```

### 4. Imputation Leakage

Imputers must be fit on training data only:

```python
# WRONG — leaks test statistics into training
from sklearn.impute import SimpleImputer
imputer = SimpleImputer(strategy='mean')
df_full_imputed = imputer.fit_transform(df_full)  # LEAKAGE!

# CORRECT — fit on train, transform both
imputer = SimpleImputer(strategy='mean')
imputer.fit(X_train)  # fit on train only
X_train_imputed = imputer.transform(X_train)
X_test_imputed = imputer.transform(X_test)
```

### 5. Feature Selection Leakage

Feature selection must be performed on training data only:

```python
# WRONG — uses full dataset for feature selection
from featurewiz import FeatureWiz
fwiz = FeatureWiz(corr_limit=0.7)
X_selected, y = fwiz.fit_transform(X_full, y_full)  # LEAKAGE!

# CORRECT — select on train, apply to test
fwiz = FeatureWiz(corr_limit=0.7)
X_train_selected, y_train = fwiz.fit_transform(X_train, y_train)
selected_features = fwiz.features
X_test_selected = X_test[selected_features]
```

## Suspicion Signals

If you see any of these, investigate immediately:
- Any single feature with >0.95 correlation with target
- Validation accuracy significantly higher than expected for the task
- Model performance drops dramatically on truly held-out data
- Features that wouldn't be available at prediction time in production

## Documentation Requirement

For every transform in the pipeline, document:
```
Transform: [name]
Fit set: training data only? [YES/NO]
Uses future info: [YES/NO]
Uses target: [YES/NO — if yes, how is leakage prevented?]
Production-safe: [YES/NO — would this work on a single new row?]
```
