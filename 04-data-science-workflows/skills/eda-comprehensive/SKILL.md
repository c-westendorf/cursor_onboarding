---
name: eda-comprehensive
description: Systematic exploratory data analysis to discover distributions, relationships, anomalies, and patterns that inform modeling strategy and feature engineering. Use when starting work with a new dataset, before any modeling effort, after data updates, when debugging data issues, when investigating model performance degradation, when evaluating a new data source, or whenever you need to understand a dataset's structure and quality. Produces both human-readable reports and machine-readable findings that feed directly into feature engineering. Handles classification, regression, time-series, NLP, and clustering tasks.
---

# EDA: Comprehensive Exploratory Data Analysis

## Why EDA Matters

Skipping EDA produces garbage-in-garbage-out models. A model trained without EDA will:
- Fail silently on skewed targets that needed log transforms
- Leak through high-correlation features that were never audited
- Underperform because class imbalance was never detected
- Break in production when distributions shift in ways that were never characterized

EDA is also the primary input to feature engineering. You cannot engineer useful features from data you do not understand.

---

## When to Activate

- Starting work with any new dataset
- Before any modeling effort begins
- After the data pipeline is updated or data is refreshed
- When a model's performance degrades unexpectedly
- When evaluating whether a new data source is worth using
- When debugging unexplained model behavior

---

## Prerequisites

Before beginning:
1. You have a clean DataFrame loaded into memory (`df`). If not, run the data-cleaning skill first.
2. You have declared the **task type**: `classification`, `regression`, `time_series`, `nlp`, or `clustering`.
3. For supervised tasks, you have the **target column name**.
4. Dependencies installed: `pandas`, `numpy`, `scipy`, `matplotlib`, `seaborn`, `sklearn`, `statsmodels`.

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.feature_selection import mutual_info_classif, mutual_info_regression
import warnings
warnings.filterwarnings('ignore')

# Set consistent plot style
sns.set_theme(style='whitegrid', palette='muted')
plt.rcParams['figure.figsize'] = (10, 5)
```

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
qa_path = Path("qa_report.json")
if qa_path.exists():
    qa = json.load(open(qa_path))
    verdict = qa.get("verdict", "UNKNOWN")

    if verdict == "FAIL":
        print("⛔ QA verdict is FAIL. EDA on failed-QA data will produce unreliable findings.")
        print("   Recommendation: Fix data quality issues first.")
        # WARN but allow — EDA can be diagnostic
    elif verdict == "CONDITIONAL_PASS":
        print("⚠️  QA verdict is CONDITIONAL_PASS. EDA results may be affected by known issues.")
        print(f"   Known issues: {[i['description'] for i in qa.get('issues', []) if i.get('severity') == 'critical']}")
```

> **Plain language:** We check the data quality report. If there are known problems, we note them so the analysis results can be interpreted correctly.

### Step 1: Initial Inspection

Get a factual picture of shape, memory, and types before any analysis.

```python
print(f"Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"Memory: {df.memory_usage(deep=True).sum() / 1e6:.1f} MB")
print()
print("Dtypes:")
print(df.dtypes.value_counts())
print()
print("First 5 rows:")
display(df.head())
print("Last 5 rows:")
display(df.tail())
print("Describe (numeric):")
display(df.describe())
print("Describe (object):")
display(df.describe(include='object'))
```

**Shape classification — branch your strategy based on what you find.**
Reference `references/shape-aware-strategy.md` for the full branching table.

Quick decision:
- `n_cols > 100` → wide: automated screening only, mutual information instead of pairwise matrix
- `n_rows > 1_000_000` → tall: stratified sampling for visualization
- `sparse_col_rate > 0.30` → sparse: non-zero distributions, co-occurrence matrices
- Datetime index or datetime columns → time_series: decomposition, ADF test
- Otherwise → standard: run all steps with full depth

```python
# Run shape classifier from shape-aware-strategy.md
def classify_shape(df):
    n_rows, n_cols = df.shape
    sparse_col_rate = (df.isnull().mean() > 0.50).mean()
    has_datetime = any(pd.api.types.is_datetime64_any_dtype(df[col]) for col in df.columns)
    tags = []
    if n_cols > 100: tags.append('wide')
    if n_rows > 1_000_000: tags.append('tall')
    if sparse_col_rate > 0.30: tags.append('sparse')
    if has_datetime: tags.append('time_series')
    if not tags: tags.append('standard')
    return tags

shape_tags = classify_shape(df)
print(f"Shape tags: {shape_tags}")
```

