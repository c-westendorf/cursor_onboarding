# Product-Centric Organization

[Home](../README.md) > [Workspace Organization](README.md) > Product-Centric Model

---

## The Principle

**One workspace = One data product (or tightly related set)**

A data product may include:
- ML / modeling components
- Analytics / SQL code
- Frontend / UI elements
- Pipelines / infrastructure

All of these can live in one workspace because they share context.

---

## Why Product-Centric?

### Cross-Domain Rules Don't Work

```
# Problem: "All ML" workspace
workspace-all-ml/
├── churn-prediction/      # Has specific data contracts
├── recommendation-engine/ # Completely different domain
└── fraud-detection/       # Different evaluation standards

# Rules become either:
# - Too generic to be useful
# - Full of exceptions and conditionals
```

### Product Context is Shared

```
# Solution: Product-focused workspace
churn-prediction-product/
├── ml/                # Modeling code
├── api/               # Serving API
├── analytics/         # Business metrics
├── dashboard/         # Visualization
└── .cursor/rules/     # Rules specific to THIS product
```

Rules can reference:
- The specific data dictionary
- The product's evaluation criteria
- Domain-specific patterns

---

## Workspace Boundaries

### Include in Same Workspace

| Criteria | Example |
|----------|---------|
| Shares data contracts | ML model + API that serves it |
| Shares evaluation | Training code + evaluation dashboards |
| Deploys together | Backend + frontend of same product |
| Team reviews together | Code that's always reviewed as unit |

### Separate Workspaces

| Criteria | Example |
|----------|---------|
| Different domains | Churn vs. Fraud detection |
| Different data contracts | Products using different data sources |
| Different teams | Separate team ownership |
| Independent deployment | Microservices that deploy separately |

---

## Examples

### Good: Product-Focused

```
demand-forecasting/
├── .cursor/
│   └── rules/
│       ├── core.mdc           # "No data leakage", "Reproducibility"
│       ├── forecasting.mdc    # Domain-specific patterns
│       └── sql-warehouse.mdc  # Team's warehouse patterns
├── src/
│   ├── features/              # Feature engineering
│   ├── models/                # Training code
│   └── serving/               # Inference API
├── analytics/                 # Business dashboards
├── tests/
└── docs/
    ├── data-dictionary.md
    └── evaluation-criteria.md
```

### Bad: Function-Focused

```
all-data-science/
├── .cursor/rules/
│   └── generic-ds-rules.mdc   # Too generic to be useful
├── project-a/                 # Different domain
├── project-b/                 # Different data
├── project-c/                 # Different team
└── shared/                    # What's actually shared?
```

---

## Multi-Repo Workspaces

Sometimes a product spans multiple repositories:

```
recommendation-product/ (workspace)
├── .cursor/rules/            # Shared rules
├── rec-model/                # ML repo (git submodule or folder)
├── rec-api/                  # API repo
└── rec-dashboard/            # Dashboard repo
```

### When This Works

- Repos are always worked on together
- Shared context is valuable
- Single team owns all repos

### When to Avoid

- Repos are independently maintained
- Different release cycles
- Rules would conflict

---

## Rule Scoping Within Product

### Core Rules (Always-Apply)

Apply to everything in the product:
```markdown
---
description: Demand forecasting product principles
alwaysApply: true
---

- Forecasts must include confidence intervals
- All predictions must be logged
- Never use future data in features
```

### Domain Rules (Auto-Attach)

Scope to specific directories:
```markdown
---
description: Feature engineering patterns
globs: "src/features/**/*.py"
---

# Feature Engineering

- Use consistent naming: {entity}_{aggregation}_{window}
- Document feature sources
- Include null handling
```

### Component Rules

Different rules for different components:
```
.cursor/rules/
├── core.mdc                    # alwaysApply
├── src-features.mdc            # globs: src/features/**
├── src-models.mdc              # globs: src/models/**
├── src-serving.mdc             # globs: src/serving/**
└── analytics-sql.mdc           # globs: analytics/**/*.sql
```

---

## Migration Path

### From Function-Centric

1. **Identify products**: Group work by business outcome
2. **Create workspaces**: One per product
3. **Move rules**: Product-specific rules into each workspace
4. **Refine**: Add domain context to rules

### From Monolith

1. **Keep monolith**: If it's truly one product
2. **Use directories**: Scope rules with globs
3. **Or split**: If components are independently valuable

---

## See Also

- **Next**: [Directory Structures](directory-structures.md)
- **Context**: [Workspace Model](../../cursor_playbook_v4.md) (source material)
