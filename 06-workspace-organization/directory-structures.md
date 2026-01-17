# Directory Structure Templates

[Home](../README.md) > [Workspace Organization](README.md) > Directory Structures

---

## Overview

Templates for organizing data science projects of different sizes.

---

## Small Project

**Characteristics:**
- Single person or small team
- One main model/analysis
- Quick iteration

```
small-ds-project/
├── .cursor/
│   └── rules/
│       ├── core.mdc                # 1-2 always-apply rules
│       └── python.mdc              # Python standards
├── .cursorignore
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   ├── 01-exploration.ipynb
│   ├── 02-modeling.ipynb
│   └── 03-evaluation.ipynb
├── src/
│   ├── __init__.py
│   ├── data.py
│   ├── features.py
│   └── model.py
├── tests/
│   └── test_model.py
├── requirements.txt
└── README.md
```

**Rules Strategy:**
- 1 core.mdc with essentials
- 1 python.mdc for language patterns
- Keep it simple

---

## Medium Project

**Characteristics:**
- Small team (2-5)
- Multiple components
- Production deployment

```
medium-ds-project/
├── .cursor/
│   └── rules/
│       ├── core.mdc                # Always-apply
│       ├── python-standards.mdc    # globs: **/*.py
│       ├── sql-safety.mdc          # globs: **/*.sql
│       ├── notebooks.mdc           # globs: **/*.ipynb
│       └── testing.mdc             # globs: tests/**/*
├── .cursorignore
├── .github/
│   └── workflows/
│       └── ci.yml
├── config/
│   ├── dev.yaml
│   └── prod.yaml
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── docs/
│   ├── data-dictionary.md
│   └── model-card.md
├── notebooks/
│   ├── exploration/
│   ├── experiments/
│   └── reports/
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loaders.py
│   │   └── validators.py
│   ├── features/
│   │   ├── __init__.py
│   │   └── engineering.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── train.py
│   │   └── predict.py
│   └── utils/
│       └── logging.py
├── sql/
│   ├── features/
│   └── reporting/
├── tests/
│   ├── unit/
│   └── integration/
├── Makefile
├── pyproject.toml
└── README.md
```

**Rules Strategy:**
- 1 core.mdc (always-apply)
- Domain rules with globs (python, sql, notebooks)
- Testing-specific rules
- ~5-8 total rules

---

## Large/Enterprise Project

**Characteristics:**
- Multiple teams
- Complex pipelines
- Strict governance

```
enterprise-ds-project/
├── .cursor/
│   └── rules/
│       ├── core-principles.mdc         # Always-apply (very short)
│       ├── python/
│       │   ├── standards.mdc           # **/*.py
│       │   ├── typing.mdc              # **/*.py
│       │   └── testing.mdc             # tests/**/*.py
│       ├── ml/
│       │   ├── training.mdc            # src/ml/**
│       │   ├── evaluation.mdc          # src/ml/**
│       │   └── reproducibility.mdc     # src/ml/**
│       ├── data/
│       │   ├── validation.mdc          # src/data/**
│       │   └── quality.mdc             # src/data/**
│       ├── sql/
│       │   ├── safety.mdc              # **/*.sql
│       │   └── optimization.mdc        # On-demand
│       └── reference/                  # On-demand detailed guides
│           ├── advanced-patterns.mdc
│           └── legacy-systems.mdc
├── .cursorignore
├── .devcontainer/
│   └── devcontainer.json
├── .github/
│   ├── CODEOWNERS
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── cd.yml
│   │   └── data-quality.yml
│   └── pull_request_template.md
├── config/
│   ├── environments/
│   │   ├── dev.yaml
│   │   ├── staging.yaml
│   │   └── prod.yaml
│   └── feature_flags.yaml
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── external/
├── deploy/
│   ├── kubernetes/
│   └── terraform/
├── docs/
│   ├── architecture/
│   ├── data-dictionary/
│   ├── model-cards/
│   ├── runbooks/
│   └── onboarding/
├── notebooks/
│   ├── exploration/
│   ├── experiments/
│   ├── reports/
│   └── templates/
├── scripts/
│   ├── setup.sh
│   └── deploy.sh
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   └── schemas/
│   ├── data/
│   │   ├── __init__.py
│   │   ├── connectors/
│   │   ├── loaders/
│   │   ├── validators/
│   │   └── transformers/
│   ├── features/
│   │   ├── __init__.py
│   │   ├── engineering/
│   │   └── selection/
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── training/
│   │   ├── evaluation/
│   │   ├── inference/
│   │   └── monitoring/
│   ├── pipelines/
│   │   ├── __init__.py
│   │   ├── training_pipeline.py
│   │   └── inference_pipeline.py
│   └── utils/
│       ├── __init__.py
│       ├── config.py
│       ├── logging.py
│       └── metrics.py
├── sql/
│   ├── features/
│   ├── reporting/
│   └── migrations/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── fixtures/
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── pyproject.toml
└── README.md
```

**Rules Strategy:**
- 1 very short core-principles.mdc (always-apply)
- Organized in subdirectories by domain
- On-demand reference rules for detailed guides
- ~15-25 rules total

---

## Choosing Your Structure

| Factor | Small | Medium | Large |
|--------|-------|--------|-------|
| Team size | 1-2 | 2-5 | 5+ |
| Rule count | 2-3 | 5-8 | 15-25 |
| Directory depth | 2 levels | 3 levels | 4+ levels |
| CI/CD | Optional | Yes | Required |
| Documentation | README | docs/ folder | Full docs site |

---

## Scaling Up

### Small → Medium

1. Add directory structure for organization
2. Add more specific rules with globs
3. Introduce testing requirements
4. Set up CI/CD

### Medium → Large

1. Organize rules into subdirectories
2. Add governance and CODEOWNERS
3. Create on-demand reference rules
4. Set up devcontainer for consistency

---

## See Also

- **Previous**: [Product-Centric Model](product-centric-model.md)
- **Next**: [.cursorignore Guide](cursorignore-guide.md)
- **Templates**: [Project Templates](../templates/README.md)
