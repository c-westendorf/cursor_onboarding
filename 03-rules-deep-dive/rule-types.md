# Rule Types

[Home](../README.md) > [Rules Deep Dive](README.md) > Rule Types

---

## Overview

Cursor rules activate in different ways depending on their configuration. Understanding these types helps you choose the right activation strategy.

---

## The Three Types

```
┌─────────────────┐    ┌─────────────────────┐    ┌─────────────────┐
│  Always Apply   │───▶│    Auto-Attach      │───▶│    On-Demand    │
│Global Invariants│    │File-Type Triggered  │    │@rule Invocation │
└─────────────────┘    └─────────────────────┘    └─────────────────┘
      1-2 rules            5-20 rules              Many rules
```

---

## Type 1: Always-Apply Rules

### Configuration

```yaml
---
description: Core project standards
alwaysApply: true
---
```

### When Active
Every single interaction with the AI, regardless of what files are open or what you're asking.

### Use For
- Universal project principles
- Non-negotiable constraints
- Cross-cutting concerns that apply everywhere

### Examples
| Rule Content | Why Always-Apply |
|--------------|------------------|
| "Never fabricate data or results" | Ethical constant |
| "Set random seeds for reproducibility" | Applies to all code |
| "No hardcoded credentials" | Security everywhere |

### Guidelines
- **Limit to 1-2 rules per project**
- Keep content short (under 100 lines)
- Only truly universal knowledge

### Example File

```markdown
---
description: Core data science principles
alwaysApply: true
---

# Core Principles

1. **Reproducibility**: All results must be reproducible. Set random seeds.
2. **Data Integrity**: Never modify source data. Work on copies.
3. **No Fabrication**: Never fabricate metrics, data, or results.
4. **Explicit > Implicit**: Be explicit about data transformations and assumptions.
```

---

## Type 2: Auto-Attach Rules

### Configuration

```yaml
---
description: Python-specific standards
globs: "**/*.py"
alwaysApply: false
---
```

### When Active
Automatically included when files matching the glob pattern are in context (open, referenced, or being discussed).

### Use For
- File-type specific guidance (Python, SQL, notebooks)
- Directory-specific rules (ml/, analytics/, frontend/)
- Domain-specific patterns

### Examples
| Glob Pattern | Rule Content |
|--------------|--------------|
| `**/*.py` | Python style and patterns |
| `**/*.sql` | SQL safety and optimization |
| `**/*.ipynb` | Notebook best practices |
| `src/ml/**/*` | ML-specific guidelines |
| `tests/**/*` | Testing standards |

### Guidelines
- **Most rules should be this type**
- Use specific globs to limit scope
- Can have 5-20+ of these rules

### Example File

```markdown
---
description: Pandas DataFrame best practices
globs: "**/*.py"
alwaysApply: false
---

# Pandas Best Practices

## Prefer Vectorized Operations

```python
# Bad
for i, row in df.iterrows():
    df.loc[i, 'new'] = row['a'] + row['b']

# Good
df['new'] = df['a'] + df['b']
```

## Use Explicit Column Selection

```python
# Bad: Implicit
result = df.copy()

# Good: Explicit
cols = ['id', 'name', 'value']
result = df[cols].copy()
```

## Method Chaining

```python
result = (
    df
    .query('age > 18')
    .groupby('category')
    .agg({'sales': 'sum'})
    .reset_index()
)
```
```

---

## Type 3: On-Demand Rules

### Configuration

```yaml
---
description: Specialized SQL optimization patterns
alwaysApply: false
# No globs — only activates when explicitly requested
---
```

### When Active
Only when explicitly invoked using `@rule-name` in a prompt.

### Use For
- Specialized knowledge that's rarely needed
- Long reference documentation
- Situation-specific guidance
- Detailed procedures that would bloat context

