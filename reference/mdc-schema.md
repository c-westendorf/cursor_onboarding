# MDC Schema Reference

[Home](../README.md) > [Reference](README.md) > MDC Schema

---

## Overview

Complete specification for `.mdc` rule file format.

---

## File Structure

```
┌─────────────────────────────────┐
│ --- (YAML frontmatter start)   │
│ description: ...               │
│ globs: ...                     │
│ alwaysApply: ...               │
│ --- (YAML frontmatter end)     │
├─────────────────────────────────┤
│                                │
│ # Rule Title                   │
│                                │
│ Markdown content...            │
│                                │
└─────────────────────────────────┘
```

---

## YAML Frontmatter

### Required Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `description` | string | Max 100 chars | Brief summary shown in rule picker |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `globs` | string or array | none | File patterns for auto-attach |
| `alwaysApply` | boolean | `false` | Include in every conversation |

---

## Field Specifications

### description (Required)

**Purpose:** Displayed in Cursor's rule selection UI.

**Constraints:**
- Maximum 100 characters
- Should be descriptive enough to identify rule purpose
- No line breaks

**Examples:**
```yaml
# Good
description: Python testing standards for pytest

# Good
description: SQL query safety guidelines

# Bad (too long)
description: This rule provides comprehensive guidance for writing Python tests using the pytest framework including fixtures, mocking, and assertions

# Bad (too vague)
description: Code stuff
```

### globs (Optional)

**Purpose:** Automatically attach rule when matching files are in context.

**Syntax:** Standard glob patterns

**Single Pattern:**
```yaml
globs: "**/*.py"
```

**Multiple Patterns (array):**
```yaml
globs:
  - "**/*.py"
  - "**/*.ipynb"
```

**Alternative (brace expansion):**
```yaml
globs: "**/*.{py,ipynb}"
```

**Pattern Reference:**

| Pattern | Matches |
|---------|---------|
| `*` | Any characters except `/` |
| `**` | Any characters including `/` |
| `?` | Single character |
| `[abc]` | Character class |
| `{a,b}` | Alternation |

**Common Patterns:**

| Use Case | Pattern |
|----------|---------|
| All Python files | `**/*.py` |
| Python in src/ | `src/**/*.py` |
| Test files | `**/test_*.py` or `**/*_test.py` |
| Config files | `*.{json,yaml,yml,toml}` |
| SQL files | `**/*.sql` |
| Notebooks | `**/*.ipynb` |
| Everything in folder | `folder/**/*` |

### alwaysApply (Optional)

**Purpose:** Include rule in every conversation regardless of context.

**Values:**
- `true` - Always included
- `false` - Only when invoked or matched (default)

**Use Cases for `alwaysApply: true`:**
- Code style enforcement
- Security requirements
- Project conventions
- Response formatting

**Example:**
```yaml
---
description: Always use type hints in Python
alwaysApply: true
---
```

---

## Activation Matrix

| Configuration | Activation | Use Case |
|--------------|------------|----------|
| `alwaysApply: true` | Every conversation | Universal standards |
| `globs: "pattern"` | Matching files in context | Language/framework specific |
| Neither | Manual `@rulename` | Specialized guidance |

**Precedence:** `alwaysApply` > `globs` > Manual

---

## Markdown Body

### Recommended Structure

```markdown
---
description: Rule description
---

# Rule Title

Brief overview of what this rule covers.

## Requirements

- Requirement 1
- Requirement 2

## Patterns

### Good Pattern

```python
# Example of correct approach
```

### Bad Pattern

```python
# Example of what to avoid
```

## Exceptions

When this rule doesn't apply.
```

### Best Practices

**Do:**
- Use headers to organize sections
- Include code examples
- Show both good and bad patterns
- Keep total length under 300 lines
- Use bullet points for lists

**Don't:**
- Include tutorials or explanations
- Add excessive commentary
- Duplicate content from other rules
- Use complex nested structures

---

## Extended Frontmatter (Custom Fields)

While Cursor only uses `description`, `globs`, and `alwaysApply`, you can add custom fields for organization:

```yaml
---
description: Model evaluation standards
globs: "**/*.py"
alwaysApply: false
# Custom fields (ignored by Cursor, useful for governance)
version: "1.2.0"
author: "ml-team"
category: "ml"
tags: ["evaluation", "metrics"]
last_updated: "2024-01-15"
---
```

---

## Validation

### Schema Check

Ensure YAML is valid:
```bash
# Using yq
yq eval '.description' rule.mdc

# Using Python
python -c "import yaml; yaml.safe_load(open('rule.mdc').read().split('---')[1])"
```

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| Rule not appearing | Missing `---` delimiters | Ensure frontmatter has opening and closing `---` |
| Glob not matching | Wrong pattern syntax | Test pattern with `glob` tool |
| Description truncated | Over 100 characters | Shorten description |
| YAML parse error | Invalid syntax | Check for proper quoting, indentation |

---

## Complete Examples

### Always-Apply Rule

```yaml
---
description: Python code style requirements
alwaysApply: true
---

# Python Style

## Requirements

- Use type hints for all function signatures
- Maximum line length: 88 characters
- Use f-strings over .format()
```

### Auto-Attach Rule

```yaml
---
description: SQL query safety guidelines
globs: "**/*.sql"
---

# SQL Safety

## Requirements

- Always use parameterized queries
- Include comments explaining complex joins
- Limit result sets with TOP/LIMIT
```

### On-Demand Rule

```yaml
---
description: Database migration checklist
---

# Migration Checklist

Invoke with @migration-checklist when writing migrations.

## Pre-Migration

- [ ] Backup database
- [ ] Test in staging
- [ ] Review rollback plan
```

---

## See Also

- [MDC File Anatomy](../03-rules-deep-dive/mdc-file-anatomy.md)
- [Rule Types](../03-rules-deep-dive/rule-types.md)
- [Writing Effective Rules](../03-rules-deep-dive/writing-effective-rules.md)
