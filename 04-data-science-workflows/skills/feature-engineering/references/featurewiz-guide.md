# Featurewiz Guide (AutoViML)

featurewiz automates two of the most tedious and error-prone parts of feature engineering: removing redundant features (SULOV) and selecting the most predictive ones (MRMR via recursive XGBoost). Use it as the primary automated selection layer; supplement with manual engineering for domain-specific features that automated methods cannot discover.

---

## What featurewiz Does

1. **SULOV** — removes mutually redundant features based on pairwise correlation and mutual information
2. **MRMR** — selects the minimal set of features with maximum predictive power via recursive XGBoost
3. **Optional feature engineering** — can generate interaction terms and GroupBy aggregations automatically

---

## SULOV: Searching for Uncorrelated List of Variables

SULOV removes features that carry redundant information relative to each other.

**Algorithm:**
1. Compute mutual information scores between all feature pairs
2. Identify clusters of features that are mutually correlated above `corr_limit`
3. Within each cluster, keep the feature most correlated with the target; discard the rest
4. Result: a non-redundant feature set

**Key parameter:** `corr_limit` (default `0.7`)
- Range: 0.0 to 1.0
- Lower value = more aggressive pruning (fewer features pass through)
- `corr_limit=0.5` is recommended for wide datasets (>50 correlated columns)
- `corr_limit=0.9` is permissive (keeps near-duplicates)

**Skipping SULOV:** Set `skip_sulov=True` to bypass entirely and go straight to MRMR. Use this when you suspect SULOV is eliminating known-important features.

---

## MRMR: Minimum Redundancy Maximum Relevance via Recursive XGBoost

MRMR selects the minimal set of features that provides maximum predictive signal.

**Algorithm:**
1. Run XGBoost on the SULOV-filtered feature set
2. Extract top features by importance score
3. Repeat across multiple permutations
4. Combine importance rankings, deduplicate, and select the top-ranked features
5. Result: a compact, predictive feature set

**Key behavior:** The number of selected features is determined automatically — featurewiz does not require you to set a target count. The result is the smallest set that explains the data.

**Skipping MRMR:** Set `skip_xgboost=True` to bypass and use SULOV output directly. Use only for very fast prototyping or when XGBoost is unavailable.

---

## Modern API

```python
from featurewiz import FeatureWiz

# Basic usage — classification
fwiz = FeatureWiz(corr_limit=0.7, feature_engg='', verbose=0)
X_train_selected, y_train = fwiz.fit_transform(X_train, y_train)
X_test_selected = fwiz.transform(X_test)
selected_features = fwiz.features

print(f"Selected {len(selected_features)} features from {X_train.shape[1]} input features")
print(selected_features)
```

**Critical:** Always call `.fit_transform()` on training data ONLY. Apply `.transform()` to test/validation splits. Never call `.fit_transform()` on the full dataset — that is leakage. See `references/leakage-guard.md`, section "Feature Selection Leakage".

---

## Full Parameter Reference

| Parameter | Default | Purpose |
|---|---|---|
| `corr_limit` | `0.7` | SULOV correlation threshold. Lower = more aggressive redundancy pruning. |
| `feature_engg` | `''` | Auto-engineering mode: `''` (none), `'interactions'`, `'groupby'` |
| `nrows_limit` | `None` | Subsample N rows for speed on large datasets. `None` = use all rows. |
| `transform_target` | `False` | Apply Box-Cox to regression targets (helps with skewed targets). |
| `skip_sulov` | `False` | Bypass SULOV; use only MRMR. |
| `skip_xgboost` | `False` | Bypass MRMR; use only SULOV output. |
| `dask_xgboost_flag` | `False` | Use Dask for parallel XGBoost on large datasets. |
| `verbose` | `0` | Output detail: `0` = silent, `1` = progress, `2` = full debug. |

---

## Configuration Recipes

**Standard classification (default):**
```python
fwiz = FeatureWiz(corr_limit=0.7, feature_engg='', verbose=0)
```

**Regression with skewed target:**
```python
fwiz = FeatureWiz(corr_limit=0.7, transform_target=True, verbose=1)
```

**Wide dataset (>50 correlated columns):**
```python
# Lower corr_limit prunes more aggressively, preventing the MRMR step from
# being overwhelmed by near-duplicate features.
fwiz = FeatureWiz(corr_limit=0.5, verbose=1)
```

**Large dataset (>1M rows):**
```python
# dask_xgboost_flag enables parallel processing.
# nrows_limit subsamples for SULOV — useful if full dataset is too slow.
fwiz = FeatureWiz(corr_limit=0.7, dask_xgboost_flag=True, nrows_limit=200_000)
```

**Automated interaction features:**
```python
# WARNING: 'interactions' can create a very large number of features.
# Only use on datasets with ≤30 base features to avoid explosion.
fwiz = FeatureWiz(corr_limit=0.7, feature_engg='interactions')
```

**GroupBy aggregations:**
```python
# Automatically generates mean/std/count aggregations grouped by categorical columns.
# Useful for customer-level aggregations from transaction data.
fwiz = FeatureWiz(corr_limit=0.7, feature_engg='groupby')
```

**Known-important features being dropped:**
```python
# If featurewiz eliminates features you know are important (domain knowledge),
# bypass SULOV and let MRMR decide.
fwiz = FeatureWiz(corr_limit=0.7, skip_sulov=True)
```

---

## Reading featurewiz Output

```python
fwiz = FeatureWiz(corr_limit=0.7, verbose=2)
X_train_sel, y_train = fwiz.fit_transform(X_train, y_train)

# Inspect results
print("Selected features:", fwiz.features)
print("Feature count in:", X_train.shape[1])
print("Feature count out:", len(fwiz.features))
print("Reduction:", round((1 - len(fwiz.features) / X_train.shape[1]) * 100, 1), "%")

# Apply to test — uses the SAME selected feature list
X_test_sel = fwiz.transform(X_test)
assert list(X_test_sel.columns) == list(X_train_sel.columns), "Column mismatch"
```

---

## When featurewiz Does NOT Work

| Situation | Why it fails | What to do instead |
|---|---|---|
| No target variable (clustering) | MRMR requires a target | Manual selection only |
| Datetime columns present | XGBoost cannot consume datetime | Extract datetime features first (year/month/dow/hour), then run featurewiz |
| Text columns present | XGBoost cannot consume raw strings | Vectorize to TF-IDF or embeddings first, then run featurewiz on numeric outputs |
| Python < 3.12 | Compatibility constraint | Upgrade Python |
| pandas < 2.0 | Compatibility constraint | Upgrade pandas |
| Single-row prediction at inference | featurewiz transform expects DataFrames | Wrap single rows in `pd.DataFrame([row])` |

---

## Comparison with Alternatives

| Tool | Approach | Strengths | Weaknesses |
|---|---|---|---|
| **featurewiz** (primary) | SULOV + MRMR via XGBoost | Fast, handles correlated features, automatically determines feature count | Requires target; no datetime/text support |
| Boruta | Random forest shadow features | Robust, well-proven in academia | Slow on large data; requires tuning |
| SelectKBest | Univariate statistical tests | Simple, fast, no model needed | Misses interactions; ignores redundancy |
| Manual domain | Expert feature crafting | Best for domain-specific features featurewiz cannot discover | Does not scale; subjective |
| RFECV | Recursive feature elimination + CV | Model-agnostic; cross-validated | Very slow on large feature sets |

**Recommendation:** Start with featurewiz for automated selection on any supervised task with clean numeric features. Supplement with manual engineering for domain features (ratios, lag features, business-rule aggregations) that automated discovery misses.