> **CHECKPOINT — Step 1**
> - [ ] Assert: `df.shape[0] >= 10` (minimum viable sample for statistics)
> - [ ] Assert: `df.shape[1] >= 1`
> - [ ] PASS: Dataset has sufficient size for analysis
> - [ ] On FAIL (rows < 10): WARN — "Dataset too small for reliable statistics. Proceeding with descriptive analysis only (no statistical tests)."
> - [ ] On FAIL (0 rows): HALT — "Empty dataset."

---

### Step 2: Run Dataset Audit

Run the full 5-dimension audit (completeness, consistency, accuracy, timeliness, relevance) before any analysis. Issues found here may require returning to data cleaning.

Reference: `references/dataset-audit-pattern.md`

```python
# From dataset-audit-pattern.md:

def audit_completeness(df):
    null_rates = (df.isnull().sum() / len(df)).to_dict()
    issues = []
    for col, rate in null_rates.items():
        if rate == 0:
            continue
        severity = 'critical' if rate > 0.50 else 'medium' if rate > 0.10 else 'low'
        fix = 'Drop column' if rate > 0.80 else 'Impute (see missing-data-imputation skill)'
        issues.append({'column': col, 'null_rate': round(rate, 4), 'severity': severity, 'fix': fix})
    score = round((1 - df.isnull().sum().sum() / df.size) * 100, 1)
    return {'score': score, 'issues': issues}

completeness = audit_completeness(df)
print(f"Completeness score: {completeness['score']}")
critical = [i for i in completeness['issues'] if i['severity'] == 'critical']
if critical:
    print(f"CRITICAL null issues: {critical}")

# Check for duplicates
dup_count = df.duplicated().sum()
print(f"Duplicate rows: {dup_count} ({dup_count/len(df):.2%})")

# Check constant columns (zero relevance)
constant_cols = [col for col in df.columns if df[col].nunique() <= 1]
print(f"Constant columns (drop these): {constant_cols}")

# Check mixed types in object columns
for col in df.select_dtypes(include=['object']).columns[:20]:
    sample = df[col].dropna().head(500)
    numeric_frac = sample.apply(lambda x: str(x).replace('.','').replace('-','').isdigit()).mean()
    if 0.2 < numeric_frac < 0.8:
        print(f"Mixed types in '{col}': {numeric_frac:.0%} look numeric")
```

**Assumption audit checkpoint.** Before proceeding, run the 4-question audit from `references/assumption-audit-pattern.md`:
1. What am I assuming about data quality?
2. What am I assuming about the data generation process?
3. What would invalidate these assumptions?
4. What checks will I run before proceeding?

---

### Step 3: Univariate Analysis

Characterize every column's distribution individually. Depth depends on column count.

**Decision point:**

- **Path A: ≤30 columns** — Full per-column analysis: histogram + boxplot for each numeric col (skew, kurtosis, outlier count); value counts bar chart for each categorical col.
- **Path B: 31–100 columns** — Build summary tables (null_rate, n_unique, mean, std, skew, kurtosis, outlier_pct); visualize top 5 most skewed; equivalent summary table for categoricals.
- **Path C: >100 columns** — Automated screening by variance/skew/null_rate; flag near-zero-variance columns; visualize top 20 by absolute skew.

See `references/eda-code-recipes.md` for complete copy-paste code for all three paths.

> **CHECKPOINT — Step 3**
> - [ ] Assert: At least 1 column analyzed (numeric OR categorical)
> - [ ] Assert: If zero numeric columns, numeric analysis path was skipped (not failed)
> - [ ] Assert: If zero categorical columns, categorical analysis path was skipped (not failed)
> - [ ] PASS: Univariate analysis complete for all applicable column types
> - [ ] On FAIL: HALT — "No columns could be analyzed. Check dtype classification."

---

### Step 4: Target Variable Analysis (Supervised Tasks Only)

Skip this step for clustering.

**Decision point by task:**

#### Classification

