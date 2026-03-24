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

## Scale Classification

Alongside shape tags, classify the dataset's scale tier to drive strategy selection:

```python
def classify_scale(df):
    """Returns scale tier that drives strategy selection.

    Tiers:
      - "small":      ≤100K rows, <500MB — full pandas, no sampling needed
      - "medium":     ≤1M rows, <2GB — pandas OK, some operations need sampling
      - "large":      ≤10M rows, <16GB — sample for statistics, consider Polars/Dask
      - "very_large": >10M rows or >16GB — must use Dask/Polars, mandatory sampling
    """
    mem_gb = df.memory_usage(deep=True).sum() / 1e9
    n_rows = len(df)
    if n_rows <= 100_000 and mem_gb < 0.5:
        return "small"
    elif n_rows <= 1_000_000 and mem_gb < 2:
        return "medium"
    elif n_rows <= 10_000_000 and mem_gb < 16:
        return "large"
    else:
        return "very_large"
```

### Scale-Aware Strategy Table

| Skill | small/medium | large | very_large |
|---|---|---|---|
| **data-cleaning** | Standard pandas workflow | Replace `.apply()` regex with vectorized `.str.replace()`. Use `dask.dataframe.read_csv()` instead of chunked concat. | Mandatory Dask/Polars for loading. Partition-level dedup. Skip full-dataset `.drop_duplicates()`. |
| **data-quality-assurance** | Full statistical profiling | Sample 500K rows for `.quantile()`, KS-test, `.value_counts()`. Full-data checks limited to schema + null rates. | All statistical tests on 1M stratified sample. Use effect size (Cohen's d) alongside p-values (KS-test inflates on large N). |
| **missing-data-imputation** | IterativeImputer, KNNImputer | Replace KNNImputer with median for MAR. Fit IterativeImputer on 200K sample, apply to full. | Median/mode only. Fit on 500K sample, apply to partitions. Consider missingness-as-feature instead of imputation. |
| **eda-comprehensive** | Full correlation matrix, all tests | Statistics on 500K sample. Replace Pearson/Spearman matrix with mutual information. Skip pairwise chi-squared for >50 categoricals. | All analysis on 1M sample with confidence intervals. Replace correlation with LightGBM importance. Automated screening only for >200 cols. |
| **feature-engineering** | Standard featurewiz | `featurewiz(nrows_limit=200_000, dask_xgboost_flag=True)`. Fit manual transforms on 200K sample. | `featurewiz(nrows_limit=200_000, corr_limit=0.5, dask_xgboost_flag=True)`. Consider Polars for string/datetime ops. |

### When to Sample vs. When to Use Full Data

| Operation | Sample OK? | Rationale |
|---|---|---|
| Schema validation, dtype checks | **Never sample** | Must check all columns |
| Null rate computation | **Never sample** | O(n) scan, fast on full data |
| Column name normalization | **Never sample** | Must apply to all data |
| Deduplication | **Never sample** | Must check all rows |
| Statistical tests (KS, chi², Kruskal-Wallis) | **Always sample at large/very_large** | Tests have inflated power on large N |
| Correlation matrices | **Always sample at large/very_large** | O(n × p²) compute |
| Outlier detection (IQR) | **Sample OK at large/very_large** | Quantiles estimated from sample |
| Imputer fitting (Iterative, KNN) | **Always sample at large/very_large** | O(n²) compute |
| Transform fitting (StandardScaler, etc.) | **Sample OK at large** | Statistics (mean, std) converge quickly |
