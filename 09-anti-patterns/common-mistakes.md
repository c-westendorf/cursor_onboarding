# Common Mistakes

[Home](../README.md) > [Anti-Patterns](README.md) > Common Mistakes

---

## Over-Codification

### What It Looks Like

```
.cursor/rules/
├── style.mdc           (alwaysApply: true)
├── testing.mdc         (alwaysApply: true)
├── security.mdc        (alwaysApply: true)
├── documentation.mdc   (alwaysApply: true)
├── naming.mdc          (alwaysApply: true)
├── error-handling.mdc  (alwaysApply: true)
├── logging.mdc         (alwaysApply: true)
├── performance.mdc     (alwaysApply: true)
├── pandas.mdc          (alwaysApply: true)
├── sql.mdc             (alwaysApply: true)
└── ... (15 more)
```

### Why It's Bad

- **Context bloat**: Rules consume tokens, leaving less for actual work
- **Conflicts**: More rules = more chance of contradictions
- **Slow responses**: AI processing all that context
- **Ignored rules**: AI may skip rules when overwhelmed

### How to Fix

1. **Audit rules**: Which are actually used?
2. **Demote**: Always-apply → Auto-attach → On-demand
3. **Consolidate**: Merge similar rules
4. **Delete**: Remove unused rules

**Target:**
- 1-2 always-apply rules
- 5-10 auto-attach rules
- On-demand for detailed references

---

## Under-Codification

### What It Looks Like

- No `.cursor/rules/` directory
- One generic rule (or none)
- Repeating same corrections in every chat
- "The AI doesn't understand our project"

### Why It's Bad

- **Inconsistency**: AI reinvents patterns each time
- **Waste**: Repeating same instructions
- **Poor quality**: Missing domain-specific guidance
- **Slow onboarding**: New members don't get team knowledge

### How to Fix

1. **Track patterns**: Note repeated corrections
2. **Create rules**: For frequently-repeated guidance
3. **Add context**: Project-specific information
4. **Start small**: 2-3 focused rules, then expand

**Start with:**
```markdown
---
description: Core project standards
alwaysApply: true
---

# Project Standards

- [Your top 3-5 most common corrections]
- [Key project-specific patterns]
- [Important domain knowledge]
```

---

## Wrong Codification

### Tutorial Rules

**Bad:**
```markdown
# How to Use Pandas

Step 1: Import pandas with `import pandas as pd`
Step 2: Load your data with `pd.read_csv()`
Step 3: Check the shape with `df.shape`
Step 4: Look at the head with `df.head()`
...
```

**Good:**
```markdown
# Pandas Standards

- Use vectorized operations, not loops
- Prefer explicit column selection
- Handle nulls explicitly
- Use method chaining for transformations
```

**Fix:** Rules are constraints, not tutorials. State what to do/avoid, not how-to steps.

### Ephemeral Rules

**Bad:**
```markdown
# Current Sprint Focus

- We're using XGBoost for the churn model
- John is the SME for customer data
- Deploy to staging by Friday
```

**Good:** Don't put ephemeral information in rules. Use:
- Project documentation
- Team chat
- Tickets/issues

### Wrong Activation Type

**Bad:**
```yaml
# Detailed SQL reference (500 lines)
alwaysApply: true
```

**Good:**
```yaml
# Detailed SQL reference (500 lines)
alwaysApply: false
# On-demand, invoke with @sql-reference
```

**Fix:** Match activation to usage:
- Always-apply: Only universal, short principles
- Auto-attach: Domain-specific, medium length
- On-demand: Detailed references, rarely needed

---

## Workspace Mistakes

### Giant Workspace

**Bad:**
```
company-workspace/
├── project-a/          # Different team
├── project-b/          # Different domain
├── project-c/          # Different data
├── shared-utils/       # Used everywhere
└── .cursor/rules/      # Rules for everything?
```

**Good:**
```
project-a-workspace/
├── src/
└── .cursor/rules/      # Rules for project-a only

project-b-workspace/
├── src/
└── .cursor/rules/      # Rules for project-b only
```

**Fix:** Organize by product, not by org chart.

### Cross-Domain Rules

**Bad:**
```markdown
# Global Data Standards

For customer analytics: do X
For fraud detection: do Y
For recommendation engine: do Z
```

**Good:** Separate rules for separate domains.

---

## Recovery Strategies

### If Over-Codified

1. **List all rules** and their activation type
2. **Audit usage**: Which rules are actually helping?
3. **Consolidate**: Merge overlapping rules
4. **Demote**: Move rarely-used to on-demand
5. **Delete**: Remove unused rules

### If Under-Codified

1. **Track feedback**: What do you repeat?
2. **Prioritize**: Most common first
3. **Create incrementally**: One rule at a time
4. **Test**: Verify rules work

### If Wrongly Codified

1. **Apply decision flow**: Where should this knowledge be?
2. **Rewrite**: Convert tutorials to constraints
3. **Move**: Ephemeral info out of rules
4. **Restructure**: Match activation to usage

---

## See Also

- **Decision Framework**: [Decision Flow](../02-core-concepts/decision-flow/README.md)
- **Context Management**: [Context Budgeting](../03-rules-deep-dive/context-budgeting.md)
- **Organization**: [Workspace Organization](../06-workspace-organization/README.md)
