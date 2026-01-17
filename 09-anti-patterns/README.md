# Anti-Patterns

[Home](../README.md) > Anti-Patterns

---

## Overview

Common mistakes when using Cursor that reduce effectiveness. Learn what to avoid and how to recover.

---

## Quick Reference

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Over-codification | Too many rules, context bloat | Fewer, focused rules |
| Under-codification | Repeating same feedback | Add targeted rules |
| Tutorial rules | Rules that teach instead of constrain | Rewrite as constraints |
| Workspace sprawl | Giant workspace, conflicting rules | Product-centric organization |

---

## Documents in This Section

| Document | Description |
|----------|-------------|
| [Common Mistakes](common-mistakes.md) | Detailed anti-patterns and fixes |

---

## The Three Failure Modes

### 1. Over-Codification

**Symptoms:**
- 20+ rules loaded at once
- AI responses slow or inconsistent
- Rules contradict each other
- Every guideline is a rule

**Fix:** [See Over-Codification](common-mistakes.md#over-codification)

### 2. Under-Codification

**Symptoms:**
- Repeating same corrections in code review
- Inconsistent output across team members
- "The AI doesn't understand our project"
- No rules at all

**Fix:** [See Under-Codification](common-mistakes.md#under-codification)

### 3. Wrong Codification

**Symptoms:**
- Rules that read like tutorials
- Ephemeral information in rules
- Conflicting guidance
- Rules in wrong activation category

**Fix:** [See Wrong Codification](common-mistakes.md#wrong-codification)

---

## Self-Assessment

### Signs You're Over-Codifying
- [ ] More than 2 always-apply rules
- [ ] Rules over 300 lines
- [ ] AI seems to ignore some rules
- [ ] Responses are slow

### Signs You're Under-Codifying
- [ ] No custom rules
- [ ] Repeating same feedback
- [ ] AI output varies wildly
- [ ] New team members struggle

### Signs of Wrong Codification
- [ ] Rules contain step-by-step tutorials
- [ ] Rules mention specific deadlines/versions
- [ ] Rules for one-off situations
- [ ] Can't decide rule vs skill vs prompt

---

## See Also

- **Detailed Guide**: [Common Mistakes](common-mistakes.md)
- **Decision Framework**: [Decision Flow](../02-core-concepts/decision-flow/README.md)
- **Context Management**: [Context Budgeting](../03-rules-deep-dive/context-budgeting.md)
