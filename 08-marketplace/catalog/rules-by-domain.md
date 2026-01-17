# Rules by Domain

[Home](../../README.md) > [Marketplace](../README.md) > [Catalog](README.md) > Rules by Domain

---

## Overview

Marketplace rules organized by domain. Each rule is available in the `cursor-marketplace` repository.

---

## ML

Machine learning rules for training, evaluation, and deployment.

| Rule | Description | Activation |
|------|-------------|------------|
| `ml/model-training.mdc` | Training pipeline standards | Auto: `src/ml/**` |
| `ml/evaluation-metrics.mdc` | Evaluation requirements | Auto: `src/ml/**` |
| `ml/hyperparameter-tuning.mdc` | Hyperparameter best practices | Auto: `src/ml/**` |
| `ml/data-leakage-prevention.mdc` | Prevent train/test leakage | Auto: `**/*.py` |
| `ml/reproducibility.mdc` | Reproducibility requirements | Always |

### ml/model-training.mdc

**Purpose:** Standards for ML training pipelines

**Key points:**
- Split data before preprocessing
- Set random seeds
- Log all hyperparameters
- Save model configs

### ml/evaluation-metrics.mdc

**Purpose:** Model evaluation requirements

**Key points:**
- Always compare to baseline
- Report multiple metrics
- Include confidence intervals
- Document failure modes

### ml/data-leakage-prevention.mdc

**Purpose:** Prevent data leakage in ML pipelines

**Key points:**
- Fit transformers on training data only
- Validate temporal ordering
- Check for target leakage in features

---

## Analytics

Rules for SQL, dashboards, and business analytics.

| Rule | Description | Activation |
|------|-------------|------------|
| `analytics/sql-safety.mdc` | SQL security and quality | Auto: `**/*.sql` |
| `analytics/data-validation.mdc` | Data quality checks | Auto: `**/*.py` |
| `analytics/dashboard-standards.mdc` | Dashboard best practices | Auto: `dashboards/**` |
| `analytics/reporting-quality.mdc` | Report generation standards | On-demand |

### analytics/sql-safety.mdc

**Purpose:** SQL security and quality patterns

**Key points:**
- Use parameterized queries
- Explicit column selection
- Limit results for exploration
- Comment complex joins

### analytics/data-validation.mdc

**Purpose:** Data quality validation patterns

**Key points:**
- Schema validation
- Value range checks
- Null handling
- Duplicate detection

---

## Data Engineering

Rules for pipelines, schemas, and infrastructure.

| Rule | Description | Activation |
|------|-------------|------------|
| `data-eng/pipeline-standards.mdc` | Pipeline best practices | Auto: `pipelines/**` |
| `data-eng/schema-validation.mdc` | Schema enforcement | Auto: `**/*.py` |
| `data-eng/logging-requirements.mdc` | Logging standards | Auto: `**/*.py` |

### data-eng/pipeline-standards.mdc

**Purpose:** Data pipeline standards

**Key points:**
- Idempotent operations
- Error handling and retries
- Checkpoint/recovery
- Monitoring and alerting

### data-eng/schema-validation.mdc

**Purpose:** Schema enforcement patterns

**Key points:**
- Validate on ingestion
- Type checking
- Required field validation
- Schema evolution handling

---

## General

Cross-cutting rules that apply broadly.

| Rule | Description | Activation |
|------|-------------|------------|
| `general/core-principles.mdc` | Universal principles | Always |
| `general/python-standards.mdc` | Python code quality | Auto: `**/*.py` |
| `general/documentation.mdc` | Documentation requirements | Auto: `**/*.py` |

### general/core-principles.mdc

**Purpose:** Universal project principles (always-apply)

**Key points:**
- Reproducibility
- No fabrication
- Explicit over implicit
- Error handling

---

## Using These Rules

### Copy Individual Rules

```bash
# Copy specific rule
cp cursor-marketplace/rules/ml/model-training.mdc .cursor/rules/

# Customize for your project
vi .cursor/rules/model-training.mdc
```

### Use All Rules (Submodule)

```bash
git submodule add https://github.com/org/cursor-marketplace .cursor/shared
```

---

## See Also

- [Shared Skills](shared-skills.md)
- [Prompt Templates](prompt-templates.md)
- [Distribution Guide](../distribution/README.md)
