# Box 3: Scope Check

[Home](../../README.md) > [Core Concepts](../README.md) > [Decision Flow](README.md) > Scope Check

---

## The Question

**Does this knowledge apply broadly across files, languages, or workflows?**

---

## What This Tests

Whether Cursor should **auto-apply** this guidance or wait for it to be explicitly requested.

- Broad scope → **Always-apply** or **auto-attach** rule
- Narrow scope → **On-demand** rule or continue to next check

---

## Decision Criteria

### Answer YES (Broad Scope) if:

| Criterion | Example |
|-----------|---------|
| Applies to all/most files in project | "Use consistent logging format" |
| Applies across multiple file types | "Document all public interfaces" |
| Relevant regardless of specific task | "Set random seeds" |
| Cross-cutting concern | "Handle errors explicitly" |
| Would catch issues anywhere | "Validate inputs" |

### Answer NO (Narrow Scope) if:

| Criterion | Example |
|-----------|---------|
| Only applies to specific file types | "SQL query optimization patterns" |
| Only relevant for certain tasks | "Model hyperparameter tuning" |
| Domain-specific knowledge | "Customer segmentation rules" |
| Rarely needed | "Legacy system integration" |
| Could cause confusion in other contexts | "Use method X" (but only for problem Y) |

---

## Rule Activation Strategies

Based on scope, choose the right activation:

### Always-Apply Rules
```markdown
---
description: Core project standards
alwaysApply: true
---
```
**Use for:** Universal principles that apply to everything.
**Count:** Keep to 1-2 maximum to preserve context window.

### Auto-Attach Rules (Glob-Based)
```markdown
---
description: Python-specific guidelines
globs: "**/*.py"
alwaysApply: false
---
```
**Use for:** File-type or directory-specific guidance.
**Benefit:** Only loads when relevant.

### On-Demand Rules
```markdown
---
description: SQL optimization patterns
alwaysApply: false
---
```
**Use for:** Specialized knowledge invoked with `@rule-name`.
**Benefit:** Available but not cluttering context.

---

## Examples

### Broad Scope (YES → Cursor Rule)

| Knowledge | Scope | Rule Type |
|-----------|-------|-----------|
| "Never fabricate data or results" | All work | Always-apply |
| "Add type hints to Python functions" | All Python | Auto-attach (*.py) |
| "Follow PEP8 style" | All Python | Auto-attach (*.py) |
| "Use parameterized queries" | All SQL | Auto-attach (*.sql) |
| "Handle exceptions explicitly" | All code | Always-apply |

### Narrow Scope (NO → Continue to Repeatability)

| Knowledge | Why Narrow | What Instead |
|-----------|------------|--------------|
| "Hyperparameter tuning strategies" | Only for ML training | Skill or on-demand rule |
| "Customer churn prediction features" | Domain-specific | On-demand or skill |
| "Legacy API migration patterns" | Specific situation | On-demand rule |
| "Dashboard visualization standards" | Only for dashboards | Auto-attach (dashboard/*) |

---

## Scope vs. Context Budgeting

Every rule consumes context tokens. Balance scope against budget:

### The Trade-off

```
More Always-Apply Rules
        ↓
More Context Usage
        ↓
Less Room for Code
        ↓
Potentially Worse Performance
```

### Guidelines

| Project Size | Always-Apply Rules | Auto-Attach Rules | On-Demand Rules |
|--------------|-------------------|-------------------|-----------------|
| Small | 1-2 | 2-3 | Few |
| Medium | 1-2 | 5-10 | Several |
| Large | 1-2 | 10-20 | Many |

**Key insight:** Keep always-apply rules minimal. Most rigor should be in auto-attach rules.

---

## Edge Cases

### "It applies to everything, but it's long"

**Answer:** Split into:
- Short always-apply summary
- Detailed on-demand reference

```markdown
# Always-apply (short)
---
description: Data validation principles
alwaysApply: true
---
Validate all data inputs. For detailed validation patterns, invoke @data-validation-patterns.

# On-demand (detailed)
---
description: Detailed data validation patterns
alwaysApply: false
---
[Comprehensive validation examples and patterns...]
```

### "It applies to Python AND notebooks"

**Answer:** Use multiple globs or separate rules.

```markdown
---
description: Data science standards
globs:
  - "**/*.py"
  - "**/*.ipynb"
---
```

### "It's broad, but I'm not sure it's always relevant"

**Answer:** Start with auto-attach, promote to always-apply if needed.
- Observe how often it's relevant
- If consistently useful, broaden scope
- If often irrelevant, narrow scope

### "Different teams need different scopes"

**Answer:** Use directory-based auto-attach.

```markdown
# Team A
---
globs: "team-a/**/*.py"
---

# Team B
---
globs: "team-b/**/*.py"
---
```

---

## Common Mistakes

### Mistake 1: Everything Always-Applies
```
# BAD: 10 always-apply rules
Context window is overwhelmed

# BETTER: 2 always-apply, rest auto-attach
Core principles always, details on-demand
```

### Mistake 2: Too Narrow Auto-Attach
```
# BAD: Only applies to one file
globs: "src/utils/specific_file.py"

# BETTER: If it's that specific, make it on-demand or inline comment
```

### Mistake 3: Ignoring File Types
```
# BAD: Python rule applied to everything
alwaysApply: true
"Use list comprehensions instead of loops"

# BETTER: Scope to Python
globs: "**/*.py"
```

---

## Outcomes

| Answer | Artifact Type | Activation |
|--------|---------------|------------|
| **YES (universal)** | Cursor Rule | Always-apply |
| **YES (file-type)** | Cursor Rule | Auto-attach with globs |
| **NO** | Continue | [Repeatability Check](repeatability-check.md) |

---

## See Also

- **Previous Decision**: [Enforcement Check](enforcement-check.md)
- **Next Decision**: [Repeatability Check](repeatability-check.md)
- **Related**: [Context Budgeting](../../03-rules-deep-dive/context-budgeting.md)
- **Overview**: [Decision Flow](README.md)
