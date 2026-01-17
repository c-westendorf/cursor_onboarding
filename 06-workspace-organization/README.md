# Workspace Organization

[Home](../README.md) > Workspace Organization

---

## Overview

How you organize your Cursor workspace directly impacts rule effectiveness and team collaboration. This section covers organization strategies for data science projects.

---

## Key Principle

**Organize by product, not by function.**

A workspace should map to a data product or tightly related set of products — not to "all ML work" or "all analytics."

---

## Documents in This Section

| Document | Description |
|----------|-------------|
| [Product-Centric Model](product-centric-model.md) | Workspace = Product philosophy |
| [Directory Structures](directory-structures.md) | Templates for small/medium/large projects |
| [.cursorignore Guide](cursorignore-guide.md) | Excluding files from indexing |

---

## Quick Reference

### Workspace Scope

| Good Workspace Scope | Bad Workspace Scope |
|---------------------|---------------------|
| Customer churn prediction product | All ML projects |
| Demand forecasting system | Everything by data team |
| Recommendation engine | All Python code |

### Rule Placement

```
.cursor/rules/
├── core.mdc              # Always-apply (1-2 only)
├── python/               # Auto-attach for *.py
├── ml/                   # Auto-attach for ml/**/*
├── sql/                  # Auto-attach for *.sql
└── reference/            # On-demand
```

### .cursorignore

```
# Data
data/
*.csv
*.parquet

# Models
models/
*.pkl
*.h5

# Logs
logs/
*.log
```

---

## Workspace Model

```
       ┌─────────────────────┐
       │     Workspace       │
       │   (Data Product)    │
       └──────────┬──────────┘
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
   ┌────────┐ ┌────────┐ ┌────────┐
   │ Repo A │ │ Repo B │ │ Repo C │
   │  (ML)  │ │ (API)  │ │ (UI)   │
   └────────┘ └────────┘ └────────┘
```

Only group repos that:
- Share data contracts
- Share evaluation standards
- Share architectural assumptions

---

## See Also

- **Previous Section**: [MCP Integration](../05-mcp-integration/README.md)
- **Next Section**: [Team Maturity](../07-team-maturity-journey/README.md)
- **Context**: [Context Budgeting](../03-rules-deep-dive/context-budgeting.md)
