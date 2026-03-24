# EDA Code Recipes

Complete, copy-paste-ready code for the EDA workflow steps that are summarized in `SKILL.md`. Use these during Steps 3, 5, 6, and 7 of the eda-comprehensive workflow.

---

## Step 3: Univariate Analysis — Full Code by Path

### Path A: ≤30 columns — Full per-column analysis

```python
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

# Numeric: distribution plot + stats + outlier flag
for col in numeric_cols:
    series = df[col].dropna()
    skew = series.skew()
    kurt = series.kurtosis()
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    n_outliers = ((series < q1 - 1.5*iqr) | (series > q3 + 1.5*iqr)).sum()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    series.hist(bins=40, ax=ax1)
    ax1.set_title(f'{col} — histogram')
    series.plot.box(ax=ax2)
    ax2.set_title(f'{col} — boxplot')
    plt.suptitle(f'{col}: skew={skew:.2f}, kurt={kurt:.2f}, outliers={n_outliers}')
    plt.tight_layout()
    plt.show()

# Categorical: value counts + bar chart
for col in categorical_cols:
    vc = df[col].value_counts()
    n_unique = len(vc)
    top10 = vc.head(10)
    print(f"\n{col}: {n_unique} unique values, null_rate={df[col].isnull().mean():.2%}")
    top10.plot.bar(figsize=(10, 3), title=f'{col} — top 10 values')
    plt.tight_layout()
    plt.show()
```

### Path B: 31–100 columns — Summary tables + top 5 most interesting

```python
# Build summary table for all numeric columns
numeric_summary = pd.DataFrame({
    'null_rate': df[numeric_cols].isnull().mean(),
    'n_unique': df[numeric_cols].nunique(),
    'mean': df[numeric_cols].mean(),
    'std': df[numeric_cols].std(),
    'skew': df[numeric_cols].skew(),
    'kurtosis': df[numeric_cols].kurtosis(),
}).round(4)
numeric_summary['outlier_pct'] = [
    round(((df[c].dropna() < df[c].quantile(0.25) - 1.5*(df[c].quantile(0.75)-df[c].quantile(0.25))) |
           (df[c].dropna() > df[c].quantile(0.75) + 1.5*(df[c].quantile(0.75)-df[c].quantile(0.25)))).mean(), 4)
    for c in numeric_cols
]
display(numeric_summary.sort_values('skew', ascending=False))

# Visualize the 5 most skewed columns
top_skewed = numeric_summary['skew'].abs().nlargest(5).index.tolist()
df[top_skewed].hist(bins=30, figsize=(15, 6), layout=(2, 3))
plt.suptitle('Top 5 Most Skewed Columns')
plt.tight_layout()
plt.show()

# Build summary table for categorical columns
cat_summary = pd.DataFrame({
    'null_rate': df[categorical_cols].isnull().mean(),
    'n_unique': df[categorical_cols].nunique(),
    'top_value': [df[c].mode()[0] if len(df[c].dropna()) > 0 else None for c in categorical_cols],
    'top_value_freq': [df[c].value_counts(normalize=True).iloc[0] if len(df[c].dropna()) > 0 else 0
                       for c in categorical_cols],
}).round(4)
display(cat_summary.sort_values('n_unique', ascending=False))
```

### Path C: >100 columns — Automated screening, visualize top 20

```python
# Automated screening: variance, skew, null rate
numeric_screen = pd.DataFrame({
    'null_rate': df[numeric_cols].isnull().mean(),
    'variance': df[numeric_cols].var(),
    'skew': df[numeric_cols].skew().abs(),
    'near_zero_var': df[numeric_cols].var() < 1e-6,
}).sort_values('skew', ascending=False)

# Flag low-variance columns
low_var_cols = numeric_screen[numeric_screen['near_zero_var']].index.tolist()
print(f"Low-variance columns to review: {low_var_cols}")

# Visualize top 20 by absolute skew (most "interesting")
top20 = numeric_screen.head(20).index.tolist()
df[top20].hist(bins=30, figsize=(20, 12), layout=(4, 5))
plt.suptitle('Top 20 Columns by Skewness')
plt.tight_layout()
plt.show()
```

