# Assumption Audit Pattern

Run this audit before every major decision point in a data workflow. The goal is to surface hidden assumptions that could invalidate your analysis.

## The 4 Questions

Before proceeding with any data operation, ask:

### 1. What am I assuming about data quality?

Common hidden assumptions:
- "Nulls are random" — they might be systematic (e.g., high-income users skip income fields)
- "Column types are correct" — object columns might contain mixed types
- "No duplicates exist" — upstream joins can silently create duplicates
- "Values are within expected ranges" — sentinel values (-999, 9999) may masquerade as real data

### 2. What am I assuming about the data generation process?

Common hidden assumptions:
- "Data was collected uniformly" — collection methods may have changed over time
- "Observations are independent" — users may appear multiple times, creating autocorrelation
- "The sample represents the population" — survivorship bias, selection bias
- "Features are measured the same way across records" — definition changes, unit changes
- "Time-series data is regularly spaced" — gaps, timezone issues, DST

### 3. What would invalidate these assumptions?

For each assumption, define the falsification condition:
- "If nulls correlate with the target variable, they are NOT random" → run logistic regression of `is_null ~ target`
- "If distributions shift across time windows, data is NOT stationary" → KS-test on rolling windows
- "If duplicate rates exceed 1%, upstream joins need investigation" → check join cardinality

### 4. What checks should I run before proceeding?

Map each assumption to a concrete validation:

| Assumption | Validation Check | Code |
|---|---|---|
| Nulls are random | `df.isnull().corr()` shows no pattern | `msno.heatmap(df)` |
| No distribution shift | KS-test between time slices | `scipy.stats.ks_2samp(early, late)` |
| Features are independent | VIF < 10 for all features | `statsmodels.stats.outliers_influence.variance_inflation_factor` |
| Sample is representative | Compare summary stats to known population | Manual comparison |
| No target leakage | No feature has >0.95 correlation with target | `df.corrwith(df[target]).abs().sort_values()` |

## Usage in Playbooks

Invoke this pattern at these moments:
- **Before data cleaning**: "Am I assuming this file is well-formed? What if the encoding is wrong?"
- **Before imputation**: "Am I assuming MCAR? What if missingness is informative?"
- **Before EDA conclusions**: "Am I assuming stationarity? Would a time split tell a different story?"
- **Before feature engineering**: "Am I assuming these transforms are production-safe? What about unseen categories?"
- **Before model training**: "Am I assuming the training distribution matches production?"

## Template

Copy this into your analysis notebook:

```markdown
## Assumption Audit: [Step Name]

**What I'm assuming about data quality:**
- [ ] ...

**What I'm assuming about data generation:**
- [ ] ...

**What would invalidate these assumptions:**
- [ ] ...

**Checks I will run:**
- [ ] ...

**Audit result:** [PROCEED / PROCEED WITH CAUTION / STOP AND INVESTIGATE]
```