```python
target = 'YOUR_TARGET_COLUMN'

# Class balance
vc = df[target].value_counts()
vc_pct = df[target].value_counts(normalize=True)
print("Class distribution:")
print(pd.DataFrame({'count': vc, 'pct': vc_pct.round(4)}))

min_class_pct = vc_pct.min()
if min_class_pct < 0.02:
    print("SEVERE imbalance — use SMOTE + class_weight='balanced', evaluate with PR-AUC")
elif min_class_pct < 0.10:
    print("MODERATE imbalance — use class_weight='balanced', evaluate with macro F1 or PR-AUC")
elif min_class_pct < 0.20:
    print("MILD imbalance — monitor per-class recall")

# Visual
vc.plot.bar(title=f'{target} — class distribution', figsize=(8, 4))
plt.tight_layout()
plt.show()
```

#### Regression

```python
target = 'YOUR_TARGET_COLUMN'

series = df[target].dropna()
skew = series.skew()
print(f"Target stats: mean={series.mean():.2f}, median={series.median():.2f}, "
      f"std={series.std():.2f}, skew={skew:.2f}")

# Normality test (use for n < 5000)
if len(series) < 5000:
    stat, p = stats.shapiro(series)
    print(f"Shapiro-Wilk: stat={stat:.4f}, p={p:.4f} — {'normal' if p > 0.05 else 'non-normal'}")

# Transform recommendation
if skew > 1.0 and series.min() > 0:
    print("Recommendation: log1p transform — df['target_log'] = np.log1p(df[target])")
elif skew > 1.0:
    print("Recommendation: quantile transform (has zeros/negatives)")
elif skew < -1.0:
    print("Recommendation: reflect + log transform")
else:
    print("Recommendation: no transform needed")

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
series.hist(bins=40, ax=axes[0])
axes[0].set_title(f'{target} — original')
np.log1p(series.clip(lower=0)).hist(bins=40, ax=axes[1])
axes[1].set_title(f'{target} — log1p')
plt.tight_layout()
plt.show()
```

#### Time-Series

```python
target = 'YOUR_TARGET_COLUMN'

# Stationarity test
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

series = df[target].dropna()
adf_result = adfuller(series)
print(f"ADF statistic: {adf_result[0]:.4f}")
print(f"ADF p-value: {adf_result[1]:.4f}")
print(f"Stationary: {adf_result[1] < 0.05}")

if adf_result[1] >= 0.05:
    print("Non-stationary — apply .diff() before ARIMA. Prophet handles this natively.")

# Decomposition (adjust period to match seasonality)
decomp = seasonal_decompose(series, model='additive', period=12)
decomp.plot()
plt.tight_layout()
plt.show()

# ACF / PACF
fig, axes = plt.subplots(2, 1, figsize=(12, 8))
plot_acf(series, lags=40, ax=axes[0])
plot_pacf(series, lags=40, ax=axes[1])
plt.tight_layout()
plt.show()
```

---

### Step 5: Feature-Target Relationships

Measure how much each feature associates with the target. Reference `references/statistical-tests-guide.md` for full test selection logic.

> **At scale (large/very_large):** Run statistical tests on a 100K sample to avoid inflated power. Report Cohen's d or Cramer's V alongside p-values. Flag results where p < 0.001 but effect size is "small" — these are statistically significant but practically meaningless.

**Decision point by feature type × task type:**

#### Classification + Numeric Feature → boxplots + Kruskal-Wallis / Mann-Whitney

```python
target = 'YOUR_TARGET_COLUMN'
numeric_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c != target]
n_classes = df[target].nunique()

results = []
for col in numeric_cols[:50]:
    groups = [df.loc[df[target] == cls, col].dropna().values
              for cls in df[target].unique() if (df[target] == cls).sum() >= 3]
    if len(groups) < 2:
        continue
    if n_classes == 2:
        stat, p = stats.mannwhitneyu(*groups[:2], alternative='two-sided')
        method = 'mann_whitney'
    else:
        stat, p = stats.kruskal(*groups)
        method = 'kruskal_wallis'
    results.append({'feature': col, 'method': method, 'statistic': stat, 'p_value': p})

results_df = pd.DataFrame(results).sort_values('p_value')
print("Top features by statistical test:")
display(results_df.head(15))

# Visualize top 6
for col in results_df.head(6)['feature']:
    plt.figure(figsize=(8, 4))
    df.boxplot(column=col, by=target)
    plt.title(f'{col} by {target}')
    plt.suptitle('')
    plt.tight_layout()
    plt.show()
```

#### Classification + Categorical Feature → Chi-squared + Cramer's V

