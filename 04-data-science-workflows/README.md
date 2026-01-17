# Data Science Workflows

[Home](../README.md) > Data Science Workflows

---

## Overview

This section covers Cursor features and patterns specifically relevant to data science work: notebooks, databases, and common DS challenges.

---

## Documents in This Section

| Document | Description |
|----------|-------------|
| [Jupyter Notebooks](jupyter-notebooks.md) | Notebook support, limitations, and workarounds |
| [Database Integration](database-integration.md) | MCP servers vs IDE extensions for DB access |
| [Common Challenges](common-challenges.md) | Pandas quirks, PEP8, complex operations |
| [Data Contracts](data-contracts.md) | Schema validation, quality SLAs, enforcement |
| [Workflows](workflows/README.md) | EDA, model evaluation, and other DS workflows |

---

## Quick Reference

### Cursor's DS Strengths

| Feature | How It Helps |
|---------|--------------|
| Code completion | Fast pandas/numpy autocomplete |
| Chat with context | Explain complex transformations |
| Agent mode | Multi-step data processing |
| MCP integration | Direct database queries |

### Key Configurations for DS

```
.cursor/rules/
├── data-science-core.mdc    # Always-apply principles
├── pandas-operations.mdc    # Auto-attach for *.py
├── sql-safety.mdc           # Auto-attach for *.sql, *.py
├── notebooks.mdc            # Auto-attach for *.ipynb
└── data-contracts.mdc       # Auto-attach for *.py, *.yaml

contracts/                   # Data contract definitions
├── feature_store.yaml
├── training_data.yaml
└── inference_input.yaml

.cursorignore
├── data/
├── *.csv
├── *.parquet
└── models/
```

---

## Data Science Workflow Patterns

### Pattern 1: Exploratory Analysis

```
1. Load data with context (@data-dictionary)
2. Ask for EDA summary (use workflows/eda-workflow.md)
3. Iterate on visualizations
4. Document findings
```

### Pattern 2: Model Development

```
1. Reference existing patterns (@ml-training rule)
2. Establish baseline
3. Iterate with agent mode
4. Evaluate with protocol (workflows/model-evaluation.md)
```

### Pattern 3: SQL Analysis

```
1. Connect via MCP (recommended) or extension
2. Explore schema in chat
3. Build queries iteratively
4. Export to pandas for further analysis
```

---

## Common Questions

### Can Cursor run my Jupyter notebooks?

Yes, Cursor has native `.ipynb` support. However, agent mode has some limitations with cell-level editing. See [Jupyter Notebooks](jupyter-notebooks.md) for workarounds.

### How do I connect to my database?

Two options:
1. **MCP Server** (recommended): Agent can query directly
2. **IDE Extension**: Manual queries, good for exploration

See [Database Integration](database-integration.md) for setup.

### Why is AI struggling with my pandas code?

Complex groupby and aggregation operations can be challenging. See [Common Challenges](common-challenges.md) for tips on providing better context.

---

## See Also

- **Previous Section**: [Rules Deep Dive](../03-rules-deep-dive/README.md)
- **Next Section**: [MCP Integration](../05-mcp-integration/README.md)
- **Quick Start**: [DS Quickstart](../01-getting-started/data-science-quickstart.md)
