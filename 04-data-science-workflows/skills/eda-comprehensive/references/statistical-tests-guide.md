# Statistical Tests Guide

Reference for choosing the correct statistical test given feature type, target type, and task.
For each test: when to use, assumptions, code, interpretation, and p-value thresholds.

---

## 1. Numeric Feature vs. Categorical Target (Classification)

### ANOVA F-test
**When to use:** Numeric feature, multi-class target, roughly normal distributions, similar variances across classes.
**Assumptions:** Normality within groups, homoscedasticity (Levene's test), observations independent.
**P-value threshold:** p < 0.05 → feature differs significantly across classes.

```python
from scipy import stats

groups = [group[feature].dropna().values for _, group in df.groupby(target)]
f_stat, p_value = stats.f_oneway(*groups)
# Interpretation: low p → feature mean differs across at least one class pair
```

### Kruskal-Wallis (non-parametric alternative)
**When to use:** Numeric feature, multi-class target, skewed distributions or small samples. Prefer over ANOVA when Shapiro-Wilk rejects normality.
**Assumptions:** Ordinal data acceptable, groups independent.

```python
from scipy import stats

groups = [group[feature].dropna().values for _, group in df.groupby(target)]
h_stat, p_value = stats.kruskal(*groups)
# Interpretation: low p → at least one class has different median
```

### Mann-Whitney U (binary targets)
**When to use:** Numeric feature, binary target (two classes only). More powerful than Kruskal-Wallis for the two-sample case.
**Assumptions:** Groups independent, ordinal scale.

```python
from scipy import stats

class_vals = df[target].unique()
group_a = df.loc[df[target] == class_vals[0], feature].dropna()
group_b = df.loc[df[target] == class_vals[1], feature].dropna()
u_stat, p_value = stats.mannwhitneyu(group_a, group_b, alternative='two-sided')
# Interpretation: low p → distributions differ between the two classes
```

**Decision rule:**
1. Check normality with Shapiro-Wilk (n < 5000) or visual inspection.
2. If normal → ANOVA. If skewed → Kruskal-Wallis (multi-class) or Mann-Whitney (binary).

---

## 2. Categorical Feature vs. Categorical Target

### Chi-Squared Test of Independence
**When to use:** Both feature and target are categorical. Tests whether the two variables are independent.
**Assumptions:** Expected cell frequency ≥ 5 for 80% of cells, n ≥ 20.
**P-value threshold:** p < 0.05 → dependence exists.

```python
import pandas as pd
from scipy import stats

contingency = pd.crosstab(df[feature], df[target])
chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
# Interpretation: low p → feature and target are NOT independent
```

### Cramer's V (effect size for chi-squared)
**When to use:** After chi-squared confirms dependence. Measures association strength (0 = no association, 1 = perfect association).

```python
import numpy as np

def cramers_v(chi2, n, r, c):
    """r = rows, c = cols in contingency table."""
    return np.sqrt(chi2 / (n * (min(r, c) - 1)))

contingency = pd.crosstab(df[feature], df[target])
chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
n = contingency.sum().sum()
r, c = contingency.shape
v = cramers_v(chi2, n, r, c)
# Interpretation: v < 0.1 weak, 0.1-0.3 moderate, > 0.3 strong
```

---

## 3. Numeric Feature vs. Numeric Target (Regression)

### Pearson Correlation
**When to use:** Both numeric, linear relationship expected, no severe outliers.
**Assumptions:** Approximately bivariate normal, no extreme outliers, linear relationship.
**Interpretation:** |r| < 0.1 negligible, 0.1-0.3 weak, 0.3-0.5 moderate, > 0.5 strong.

```python
from scipy import stats

r, p_value = stats.pearsonr(df[feature].dropna(), df[target].dropna())
# Interpretation: sign = direction, magnitude = strength of LINEAR relationship
```

### Spearman Rank Correlation
**When to use:** Monotonic (not necessarily linear) relationship, or presence of outliers, or ordinal data.
**Assumptions:** Monotonic relationship, no tied ranks (or few ties).

```python
from scipy import stats

rho, p_value = stats.spearmanr(df[feature].dropna(), df[target].dropna())
# Interpretation: same scale as Pearson, but captures monotonic (not just linear)
```

**When Pearson and Spearman diverge significantly (|pearson - spearman| > 0.15):**
This signals a non-linear monotonic relationship. Investigate with a scatter plot and consider polynomial features or log transforms.

---

## 4. Correlation Between Features

### Numeric-Numeric Pairs
Use both Pearson and Spearman. Divergence flags non-linearity.

```python
pearson_r, _ = stats.pearsonr(df[col_a], df[col_b])
spearman_r, _ = stats.spearmanr(df[col_a], df[col_b])
```

### Categorical-Categorical Pairs
Use Cramer's V (see Section 2 above).

### Numeric vs. Binary (Point-Biserial)
Mathematically equivalent to Pearson when one variable is binary (0/1).

```python
from scipy import stats

r, p_value = stats.pointbiserialr(df[binary_col], df[numeric_col])
# Interpretation: same as Pearson; captures linear relationship with a binary variable
```

### Universal: Mutual Information
**When to use:** Any feature type × any target type. Captures non-linear dependencies. Preferred for wide datasets (>100 features) where pairwise matrix is intractable.
**Interpretation:** 0 = independence, higher = stronger dependency (no fixed upper bound).

```python
from sklearn.feature_selection import mutual_info_classif, mutual_info_regression
import numpy as np

# For classification:
mi_scores = mutual_info_classif(X, y, discrete_features='auto', random_state=42)
mi_series = pd.Series(mi_scores, index=X.columns).sort_values(ascending=False)

# For regression:
mi_scores = mutual_info_regression(X, y, discrete_features='auto', random_state=42)
mi_series = pd.Series(mi_scores, index=X.columns).sort_values(ascending=False)
```

---

## 5. Time-Series Specific Tests

### ADF Test (Stationarity)
**When to use:** Before any time-series modeling. Non-stationary series require differencing or detrending.
**Null hypothesis:** Series has a unit root (non-stationary).
**Interpretation:** p < 0.05 → reject null → series IS stationary.

```python
from statsmodels.tsa.stattools import adfuller

result = adfuller(series.dropna())
adf_stat, p_value, lags, nobs, critical_values, icbest = result
print(f"ADF: {adf_stat:.4f}, p={p_value:.4f}")
print(f"Stationary: {p_value < 0.05}")
# If NOT stationary: apply .diff() and retest
```

### ACF / PACF (Autocorrelation)
**When to use:** To identify AR and MA order for ARIMA; to detect seasonality period.

```python
from statsmodels.tsa.stattools import acf, pacf
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

fig, axes = plt.subplots(2, 1, figsize=(12, 8))
plot_acf(series.dropna(), lags=40, ax=axes[0])
plot_pacf(series.dropna(), lags=40, ax=axes[1])
plt.tight_layout()
# ACF: slow decay → non-stationary. Spikes at lag k → MA(k)
# PACF: spikes at lag k → AR(k)
```

### Granger Causality
**When to use:** To test whether one time series helps predict another. Useful for multi-variate time series.
**Null hypothesis:** Series X does NOT Granger-cause series Y.

```python
from statsmodels.tsa.stattools import grangercausalitytests

data = pd.DataFrame({'y': y_series, 'x': x_series}).dropna()
results = grangercausalitytests(data[['y', 'x']], maxlag=5, verbose=False)
for lag, result in results.items():
    p = result[0]['ssr_ftest'][1]
    print(f"Lag {lag}: p={p:.4f} {'SIGNIFICANT' if p < 0.05 else ''}")
```

### Seasonal Decomposition
**When to use:** To separate trend, seasonality, and residual components before modeling.

```python
from statsmodels.tsa.seasonal import seasonal_decompose

decomposition = seasonal_decompose(series, model='additive', period=12)  # adjust period
fig = decomposition.plot()
fig.set_size_inches(12, 8)
# Review: trend (long-term direction), seasonal (repeating pattern), residual (noise)
```

---

## 6. Distribution Tests

### Shapiro-Wilk (Normality Test)
**When to use:** Before applying parametric tests (ANOVA, Pearson). Use for n < 5000 only; for larger samples, virtually any distribution will reject.
**Null hypothesis:** Data is normally distributed.

```python
from scipy import stats

stat, p_value = stats.shapiro(series.dropna()[:5000])  # cap at 5000
print(f"Normal: {p_value > 0.05} (p={p_value:.4f})")
# p > 0.05 → fail to reject normality (proceed with parametric tests)
# p < 0.05 → non-normal (use non-parametric alternatives)
```

### KS Two-Sample Test (Distribution Comparison)
**When to use:** Compare two distributions — e.g., train vs. test split, before vs. after a date cutoff, different data sources.
**Null hypothesis:** Both samples come from the same distribution.

```python
from scipy import stats

stat, p_value = stats.ks_2samp(sample_a, sample_b)
print(f"Same distribution: {p_value > 0.05} (p={p_value:.4f})")
# p < 0.05 → distributions differ → potential data drift
```

### Chi-Squared Goodness of Fit (Categorical Distribution Check)
**When to use:** Test whether an observed categorical distribution matches an expected one.

```python
from scipy import stats
import numpy as np

observed_counts = df[col].value_counts().sort_index()
expected_counts = np.full(len(observed_counts), len(df) / len(observed_counts))  # uniform
chi2, p_value = stats.chisquare(observed_counts, f_exp=expected_counts)
# p < 0.05 → distribution is NOT uniform (expected may vary by domain knowledge)
```

---

## 7. Clustering-Specific Metrics

### Hopkins Statistic (Clusterability)
**When to use:** Before running any clustering algorithm. Measures whether data has meaningful cluster structure vs. uniform random distribution.
**Interpretation:** H > 0.75 → data is clusterable. H near 0.5 → no cluster tendency.

```python
import numpy as np
from sklearn.neighbors import NearestNeighbors

def hopkins_statistic(X, sample_ratio=0.1):
    """Estimate Hopkins statistic for clusterability."""
    n = X.shape[0]
    m = max(1, int(n * sample_ratio))
    nbrs = NearestNeighbors(n_neighbors=1).fit(X)

    # Random sample from data
    rand_idx = np.random.choice(n, m, replace=False)
    d_data, _ = nbrs.kneighbors(X[rand_idx])

    # Random sample from uniform space
    mins = X.min(axis=0)
    maxs = X.max(axis=0)
    random_points = np.random.uniform(mins, maxs, (m, X.shape[1]))
    d_rand, _ = nbrs.kneighbors(random_points)

    h = d_rand.sum() / (d_data.sum() + d_rand.sum())
    return float(h)

# Example:
from sklearn.preprocessing import StandardScaler
X_scaled = StandardScaler().fit_transform(df[numeric_cols].dropna())
h = hopkins_statistic(X_scaled)
print(f"Hopkins statistic: {h:.3f} ({'clusterable' if h > 0.75 else 'no clear cluster structure'})")
```

### Silhouette Score Interpretation
**When to use:** After fitting a clustering model, to assess cluster quality.
**Interpretation:** +1 = perfectly separated, 0 = on boundary, -1 = misclassified.

```python
from sklearn.metrics import silhouette_score

score = silhouette_score(X_scaled, cluster_labels)
# > 0.7: strong structure
# 0.5-0.7: reasonable structure
# 0.25-0.5: weak structure
# < 0.25: no substantial structure (reconsider k or algorithm)
```

---

## Quick-Reference Decision Table

| Feature Type | Target Type | Task | Recommended Test |
|---|---|---|---|
| Numeric | Categorical (multi) | Classification | ANOVA (normal) or Kruskal-Wallis (skewed) |
| Numeric | Binary | Classification | Mann-Whitney U |
| Categorical | Categorical | Classification | Chi-squared + Cramer's V |
| Numeric | Numeric | Regression | Pearson + Spearman (compare both) |
| Categorical | Numeric | Regression | ANOVA per category level |
| Numeric | Numeric | Time-series | Cross-correlation, Granger causality |
| Any | Any | Wide datasets | Mutual information (universal) |
| Numeric | — | Distribution check | Shapiro-Wilk (normality), KS two-sample (drift) |
| Numeric | — | Time-series | ADF (stationarity), ACF/PACF (structure) |
| Numeric | — | Clustering | Hopkins statistic, Silhouette score |
