# Artifact Types Comparison

[Home](../README.md) > [Core Concepts](README.md) > Artifact Types

---

## Overview

Cursor's knowledge system uses four main artifact types. Each serves a different purpose, has different file formats, and activates differently. Understanding these distinctions is critical for **efficient usage**—the right artifact in the right place makes the single agent behave like a specialist.

**Key insight:** You don't create specialized agents—you configure ONE agent through these artifacts. Rules auto-load to constrain behavior, skills provide procedures on-demand, and prompts kick off specific tasks.

---

## The Four Artifact Types

```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│   Rules     │   Skills    │  Prompts    │  Code/CI    │
│   (.mdc)    │   (.md)     │   (.md)     │  (.py/.yml) │
├─────────────┼─────────────┼─────────────┼─────────────┤
│ Constraints │ Procedures  │ Task kicks  │ Hard checks │
│ "Don't..."  │ "How to..." │ "Do X..."   │ "Fail if..."|
├─────────────┼─────────────┼─────────────┼─────────────┤
│ AUTO-LOADED │ REFERENCED  │ COPY/PASTE  │ EXTERNAL    │
│ by Cursor   │ via @mention│ into chat   │ CI/CD runs  │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

---

## Critical File Format Distinctions

### `.mdc` Files (Rules)

**What they are:** Cursor-specific markdown files with YAML frontmatter that Cursor automatically processes.

**Key characteristics:**
- **Extension must be `.mdc`** (not `.md`) for Cursor to recognize as a rule
- **Location:** Must be in `.cursor/rules/` directory
- **Activation:** Automatic based on `alwaysApply` or `globs` settings
- **Audience:** Primarily the AI agent (instructions for behavior)

```yaml
---
description: Brief description (required, <100 chars)
globs: "**/*.py"      # Auto-attach to matching files
alwaysApply: false    # Or true for always-on
---

# Rule content in markdown
Instructions for the AI...
```

### `.md` Files (Skills & Prompts)

**What they are:** Standard markdown files containing procedures or prompt templates. NOT automatically loaded by Cursor.

**Key characteristics:**
- **Extension is `.md`** (standard markdown)
- **Location:** Anywhere (docs folder, marketplace, wiki)
- **Activation:** Manual — user must reference or copy content
- **Audience:** Humans AND AI (guidance for both)

**Skills** = Step-by-step procedures with checkpoints
**Prompts** = Reusable templates with fill-in variables

```markdown
# Skill: EDA Workflow

## Step 1: Load and Inspect
- Check shape and dtypes
- [Checkpoint] Data loaded successfully

## Step 2: Missing Values
- Calculate null percentages
- [Checkpoint] Missing data documented
```

---

## How Each Artifact Activates

| Artifact | File Type | How It Activates | User Action Required |
|----------|-----------|------------------|---------------------|
| **Rule** | `.mdc` | Cursor loads automatically | None (or `@rulename`) |
| **Skill** | `.md` | User references in conversation | `@skill.md` or copy content |
| **Prompt** | `.md` | User copies into chat | Copy/paste template |
| **Code/CI** | `.py/.yml` | CI system runs | Push code to trigger |

### Activation Flow Diagram

```
USER STARTS CONVERSATION
         │
         ▼
┌─────────────────────────────────────┐
│  RULES (.mdc) AUTO-LOAD             │
│  ┌─────────────────────────────┐    │
│  │ alwaysApply: true rules     │────┼──► Always in context
│  └─────────────────────────────┘    │
│  ┌─────────────────────────────┐    │
│  │ globs-matched rules         │────┼──► If matching files open
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  USER MANUALLY ADDS                 │
│  ┌─────────────────────────────┐    │
│  │ @skill.md reference         │────┼──► Pulls in skill content
│  └─────────────────────────────┘    │
│  ┌─────────────────────────────┐    │
│  │ Pasted prompt template      │────┼──► Starts specific task
│  └─────────────────────────────┘    │
│  ┌─────────────────────────────┐    │
│  │ @rulename (on-demand rule)  │────┼──► Pulls in specific rule
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
         │
         ▼
    AI RESPONDS
    (shaped by all active context)