```python
cat_cols = [c for c in df.select_dtypes(include=['object','category']).columns if c != target]

cat_results = []
for col in cat_cols:
    try:
        contingency = pd.crosstab(df[col], df[target])
        chi2, p, dof, expected = stats.chi2_contingency(contingency)
        n = contingency.sum().sum()
        r, c = contingency.shape
        v = np.sqrt(chi2 / (n * (min(r, c) - 1))) if (n * (min(r, c) - 1)) > 0 else 0
        cat_results.append({'feature': col, 'chi2': chi2, 'p_value': p, 'cramers_v': v})
    except Exception as e:
        print(f"Skipping {col}: {e}")

cat_results_df = pd.DataFrame(cat_results).sort_values('p_value')
display(cat_results_df)
```

#### Regression + Numeric Feature → Pearson + Spearman (both); flag `divergence > 0.15` as non-linear

#### Regression + Categorical Feature → ANOVA per category level (`stats.f_oneway`)

#### Time-Series → Granger causality per feature (`grangercausalitytests`, `maxlag=4`)

#### Clustering → mutual information heatmap (pairwise `mutual_info_regression`, no target needed)

See `references/eda-code-recipes.md` for complete code for all four paths above.

> **CHECKPOINT — Step 5**
> - [ ] Assert: `results_df` is non-empty (at least 1 feature-target test computed)
> - [ ] PASS: Feature-target relationships assessed
> - [ ] On FAIL (all p > 0.05): WARN — "No statistically significant feature-target relationships found. Consider: (1) target may need transformation, (2) relationships may be non-linear, (3) sample size may be insufficient."
> - [ ] On FAIL (no tests computed): WARN — "Insufficient data for statistical tests. Proceeding with correlation-only analysis."

---

### Step 6: Correlation Analysis

> **At scale (large/very_large):** Skip full Pearson/Spearman correlation matrix — use `mutual_info_classif`/`mutual_info_regression` from sklearn instead (O(n × p) not O(p²)). Compute on a 500K stratified sample. For >200 columns, use LightGBM feature importance as a faster proxy for feature ranking.

**Decision point by data types and column count:**

- **Both continuous (≤100 cols):** Compute Pearson + Spearman matrices; plot heatmap; flag pairs where `|pearson - spearman| > 0.15` as non-linear (candidates for polynomial/interaction features).
- **Wide dataset (>100 cols):** Use mutual information instead of pairwise matrix (see clustering path in Step 5).
- **Ordinal features:** Spearman only — Pearson assumes interval scale.
- **Nominal categorical pairs:** Cramer's V (see Step 5 Classification + Categorical code).
- **High correlation flags:** Find pairs with `|r| > 0.85` — multicollinearity candidates to prune before linear modeling.

> **Plain language:** We compute two types of correlation — one assumes a straight-line relationship (Pearson), the other doesn't (Spearman). If they disagree by more than 0.15, the relationship is probably curved or non-linear. This means simple linear features won't capture it — consider polynomial or interaction features.

See `references/eda-code-recipes.md` for the full Pearson/Spearman heatmap code and high-correlation pair finder.

---

### Step 7: Outlier Analysis

Use IQR method to identify outliers for every numeric column, then assign a disposition based on outlier rate and skewness. Produces `outlier_df` sorted by `pct_outliers` descending.

See `references/eda-code-recipes.md` for the full `outlier_report` loop.

**Disposition rules:**
- **Beyond physical plausibility** (e.g., age = -5, percentage = 150%) → data error: return to data cleaning
- **Plausible extreme** but rare (<3%) → flag for winsorization in feature engineering step
- **Clustered outliers** (>5%, heavy tail) → heavy-tailed distribution: use robust methods (Huber, quantile regression) or log transform
- **Time-series spike** → check against known events (outages, holidays, data collection issues)

> **CHECKPOINT — Step 7**
> - [ ] Assert: Every numeric column has an outlier disposition assigned
> - [ ] Assert: IQR=0 columns (constant) have disposition = `drop_candidate`
> - [ ] PASS: All outlier dispositions documented
> - [ ] On FAIL: Assign default disposition `review_required` to unclassified columns.

---

### Step 8: Synthesize Findings

Produce `eda_report.md` (human-readable) and `eda_findings.json` (machine-readable, feeds feature engineering).

**Modeling strategy decision tree:**

