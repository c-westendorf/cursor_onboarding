# Sampling Strategy Pattern

Reusable sampling utility for skills that need to handle large datasets. Used by all skills when `classify_scale()` returns `"large"` or `"very_large"`.

## Core Sampling Function

```python
def get_analysis_sample(df, max_rows=500_000, stratify_col=None, random_state=42):
    """Get a representative sample for statistical analysis.

    Use when:
      - Dataset > 500K rows AND
      - Operation is O(n²) or involves statistical testing

    Do NOT use for:
      - Schema checks, null rate computation, deduplication
      - Column name normalization
      - Any operation that must see all rows

    Args:
        df: Input DataFrame
        max_rows: Maximum sample size (default 500K balances speed and accuracy)
        stratify_col: Column to stratify by (preserves class balance).
                      Must have <100 unique values.
        random_state: Reproducibility seed

    Returns:
        DataFrame — either the original (if small enough) or a sample
    """
    if len(df) <= max_rows:
        return df

    if stratify_col and stratify_col in df.columns:
        n_unique = df[stratify_col].nunique()
        if n_unique < 100:
            from sklearn.model_selection import train_test_split
            sample, _ = train_test_split(
                df, train_size=max_rows,
                stratify=df[stratify_col],
                random_state=random_state
            )
            return sample

    return df.sample(n=max_rows, random_state=random_state)
```

## Manifest Reporting

When sampling is used, the manifest should document it:

```python
manifest["sampling"] = {
    "sample_used": True,
    "sample_size": len(sample),
    "total_rows": len(df),
    "sample_fraction": len(sample) / len(df),
    "stratify_col": stratify_col,
    "random_state": random_state
}
```

When no sampling is used:
```python
manifest["sampling"] = {
    "sample_used": False,
    "sample_size": len(df),
    "total_rows": len(df)
}
```

## Sample Size Guidelines

| Operation | Recommended max_rows | Rationale |
|---|---|---|
| Correlation matrix | 500,000 | Pearson converges well at this N |
| KS-test / chi-squared | 100,000 | Statistical tests over-reject at large N |
| IterativeImputer fitting | 200,000 | O(n × p × max_iter) compute |
| KNNImputer fitting | 100,000 | O(n²) distance calculation |
| featurewiz SULOV/MRMR | 200,000 | Built-in via `nrows_limit` parameter |
| Outlier detection (IQR) | 500,000 | Quantiles stable at this N |
| Logistic regression (MCAR diagnosis) | 200,000 | Converges quickly |

## Effect Size Guidance for Large Samples

> **Plain language:** When you have millions of rows, every tiny difference looks "statistically significant" because the tests have so much data. Use effect sizes to distinguish real patterns from noise.

| Test | Effect Size Metric | Small | Medium | Large |
|---|---|---|---|---|
| KS-test | KS statistic (D) | 0.01 | 0.06 | 0.14 |
| Chi-squared | Cramer's V | 0.10 | 0.30 | 0.50 |
| t-test / Mann-Whitney | Cohen's d | 0.20 | 0.50 | 0.80 |
| Correlation | |r| | 0.10 | 0.30 | 0.50 |

When `classify_scale()` returns `"large"` or `"very_large"`, report effect sizes alongside p-values in all manifests.
