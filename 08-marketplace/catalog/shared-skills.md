# Shared Skills

[Home](../../README.md) > [Marketplace](../README.md) > [Catalog](README.md) > Shared Skills

---

## Overview

Skills are repeatable procedures that guide reasoning without enforcing outcomes.

---

## Available Skills

| Skill | Domain | Purpose |
|-------|--------|---------|
| Data QA Checklist | Data | Validate data quality |
| Model Evaluation Protocol | ML | Comprehensive model assessment |
| EDA Workflow | Analytics | Systematic exploration |
| Feature Engineering | ML | Feature creation process |
| Error Analysis | ML | Debug model failures |

---

## Data QA Checklist

**Location:** `skills/data-qa-checklist.md`

**Purpose:** Systematic data quality assessment

**When to use:**
- Receiving new data
- After data pipeline runs
- Before model training

**Steps:**
1. Schema validation (columns, types)
2. Completeness check (nulls, missing)
3. Validity check (ranges, formats)
4. Consistency check (duplicates, conflicts)
5. Freshness check (timestamps, versions)

---

## Model Evaluation Protocol

**Location:** `skills/model-evaluation-protocol.md`

**Purpose:** Comprehensive model evaluation before deployment

**When to use:**
- After model training
- Before production deployment
- During model review

**Steps:**
1. Establish baseline
2. Calculate primary metrics
3. Generate confusion matrix / residual plots
4. Analyze feature importance
5. Perform error analysis
6. Document findings

---

## EDA Workflow

**Location:** `skills/eda-workflow.md`

**Purpose:** Systematic exploratory data analysis

**When to use:**
- Starting with new dataset
- After data changes
- Before modeling

**Steps:**
1. Initial inspection (shape, types)
2. Missing value analysis
3. Distribution analysis
4. Correlation analysis
5. Target analysis
6. Outlier detection
7. Summary documentation

---

## Feature Engineering

**Location:** `skills/feature-engineering.md`

**Purpose:** Systematic feature creation

**When to use:**
- Building ML models
- Improving model performance
- Creating derived variables

**Steps:**
1. Understand domain and target
2. Identify raw features
3. Create temporal features
4. Create aggregation features
5. Create interaction features
6. Validate no leakage
7. Document features

---

## Error Analysis

**Location:** `skills/error-analysis.md`

**Purpose:** Systematic model failure investigation

**When to use:**
- Model underperforming
- Debugging predictions
- Understanding failure modes

**Steps:**
1. Sample errors (stratified)
2. Categorize error types
3. Identify patterns
4. Hypothesize causes
5. Test hypotheses
6. Document findings
7. Plan improvements

---

## Using Skills

### As a Guide
Read through steps and follow manually.

### As a Prompt
```
Follow the Model Evaluation Protocol from @skills/model-evaluation-protocol.md
to evaluate my trained classifier.
```

### In Agent Mode
```
Using the EDA Workflow skill, analyze @data/customers.csv
```

---

## See Also

- [Rules Catalog](rules-by-domain.md)
- [Prompt Templates](prompt-templates.md)
- [DS Workflows](../../04-data-science-workflows/workflows/README.md)
