# Marketplace Catalog

[Home](../../README.md) > [Marketplace](../README.md) > Catalog

---

## Overview

Browse all available rules, skills, and prompts in the marketplace.

---

## Browse by Type

| Type | Description | View |
|------|-------------|------|
| **Rules** | Cursor .mdc rules by domain | [Rules](rules-by-domain.md) |
| **Skills** | Repeatable procedures | [Skills](shared-skills.md) |
| **Prompts** | Reusable prompt templates | [Prompts](prompt-templates.md) |

---

## Browse by Domain

### ML / Modeling
Rules and skills for machine learning work.
- [ML Rules](rules-by-domain.md#ml)
- [Model Evaluation Skill](shared-skills.md#model-evaluation)

### Analytics
Rules and skills for SQL and analytics work.
- [Analytics Rules](rules-by-domain.md#analytics)
- [EDA Workflow Skill](shared-skills.md#eda-workflow)

### Data Engineering
Rules for pipelines and infrastructure.
- [Data-Eng Rules](rules-by-domain.md#data-engineering)

### General
Cross-cutting rules that apply broadly.
- [General Rules](rules-by-domain.md#general)

---

## Popular Resources

### Most Used Rules
1. `ml/model-training.mdc` - Training standards
2. `analytics/sql-safety.mdc` - SQL security
3. `ml/evaluation-metrics.mdc` - Evaluation requirements

### Most Used Skills
1. EDA Workflow - Exploratory data analysis
2. Model Evaluation Protocol - Comprehensive evaluation

### Most Used Prompts
1. Initial Exploration - Start EDA
2. Model Performance Debug - Debug models

---

## How to Use

### In Your Project

**Option 1: Copy individual files**
```bash
cp cursor-marketplace/rules/ml/model-training.mdc .cursor/rules/
```

**Option 2: Git submodule (all resources)**
```bash
git submodule add https://github.com/org/cursor-marketplace .cursor/shared
```

See [Distribution Guide](../distribution/README.md) for details.

---

## See Also

- [Distribution](../distribution/README.md)
- [Contributing](../governance/contribution-guide.md)