---

## Step 5: Feature-Target Relationships — Regression and Other Task Paths

### Regression + Numeric Feature → Pearson + Spearman

```python
target = 'YOUR_TARGET_COLUMN'
numeric_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c != target]

reg_results = []
for col in numeric_cols[:50]:
    shared = df[[col, target]].dropna()
    if len(shared) < 10:
        continue
    pearson_r, pearson_p = stats.pearsonr(shared[col], shared[target])
    spearman_r, spearman_p = stats.spearmanr(shared[col], shared[target])
    divergence = abs(abs(pearson_r) - abs(spearman_r))
    reg_results.append({
        'feature': col, 'pearson_r': pearson_r, 'pearson_p': pearson_p,
        'spearman_r': spearman_r, 'spearman_p': spearman_p,
        'divergence': divergence, 'nonlinear_flag': divergence > 0.15,
    })

reg_df = pd.DataFrame(reg_results).sort_values('spearman_p')
display(reg_df.head(15))

# Flag non-linear relationships for special treatment in feature engineering
nonlinear = reg_df[reg_df['nonlinear_flag']]
if len(nonlinear) > 0:
    print(f"\nNon-linear relationships detected (|Pearson - Spearman| > 0.15):")
    display(nonlinear[['feature', 'pearson_r', 'spearman_r', 'divergence']])
```

### Regression + Categorical Feature → ANOVA per category

```python
cat_cols = [c for c in df.select_dtypes(include=['object','category']).columns if c != target]

for col in cat_cols:
    groups = [df.loc[df[col] == val, target].dropna().values
              for val in df[col].unique() if (df[col] == val).sum() >= 3]
    if len(groups) < 2:
        continue
    f_stat, p = stats.f_oneway(*groups)
    print(f"{col}: ANOVA F={f_stat:.2f}, p={p:.4f} {'*' if p < 0.05 else ''}")
```

### Time-Series → Granger causality

```python
from statsmodels.tsa.stattools import grangercausalitytests

target = 'YOUR_TARGET_COLUMN'
numeric_features = [c for c in df.select_dtypes(include=[np.number]).columns if c != target]

for feat in numeric_features[:10]:
    data = df[[target, feat]].dropna()
    print(f"\nGranger causality: {feat} → {target}")
    try:
        gc_results = grangercausalitytests(data, maxlag=4, verbose=False)
        for lag, res in gc_results.items():
            p = res[0]['ssr_ftest'][1]
            print(f"  lag {lag}: p={p:.4f} {'SIGNIFICANT' if p < 0.05 else ''}")
    except Exception as e:
        print(f"  Error: {e}")
```

### Clustering → Mutual information heatmap (no target)

```python
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
from sklearn.feature_selection import mutual_info_regression

if len(numeric_cols) <= 50:
    mi_matrix = pd.DataFrame(index=numeric_cols, columns=numeric_cols, dtype=float)
    for col in numeric_cols:
        mi = mutual_info_regression(df[numeric_cols].fillna(df[numeric_cols].median()),
                                    df[col].fillna(df[col].median()), random_state=42)
        mi_matrix[col] = mi
    sns.heatmap(mi_matrix, cmap='YlOrRd', square=True, figsize=(12, 10))
    plt.title('Mutual Information Between Features')
    plt.tight_layout()
    plt.show()
```

---

## Step 6: Correlation Analysis — Full Code

### Pearson + Spearman heatmap (≤100 numeric columns)