```

---

## Detailed Comparison

| Aspect | Rules (.mdc) | Skills (.md) | Prompts (.md) | Code/CI |
|--------|-------------|--------------|---------------|---------|
| **File Extension** | `.mdc` | `.md` | `.md` | `.py/.yml` |
| **Purpose** | Shape AI behavior | Teach procedures | Start specific tasks | Enforce correctness |
| **Volatility** | Low (6+ months) | Medium | High (per-task) | Low |
| **Activation** | Automatic | Manual reference | Manual copy | CI triggers |
| **Enforcement** | Soft (AI follows) | None (guidance) | None (starting point) | Hard (blocks) |
| **Audience** | AI agent | Human + AI | Human + AI | Systems |
| **Location** | `.cursor/rules/` | Anywhere | Anywhere | Code/CI config |
| **Cursor Loads** | Yes (auto) | No | No | No |

---

## When to Use Each

### Rules (`.mdc` files)

**Use when:**
- The guidance is stable (won't change for months)
- It applies broadly across the project
- Violations are clearly mistakes
- You'd teach this to every new team member

**Examples:**
- "Never hardcode credentials"
- "Always validate input data shapes"
- "Use vectorized pandas operations"
- "Set random seeds for reproducibility"

**Don't use when:**
- The guidance is situational
- It's a tutorial or how-to
- It changes frequently
- It only applies to specific edge cases

---

### Skills

**Use when:**
- You have a repeatable procedure
- Human judgment is part of the process
- The steps may vary by context
- You want to teach thinking, not enforce rules

**Examples:**
- EDA checklist
- Model evaluation protocol
- Data quality assessment procedure
- Error analysis workflow

**Don't use when:**
- The outcome should be enforced automatically
- There's no human decision-making involved
- It's a one-time procedure

---

### Prompts (Templates)

**Use when:**
- Starting a specific type of task
- The task is common but context-dependent
- You want consistency in how tasks begin
- Different users might approach it differently

**Examples:**
- "Run EDA on this dataset, focusing on..."
- "Review this model's performance against..."
- "Generate test cases for..."
- "Refactor this function to..."

**Don't use when:**
- The task should always happen automatically
- There's no variation in how it's done
- It's a rule that should always apply

---

### Code/CI (Including Data Contracts)

**Use when:**
- Violations should block production
- Silent failure is unacceptable
- An audit trail is required
- No human judgment should be involved

**Examples:**
- Schema validation
- Data type checks
- Test coverage requirements
- Security scans
- Linting rules
- **Data contracts** (schema, quality SLAs, freshness)

**Data Contracts** deserve special mention for data scientists:
```yaml
# Example contract enforcement
schema:
  - name: customer_id
    type: string
    not_null: true
quality:
  freshness: "< 24 hours"
  null_rate: "< 0.01"
