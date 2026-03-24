# Shape-Aware Strategy

Data shape determines which algorithms, sampling strategies, and visualization approaches are appropriate. Classify shape first, then branch.

## Shape Classification

```python
def classify_shape(df):
    """Classify a DataFrame's shape characteristics."""
    n_rows, n_cols = df.shape
    null_rate = df.isnull().sum().sum() / df.size
    sparse_col_rate = (df.isnull().mean() > 0.50).mean()  # fraction of cols >50% null

    has_nested = any(
        df[col].dropna().apply(lambda x: isinstance(x, (dict, list))).any()
        for col in df.select_dtypes(include=['object']).columns[:10]  # sample for speed
    )

    has_datetime_index = (
        isinstance(df.index, pd.DatetimeIndex) or
        any(pd.api.types.is_datetime64_any_dtype(df[col]) for col in df.columns)
    )

    shape_tags = []
    if n_cols > 100:
        shape_tags.append('wide')
    if n_rows > 1_000_000:
        shape_tags.append('tall')
    if sparse_col_rate > 0.30:
        shape_tags.append('sparse')
    if has_nested:
        shape_tags.append('nested')
    if has_datetime_index:
        shape_tags.append('time_series')

    if not shape_tags:
        shape_tags.append('standard')

    return {
        'tags': shape_tags,
        'rows': n_rows,
        'cols': n_cols,
        'overall_null_rate': round(null_rate, 4),
        'sparse_col_fraction': round(sparse_col_rate, 4),
    }
```

## Branching Rules

### Wide (>100 columns)

| Playbook | Adaptation |
|----------|------------|
| **Cleaning** | Batch column-name normalization; group by prefix for systematic cleaning |
| **QA** | Batch quality checks; report by column group, not individual |
| **Imputation** | Batch by column-type group; multivariate methods (IterativeImputer) for correlated blocks |
| **EDA** | Automated screening only: variance/skew/null rate for all; visualize top 20. Skip pairwise correlation matrix (use mutual information instead) |
| **Feature Engineering** | Aggressive selection is MANDATORY. featurewiz SULOV ideal here. Consider PCA for dimension reduction |

### Tall (>1M rows)

| Playbook | Adaptation |
|----------|------------|
| **Cleaning** | Chunked reading with `chunksize` parameter or dask |
| **QA** | Sample-based statistical tests with confidence intervals |
| **Imputation** | Sample for missingness diagnosis; apply imputer to full data |
| **EDA** | Stratified sampling for visualization; binned aggregation for scatter plots |
| **Feature Engineering** | Use `dask_xgboost_flag=True` in featurewiz; sampling for validation |

### Sparse (>30% of columns are >50% null)

| Playbook | Adaptation |
|----------|------------|
| **Cleaning** | Flag sparse columns early; separate sparse vs dense pipelines |
| **QA** | Sparsity-aware thresholds (lower completeness expectations for known-sparse) |
| **Imputation** | Consider matrix factorization or KNN with sparse-aware distance |
| **EDA** | Non-zero value distributions; co-occurrence matrices |
| **Feature Engineering** | Sparse-compatible transforms (CSR matrix); avoid polynomial features (combinatorial explosion) |

### Nested (columns contain dicts/lists/JSON)

| Playbook | Adaptation |
|----------|------------|
| **Cleaning** | Flatten with `pd.json_normalize()`; decide max depth; handle arrays (explode vs. aggregate) |
| **QA** | Validate post-flatten structure matches expected schema |
| **Imputation** | Handle structural nulls (field absent vs. field=null) differently |
| **EDA** | Analyze after flattening |
| **Feature Engineering** | JSON path features, array length features, nested aggregations |

### Time-Series (has temporal index or datetime columns)

| Playbook | Adaptation |
|----------|------------|
| **Cleaning** | Sort by timestamp; infer and validate frequency; detect and classify gaps |
| **QA** | Validate temporal completeness (no unexpected gaps); check stationarity |
| **Imputation** | ONLY backward-looking interpolation; NEVER use future values; respect gap thresholds |
| **EDA** | Trend/seasonality decomposition; ACF/PACF; ADF stationarity test |
| **Feature Engineering** | Lag features, rolling windows (backward only), cyclical encoding. featurewiz for selection AFTER manual temporal features |

## Standard (<100 cols, <1M rows, not sparse/nested/temporal)

No special adaptations needed. Run all playbooks with default settings.
