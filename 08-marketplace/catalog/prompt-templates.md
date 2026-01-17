# Prompt Templates

[Home](../../README.md) > [Marketplace](../README.md) > [Catalog](README.md) > Prompt Templates

---

## Overview

Reusable prompt templates for common data science tasks.

---

## Available Prompts

### EDA Prompts
| Prompt | Purpose |
|--------|---------|
| Initial Exploration | Start systematic EDA |
| Distribution Analysis | Analyze variable distributions |
| Correlation Check | Find relationships |

### Debugging Prompts
| Prompt | Purpose |
|--------|---------|
| Model Performance | Debug underperforming models |
| Data Quality Issues | Investigate data problems |

### Code Review Prompts
| Prompt | Purpose |
|--------|---------|
| ML Code Review | Review ML code |

---

## EDA: Initial Exploration

**Location:** `prompts/eda/initial-exploration.md`

**Purpose:** Start comprehensive EDA on a new dataset

**Variables:**
- `[dataset]` - File path or DataFrame name
- `[target]` - Target variable name (if any)

**Prompt:**
```
Run initial exploratory data analysis on [dataset]:

1. Show shape and column data types
2. Summarize missing values (count and percentage)
3. Display summary statistics for numeric columns
4. Show value counts for categorical columns (top 10)
5. Identify potential data quality issues

Target variable: [target]

Present findings in a structured format with clear sections.
```

---

## EDA: Distribution Analysis

**Location:** `prompts/eda/distribution-analysis.md`

**Purpose:** Analyze distributions of variables

**Variables:**
- `[dataset]` - DataFrame name
- `[columns]` - Columns to analyze (or "all numeric")

**Prompt:**
```
Analyze the distributions of [columns] in [dataset]:

For each variable:
1. Create histogram with appropriate bins
2. Calculate skewness and kurtosis
3. Identify potential outliers (IQR method)
4. Suggest transformations if needed (log, sqrt, etc.)
5. Note any concerning patterns

Summarize which variables may need transformation before modeling.
```

---

## EDA: Correlation Check

**Location:** `prompts/eda/correlation-check.md`

**Purpose:** Find relationships between variables

**Variables:**
- `[dataset]` - DataFrame name
- `[target]` - Target variable

**Prompt:**
```
Analyze correlations in [dataset] with target [target]:

1. Create correlation matrix for numeric variables
2. Highlight highly correlated pairs (|r| > 0.7)
3. Show top 10 features correlated with target
4. Visualize key relationships with scatter plots
5. Identify potential multicollinearity issues

Recommend features to consider dropping or combining.
```

---

## Debug: Model Performance

**Location:** `prompts/debugging/model-performance.md`

**Purpose:** Debug underperforming models

**Variables:**
- `[model]` - Model object name
- `[X_test]` - Test features
- `[y_test]` - Test labels
- `[metric]` - Primary metric of concern

**Prompt:**
```
Help me debug why [model] is underperforming on [metric].

Current situation:
- Model: [model]
- Test data: [X_test], [y_test]
- Problematic metric: [metric]

Please:
1. Calculate detailed performance metrics
2. Analyze error distribution
3. Sample and examine misclassified/high-error examples
4. Check for data quality issues in test set
5. Compare feature distributions between correct/incorrect predictions
6. Suggest potential causes and fixes

Prioritize actionable insights.
```

---

## Debug: Data Quality Issues

**Location:** `prompts/debugging/data-quality-issues.md`

**Purpose:** Investigate data problems

**Variables:**
- `[dataset]` - DataFrame name
- `[issue]` - Observed issue description

**Prompt:**
```
Investigate data quality issues in [dataset].

Observed issue: [issue]

Please:
1. Validate schema (expected vs actual columns/types)
2. Check for unexpected nulls or values
3. Identify duplicates or inconsistencies
4. Trace potential data pipeline issues
5. Quantify the scope of the problem
6. Suggest remediation steps

Provide both immediate fixes and long-term prevention.
```

---

## Code Review: ML Code

**Location:** `prompts/code-review/ml-code-review.md`

**Purpose:** Review ML code for best practices

**Variables:**
- `[file]` - File to review

**Prompt:**
```
Review [file] for ML best practices:

Check for:
1. Data leakage (fit on train only, temporal ordering)
2. Reproducibility (random seeds, version logging)
3. Code quality (type hints, docstrings, error handling)
4. Performance (vectorization, memory efficiency)
5. Testing (test coverage for critical paths)

For each issue found:
- Severity (critical/medium/low)
- Location (line number)
- Problem description
- Suggested fix

Summarize overall code health and priority fixes.
```

---

## Using Prompts

### Direct Use
Copy and fill in variables:
```
Run initial exploratory data analysis on df_customers:
[rest of prompt...]
```

### With @-reference
```
Using the prompt template @prompts/eda/initial-exploration.md,
analyze the sales_data DataFrame with target column 'converted'.
```

---

## See Also

- [Rules Catalog](rules-by-domain.md)
- [Shared Skills](shared-skills.md)
- [Contributing Prompts](../governance/contribution-guide.md)