```python
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

if len(numeric_cols) <= 100:
    pearson_corr = df[numeric_cols].corr(method='pearson')
    spearman_corr = df[numeric_cols].corr(method='spearman')

    # Pearson heatmap
    plt.figure(figsize=(12, 10))
    mask = np.triu(np.ones_like(pearson_corr, dtype=bool))
    sns.heatmap(pearson_corr, mask=mask, annot=len(numeric_cols) <= 20,
                fmt='.2f', cmap='coolwarm', vmin=-1, vmax=1, square=True)
    plt.title('Pearson Correlation Matrix')
    plt.tight_layout()
    plt.show()

    # Find pairs where Pearson and Spearman diverge (non-linearity signal)
    divergent_pairs = []
    for i, col_a in enumerate(numeric_cols):
        for col_b in numeric_cols[i+1:]:
            p_r = pearson_corr.loc[col_a, col_b]
            s_r = spearman_corr.loc[col_a, col_b]
            if abs(abs(p_r) - abs(s_r)) > 0.15:
                divergent_pairs.append({'col_a': col_a, 'col_b': col_b,
                                        'pearson': p_r, 'spearman': s_r,
                                        'divergence': abs(abs(p_r)-abs(s_r))})
    if divergent_pairs:
        print("Non-linear pairs (consider polynomial or interaction features):")
        display(pd.DataFrame(divergent_pairs).sort_values('divergence', ascending=False))
else:
    print("Wide dataset — using mutual information instead of pairwise matrix")
    # See clustering path in Step 5 for mutual information code
```

### High correlation pair finder

```python
high_corr_threshold = 0.85
corr_matrix = df[numeric_cols].corr().abs()
upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
high_corr_pairs = [(col, row, upper.loc[row, col])
                   for col in upper.columns for row in upper.index
                   if upper.loc[row, col] > high_corr_threshold]
if high_corr_pairs:
    print(f"Highly correlated pairs (>{high_corr_threshold}):")
    for a, b, r in sorted(high_corr_pairs, key=lambda x: x[2], reverse=True):
        print(f"  {a} — {b}: {r:.3f}")
```

---

## Step 7: Outlier Analysis — Full Code

```python
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
outlier_report = []

for col in numeric_cols:
    series = df[col].dropna()
    if len(series) < 10:
        continue
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        continue
    lower_fence = q1 - 1.5 * iqr
    upper_fence = q3 + 1.5 * iqr
    outliers = series[(series < lower_fence) | (series > upper_fence)]
    pct = len(outliers) / len(series)

    if pct == 0:
        continue

    skewness = series.skew()
    if pct > 0.05 and abs(skewness) > 2:
        disposition = 'heavy_tailed — use robust methods or log transform'
    elif pct < 0.01:
        disposition = 'likely data error — investigate individual values; re-clean if implausible'
    elif pct < 0.03:
        disposition = 'plausible extremes — flag for winsorization in feature engineering'
    else:
        disposition = 'moderate rate — consider winsorization or RobustScaler'

    outlier_report.append({
        'column': col, 'n_outliers': len(outliers),
        'pct_outliers': round(pct, 4),
        'lower_fence': round(lower_fence, 4), 'upper_fence': round(upper_fence, 4),
        'disposition': disposition,
    })

outlier_df = pd.DataFrame(outlier_report).sort_values('pct_outliers', ascending=False)
display(outlier_df)
```

---

## Step 8: eda_findings.json — Full Dict Structure

```python
import json
from datetime import datetime, timezone

eda_findings = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "task": task,  # set from your task declaration
    "target_column": target,
    "dataset_summary": {
        "rows": df.shape[0],
        "cols": df.shape[1],
        "memory_mb": round(df.memory_usage(deep=True).sum() / 1e6, 3),
        "shape_tags": shape_tags,
    },
    "target_analysis": target_analysis,  # from Step 4
    "recommended_transforms": [
        # from Step 3 skewness analysis — list dicts with column, transform_type, reason, code_snippet
    ],
    "feature_candidates": [
        # from Step 5 divergent pairs — list dicts with columns, interaction_type, expected_signal
    ],
    "drop_candidates": [
        # from Step 2 audit + Step 3 — constant cols, >80% null, high-cardinality IDs
    ],
    "top_features": results_df.head(20).to_dict(orient='records'),  # from Step 5
    "outlier_summary": outlier_df.to_dict(orient='records'),  # from Step 7
    "modeling_notes": [
        # bullet strings summarizing key findings and strategy
    ],
}

with open('eda_findings.json', 'w') as f:
    json.dump(eda_findings, f, indent=2, default=str)

print("Saved: eda_findings.json")
```
