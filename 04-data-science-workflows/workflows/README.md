# Data Science Workflows

[Home](../../README.md) > [DS Workflows](../README.md) > Workflows

---

## Overview

This section contains structured workflows for common data science tasks. Each workflow can be used as a guide or invoked as a prompt template.

---

## Available Workflows

| Workflow | Purpose |
|----------|---------|
| [EDA Workflow](eda-workflow.md) | Systematic exploratory data analysis |
| [Model Evaluation](model-evaluation.md) | Comprehensive model assessment |

---

## How to Use Workflows

### As a Guide

Read through the workflow steps and follow them manually:

1. Open workflow document
2. Work through each section
3. Check off completed items
4. Document findings

### As a Prompt

Reference the workflow in chat:

```
Following the EDA workflow in @04-data-science-workflows/workflows/eda-workflow.md,
analyze @data/customer_data.csv
```

### As a Skill

For repeatable workflows, the agent can follow structured steps:

```
User: Run the model evaluation protocol on my trained model

Agent: [Follows model-evaluation.md steps]
1. Loading model and test data...
2. Calculating baseline metrics...
3. Generating confusion matrix...
[etc.]
```

---

## Workflow Design Principles

### 1. Ordered Steps
Each workflow has a clear sequence that builds on previous steps.

### 2. Decision Points
Workflows include conditional branches for different scenarios.

### 3. Documentation Prompts
Workflows remind you to document findings at key points.

### 4. Validation Checkpoints
Built-in checks to ensure quality before proceeding.

---

## Creating Custom Workflows

Template for new workflows:

```markdown
# [Workflow Name]

## Purpose
What this workflow accomplishes.

## When to Use
Scenarios where this workflow applies.

## Prerequisites
- Required data
- Required tools/libraries
- Prior steps completed

## Steps

### 1. [First Step]
**Goal:** What this step accomplishes
**Actions:**
- Action 1
- Action 2
**Output:** What should result
**Checkpoint:** How to verify success

### 2. [Second Step]
...

## Documentation Template
What to record when complete.

## Common Issues
Known problems and solutions.
```

---

## See Also

- **Parent**: [DS Workflows](../README.md)
- **EDA**: [EDA Workflow](eda-workflow.md)
- **Evaluation**: [Model Evaluation](model-evaluation.md)
- **Shared Skills**: [Marketplace Skills](../../08-marketplace/catalog/shared-skills.md)
