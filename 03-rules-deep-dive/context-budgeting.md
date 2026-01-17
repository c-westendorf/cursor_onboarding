# Context Budgeting

[Home](../README.md) > [Rules Deep Dive](README.md) > Context Budgeting

---

## Overview

Every rule consumes tokens from Cursor's context window. Effective context budgeting ensures your rules help rather than hinder.

---

## The Problem

```
┌─────────────────────────────────────────────┐
│              Context Window                  │
│  ┌────────────────────────────────────────┐ │
│  │ Your Code (what you're working on)     │ │
│  ├────────────────────────────────────────┤ │
│  │ Rules (always-apply + auto-attach)     │ │
│  ├────────────────────────────────────────┤ │
│  │ Conversation History                   │ │
│  ├────────────────────────────────────────┤ │
│  │ AI's Response Space                    │ │
│  └────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘

If rules take up too much space:
- Less room for your actual code
- Less room for AI to reason
- Slower responses
- Higher costs
```

---

## Budget Guidelines

### Token Estimates

| Content Type | Approximate Tokens |
|--------------|-------------------|
| 100 words of rule content | ~150 tokens |
| Code example (10 lines) | ~50-100 tokens |
| Average rule file (100 lines) | ~500-1000 tokens |

### Budget Allocation

| Project Size | Always-Apply | Auto-Attach (active) | Available for Code |
|--------------|--------------|---------------------|-------------------|
| Small | 1-2 rules (~1K tokens) | 2-3 rules (~2K) | High |
| Medium | 1-2 rules (~1K tokens) | 5-10 rules (~5K) | Medium |
| Large | 1-2 rules (~1K tokens) | 10-20 rules (~10K) | Monitor |

**Key insight:** Always-apply rules are always consuming budget. Auto-attach rules only consume when relevant files are in context.

---

## Optimization Strategies

### 1. Minimize Always-Apply Rules

```markdown
# BAD: Many always-apply rules
.cursor/rules/
├── style.mdc          (alwaysApply: true)
├── testing.mdc        (alwaysApply: true)
├── security.mdc       (alwaysApply: true)
├── documentation.mdc  (alwaysApply: true)
└── logging.mdc        (alwaysApply: true)

# GOOD: One core always-apply, rest auto-attach
.cursor/rules/
├── core-principles.mdc  (alwaysApply: true)  # 50 lines
├── python-style.mdc     (globs: **/*.py)
├── testing.mdc          (globs: tests/**/*.py)
├── security.mdc         (globs: **/*.py)
└── documentation.mdc    (globs: docs/**/*.md)
```

### 2. Use Specific Globs

```yaml
# BAD: Too broad
globs: "**/*"  # Matches everything!

# GOOD: Specific
globs: "**/*.py"  # Only Python files

# BETTER: Even more specific
globs: "src/ml/**/*.py"  # Only ML module
```

### 3. Keep Rules Concise

```markdown
# BAD: 500-line rule with extensive examples
[Long explanation...]
[10 examples...]
[Full API documentation...]

# GOOD: Core guidance with reference to details
[Key principles in 50 lines]
For detailed examples, use @rule-name-detailed
```

### 4. Split Large Rules

```markdown
# BAD: One massive rule
sql-everything.mdc (400 lines)

# GOOD: Focused rules
sql-safety.mdc (50 lines, auto-attach)
sql-optimization.mdc (200 lines, on-demand)
sql-migrations.mdc (100 lines, on-demand)
```

### 5. Use On-Demand for Reference

```markdown
# Short auto-attach rule
---
description: SQL basics
globs: "**/*.sql"
---

# SQL Safety

- Use parameterized queries
- Limit results for exploration
- Be explicit about columns

For optimization patterns: @sql-optimization
For migration patterns: @sql-migrations
```

---

## Measuring Usage

### Check Active Rules

In Cursor, you can see which rules are currently active. Monitor:
- How many rules activate for typical workflows
- Which rules are rarely/never used
- Total token consumption

### Signs of Over-Budget

| Symptom | Likely Cause |
|---------|--------------|
| Slow responses | Too much context |
| Rules being ignored | Too many competing rules |
| Truncated code in responses | No room for output |
| Inconsistent behavior | Rules conflicting |

---

## Rule Pruning

### Quarterly Audit

1. **List all rules**
2. **Check usage frequency**
   - Which rules are actively helping?
   - Which are never triggered?
3. **Assess value**
   - Does this rule prevent real problems?
   - Is it teaching something useful?
4. **Take action**
   - Demote: always-apply → auto-attach
   - Narrow: broad globs → specific globs
   - Consolidate: merge similar rules
   - Remove: delete unused rules

### Demotion Patterns

```
Always-Apply → Auto-Attach
(if it doesn't need to apply everywhere)

Auto-Attach → On-Demand
(if it's rarely needed)

On-Demand → Remove
(if never invoked)
```

---

## The `.cursorignore` Strategy

Excluding files from indexing also helps with context:

```
# .cursorignore

# Large data files
data/
*.csv
*.parquet

# Build artifacts
dist/
build/
node_modules/

# Logs and outputs
logs/
*.log
output/

# Model files
models/
*.pkl
*.h5

# Documentation not needed in context
docs/archive/
```

**Why this helps:**
- Less to search through
- Faster indexing
- More focused context

---

## Context-Aware Rule Design

### Principle: Load What's Needed

```markdown
# Core rule (always-apply, short)
---
description: Universal principles
alwaysApply: true
---

Be reproducible. Be explicit. Don't fabricate.

# Domain rules (auto-attach, medium)
---
description: ML training guidelines
globs: "src/ml/**/*.py"
---

[ML-specific guidance...]

# Reference (on-demand, can be long)
---
description: Comprehensive ML patterns
alwaysApply: false
---

[Detailed patterns, invoked when needed...]
```

### Principle: Gradual Depth

```
Level 1: Core principles (always visible)
    ↓
Level 2: Domain patterns (visible in relevant files)
    ↓
Level 3: Detailed reference (visible when invoked)
```

---

## Example: Optimized Rule Set

### Small Project (~3K tokens of rules)

```
.cursor/rules/
├── core.mdc              # alwaysApply, 30 lines (~200 tokens)
├── python.mdc            # globs: **/*.py, 80 lines (~500 tokens)
└── sql.mdc               # globs: **/*.sql, 60 lines (~400 tokens)
```

### Medium Project (~8K tokens of rules)

```
.cursor/rules/
├── core.mdc              # alwaysApply, 50 lines
├── python/
│   ├── style.mdc         # globs: **/*.py
│   ├── testing.mdc       # globs: tests/**/*.py
│   └── typing.mdc        # globs: **/*.py
├── ml/
│   ├── training.mdc      # globs: src/ml/**/*
│   └── evaluation.mdc    # globs: src/ml/**/*
├── sql/
│   ├── safety.mdc        # globs: **/*.sql
│   └── optimization.mdc  # on-demand
└── notebooks/
    └── practices.mdc     # globs: **/*.ipynb
```

### Large Project (budget carefully)

```
.cursor/rules/
├── core.mdc              # alwaysApply, VERY short
├── [domain-specific auto-attach rules]
└── reference/            # All on-demand
    ├── detailed-patterns.mdc
    ├── legacy-systems.mdc
    └── advanced-topics.mdc
```

---

## See Also

- **Previous**: [Writing Effective Rules](writing-effective-rules.md)
- **Next**: [Rule Examples](examples/README.md)
- **Related**: [Workspace Organization](../06-workspace-organization/README.md)
