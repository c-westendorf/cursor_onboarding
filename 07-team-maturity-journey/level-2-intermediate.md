# Level 2: Intermediate

[Home](../README.md) > [Team Maturity](README.md) > Level 2: Intermediate

---

## Timeline: Weeks 2-4

---

## Goals

1. Master rule types and activation
2. Manage context effectively
3. Build domain-specific rules
4. Understand the decision flow

---

## Learning Path

### Week 2-3: Rule Mastery

**Rule Types**
- [ ] Read [Rule Types](../03-rules-deep-dive/rule-types.md)
- [ ] Convert always-apply rules to auto-attach where appropriate
- [ ] Create on-demand rules for detailed references
- [ ] Understand globs patterns

**Decision Framework**
- [ ] Read [Decision Flow](../02-core-concepts/decision-flow/README.md)
- [ ] Walk through flow with existing rules
- [ ] Identify knowledge that should be rules
- [ ] Identify knowledge that should be skills/prompts

### Week 3-4: Context Management

**Budgeting**
- [ ] Read [Context Budgeting](../03-rules-deep-dive/context-budgeting.md)
- [ ] Audit current rules for efficiency
- [ ] Set up comprehensive `.cursorignore`
- [ ] Optimize rule lengths

**Organization**
- [ ] Read [Directory Structures](../06-workspace-organization/directory-structures.md)
- [ ] Organize rules by domain
- [ ] Create reference documents for AI

---

## Key Skills to Develop

### Rule Activation Strategy

```
.cursor/rules/
├── core.mdc              # alwaysApply: true (1-2 only)
├── python-style.mdc      # globs: **/*.py
├── sql-safety.mdc        # globs: **/*.sql
├── ml-training.mdc       # globs: src/ml/**/*
└── detailed-patterns.mdc # On-demand (@detailed-patterns)
```

### Glob Patterns

| Pattern | Matches |
|---------|---------|
| `**/*.py` | All Python files |
| `src/ml/**/*` | Everything under src/ml |
| `*.{py,ipynb}` | Python files and notebooks |
| `tests/**/*.py` | Test Python files |

### Context-Aware Prompting

**Good:**
```
Using the patterns in @ml-training.mdc and the schema in
@docs/data-dictionary.md, write a feature engineering pipeline
for customer churn prediction.
```

**Better:**
```
Context:
- Following @ml-training.mdc patterns
- Using @docs/data-dictionary.md schema
- Target: customer churn (binary classification)

Task: Create feature engineering pipeline with:
1. Temporal features (recency, frequency)
2. Behavioral features (from events table)
3. Demographic features (from users table)
```

---

## Rules to Create

### Domain-Specific Rule

```markdown
---
description: ML training standards for this project
globs: "src/ml/**/*.py"
alwaysApply: false
---

# ML Training Standards

## Data Splitting
- Always split before preprocessing
- Use stratification for imbalanced classes
- Set random_state for reproducibility

## Evaluation
- Always compare to baseline
- Report multiple metrics
- Include confidence intervals

## Logging
- Log all hyperparameters
- Save model configs
- Track data versions
```

### On-Demand Reference

```markdown
---
description: Detailed pandas patterns (use @pandas-patterns)
alwaysApply: false
---

# Advanced Pandas Patterns

[Detailed examples and patterns...]
[This can be longer since it's on-demand]
```

---

## Milestone: Level 2 Complete

You've completed Level 2 when:

- [ ] Using multiple rule types effectively
- [ ] Rules organized by scope and domain
- [ ] Context usage is optimized
- [ ] Understand decision flow for new knowledge
- [ ] Can teach Level 1 to others

---

## Common Challenges

### "Too many rules are loading"

**Solution:**
1. Audit with: which rules active for typical task?
2. Convert always-apply → auto-attach
3. Make detailed rules on-demand

### "Rules conflict with each other"

**Solution:**
1. Review for overlapping guidance
2. Make one rule authoritative
3. Remove or consolidate duplicates

### "Don't know where to put new knowledge"

**Solution:** Use the decision flow:
1. Stable? → Continue
2. Should block CI? → Code
3. Applies broadly? → Rule
4. Repeatable? → Skill
5. Else → Human judgment

---

## Next Steps

When you've completed the milestone checklist:
→ [Level 3: Advanced](level-3-advanced.md)

---

## See Also

- **Previous**: [Level 1: Beginner](level-1-beginner.md)
- **Decision Flow**: [Full Framework](../02-core-concepts/decision-flow/README.md)
- **Context**: [Context Budgeting](../03-rules-deep-dive/context-budgeting.md)
