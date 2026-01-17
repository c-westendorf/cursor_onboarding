# Rules Deep Dive

[Home](../README.md) > Rules Deep Dive

---

## Overview

This section covers everything you need to know about Cursor rules: how they work, how to write them effectively, and how to manage context.

---

## Documents in This Section

| Document | Description |
|----------|-------------|
| [MDC File Anatomy](mdc-file-anatomy.md) | Structure of `.mdc` files: frontmatter and content |
| [Rule Types](rule-types.md) | Always-apply, auto-attach, and on-demand rules |
| [Writing Effective Rules](writing-effective-rules.md) | Best practices with concrete examples |
| [Context Budgeting](context-budgeting.md) | Managing token usage and rule scope |
| [Examples](examples/README.md) | Annotated real-world rule examples |

---

## Quick Reference

### File Location
```
.cursor/rules/*.mdc
```

### Basic Structure
```markdown
---
description: Short description of the rule's purpose
globs: optional/path/pattern/**/*
alwaysApply: false
---

# Rule Title

Rule content in markdown format.
```

### Rule Activation Types

| Type | Frontmatter | When Active |
|------|-------------|-------------|
| Always-Apply | `alwaysApply: true` | Every interaction |
| Auto-Attach | `globs: "**/*.py"` | When matching files are in context |
| On-Demand | `alwaysApply: false` + no globs | When invoked with `@rule-name` |

---

## Suggested Reading Order

1. **Getting Started with Rules**
   - [MDC File Anatomy](mdc-file-anatomy.md) — understand the format
   - [Rule Types](rule-types.md) — learn when rules activate

2. **Writing Good Rules**
   - [Writing Effective Rules](writing-effective-rules.md) — best practices
   - [Examples](examples/README.md) — learn from real examples

3. **Advanced Topics**
   - [Context Budgeting](context-budgeting.md) — optimize token usage

---

## Key Concepts

### Rules Are Not Tutorials
Rules encode **invariants** — things that should always (or never) be true. They are constraints and guardrails, not how-to guides.

```
# Good Rule Content
"Never train on test data"
"Always validate input shapes"
"Use parameterized SQL queries"

# Bad Rule Content (These are tutorials)
"Step 1: Import pandas"
"Step 2: Load the data"
"Step 3: Clean the data"
```

### Rules Should Be Stable
Only codify knowledge that will be valid for 6+ months. Ephemeral or situational guidance belongs in prompts or skills, not rules.

### Rules Consume Context
Every rule you add consumes tokens. Be strategic about what rules are always-apply vs. auto-attach vs. on-demand.

---

## Common Questions

### How many rules should I have?

| Project Size | Always-Apply | Auto-Attach | On-Demand |
|--------------|--------------|-------------|-----------|
| Small | 1-2 | 2-3 | Few |
| Medium | 1-2 | 5-10 | Several |
| Large | 1-2 | 10-20 | Many |

**Key:** Keep always-apply rules minimal (1-2). Most rules should be auto-attach.

### Should I put rules in version control?

**Yes.** Rules are code. They should be:
- Version controlled
- Code reviewed
- Documented
- Tested against real workflows

### How do I share rules across projects?

See [Marketplace Distribution](../08-marketplace/distribution/README.md) for:
- Git submodules approach (recommended)
- Manual import approach

---

## See Also

- **Previous Section**: [Core Concepts](../02-core-concepts/README.md)
- **Next Section**: [Data Science Workflows](../04-data-science-workflows/README.md)
- **Shared Rules**: [Marketplace Catalog](../08-marketplace/catalog/README.md)
- **Reference**: [MDC Schema](../reference/mdc-schema.md)