### Examples
| Rule Name | Content |
|-----------|---------|
| `@sql-optimization` | Detailed query optimization patterns |
| `@legacy-api` | Legacy system integration details |
| `@deployment-checklist` | Production deployment steps |
| `@security-audit` | Security review checklist |

### Guidelines
- Use for specialized or lengthy content
- Reference from other rules: "For details, use @rule-name"
- Good for domain-specific deep dives

### Example File

```markdown
---
description: SQL query optimization patterns (invoke with @sql-optimization)
alwaysApply: false
---

# SQL Optimization Patterns

## Index Usage

### When to Add Indexes
- Columns frequently used in WHERE clauses
- Columns used in JOIN conditions
- Columns used in ORDER BY

### When to Avoid Indexes
- Small tables (< 1000 rows)
- Columns with low cardinality
- Tables with frequent writes

## Query Patterns

### Pagination
```sql
-- Bad: OFFSET for large pages
SELECT * FROM users OFFSET 10000 LIMIT 10;

-- Good: Keyset pagination
SELECT * FROM users
WHERE id > :last_seen_id
ORDER BY id
LIMIT 10;
```

### Avoiding N+1
```sql
-- Bad: N+1 queries
SELECT * FROM orders WHERE user_id = ?;  -- called N times

-- Good: Single query with JOIN
SELECT o.*, u.name
FROM orders o
JOIN users u ON o.user_id = u.id;
```

[... more detailed patterns ...]
```

---

## Choosing the Right Type

### Decision Flow

```
Is this a universal project constraint?
│
├── YES → Always-Apply
│
└── NO → Does it apply to specific file types?
         │
         ├── YES → Auto-Attach (with globs)
         │
         └── NO → Is it frequently needed?
                  │
                  ├── YES → Auto-Attach (broad globs)
                  │
                  └── NO → On-Demand
```

### Quick Reference

| Characteristic | Rule Type |
|----------------|-----------|
| Ethical constraints | Always-Apply |
| Security fundamentals | Always-Apply |
| Python patterns | Auto-Attach (`**/*.py`) |
| SQL patterns | Auto-Attach (`**/*.sql`) |
| ML-specific | Auto-Attach (`ml/**/*`) |
| Specialized reference | On-Demand |
| Rare procedures | On-Demand |
| Long documentation | On-Demand |

---

## Combining Types

A mature project might have:

```
.cursor/rules/
├── core-principles.mdc        # Always-Apply (1 rule)
├── python-standards.mdc       # Auto-Attach: **/*.py
├── sql-safety.mdc             # Auto-Attach: **/*.sql
├── notebook-practices.mdc     # Auto-Attach: **/*.ipynb
├── ml-training.mdc            # Auto-Attach: src/ml/**/*
├── sql-optimization.mdc       # On-Demand (detailed)
└── legacy-integration.mdc     # On-Demand (specialized)
```

### Reference Pattern

In a shorter auto-attach rule, reference the detailed on-demand rule:

```markdown
---
description: SQL basics
globs: "**/*.sql"
---

# SQL Safety

Use parameterized queries. Avoid string concatenation.

For detailed optimization patterns, invoke @sql-optimization.
```

---

## Common Mistakes

### Mistake 1: Too Many Always-Apply

```
# BAD: 10 always-apply rules
Every interaction is slow, context is bloated

# GOOD: 1-2 always-apply, rest auto-attach
Core principles always, details when relevant
```

### Mistake 2: Auto-Attach Too Broad

```yaml
# BAD: Matches everything
globs: "**/*"

# GOOD: Specific to relevant files
globs: "**/*.py"
```

### Mistake 3: On-Demand Never Used

```
# BAD: Created but never referenced
Users don't know it exists

# GOOD: Mentioned in related rules
"For details, use @rule-name"
```

---

## See Also

- **Previous**: [MDC File Anatomy](mdc-file-anatomy.md)
- **Next**: [Writing Effective Rules](writing-effective-rules.md)
- **Context**: [Context Budgeting](context-budgeting.md)