| Signal | Recommended Approach |
|---|---|
| Low dimensionality, linear correlations with target | Linear baseline (LR/Ridge) first |
| Non-linear divergence detected in Step 5-6 | Tree-based models (XGBoost/LightGBM) |
| High dimensionality (>100 features) | Regularized models (L1/ElasticNet/LightGBM with regularization) |
| Temporal structure detected | ARIMA (short horizon), Prophet (trend + seasonality), LSTM (complex patterns) |
| Clustering task, Hopkins > 0.75 | K-means (spherical), DBSCAN (arbitrary shape + noise), Agglomerative (hierarchy needed) |
| Severe class imbalance | Ensemble + SMOTE; evaluate with PR-AUC not accuracy |

`eda_findings.json` must contain: `timestamp`, `task`, `target_column`, `dataset_summary` (rows/cols/memory/shape_tags), `target_analysis`, `recommended_transforms`, `feature_candidates`, `drop_candidates`, `top_features` (from Step 5 results), `outlier_summary` (from Step 7), and `modeling_notes`.

For the full dict structure and automated version, use the standalone script:
```bash
python scripts/generate_eda_findings.py \
    --input data.csv \
    --target label \
    --task classification \
    --output eda_findings.json
```

Write `eda_report.md` summarizing:
1. Dataset overview (shape, memory, shape tags)
2. Data quality issues and their severity
3. Target variable characteristics
4. Top 10 features by association with target
5. Distributions that need transforms
6. Outlier summary and dispositions
7. Recommended modeling strategy

---

## Edge Case Handling

| Edge Case | Detection | Action |
|---|---|---|
| **Empty DataFrame (0 rows)** | `len(df) == 0` | HALT — "Cannot perform EDA on empty dataset." |
| **Single-row DataFrame** | `len(df) == 1` | WARN — skip all statistical tests. Report only: dtypes, null rates, value descriptions. |
| **Zero numeric columns** | `len(df.select_dtypes(include='number').columns) == 0` | Skip: correlation matrix, outlier analysis, Shapiro-Wilk, ADF. Proceed with categorical-only analysis. |
| **Zero categorical columns** | `len(df.select_dtypes(include='object').columns) == 0` | Skip: chi-squared tests, Cramer's V, value_counts analysis. Proceed with numeric-only analysis. |
| **All columns constant** | `df.nunique().max() <= 1` | Flag all as `drop_candidates`. WARN — "No variance in dataset. EDA findings will be trivial." |
| **Target has only 1 class** | Classification target with 1 unique value | HALT — "Target has no variance. Cannot perform classification EDA. Check target column definition." |
| **Very wide dataset (>1000 cols)** | `df.shape[1] > 1000` | Skip full correlation matrix. Use automated screening (variance, null rate, cardinality). Report top 50 features by variance only. |
| **Extremely imbalanced classes (>99:1)** | Minority class < 1% | WARN — "Extreme class imbalance detected. Statistical tests may be unreliable. Consider: is this a rare-event problem requiring specialized approaches?" |
| **IQR = 0 (constant within IQR)** | `Q3 - Q1 == 0` for numeric column | Disposition = `constant_iqr` — "Column has no interquartile spread. May be quasi-constant. Flag as drop candidate." |
| **Statistical test cannot compute** | Mann-Whitney / chi-squared raises error (too few samples, empty groups) | Skip test for that feature. Log: "Test skipped — insufficient data." Assign p_value = None. |
| **Seasonal period unknown** | Time-series with no obvious seasonality | Try periods [7, 12, 24, 52, 365]. Use the one with lowest AIC in decomposition. If none work, skip decomposition with warning. |

---

## Quality Bar

An EDA is complete when:
- Every numeric column has been characterized (mean, std, skew, outlier count)
- Every categorical column has been assessed (n_unique, top values, null rate)
- Every feature has been measured against the target with a p-value or association metric
- Class balance (classification) or target distribution (regression) has been quantified
- Highly correlated feature pairs have been identified
- Outlier dispositions have been assigned (not just detected)
- `eda_findings.json` exists and is readable by the feature engineering skill

---

## Scope Boundary

This skill is **read-only**. It does NOT:
- Modify the DataFrame
- Drop columns or rows from the working data
- Engineer new features
- Fit any model

All actions taken in EDA are diagnostic. Modifications happen in the data-cleaning and feature-engineering skills, informed by EDA output.