```

Contracts formalize expectations between data producers and consumers—critical for ML pipelines where upstream changes can silently break models.

→ *Deep dive: [Data Contracts](../04-data-science-workflows/data-contracts.md)*

**Don't use when:**
- The check requires AI reasoning
- Context-dependent judgment is needed
- It would slow iteration too much

---

## Decision Matrix

Use this matrix to quickly decide where knowledge belongs:

| Knowledge Characteristic | → Artifact Type |
|-------------------------|-----------------|
| Stable + Universal + Soft enforcement | **Rule** |
| Stable + Universal + Hard enforcement | **Code/CI** |
| Stable + Narrow scope | **On-demand Rule** |
| Evolving + Procedural | **Skill** |
| Contextual + Task-starting | **Prompt** |
| Ephemeral + Situational | **Human judgment** |

---

## How Artifacts Work Together

### Example: Model Training Workflow

```
┌─────────────────────────────────────────────────────────┐
│  RULES (Always active)                                  │
│  - "Set random seeds"                                   │
│  - "Never train on test data"                           │
│  - "Log all hyperparameters"                            │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  SKILL (On-demand procedure)                            │
│  "Model Training Protocol"                              │
│  1. Validate data quality                               │
│  2. Establish baseline                                  │
│  3. Train with cross-validation                         │
│  4. Evaluate on holdout                                 │
│  5. Document results                                    │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  PROMPTS (Task-specific)                                │
│  "Train a classifier for churn prediction using        │
│   the customer_features table. Compare against         │
│   the baseline model from Q3."                         │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  CODE/CI + DATA CONTRACTS (Enforcement)                 │
│  - test_no_data_leakage.py                              │
│  - test_reproducibility.py                              │
│  - CI: minimum F1 score threshold                       │
│  - contracts/customer_features.yaml (schema + quality)  │
└─────────────────────────────────────────────────────────┘
```

---

## Common Mistakes

### Over-using Rules
**Symptom:** 20+ rules, AI becomes slow, rules conflict
**Fix:** Move tutorials to skills, situational guidance to prompts

### Under-using Rules
**Symptom:** Repeating same corrections in code review
**Fix:** Codify common corrections as rules

### Mixing Artifact Types
**Symptom:** Rule file contains "Step 1, Step 2, Step 3..."
**Fix:** That's a skill, not a rule. Rules are constraints.

### Skipping Code/CI for Critical Checks
**Symptom:** Relying on AI to catch security issues
**Fix:** Critical checks should fail CI, not just be in rules

---

## Practical Management Guide

### Where to Store Each Artifact

```
your-project/
├── .cursor/
│   └── rules/                    # .mdc files ONLY
│       ├── always-on.mdc         # alwaysApply: true
│       ├── python-standards.mdc  # globs: "**/*.py"
│       └── sql-safety.mdc        # globs: "**/*.sql"
│
├── docs/
│   ├── skills/                   # .md skill files
│   │   ├── eda-workflow.md
│   │   └── model-evaluation.md
│   │
│   └── prompts/                  # .md prompt templates
│       ├── debug-model.md
│       └── data-validation.md
│
└── .github/
    └── workflows/                # CI enforcement
        └── data-quality.yml
```

### How to Use Each in Practice

**Rules (.mdc):** Set and forget — they work automatically
```bash
# Create a rule
echo "---
description: Always use type hints
alwaysApply: true
---
Use type hints for all function parameters." > .cursor/rules/type-hints.mdc
```

**Skills (.md):** Reference when starting a workflow
```
# In Cursor chat:
"I'm starting EDA. Please follow @docs/skills/eda-workflow.md"
```

**Prompts (.md):** Copy template, fill variables, paste in chat
```
# From docs/prompts/debug-model.md, copy:
"Debug why my [MODEL_TYPE] has [CURRENT_METRIC] when target is [TARGET_METRIC]..."

# Fill in and paste:
"Debug why my XGBoost classifier has F1=0.65 when target is F1=0.80..."
```

### Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Putting rules in `.md` files | Cursor won't auto-load them | Use `.mdc` extension |
| Putting skills in `.cursor/rules/` | Bloats context unnecessarily | Move to `docs/skills/` |
| Making rules too long | Context budget exhausted | Keep rules <300 lines |
| Putting tutorials in rules | Rules should be constraints | Move to skills |

---

## See Also

- **Previous**: [3-Layer Stack](3-layer-stack.md)
- **Next**: [Agent Execution Model](agent-execution-model.md)
- **Then**: [Decision Flow](decision-flow/README.md)
- **Practical**: [Writing Effective Rules](../03-rules-deep-dive/writing-effective-rules.md)
- **Examples**: [Rule Examples](../03-rules-deep-dive/examples/README.md)
