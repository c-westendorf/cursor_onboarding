# Dataset Audit Pattern

Run this audit at the start of any data workflow. Score each dimension, flag issues with severity, and recommend fixes.

## The 5 Dimensions

### 1. Completeness
Are all expected values present?

```python
def audit_completeness(df, expected_columns=None):
    """Score completeness: missing values and coverage gaps."""
    results = {}

    # Column presence
    if expected_columns:
        missing_cols = set(expected_columns) - set(df.columns)
        results['missing_columns'] = list(missing_cols)
        results['column_coverage'] = 1 - len(missing_cols) / len(expected_columns)

    # Per-column null rates
    null_rates = (df.isnull().sum() / len(df)).to_dict()
    results['null_rates'] = {col: rate for col, rate in null_rates.items() if rate > 0}

    # Severity assignment
    results['issues'] = []
    for col, rate in results['null_rates'].items():
        if rate > 0.50:
            severity = 'critical'
        elif rate > 0.10:
            severity = 'medium'
        else:
            severity = 'low'
        results['issues'].append({
            'column': col, 'null_rate': round(rate, 4),
            'severity': severity,
            'fix': 'Drop column' if rate > 0.80 else 'Impute (see missing-data-imputation skill)'
        })

    results['score'] = round((1 - df.isnull().sum().sum() / df.size) * 100, 1)
    return results
```

### 2. Consistency
Are records internally consistent? No contradictions, duplicates, or schema drift?

```python
def audit_consistency(df, key_columns=None):
    """Score consistency: duplicates, type stability, format uniformity."""
    results = {'issues': []}

    # Duplicate check
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        results['issues'].append({
            'type': 'duplicates', 'count': int(dup_count),
            'severity': 'medium' if dup_count / len(df) < 0.05 else 'critical',
            'fix': 'Deduplicate on natural key or all columns'
        })

    # Key uniqueness
    if key_columns:
        key_dups = df.duplicated(subset=key_columns).sum()
        if key_dups > 0:
            results['issues'].append({
                'type': 'key_duplicates', 'columns': key_columns, 'count': int(key_dups),
                'severity': 'critical',
                'fix': 'Deduplicate on key columns, keep latest'
            })

    # Mixed types in object columns
    for col in df.select_dtypes(include=['object']).columns:
        sample = df[col].dropna().head(1000)
        numeric_frac = sample.apply(lambda x: str(x).replace('.', '').replace('-', '').isdigit()).mean()
        if 0.2 < numeric_frac < 0.8:
            results['issues'].append({
                'type': 'mixed_types', 'column': col,
                'numeric_fraction': round(numeric_frac, 2),
                'severity': 'medium',
                'fix': 'Investigate and cast to correct dtype'
            })

    results['score'] = max(0, 100 - len(results['issues']) * 15)
    return results
```

### 3. Accuracy
Do values make sense given the domain?

Check for:
- Values outside physically plausible ranges (negative ages, percentages > 100)
- Sentinel values masquerading as data (-999, 9999, "N/A", "#REF!")
- Statistical anomalies (values > 5 standard deviations from mean)

Severity: **critical** if it would corrupt a model, **medium** if it would degrade performance, **low** if cosmetic.

### 4. Timeliness
Is the data current enough for the intended use?

Check:
- Date range: does `max(date_column)` match expectations?
- Freshness: how old is the most recent record?
- Gaps: are there unexpected holes in the timeline?

Severity: **critical** if data is from wrong time period, **medium** if stale but usable, **low** if minor gaps.

### 5. Relevance
Does this data actually answer our question?

Check:
- Are there columns with zero variance (constant values)?
- Are there columns completely unrelated to the modeling task?
- Is the granularity correct (row = one observation of the entity we care about)?

## Synthesize

```python
def synthesize_audit(completeness, consistency, accuracy_notes, timeliness_notes, relevance_notes):
    """Combine all dimensions into a single audit report."""
    all_issues = (
        completeness.get('issues', []) +
        consistency.get('issues', []) +
        accuracy_notes + timeliness_notes + relevance_notes
    )

    critical_count = sum(1 for i in all_issues if i.get('severity') == 'critical')

    return {
        'overall_health': 'poor' if critical_count > 0 else 'fair' if len(all_issues) > 5 else 'good',
        'dimensions': {
            'completeness': completeness.get('score', 0),
            'consistency': consistency.get('score', 0),
        },
        'total_issues': len(all_issues),
        'critical_issues': critical_count,
        'all_issues': all_issues,
    }
```
