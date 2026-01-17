# Review Process

[Home](../../README.md) > [Marketplace](../README.md) > [Governance](README.md) > Review Process

---

## Overview

All marketplace contributions require review by two people before merging.

---

## Review Workflow

```
Submission → Automated Checks → Reviewer 1 → Reviewer 2 → Merge
```

### 1. Automated Checks (CI/CD)

Runs automatically on PR:
- YAML frontmatter validation
- Markdown linting
- Spell check
- Length limits
- Duplicate detection

**Must pass before human review.**

### 2. Domain Review

First reviewer is a **domain expert**:
- Content is technically accurate
- Examples work correctly
- Patterns are appropriate
- Fills a real need

### 3. Governance Review

Second reviewer checks **process**:
- Follows templates
- Proper categorization
- No conflicts with existing rules
- Documentation complete

---

## Review Criteria

### For Rules

| Criterion | Check |
|-----------|-------|
| Stability | Knowledge valid 6+ months? |
| Scope | Applies broadly across teams? |
| Clarity | Clear what to do/not do? |
| Examples | Working code examples? |
| Length | Under 300 lines? |
| No conflicts | Doesn't contradict existing? |

### For Skills

| Criterion | Check |
|-----------|-------|
| Repeatability | Clear steps to follow? |
| Value | Helps multiple teams? |
| Structure | Follows template? |
| Checkpoints | Validation points included? |

### For Prompts

| Criterion | Check |
|-----------|-------|
| Usefulness | Solves real problem? |
| Variables | Clearly marked? |
| Example | Shows actual usage? |

---

## Providing Feedback

### Requesting Changes

```markdown
## Changes Requested

### Content
- [ ] Example in line 45 has syntax error
- [ ] Missing handling for edge case X

### Process
- [ ] Add `category` to frontmatter
- [ ] Reduce length (currently 350 lines, max 300)
```

### Approving

```markdown
LGTM (Looks Good To Me)

✅ Content accurate
✅ Examples work
✅ Follows standards
```

---

## Timeline

| Stage | Expected Time |
|-------|---------------|
| Automated checks | Minutes |
| First reviewer assigned | 24-48 hours |
| First review complete | 3-5 business days |
| Second review complete | 2-3 business days |
| Merge | Same day as final approval |

---

## Escalation

If review is delayed:
1. Comment on PR asking for update
2. Tag marketplace maintainers
3. Raise in team channel

---

## See Also

- [Quality Standards](quality-standards.md)
- [Contribution Guide](contribution-guide.md)
