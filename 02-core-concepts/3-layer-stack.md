# The 3-Layer Knowledge Stack

[Home](../README.md) > [Core Concepts](README.md) > 3-Layer Stack

---

## Overview

Effective use of Cursor requires separating concerns into three distinct layers. Each layer has a different purpose, volatility, and enforcement mechanism.

---

## The Stack

```
┌────────────────────────────────────┐
│  Layer 1: Principles               │
│  Rules (.mdc files)                │
│  "What NOT to do / invariants"     │
└────────────────┬───────────────────┘
                 ▼
┌────────────────────────────────────┐
│  Layer 2: Playbooks                │
│  Skills + Prompts                  │
│  "How to do it well"               │
└────────────────┬───────────────────┘
                 ▼
┌────────────────────────────────────┐
│  Layer 3: Enforcement              │
│  Code + CI                         │
│  "Fail if wrong"                   │
└────────────────────────────────────┘
```

---

## Layer 1: Principles (Rules)

**Purpose:** Encode invariants — things that should always (or never) be true.

**Characteristics:**
- Low volatility (stable for 6+ months)
- Shape default AI behavior
- Not tutorials or how-tos

**Examples:**
| Good Rules (Invariants) | Bad Rules (Not Invariants) |
|-------------------------|---------------------------|
| "Never fabricate metrics or results" | "How to use pandas groupby" |
| "Always set random seeds for reproducibility" | "Our preferred model architectures" |
| "No hardcoded credentials in code" | "Steps to deploy a model" |
| "Validate data shapes after transformations" | "Our team's meeting schedule" |

**Location:** `.cursor/rules/*.mdc`

**Key insight:** Rules are **not tutorials**. They're constraints and guardrails.

---

## Layer 2: Playbooks (Skills + Prompts)

**Purpose:** Encode repeatable procedures and workflows.

**Characteristics:**
- Medium volatility (may evolve as practices mature)
- Guide reasoning, don't enforce
- Human-in-the-loop

**Examples:**
| Skills (Procedures) | Prompt Templates (Task Starters) |
|--------------------|----------------------------------|
| Data QA checklist | "Run EDA on this dataset" |
| Model evaluation protocol | "Help me debug this model's performance" |
| SQL safety review playbook | "Review this query for optimization" |
| Feature engineering workflow | "Generate features for [X] prediction" |

**Location:** Skills in docs or marketplace, prompts used interactively

**Key insight:** Playbooks help humans **think**, they don't force outcomes.

---

## Layer 3: Enforcement (Code + CI + Data Contracts)

**Purpose:** Guarantee correctness through automated checks.

**Characteristics:**
- Highest confidence requirements
- Blocks production if violated
- No human judgment required

**Examples:**
| Enforced in Code | Enforced in CI | Data Contracts |
|------------------|----------------|----------------|
| Schema validation | Linting (PEP8, type checks) | Column types & constraints |
| Input validation | Test coverage requirements | Freshness SLAs |
| Data type checks | Data leakage tests | Row count expectations |
| Required error handling | Evaluation metric thresholds | Null rate limits |

**Location:** Application code, test suites, CI/CD pipelines, contract definitions

**Key insight:** If correctness matters, **enforce it in code, not prose.**

### Data Contracts: A Critical Enforcement Mechanism

Data contracts formalize expectations between data producers and consumers. They belong in Layer 3 because they **enforce** rather than **suggest**.

```yaml
# Example: customer_features contract
contract:
  name: customer_features
  owner: ml-team@company.com

schema:
  - name: customer_id
    type: string
    not_null: true
  - name: lifetime_value
    type: float
    range: [0, 1000000]
  - name: churn_score
    type: float
    range: [0, 1]

quality:
  freshness: "< 24 hours"
  row_count: "> 10000"
  null_rate:
    lifetime_value: "< 0.01"
```

**Why data contracts matter for data scientists:**
- **Upstream changes don't silently break models** — contract violations trigger alerts
- **Data quality expectations are explicit** — not buried in code or tribal knowledge
- **Cross-team agreements are enforceable** — not just documented hopes

→ *Deep dive: [Data Contracts](../04-data-science-workflows/data-contracts.md)*

---

## Why Separation Matters

Each layer optimizes for different things:

| Layer | Optimizes For | Trade-off |
|-------|---------------|-----------|
| Rules | Consistency | Can cause context bloat if overused |
| Playbooks | Flexibility | Requires human judgment |
| Code/CI | Correctness | Slower to iterate |

### Anti-patterns from Poor Separation

**Everything as rules:**
- Context window fills up
- AI becomes slow/expensive
- Rules conflict with each other

**Everything as prompts:**
- Inconsistent application
- Knowledge isn't reusable
- "Tribal knowledge" returns

**Everything as code:**
- Slow iteration
- Over-engineering simple checks
- Rigidity where flexibility is needed

---

## Decision Heuristics

### Move UP the stack (toward Rules) when:
- You keep repeating the same correction in code review
- A mistake is consistently being made
- The guidance is stable and universal

### Move DOWN the stack (toward Code) when:
- Violations cause real damage
- You need audit-trail enforcement
- Human judgment shouldn't be involved

### Keep in Playbooks when:
- The procedure is valuable but situational
- Different contexts need different approaches
- Human insight is part of the process

---

## Example: Data Leakage Prevention

Let's see how the same concern appears at each layer:

### Layer 1 (Rule)
```markdown
---
description: Prevent data leakage in ML pipelines
alwaysApply: true
---

# Data Leakage Prevention

- Never fit transformers on test data
- Split data before any preprocessing
- Validate temporal ordering in time-series
```

### Layer 2 (Skill)
```markdown
# Data Leakage Review Checklist

When reviewing ML code:
1. Trace data flow from raw to model
2. Identify all fit/transform operations
3. Verify train/test split happens first
4. Check for target leakage in features
5. Validate no future data in training
```

### Layer 3 (Code)
```python
# test_no_data_leakage.py
def test_no_leakage_in_features():
    """Verify no features contain target-derived information."""
    feature_cols = model.feature_names_
    assert 'target' not in feature_cols
    assert not any('future_' in col for col in feature_cols)

def test_temporal_ordering():
    """Verify training data predates test data."""
    assert train_df['date'].max() < test_df['date'].min()
```

---

## Practical Application

### For a New Project

1. **Start with 1-2 core rules** (Layer 1)
   - Project-wide invariants only
   - Keep them short

2. **Add playbooks as patterns emerge** (Layer 2)
   - When you find yourself explaining the same workflow
   - When code review catches the same issues

3. **Enforce critical paths in CI** (Layer 3)
   - Schema validation
   - Critical business logic
   - Security requirements

### For a Mature Project

Audit existing documentation:
- What's currently in docs that should be a rule?
- What rules are actually tutorials? (Move to playbooks)
- What playbook steps should be automated tests?

---

## See Also

- **Previous**: [Knowledge Execution System](knowledge-execution-system.md)
- **Next**: [Artifact Types](artifact-types.md)
- **Decision Framework**: [Decision Flow](decision-flow/README.md)
- **Practical**: [Writing Effective Rules](../03-rules-deep-dive/writing-effective-rules.md)
